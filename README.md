##  README.md

**Telegram MTProxy Tester with tdlib**

This project provides a Python script to test connection, speed, and ping of Telegram MTProto proxies using the tdlib library.

### Features

* Test connection to a Telegram MTProxy server.
* Measure download speed through the proxy. (Requires Telegram bot token)
* Get ping latency of the proxy server. 

### Setup

**Requirements:**

* Python 3.9 or above
* pip (package manager)

**Installation:**

1. Clone this repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. **Compile tdlib (Optional):**
   - If you're not using Ubuntu 20.04 or 22.04, you'll need to compile your own tdlib library following the instructions here: [https://tdlib.github.io/td/build.html](https://tdlib.github.io/td/build.html)
   - The included `libtdjson.so` file is pre-compiled for Ubuntu 20.04 and 22.04.

**Telegram App Credentials:**

1. Obtain your Telegram application ID and hash from the Telegram Developer Portal: [https://core.telegram.org/](https://core.telegram.org/) 

### Usage

**1. Import MTPClient**

```python
from mtp import MTPClient
```

**2. Client Setup**

```python
# Replace with your Telegram App credentials
api_id = YOUR_TELEGRAM_APP_ID
api_hash = 'YOUR_TELEGRAM_APP_HASH'

# Bot token is required for speed test
bot_token = "YOUR_BOT_TOKEN"

# Other configurations (optional)
database_encryption_key = 'test'
files_directory = 'BotDB'
lib_path = './libtdjson.so'  # Path to your compiled tdlib library (if applicable)

client = MTPClient(
    api_id=api_id,
    api_hash=api_hash,
    bot_token=bot_token,
    database_encryption_key=database_encryption_key,
    files_directory=files_directory,
    lib_path=lib_path
)
```

**3. Usage Examples (Asynchronous)**

```python
async def main():
    # Start the client
    await client.start()
    # Test connection (no authorization required)
    result = await client.test_proxy("https://t.me/proxy?server=server&port=port&secret=secret")
    print(f"Test Proxy Result: {result}")  # Returns True/False

    # Speed Test (requires bot token)
    result = await client.speed_test("https://t.me/proxy?server=server&port=port&secret=secret")
    print(f"Speed Test Result: {result}")  

    # Ping Proxy (no authorization required)
    result = await client.ping_proxy("https://t.me/proxy?server=server&port=port&secret=secret")
    print(f"Ping Proxy Result: {result}")  

# Run the asynchronous program
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

**Note:**

* Install `ujson` or `orjson` for better performance (Optional)

### License

hmmm, License
