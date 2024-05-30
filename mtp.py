from pytdbot import Client, filters, types, utils
import asyncio
from pytdbot.types import LogStreamFile, Update
import logging, time
from urllib.parse import urlparse, parse_qs


"""
This class represents the results of a speed test performed using a proxy.

Attributes:
    success (bool, optional): Indicates whether the test was successful. 
    downloaded_bytes (int, optional): The number of bytes downloaded during the test. 
    download_time (float, optional): The time taken to download the data (seconds). 
    link (str, optional): The URL used for the speed test. 
    proxy (dict, optional): The proxy dictionary used for the test. 
    connect_test (bool, optional): Indicates whether the connection to the proxy was successful. 
    download_speed (float, optional): The calculated download speed in bytes per second. 
"""
class ProxySpeedTestResult:
    def __init__(self, success=None, downloaded_bytes=None, download_time=None, link=None, proxy=None, connect_test=None, download_speed=None):
        self.success = success
        self.downloaded_bytes = downloaded_bytes
        self.download_time = download_time
        self.link = link
        self.proxy = proxy
        self.connect_test = connect_test
        self.download_speed = download_speed
        self.download_time = download_time

            

"""
    A client to test MTProto proxies via telegram tdlib.

    Args:
        api_id (int): Your Telegram application ID.
        api_hash (str): Your Telegram application hash.
        database_encryption_key (bytes): The key used to encrypt the local database.
        bot_token (str, optional): Your Telegram bot token, Needed for speedtest. Defaults to None.
        files_directory (str, optional): The directory to store downloaded files. Defaults to 'BotDB'.
        lib_path (str, optional): The path to the Telegram TDLib library (.so or .dylib). Defaults to './libtdjson.so'.

    **Note:**

    You'll need to obtain your Telegram application ID and hash from the Telegram Developer Portal (https://core.telegram.org/).
"""
class MTPClient:
    def __init__(self, api_id, api_hash, database_encryption_key, bot_token=None, files_directory='BotDB', lib_path='./libtdjson.so') -> None:
        self.client = Client(
            api_id=api_id,
            api_hash=api_hash,
            token=bot_token,
            database_encryption_key=database_encryption_key,
            files_directory=files_directory,
            lib_path=lib_path
        )
        self.loop = self.client.loop
        
    async def start(self):
        await self.client.start()
        await self.client.disableProxy()
        
        
    def parse_proxy_link(self, link):
        """Parses an MTProxy link and returns a dictionary containing server, port, and secret.

        Args:
            link: The MTProxy link to parse.

        Returns:
            A dictionary containing 'server', 'port', and 'secret' keys, or None if parsing fails.

        Raises:
            ValueError: If the MTProxy link format is invalid.
        """

        parsed_url = urlparse(link)
        query_params = parse_qs(parsed_url.query)

        if 'server' not in query_params or 'port' not in query_params or 'secret' not in query_params:
            raise ValueError("Required parameters missing in MTProxy link.")

        try:
            return {
            'server': query_params['server'][0],
            'port': int(query_params['port'][0]),
            'secret': query_params['secret'][0]
            }
        except (ValueError, IndexError):
            raise ValueError("Invalid value(s) in MTProxy link parameters.")
        
        
    async def test_proxy(self, link: str = None, proxy: dict = None, dc: int = 4, timeout: int = 3) -> bool:
        """
        Sends a simple network request to the Telegram servers via proxy; for testing only. Can be called without authorization

        Args:
            link (str, optional): A proxy url.
                If provided, it will be parsed into a dictionary using `self.parse_proxy_link`
                
            proxy (dict, optional): A dictionary containing the explicit proxy configuration.
                The expected format is:

                ```
                {
                    "server": str (required),  # Proxy server domain or IP address
                    "port": int (required),    # Proxy server port number
                    "secret": str (optional),  # Proxy secret
                }
                ```
            dc (int, 4): The Telegram data center (DC) number to use for the test.
            
            timeout (int, 3): The maximum time (in seconds) to wait for a response
                from the Telegram servers. Defaults to 3 seconds.
                
        Returns:
            bool: True if the proxy connection appears successful, False otherwise.
                **Note:** This only indicates basic connectivity; it doesn't guarantee
                the proxy's functionality for Telegram API traffic.

        Raises:
            ValueError: If both `link` and `proxy` are provided, or if neither is provided.
        """

        if not link and not proxy:
            raise ValueError('link or proxy not provided')
        
        if link:
            proxy = self.parse_proxy_link(link)
            
        proxy = dict(
            type={"@type":"proxyTypeMtproto","secret": proxy['secret']}, 
            server=proxy['server'],
            port=proxy['port']
            )
        
        result = await self.client.testProxy(**proxy, timeout=timeout, dc_id=dc)
        
        if result.result['@type'] == 'ok':
            return True
        
        return False
            
    async def ping_proxy(self, link: str = None, proxy: dict = None) -> dict:
        """
            Computes time needed to receive a response from a Telegram server through a proxy. Can be called without authorization


            Args:
                link (str, optional): A proxy url.
                If provided, it will be parsed into a dictionary using `self.parse_proxy_link`
                
                proxy (dict, optional): A dictionary containing the explicit proxy configuration.
                    The expected format is:

                    ```
                    {
                        "server": str (required),  # Proxy server domain or IP address
                        "port": int (required),    # Proxy server port number
                        "secret": str (optional),  # Proxy secret
                    }
                    ```

            Returns:
                dict: A dictionary containing the response information.
                    On success:
                        {
                            '@type': 'seconds',
                            'seconds': float,  # The measured RTT in seconds
                        }
                    On error:
                        {
                            '@type': 'error',
                            'code': int,      # The error code
                            'message': str,   # A descriptive error message
                        }

            Raises:
                Exception: Any unexpected errors encountered during the operation.
            """
        
        if not link and not proxy:
            raise ValueError('link or proxy not provided')
        
        if link:
            proxy = self.parse_proxy_link(link)
            
        proxy = dict(
            type={"@type":"proxyTypeMtproto","secret": proxy['secret']}, 
            server=proxy['server'],
            port=proxy['port']
            )
        
        add_proxy = await self.client.call_method('addProxy', **proxy, enable=False)
        
        ping_result = await self.client.pingProxy(add_proxy.result['id'])
        
        return ping_result.result
    
    async def speed_test(self, link: str = None, proxy: dict = None, limit: int = 1 * 1024 * 1024, remote_file_id: str = 'BQACAgEAAxkBAAJBkGZXrkuSMvHniwYFg2ZtDyjhZPhhAAIOBQACOOlRRk53rGgovFntMAQ') -> ProxySpeedTestResult:
        """Tests the speed of a Telegram proxy server.

            This function asynchronously tests the speed of a Telegram proxy server by downloading a specific file (specified by `remote_file_id`) from Telegram servers.
            bot_token must be passed in for this method!
            
            Args:
                link (str, optional): A link to a Telegram proxy server. This can be used to automatically parse the proxy details. If not provided, `proxy` argument must be used.
                proxy (dict, optional): A dictionary containing the details of the Telegram proxy server. This includes keys like 'server' (proxy server address), 'port' (proxy server port), and 'secret' (optional secret for authenticated proxies). If not provided, `link` argument must be used. Exactly one of `link` or `proxy` must be provided.
                limit (int, optional): The maximum number of bytes to download during the test. Defaults to 1MB (1 * 1024 * 1024).
                remote_file_id (str, optional): The Telegram Media Group ID of a file to be used for the speed test. Defaults to a Telegram test file.

            Raises:
                ValueError: If neither `link` nor `proxy` is provided.

            Returns:
                ProxySpeedTestResult: An object containing the results of the speed test, including success status, downloaded bytes, download time, proxy details, download speed, and the result of the initial connection test.
            """

        if not link and not proxy:
            raise ValueError('link or proxy not provided')
        
        if link:
            proxy = self.parse_proxy_link(link)
            
        proxy = dict(
            type={"@type":"proxyTypeMtproto","secret": proxy['secret']}, 
            server=proxy['server'],
            port=proxy['port']
            )
        
        # Disabling proxy before proccessing
        await self.client.disableProxy()
        
        # Testing proxy before proccessing
        test_reult = await self.test_proxy(link)
        
        if not test_reult:
            return ProxySpeedTestResult(False, connect_test=test_reult)
        
        # add and enable the proxy
        add_proxy = await self.client.call_method('addProxy', **proxy, enable=True)
        proxy_id = add_proxy.result['id']
        proxy_link = await self.client.getProxyLink(proxy_id)
        # get remote file
        remote_file = await self.client.getRemoteFile(remote_file_id)
        
        # download the remote file with provided parameters
        start_time = time.time()
        download_result = await self.client.downloadFile(remote_file.result['id'], 32, 0, limit, True)
        end_time = time.time()
        
        # delete the downloaded file
        await self.client.deleteFile(remote_file.result['id'])
        
        success = False
        if download_result.result['local']['downloaded_size'] >= limit:
            success = True
            
        return ProxySpeedTestResult(
            success=success,
            downloaded_bytes=download_result.result['local']['downloaded_size'],
            download_time=round(end_time - start_time, 3),
            link=proxy_link.result['url'],
            proxy=proxy,
            connect_test=test_reult,
            download_speed=int(download_result.result['local']['downloaded_size'] / (end_time - start_time)),
            )
        
                         
                         

