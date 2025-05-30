 # 处理任务卡片消息
    if decrypt_data.get('EventKey', '') == 'no':
        # 返回信息
        sRespData="""<xml>
   <ToUserName>{to_username}</ToUserName>
   <FromUserName>{from_username}</FromUserName>
   <CreateTime>{create_time}</CreateTime>
   <MsgType>update_taskcard</MsgType>
   <TaskCard>
       <ReplaceName>已处理</ReplaceName>
   </TaskCard>
</xml>
""".format(to_username=decrypt_data['ToUserName'],
           from_username=decrypt_data['FromUserName'],
           create_time=decrypt_data['CreateTime'],
           event_key=decrypt_data['EventKey'],
           agentid=decrypt_data['AgentId'])