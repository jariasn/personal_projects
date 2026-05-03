from agent import Agent

def main():
    llama3_url = "http://localhost:11434/api/chat"  # URL for the Llama3 API
    agent = Agent(llama3_url)

    print("Chatbot started. Type 'exit' to leave.")

    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            print("Exiting chat...")
            break
        response = agent.get_response(user_input)
        print(f"Assistant: {response}")

if __name__ == '__main__':
    main()