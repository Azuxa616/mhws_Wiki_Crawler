import requests
import logging
import time
from requests.exceptions import RequestException, SSLError, Timeout

class HttpUtils:
    """HTTP请求工具类，处理请求异常和重试"""
    
    def __init__(self, retry_times=3, retry_interval=2, timeout=10):
        """初始化HTTP工具类
        
        Args:
            retry_times: 重试次数
            retry_interval: 重试间隔（秒）
            timeout: 请求超时时间（秒）
        """
        self.retry_times = retry_times
        self.retry_interval = retry_interval
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
        
        # 创建会话对象，用于保持连接
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def get(self, url, params=None, verify_ssl=True):
        """发送GET请求并处理可能的异常
        
        Args:
            url: 请求的URL
            params: URL参数
            verify_ssl: 是否验证SSL证书
            
        Returns:
            response: 请求响应
            
        Raises:
            RequestException: 请求失败且重试次数用尽时抛出
        """
        for i in range(self.retry_times):
            try:
                self.logger.debug(f"正在请求: {url}")
                response = self.session.get(
                    url, 
                    params=params, 
                    timeout=self.timeout,
                    verify=verify_ssl
                )
                response.raise_for_status()  # 检查HTTP错误
                return response
            except SSLError as e:
                self.logger.warning(f"SSL证书验证失败: {e}，尝试关闭SSL验证")
                if verify_ssl and i < self.retry_times - 1:
                    # 如果SSL验证失败，尝试关闭验证再次请求
                    return self.get(url, params, verify_ssl=False)
                else:
                    self.logger.error(f"SSL错误 ({i+1}/{self.retry_times}): {e}")
            except Timeout as e:
                self.logger.warning(f"请求超时 ({i+1}/{self.retry_times}): {e}")
            except RequestException as e:
                self.logger.error(f"请求失败 ({i+1}/{self.retry_times}): {e}")
            
            if i < self.retry_times - 1:
                sleep_time = self.retry_interval * (i + 1)  # 指数退避策略
                self.logger.info(f"等待 {sleep_time} 秒后重试...")
                time.sleep(sleep_time)
            else:
                self.logger.error(f"达到最大重试次数，放弃请求: {url}")
                raise
    
    def close(self):
        """关闭会话"""
        self.session.close()