import time
import logging
from typing import Dict, Tuple, Union
import xml.etree.ElementTree as ET
from .demo import _test_make
from .config import DB_NAME
from .sql import SQLiteHelper
import asyncio
from .user import _wechat_send_msg, _wechat_get_msg
from .enum import MessageType, EventType
class WeChatMsgHandler:
    """
    企业微信消息统一处理器
    功能：
    1. 统一处理加密/普通消息解析
    2. 提供消息路由功能
    3. 自动生成符合规范的回复
    """
    
    def __init__(self, wxcpt, logger=None):
        """
        :param wxcpt: WXBizMsgCrypt实例
        :param logger: 日志记录器
        """
        self.wxcpt = wxcpt
        self.logger = logger or logging.getLogger(__name__)
        self._init_msg_handlers()

    def _init_msg_handlers(self):
        """初始化消息处理器路由"""
        self.msg_handlers = {
            'text': self._handle_text_msg,
            'event': self._handle_event_msg,
            # 可以继续添加其他消息类型的处理器
            'image':self._handle_event_img
        }

    def process_request(self, request_data: Dict) -> Tuple[int, Union[str, Dict]]:
        """
        统一处理入口
        :param request_data: 包含 msg_signature, timestamp, nonce, request_body
        :return: (ret_code, response_data)
        """
        try:
            # 1. 解密消息
            ret, decrypted_msg = self._decrypt_msg(
                request_data['request_body'],
                request_data['msg_signature'],
                request_data['timestamp'],
                request_data['nonce']
            )
            if ret != 0:
                return ret, "Decrypt failed"

            # 2. 解析XML
            ret, parsed_msg = self._parse_wechat_msg(decrypted_msg)
            if ret != 0:
                return ret, "Parse XML failed"

            # 3. 路由处理
            handler = self.msg_handlers.get(parsed_msg.get('MsgType'), self._handle_unknown_msg)
            print("处理器handler:",handler,'\n')
            
            # 使用对应的路由进行处理 如果是消息-> _handle_text_msg 
            reply_content = handler(parsed_msg)

            print("微信客服回复的信息:",reply_content)

            if reply_content:
                return ret,reply_content
            
            
            # 4. 企业微信需要生成回复
            # if reply_content:
            #     ret, reply_xml = self._generate_reply(
            #         parsed_msg,
            #         reply_content,
            #         request_data['nonce']
            #     )
            #     return ret, reply_xml
            
            # 如果路由处理不好 就会返回
            return 0, ""

        except Exception as e:
            self.logger.error(f"Process error: {str(e)}", exc_info=True)
            return -1, f"Server error: {str(e)}"

    def _decrypt_msg(self, encrypted_msg: str, msg_signature: str, timestamp: str, nonce: str) -> Tuple[int, str]:
        """统一解密消息"""
        ret, sMsg = self.wxcpt.DecryptMsg(
            encrypted_msg.decode('utf-8') if isinstance(encrypted_msg, bytes) else encrypted_msg,
            msg_signature,
            timestamp,
            nonce
        )
        if ret != 0:
            self.logger.error(f"Decrypt failed with code {ret}")
        return ret, sMsg.decode('utf-8') if ret == 0 else ""

    def _parse_wechat_msg(self, xml_msg: str) -> Tuple[int, Dict]:
        """解析微信XML消息"""
        try:
            xml_tree = ET.fromstring(xml_msg)
            msg_dict = {
                elem.tag: elem.text if elem.text else ''
                for elem in xml_tree
                if elem.tag not in ['Encrypt']  # 过滤加密字段
            }
            return 0, msg_dict
        except ET.ParseError as e:
            self.logger.error(f"XML parse error: {str(e)}")
            return -2, {}

    def _generate_reply(self, received_msg: Dict, reply_content: str, nonce: str) -> Tuple[int, str]:
        # 生成符合企业微信规范的回复
        reply_xml = f"""<xml>
                    <ToUserName><![CDATA[{received_msg['FromUserName']}]]></ToUserName>
                    <FromUserName><![CDATA[{received_msg['ToUserName']}]]></FromUserName>
                    <CreateTime>{int(time.time())}</CreateTime>
                    <MsgType><![CDATA[text]]></MsgType>
                    <Content><![CDATA[{reply_content}]]></Content>
                    </xml>"""
        
        ret, encrypted_reply = self.wxcpt.EncryptMsg(client_xml, nonce)
        return ret, encrypted_reply if ret == 0 else ""



    # TODO 仅仅适用于企业微信部门 以下可以添加更多的处理

    # 当用户给机器人发送消息 这里异步有问题 不能等待make返回后再处理 而是立即返回，并且依赖调用推送消息给客户接口，这样全都定义为异步操作，可以先返回一个正在处理
    def _handle_text_msg(self, msg: Dict) -> str:
        content = msg.get('Content', '').strip()
        name = msg.get('FromUserName','').strip()
        print("name:",name,'\n')
        asyncio.ensure_future(_test_make(name, content))
        return '正在响应中,请耐心等待...'

    # 当客户给微信客服发送消息
    def _handle_event_msg(self, msg: Dict) -> str:
        db_helper = SQLiteHelper(DB_NAME)
        conn = db_helper.connect()
        if conn:
            db_helper.create_table('cursors', 'id INTEGER PRIMARY KEY AUTOINCREMENT , value TEXT NOT NULL, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP')
            event = msg.get('Event', '')
            token = msg.get('Token','').strip()
            open_kfid = msg.get('OpenKfId','').strip()
            # TODO 如果是客户发送消息给客服
            if event == 'kf_msg_or_event':
                used_cursor = ""
                has_more = 1
                # 获取某一个微信客服的消息
                while has_more != 0:
                    # 查询已经存在的cursor
                    exit_cursors = db_helper.select_data('cursors',order_by='timestamp')
                    # 如果查到的长度不为0
                    if len(exit_cursors) != 0:
                        used_cursor = exit_cursors[0][1]
                        print("使用的cursor:", used_cursor)
                        db_helper.delete_data('cursors', f"value = '{used_cursor}'")
                        
                    result = _wechat_get_msg(used_cursor, open_kfid, token, 1000)
                    if result['errcode'] == 0 and result['errmsg'] == 'ok':
                        msg_list = result['msg_list']
                        cursor = result['next_cursor']
                        has_more = result['has_more']
                        print("即将插入的cursor为:",cursor,'\n')
                        # 将 cursor 存入数据库
                        if cursor:
                            db_helper.insert_data('cursors', {'value': cursor})
                   
                        print("抓取结果", msg_list,'\n')
                        # 对结果进行处理
                        msg_item = msg_list[0]
                        
                        # 需要根据不同的消息类型 做出不同的响应
                        # msg_type = msg_item['msg_type']
                        
                        # 如果是文本类型
                        
                        
                        external_userid = msg_item['external_userid']
                        msg_id = msg_item['msgid']
                        custom_open_kfid = msg_item['open_kfid']
                        option = msg_item['text']['content']
                        text = {
                            'content':'处理中...'
                        }
                        # 给该用户发送消息，目前msg_list只抓取到了一条数据
                        _wechat_send_msg(touser=external_userid,
                                         msg_id=msg_id,
                                         open_kfid=custom_open_kfid,
                                         text=text)
                        # 异步给用户发送AI回答
                        asyncio.ensure_future(
                            _test_make(touser=external_userid,
                                        msg_id=msg_id,
                                        open_kfid=custom_open_kfid,
                                        option=option
                                    )
                        )
                        return 'success'
            return ''
        else:
            print("数据库链接错误")
            return ''
       

    # 当用户给机器人发送图片
    def _handle_event_img(self,msg:Dict) -> str:
        types = msg.get('MsgType','')
        if types == 'image' :
            return f'收到图片:{msg.get("PicUrl")}'
        return ''
    
    def _handle_unknown_msg(self, msg: Dict) -> str:
        """处理未知类型消息"""
        self.logger.warning(f"Unhandled message type: {msg.get('MsgType')}")
        return ''