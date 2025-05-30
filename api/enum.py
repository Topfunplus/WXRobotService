from enum import Enum

# 用户发的消息类型
class MessageType(Enum):
    TEXT = "text"
    IMAGE = "image"
    VOICE = "voice"
    FILE = "file"
    LOCATION = "location"
    MINIPROGRAM = "miniprogram"
    CHANNELS_SHOP_PRODUCT = "channels_shop_product"
    CHANNELS_SHOP_ORDER = "channels_shop_order"
    MERGED_MSG = "merged_msg"
    CHANNELS = "channels"
    NOTE = "note"
    EVENT = "event"


# 用户出发的事件类型 当MessageType为EVENT 时 在event对象中的event_type
class EventType(Enum):
    ENTER_SESSION = "enter_session"
    MSG_SEND_FAIL = "msg_send_fail"
    USER_RECALL_MSG = "user_recall_msg"
