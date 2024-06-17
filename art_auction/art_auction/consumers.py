import json
from channels.generic.websocket import AsyncWebsocketConsumer

class BidConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.artwork_id = self.scope['url_route']['kwargs']['artwork_id']
        self.group_name = f'artwork_{self.artwork_id}'

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        bid = data['bid']

        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'new_bid',
                'bid': bid
            }
        )

    async def new_bid(self, event):
        bid = event['bid']

        await self.send(text_data=json.dumps({
            'bid': bid
        }))

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("notifications", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("notifications", self.channel_name)

    async def receive(self, text_data):
        pass  # No logic for receiving messages from client

    async def send_notification(self, event):
        notification = event['notification']
        await self.send(text_data=json.dumps({
            'notification': notification
        }))

class BidUpdateConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.product_id = self.scope['url_route']['kwargs']['product_id']
        self.group_name = f"bid_updates_{self.product_id}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def bid_update(self, event):
        message = event['message']

        await self.send(text_data=json.dumps({
            'message': message
        }))
