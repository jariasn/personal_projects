import asyncio
from telethon import TelegramClient, events
from datetime import datetime
from queue import Queue
import sys
from collections import defaultdict
import re
import logging
import json
import yaml
import requests
import time
import base64
from io import BytesIO
from PIL import Image

def load_config_yaml():
    '''
    Helper function to load the config.yaml file.
    '''
    with open('config.yaml') as f:
        config = yaml.safe_load(f)
    return config['API_ID'], config['API_HASH'], config['GENERAL_CONTEXT']

api_id, api_hash, general_context = load_config_yaml()

# URL for the llama3 API
llama3_url = "http://localhost:11434/api/chat"

# URL for the llava API
llava_url = "http://localhost:11434/api/generate"

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the client and connect
client = TelegramClient('anon', api_id, api_hash)

# Initialize the conversation history
conversation_history = {}

# File to store prompts (just for debugging)
PROMPTS_FILE = 'llama3_prompts.json'

# Queue to store incoming messages
message_queue = Queue()

last_sender_id = None
custom_message = None

def save_prompt(messages):
    '''
    Save the prompt to a JSON file for debugging purposes.
    '''
    try:
        with open(PROMPTS_FILE, 'r+') as f:
            try:
                prompts = json.load(f)
            except json.JSONDecodeError:
                prompts = []
            
            prompts.append({
                'timestamp': datetime.now().isoformat(),
                'messages': messages
            })
            
            f.seek(0)
            json.dump(prompts, f, indent=2)
            f.truncate()
    except FileNotFoundError:
        with open(PROMPTS_FILE, 'w') as f:
            json.dump([{
                'timestamp': datetime.now().isoformat(),
                'messages': messages
            }], f, indent=2)

def llama3(messages):
    '''
    Send the messages to llama3 and return the response. 
    You can find more information about the Ollama API at https://github.com/ollama/ollama/blob/main/docs/api.md
    '''
    # Prepare the data to send to llama3
    data = {
        "model": "llama3",
        "messages": messages,
        "stream": False
    }

    headers = {
        'Content-Type': 'application/json'
    }

    # Save the prompt before sending it to llama3
    save_prompt(messages)

    response = requests.post(llama3_url, headers=headers, json=data)
    response_json = response.json()
    return response_json.get('message', {}).get('content', '')

def llava(image_path, prompt):
    '''
    Send an image to llava for analysis and return the response.
    '''
    with open(image_path, "rb") as image_file:
        image_data = base64.b64encode(image_file.read()).decode('utf-8')

    data = {
        "model": "llava",
        "prompt": prompt,
        "images": [image_data],
        "stream": False
    }

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(llava_url, headers=headers, json=data)
    response_json = response.json()
    return response_json.get('response', '')

async def fetch_chat_history(sender_id, limit=5):
    '''
    Fetch the last messages from the chat history for context.
    '''
    messages = await client.get_messages(sender_id, limit=limit)
    return [msg.message for msg in messages[::-1] if msg.message]

def update_system_prompt(context, conversation_history, sender_id):
    '''
    Update the system prompt if there are more than 5 messages in the 
    conversation history, as the previous messages are no longer relevant.
    '''
    if len(conversation_history[sender_id]) > 6:
        conversation_history[sender_id][0] = {"role": "system", "content": context}

conversation_history = defaultdict(list)
active_conversations = set()
custom_messages = {}
# Buffer to store messages for each sender
message_buffers = defaultdict(list)
# Dictionary to store the last message time for each sender
last_message_time = defaultdict(float)

async def handle_message(event):
    global conversation_history, active_conversations, message_buffers, last_message_time
    sender_id = event.sender_id

    # Add to active conversations if not already present
    active_conversations.add(sender_id)

    message_text = event.message.message  # Get the text content of the message

    if event.message.photo:
        # Handle image message
        image = await event.message.download_media(file=BytesIO())
        image_path = f"temp_image_{sender_id}.jpg"
        Image.open(image).save(image_path)
        
        # Use the message text as the prompt for Llava, or use a default prompt if no text
        prompt = message_text if message_text else "What is in this image? Give a detailed explanation"
        
        # Analyze image with Llava
        image_description = llava(image_path, prompt)
        
        # Construct a message that includes both the user's text and Llava's analysis
        combined_message = f"Based on this image analysis: {image_description}\n\nAnswer this: '{prompt}'"
        
        # Add the combined message to the buffer
        message_buffers[sender_id].append(combined_message)
    else:
        # Handle text-only message
        message_buffers[sender_id].append(message_text)
    
    last_message_time[sender_id] = time.time()
    
    logger.info(f"Received message from {sender_id}: {'Image with text' if event.message.photo else 'Text only'}")

async def process_messages():
    '''
    Process the messages in the message buffer.
    '''
    global conversation_history, custom_messages, message_buffers, last_message_time
    while True:
        current_time = time.time()
        for sender_id in list(active_conversations):
            if sender_id in message_buffers and (current_time - last_message_time[sender_id] >= 30 or sender_id in custom_messages):
                messages = message_buffers.pop(sender_id, [])
                if messages:
                    concatenated_message = " ".join(messages)
                    custom_message = custom_messages.pop(sender_id, None)
                    await process_single_message(sender_id, concatenated_message, custom_message)
        
        await asyncio.sleep(1)  # Check every second

async def process_single_message(sender_id, message_text, custom_message=None):
    '''
    Process a single message from a sender.
    '''
    global conversation_history

    # Get the sender's username and phone number
    sender = await client.get_entity(sender_id)
    sender_username = sender.username
    sender_phone = sender.phone

    logger.info(f"Processing message from sender username: {sender_username}, phone: {sender_phone}")

    # Read the contacts from the JSON file
    with open('contacts.json', 'r') as f:
        contacts = json.load(f)

    context = general_context
    name = "Default"
    # Check if the sender is in the contacts
    identifier = sender_username or sender_phone
    if identifier in contacts:
        contact = contacts[identifier]
        # Add the context from contacts
        context += " " + contact['context']
        name = contact['name']

    logger.info(f"Chatting with {name}")

    if not conversation_history[sender_id]:
        last_five_messages = await fetch_chat_history(sender_id)
        if last_five_messages:
            context_messages = " ".join(last_five_messages)
            system_prompt = f"{context} Here are the last messages from your chat for context: {context_messages}"
        else:
            system_prompt = f"{context} This is the start of your conversation."
        conversation_history[sender_id] = [{"role": "system", "content": system_prompt}]

    # Append the user message to the conversation history
    conversation_history[sender_id].append({"role": "user", "content": message_text})
    logger.info(f"User to Llama3: {message_text}")

    # Create a temporary copy of the conversation history
    temp_history = conversation_history[sender_id].copy()

    # Update the system prompt if there are more than 5 messages
    update_system_prompt(context, conversation_history, sender_id)

    if custom_message:
        custom_context = f"{context} It is IMPORTANT that you follow these instructions: {custom_message}. Now continue the conversation."
        temp_history[0] = {"role": "system", "content": custom_context}
        # Get the response from llama3 with the temporary conversation history
        response = llama3(temp_history)
    else:
        # Get the response from llama3 with the current conversation history if no custom message is provided
        response = llama3(conversation_history[sender_id])
    
    if not response:
        # Handle empty response from llama3
        logger.error("Received an empty response from llama3.")
        response = "I'm sorry, I'll get back to you soon."

    conversation_history[sender_id].append({"role": "assistant", "content": response})

    await client.send_message(sender_id, response)
    logger.info(f"Llama3 to {sender_id}: {response}")

async def custom_input_handler():
    '''
    Handle custom input from the user to send a custom message to a chat.
    '''
    global custom_messages
    while True:
        try:
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            line = line.strip()
            
            if line:
                match = re.match(r'(\d+):\s*(.*)', line)
                if match:
                    chat_id, message = match.groups()
                    chat_id = int(chat_id)
                    if chat_id in active_conversations:
                        logger.info(f"Applying custom message to chat {chat_id}: {message}")
                        custom_messages[chat_id] = message
                    else:
                        logger.info(f"Chat {chat_id} is not active. Custom message will not be applied.")
                else:
                    logger.info("Invalid format. Use 'chat_id: message' to send a custom message.")
        except Exception as e:
            logger.error(f"Error in custom input handler: {e}")
        await asyncio.sleep(0.1)

@client.on(events.NewMessage)
async def message_handler(event):
    await handle_message(event)

async def main():
    await client.start()
    logger.info("Client started")
    print("Bot is running. You can now type custom messages at any time.")
    print("Format: 'chat_id: your custom message'")
    
    asyncio.create_task(process_messages())
    asyncio.create_task(custom_input_handler())
    
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())