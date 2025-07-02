import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    active_users = dict()  # room_name: set(usernames)

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        self.username = None
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Remove user from active list
        if self.username:
            users = self.active_users.get(self.room_name, set())
            users.discard(self.username)
            self.active_users[self.room_name] = users
            await self.broadcast_user_list()
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message')
        username = data.get('username', 'Anonymous')
        if not self.username:
            self.username = username
            users = self.active_users.get(self.room_name, set())
            users.add(username)
            self.active_users[self.room_name] = users
            await self.broadcast_user_list()
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        username = event.get('username', 'Anonymous')
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': message,
            'username': username,
        }))

    async def broadcast_user_list(self):
        users = list(self.active_users.get(self.room_name, set()))
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_list',
                'users': users,
            }
        )

    async def user_list(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_list',
            'users': event['users'],
        })) 