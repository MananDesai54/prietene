import asyncio
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from mcp_use import MCPAgent, MCPClient


async def main():
    config = {
        "mcpServers": {
            "http": {
                "url": "http://127.0.0.1:8000/sse"
            }
        }
    }

    client = MCPClient.from_dict(config=config)

    llm = ChatOpenAI(model="gpt-4.1")

    agent = MCPAgent(client=client, llm=llm, max_steps=30)

    result = await agent.run("What is the weather in NewYork Today? Any alerts are available?")
    print(result)


if __name__ == "__main__":
    load_dotenv()
    asyncio.run(main())
