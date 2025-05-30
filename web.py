#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-----------------File Info-----------------------
Name: web.py
Description: web api support
Author: GentleCP
Email: me@gentlecp.com
Create Date: 2021/6/19
-----------------End-----------------------------
"""
import argparse
from fastapi import FastAPI
from fastapi import Response, Request
from fastapi import Query  # 确保导入Query

# 导入加解密相关的类
from WXBizMsgCrypt3 import WXBizMsgCrypt
from xml.etree.ElementTree import fromstring  # 可用于对xml格式进行解析
import uvicorn
from WXBizMsgCrypt3 import XMLParse
from api.utils import WeChatMsgHandler

app = FastAPI()
# 创建xml解析实例
xmlparse = XMLParse()


# 在这里接收命令行提供的参数
def parse_args():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--port', '-p', default=8000, type=int, help="port to build web server")
    arg_parser.add_argument('--token', '-t', type=str, help='token set in corpwechat app')
    arg_parser.add_argument('--aeskey', '-a', type=str, help='encoding aeskey')
    arg_parser.add_argument('--corpid', '-c', type=str, help='your corpwechat id')
    args = arg_parser.parse_args()
    return args

args = parse_args()
wxcpt = WXBizMsgCrypt(args.token, args.aeskey, args.corpid)
# 统一处理
handler = WeChatMsgHandler(wxcpt)


'''
    验证配置是否成功，处理get请求
    :param msg_signature:
    :param timestamp:
    :param nonce:
    :param echostr:
    :return:
    '''
@app.get("/")
async def verify(msg_signature: str,
                 timestamp: str,
                 nonce: str,
                 echostr: str):
    
    ret, sEchoStr = wxcpt.VerifyURL(msg_signature, timestamp, nonce, echostr)
    print("正在进行鉴权",ret,sEchoStr)
    
    if ret == 0:
        return Response(content=sEchoStr.decode('utf-8'))
    else:
        print(sEchoStr)



"""
企业微信消息回调接口
参数顺序规则：
1. 普通参数(request)
2. 有默认值的参数(Query参数)
"""
@app.post("/")
async def wechat_callback(
    request: Request,
    msg_signature: str = Query(...),  # 企业微信签名
    timestamp: str = Query(...),      # 时间戳
    nonce: str = Query(...)           # 随机数
):
    
    request_body = await request.body()
    print("响应体request_body:",request_body,'\n')
    # 统一处理
    ret,response = handler.process_request({
        'msg_signature': msg_signature,
        'timestamp': timestamp,
        'nonce': nonce,
        'request_body': request_body
    })
    
    print("wechat_callback->response:", ret,response,'\n')
    
    if ret != 0:
        return Response(content=response, status_code=400)
    
    return Response(content=response if response else "")


if __name__ == "__main__":
    uvicorn.run("web:app", port=args.port, host='0.0.0.0', reload=False,debug=True)
