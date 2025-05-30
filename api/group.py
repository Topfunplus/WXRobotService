from .api import RequestClient
from .api import RequestException
# 创建客户端实例
client = RequestClient(max_retries=3, timeout=15)


def _create_group():
    try:
        response = client.post('https://qyapi.weixin.qq.com/cgi-bin/appchat/create?access_token=D8OMmQ0bscvZWTyT-hU7LPgyG0bC8qkW1h7SRO9fiklZhmrxrycvbC7zHdUgVh7lssG3sw9EFiLMBKwJesYoE-nw4xVJ4A8TsgQFSaH33hge4I9KUn3D7mKSYjdVGJmsCm0_k_JYq8V3cmlJKA2yxe5dOFVFTpsKHO1OYduSCW06biJsUZxpIbRgyTt7-8f3Z8eam1hibr5lbfWF5YxJLQ', 
                            json_data={
                                "name" : "测试群聊",
                                "owner" : "userid1",
                                "userlist" : ["userid1", "userid2", "userid3"],
                                "chatid" : "CHATID"
                            })
        code = response.status_code
        if code == 200:
            return response.json()
    except RequestException as e:
        print(f"请求失败: {e}")

# GET请求示例
def _get_group_list()->str:
    try:
        response = client.get('https://qyapi.weixin.qq.com/cgi-bin/appchat/get', 
                            params={'access_token': 'D8OMmQ0bscvZWTyT-hU7LPgyG0bC8qkW1h7SRO9fiklZhmrxrycvbC7zHdUgVh7lssG3sw9EFiLMBKwJesYoE-nw4xVJ4A8TsgQFSaH33hge4I9KUn3D7mKSYjdVGJmsCm0_k_JYq8V3cmlJKA2yxe5dOFVFTpsKHO1OYduSCW06biJsUZxpIbRgyTt7-8f3Z8eam1hibr5lbfWF5YxJLQ',
                                    'corpsecret':'9qxlu5XFqqz19wSuqWivGpq9omGe66T7mPeM_uivsVk'})
        code = response.status_code
        if code == 200:
            return response.json()
    except RequestException as e:
        print(f"请求失败: {e}")
        
# _get_access_token()
