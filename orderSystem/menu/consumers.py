import json
from channels.generic.websocket import AsyncWebsocketConsumer

class KitchenConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # 把所有厨房端都加入同一个广播组
        await self.channel_layer.group_add("kitchen", self.channel_name)
        await self.accept()
        print("厨房端已连接")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("kitchen", self.channel_name)
        print("厨房端断开连接")

    # 后端发送更新时，所有连接的厨房端都会收到这个事件
    async def send_order_update(self, event):
        await self.send(text_data=json.dumps(event["data"]))
