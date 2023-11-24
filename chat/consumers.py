from channels.generic.websocket import AsyncWebsocketConsumer
import json

connected_users = {}
start_word = '안녕하세요'

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        # nickname을 로그인한 유저의 nickname으로 설정
        self.nickname = self.scope['user'].nickname
        print(self.nickname)
        self.room_group_name = 'chat_%s' % self.room_name

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # Add the user to the connected users dictionary
        connected_users.setdefault(self.room_group_name, []).append(self.nickname)


    async def disconnect(self, close_code):
        # Remove the user from the connected users dictionary
        if self.room_group_name in connected_users and self.nickname in connected_users[self.room_group_name]:
            connected_users[self.room_group_name].remove(self.nickname)

            # If the group is empty, remove it from the dictionary
            if not connected_users[self.room_group_name]:
                del connected_users[self.room_group_name]

        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'nickname' : self.nickname,
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        global start_word
        
        message = event['message']
        nickname = event['nickname']
        
        # print(start_word[len(start_word)-1])
        # print(message)
        if message[0] == start_word[len(start_word)-1]:
                start_word = message
                await self.send(text_data=json.dumps({
                    'message': '일치합니다--------------',
                }))
        
        if message != '':
            await self.send(text_data=json.dumps({
                'message': message,
                'nickname' : nickname,
            }))