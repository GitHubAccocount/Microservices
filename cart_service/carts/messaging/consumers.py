import pika
import json
import django
from django.conf import settings

class CartEventConsumer:
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=settings.RABBITMQ_HOST)
        )
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='inventory_updates')
        
    def callback(self, ch, method, properties, body):
        data = json.loads(body)
        # Handle inventory updates
        product_id = data['product_id']
        new_quantity = data['quantity']
        
        # Update cart items if necessary
        # For example, remove items if quantity becomes 0
        
    def start_consuming(self):
        self.channel.basic_consume(
            queue='inventory_updates',
            on_message_callback=self.callback,
            auto_ack=True
        )
        self.channel.start_consuming()