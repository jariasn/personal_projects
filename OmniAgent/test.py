from openai import OpenAI

client = OpenAI(
  organization='org-9CT3gsZd5uk2uJS8TY2jV5gw',
  project='proj_NbbWatW259IjttGw8xptkM1h',
  
)

assistant = client.beta.assistants.create(
  name="Math Tutor",
  instructions="You are a personal math tutor. Write and run code to answer math questions.",
  tools=[{"type": "code_interpreter"}],
  model="gpt-4o-mini",
)
thread = client.beta.threads.create()


message = client.beta.threads.messages.create(
  thread_id=thread.id,
  role="user",
  content="I need to solve the equation `3x + 11 = 14`. Can you help me?"
)
