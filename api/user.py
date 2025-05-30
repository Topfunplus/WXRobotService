from .api import RequestClient
from .api import RequestException
from .auth import _get_contact_access_token,_get_access_token,_get_wechat_access_token
from .config import AGENT_ID,ACCOUNT_ID
# 创建客户端实例
client = RequestClient(max_retries=3, timeout=15)


# 企业微信机器人给指定用户发送消息
async def _send_msg(username,content):
    try:
        response = _get_access_token()
        token = response.get('access_token')
        json_data = {
            "touser" : username,
            "toparty" : "",
            "totag" : "",
            "msgtype" : "text",
            "agentid" : AGENT_ID,
            "text" : {
                "content" : content
            },
            "safe":0,
            "enable_id_trans": 0,
            "enable_duplicate_check": 0,
            "duplicate_check_interval": 1800
            }
        response = client.post('https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token='+token, json_data=json_data)
        code = response.status_code
        if code == 200:
            return response.json()
    except RequestException as e:
        print(f"请求失败: {e}")

# 获取本企业
'''
@param litmit 限制人数
'''
def _get_users(limit:int)->str:
    try:
        contact_response = _get_contact_access_token()
        contact_token = contact_response.get('access_token')
        print()
        response = client.post('https://qyapi.weixin.qq.com/cgi-bin/user/list_id?access_token='+contact_token, 
                            json_data={
                                "cursor" : "",
                                "limit" : limit
                            })
        code = response.status_code
        if code == 200:
            return response.json()
    except RequestException as e:
        print(f"请求失败: {e}")

# 获取客户主动发给微信客服的消息
'''
users = _wechat_get_msg(open_kfid,token,1000)
print("获取到用户列表", users)
'''
def _wechat_get_msg(cursor, open_kfid, token, limit:int)->str:
    try:
        response = _get_wechat_access_token()
        data = {
            "cursor": cursor,
            "token": token,
            "limit": limit,
            "voice_format": 0,
            "open_kfid": open_kfid
        }
        token = response.get('access_token')
        response = client.post(' https://qyapi.weixin.qq.com/cgi-bin/kf/sync_msg?access_token='+token, json_data=data)
        code = response.status_code
        if code == 200:
            return response.json()
    except RequestException as e:
        print(f"请求失败: {e}")   

# 获取最近 48 小时内有触发用户进入会话事件或向该客服账号发过消息的客户，否则在 invalid_external_userid 返回
def _wechat_get_users(limit:int)->str:
    try:
        response = _get_wechat_access_token()
        data = {}
        token = response.get('access_token')
        response = client.post('https://qyapi.weixin.qq.com/cgi-bin/kf/customer/batchget?access_token='+token, json_data=data)
        code = response.status_code
        if code == 200:
            return response.json()
    except RequestException as e:
        print(f"请求失败: {e}")        

# 微信客服给客户发送消息
'''
@param touser 发送的EXTERNAL_USERID
@param text 文本对象
'''
def _wechat_send_msg(touser,msg_id,open_kfid,text):
    print("发送消息的客户信息:",touser,text,'\n')
    try:
        response = _get_wechat_access_token()
        token = response.get('access_token')
        data = {
            "touser": touser,
            "open_kfid": open_kfid,
            "msgtype": "text",
            "text": {
                "content": text['content']
            }
        }

        if msg_id is not None:
            data["msgid"] = msg_id
        
        response = client.post('https://qyapi.weixin.qq.com/cgi-bin/kf/send_msg?access_token='+token,json_data = data)
        print("消息发送结果:", response.json())
        code = response.status_code
        if code == 200:
            return response.json()
    except RequestException as e:
        print(f"请求失败: {e}")
