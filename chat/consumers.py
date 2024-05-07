from channels.consumer import SyncConsumer
from asgiref.sync import async_to_sync
from.models import Stock
import openai

OPENAI_API_KEY = 'your_api_key' # Replace YOUR_API_KEY with your openai apikey 

class EchoConsumer(SyncConsumer):
    def websocket_connect(self, event):
        self.room_name = 'broadcast'
        self.send({
            'type': 'websocket.accept'
        })
        async_to_sync(self.channel_layer.group_add)(self.room_name, self.channel_name)
        print(f'[{self.channel_name}] - You are now connected')

    def websocket_receive(self, event):
        # Extract the received message
        received_message = event["text"]

        # Call the OpenAI API to generate a response
        response = openai.Completion.create(
            engine="davinci",  # Choose the engine
            prompt=received_message,  # Provide the prompt (received message)
            api_key=OPENAI_API_KEY  # Pass your API key
        )

        # Extract the generated response from the API
        generated_response = response.choices[0].text.strip()

        # Send the generated response back to the client
        self.send({
            'type': 'websocket.send',
            'text': generated_response
        })

        # Print a message for debugging
        print(f'[{self.channel_name}] - Generated response: {generated_response}')

    def websocket_message(self, event):
        print(f'[{self.channel_name}] - Message send - {event["text"]}')
        self.send({
            'type': 'websocket.send',
            'text': event.get('text')
        })

    def websocket_disconnect(self, event):
        print(f'[{self.channel_name}] - Disconnected')
        async_to_sync(self.channel_layer.group_add)(self.room_name, self.channel_name)
