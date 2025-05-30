from .api import RequestClient
from .api import RequestException
from .config import CORPID
from .config import CORPSECRET,CONTACT_CORPSECRET,WECHAT_SECRECT
# 创建客户端实例
client = RequestClient(max_retries=3, timeout=15)

# 获取应用access_token 用于自建应用调用一些API
def _get_access_token()->str:
    try:
        response = client.get('https://qyapi.weixin.qq.com/cgi-bin/gettoken', 
                            params={'corpid': CORPID,'corpsecret':CORPSECRET})
        code = response.status_code
        if code == 200:
            return response.json()
    except RequestException as e:
        print(f"请求失败: {e}")
        

# 获取通讯录access_token 用于获取本企业的人员信息
def _get_contact_access_token()->str:
    try:
        response = client.get('https://qyapi.weixin.qq.com/cgi-bin/gettoken', 
                            params={'corpid': CORPID,'corpsecret':CONTACT_CORPSECRET})
        code = response.status_code
        if code == 200:
            return response.json()
    except RequestException as e:
        print(f"请求失败: {e}")
        
# 获取微信客服access_token 用于接收客服消息
def _get_wechat_access_token():
    try:
        response = client.get('https://qyapi.weixin.qq.com/cgi-bin/gettoken', 
                            params={'corpid': CORPID,'corpsecret':WECHAT_SECRECT})
        code = response.status_code
        if code == 200:
            return response.json()
    except RequestException as e:
        print(f"请求失败: {e}")