import asyncio
from browser_use import Agent
from browser_use.llm import ChatOllama

llm = ChatOllama(
    model="qwen2.5-coder:14b",
)

agent = Agent(
    task="Go to google.com and search for the release date of spiderman no way home and tell me the answer.",
    llm=llm,
)

async def main():
    await agent.run()

asyncio.run(main())