from mtp import MTPClient
import asyncio
import os

async def main():
    api_id = int(os.getenv("API_ID"))  # Get API_ID from environment variables
    api_hash = os.getenv("API_HASH")   # Get API_HASH from environment variables
    bot_token = os.getenv("BOT_TOKEN") # Get BOT_TOKEN from environment variables

    client = MTPClient(api_id, api_hash, bot_token)
    await client.start()
    result = await client.test_proxy("https://t.me/proxy?server=176.65.135.8&port=443&secret=eeRighJJvXrFGRMCIMJdCQ")
    print(f"Test Proxy Result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
