from .api import RequestClient
from .api import RequestException
from .user import _send_msg,_wechat_send_msg
import json
import asyncio
# 创建客户端实例
client = RequestClient(max_retries=3, timeout=200)

# 测试
async def _test_make(touser, msg_id, open_kfid,option)->str:
    webhook_url = 'https://hook.us2.make.com/ur6hy470w5jk32stv8a3yk99qt6b86og'
    jsondata = {'name': touser,'option': option}
   
    try:
        response = client.post(webhook_url, json_data=jsondata)
        response.encoding = "utf-8"  # 确保编码正确
        raw_text = response.text
        text = {
            'content':raw_text
        }
        print("make传递的数据",raw_text)
        _wechat_send_msg(touser,None,open_kfid,text)
        return raw_text
    except RequestException as e:
        return f"请求失败: {e}"
        
# _test_make()
# # POST JSON数据
# try:
#     data = {'key': 'value'}
#     response = client.post('https://api.example.com/create', json_data=data)
#     print(response.json())
# except RequestException as e:
#     print(f"请求失败: {e}")

# # 简便方法获取JSON
# try:
#     json_data = client.get_json('https://api.example.com/data')
#     print(json_data)
# except RequestException as e:
#     print(f"请求失败: {e}")
    
    
    
# # 自定义请求头
# headers = {
#     'Authorization': 'Bearer token123',
#     'Custom-Header': 'value'
# }

# # 带自定义头的请求
# response = client.get('https://api.example.com/protected', headers=headers)

# # 表单提交
# form_data = {'username': 'admin', 'password': '123456'}
# response = client.post('https://api.example.com/login', data=form_data)

# # 文件上传
# files = {'file': open('example.txt', 'rb')}
# response = client.post('https://api.example.com/upload', files=files)