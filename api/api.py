import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json
from typing import Optional, Dict, Any, Union

class RequestClient:
    """
    HTTP 请求客户端封装类
    
    功能：
    - 支持 GET/POST/PUT/DELETE 等常用方法
    - 自动重试机制
    - 统一的异常处理
    - 支持 JSON 和表单数据
    - 请求超时设置
    - 自动处理响应结果
    
    示例：
    >>> client = RequestClient()
    >>> response = client.get('https://api.example.com/data')
    >>> print(response.status_code, response.json())
    """

    def __init__(
        self,
        max_retries: int = 3,
        backoff_factor: float = 0.3,
        timeout: float = 10.0,
        default_headers: Optional[Dict[str, str]] = None
    ):
        """
        初始化请求客户端
        
        :param max_retries: 最大重试次数
        :param backoff_factor: 重试间隔因子
        :param timeout: 默认超时时间(秒)
        :param default_headers: 默认请求头
        """
        self.session = requests.Session()
        self.timeout = timeout
        self.default_headers = default_headers or {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        # 配置重试策略
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[408, 429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def request(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Union[Dict[str, Any], str, bytes]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        **kwargs
    ) -> requests.Response:
        """
        发送 HTTP 请求
        
        :param method: HTTP 方法 (GET, POST, PUT, DELETE等)
        :param url: 请求URL
        :param params: URL查询参数
        :param data: 表单数据
        :param json_data: JSON数据
        :param headers: 请求头
        :param timeout: 超时时间(秒)
        :param kwargs: 其他requests参数
        :return: requests.Response对象
        :raises: RequestException 当请求失败时抛出
        """
        headers = {**self.default_headers, **(headers or {})}
        timeout = timeout or self.timeout

        try:
            response = self.session.request(
                method=method.upper(),
                url=url,
                params=params,
                data=data,
                json=json_data,
                headers=headers,
                timeout=timeout,
                **kwargs
            )
            response.raise_for_status()  # 检查HTTP错误状态
            return response
        except requests.exceptions.RequestException as e:
            raise RequestException(f"Request failed: {str(e)}", original_exception=e)

    def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        **kwargs
    ) -> requests.Response:
        """发送GET请求"""
        return self.request('GET', url, params=params, headers=headers, timeout=timeout, **kwargs)

    def post(
        self,
        url: str,
        data: Optional[Union[Dict[str, Any], str, bytes]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        **kwargs
    ) -> requests.Response:
        """发送POST请求"""
        return self.request('POST', url, data=data, json_data=json_data, headers=headers, timeout=timeout, **kwargs)

    def put(
        self,
        url: str,
        data: Optional[Union[Dict[str, Any], str, bytes]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        **kwargs
    ) -> requests.Response:
        """发送PUT请求"""
        
        
        return self.request('PUT', url, data=data, json_data=json_data, headers=headers, timeout=timeout, **kwargs)

    def delete(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        **kwargs
    ) -> requests.Response:
        """发送DELETE请求"""
        return self.request('DELETE', url, headers=headers, timeout=timeout, **kwargs)

    def get_json(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Any:
        """发送GET请求并返回JSON数据"""
        response = self.get(url, params=params, headers=headers, timeout=timeout, **kwargs)
        return response.json()

    def post_json(
        self,
        url: str,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Any:
        """发送POST请求并返回JSON数据"""
        response = self.post(url, json_data=json_data, headers=headers, timeout=timeout, **kwargs)
        return response.json()


class RequestException(Exception):
    """自定义请求异常类"""
    def __init__(self, message: str, original_exception: Optional[Exception] = None):
        super().__init__(message)
        self.original_exception = original_exception