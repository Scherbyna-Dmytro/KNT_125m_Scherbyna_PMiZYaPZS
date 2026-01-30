import json
from pathlib import Path
import ssl
import sys
from aiomqtt import Client
from myappmedicine.mongoDB_methods import *
from django.core.management.base import BaseCommand

MQTT_BROKER = "localhost"
MQTT_PORT = 1883

# MQTT_BROKER = "192.168.1.108"
# MQTT_PORT = 8883
# MQTT_LOGIN = "scherbina-knt125m"
# MQTT_PASSWORD = "tjMC54%@"

# BASE_DIR = Path(__file__).resolve().parents[3]
# CA_CERT_PATH = BASE_DIR / "ca.crt"
#CA_CERT_PATH = "ca.crt"

TOPICS = [
    ("users/new", 1),
    ("products/new", 1),
    ("batches/new", 1),
    ("status/update_package", 1),
    ("status/update_batch", 1),
]


async def handle_add_user(client, data):

    print(f"Запит на реєстрацію користувача \"{ data['login'] }\" - [Address: {data['address']}] оброблюється.")

    result = None

    if await AddUser(data["login"], data["password"], data["address"]):
        print(f"Користувача \"{ data['login'] }\" - [Address: {data['address']}] зареєстровано.")
        result = True
    
    else:
        print(f"Користувач \"{ data['login'] }\" - [Address: {data['address']}] вже існує. Скасування операції.")
        result = False
    
    response_payload = {
        "request_id": data["request_id"],
        "result": result
    }

    reply_to = data['reply_to']

    await client.publish(data['reply_to'], json.dumps(response_payload), qos = 1)
    print(f"Відповідь на {reply_to} надіслана. Result: {result}.")

async def handle_add_product(client, data):

    print(f"Запит на реєстрацію продукту \"{ data['product_name']}\" - [Manufacturer: {data['manufacturer_name']}] оброблюється.")

    result = None

    if await AddProduct(data["product_name"], data["manufacturer_name"]):
        print(f"Продукт \"{ data['product_name']}\" - [Manufacturer: {data['manufacturer_name']}] зареєстровано.")
        result = True
    
    else:
        print(f"Продукт \"{ data['product_name']}\" [Manufacturer: {data['manufacturer_name']}] вже існує. Скасування операції.")
        result = False
    
    response_payload = {
        "request_id": data["request_id"],
        "result": result
    }

    reply_to = data['reply_to']

    await client.publish(data['reply_to'], json.dumps(response_payload), qos = 1)
    print(f"Відповідь на {reply_to} надіслана. Result: {result}.")

async def handle_add_batch(client, data):

    print(f"Запит на реєстрацію партії \"ProductID: { data['product_id']}\" - [Size: {data['package_size']}] для [UserID: {data['user_id']}] оброблюється.")

    result = None

    if await AddBatch(data["product_id"], data["user_id"], data["package_size"], data["expiration_date_1"],
                    data["expiration_date_2"], data["number_of_packages"]):
        
        print(f"Партію товару \"ProductID: { data['product_id']}\" - [Size: {data['package_size']}] для [UserID: {data['user_id']}]",
              f" зареєстровано.")
        result = True
    
    else:
        print(f"При реєстрації партії товару \"{ data['product_id']}\" - [Size: {data['package_size']}] для [UserID: {data['user_id']}] виникла помилка. Скасування операції.")
        result = False
    
    response_payload = {
        "request_id": data["request_id"],
        "result": result
    }

    reply_to = data['reply_to']

    await client.publish(data['reply_to'], json.dumps(response_payload), qos = 1)
    print(f"Відповідь на {reply_to} надіслана. Result: {result}.")

async def handle_change_status_for_package(client, data):

    print(f"Запит на зміну статусу упаковки \"{ data['selected_package_id']}\" - [Batch: {data['selected_batch_id']}]", 
              f" - [Product: {data['selected_product_id']}] на \"{ data['new_status']}\" оброблюється.")

    result = None

    if await ChangeStatusForPackage(data["selected_package_id"], data["selected_batch_id"], data["selected_product_id"],
                            data["selected_expiration_date_1"], data["selected_expiration_date_2"], data["new_status"]):
        
        print(f"Для упаковки \"{ data['selected_package_id']}\" - [Batch: {data['selected_batch_id']}]", 
              f" - [Product: {data['selected_product_id']}] статус змінено на \"{ data['new_status']}\".")
        
        result = True
    
    else:
        
        print(f"При зміні статусу упаковки \"{ data['selected_package_id']}\" - [Batch: {data['selected_batch_id']}]",
              f" - [Product: {data['selected_product_id']}] на \"{ data['new_status']}\" виникла помилка.")
        
        result = False
    
    response_payload = {
        "request_id": data["request_id"],
        "result": result
    }

    reply_to = data['reply_to']

    await client.publish(data['reply_to'], json.dumps(response_payload), qos = 1)
    print(f"Відповідь на {reply_to} надіслана. Result: {result}.")

async def handle_change_status_for_batch(client, data):

    print(f"Запит на зміну статусу партії упаковок {data['selected_batch_id']} - [Product: {data['selected_product_id']}]", 
              f" на \"{ data['new_status']}\" оброблюється.")

    result = None

    if await ChangeStatusForBatch(data["selected_batch_id"], data["selected_product_id"],
                            data["selected_expiration_date_1"], data["selected_expiration_date_2"], data["new_status"]):
        
        print(f"Для партії {data['selected_batch_id']} - [Product: {data['selected_product_id']}]", 
              f" статус змінено на \"{ data['new_status']}\".")
        
        result = True
    
    else:
        
        print(f"При зміні статусу партії {data['selected_batch_id']} - [Product: {data['selected_product_id']}]",
              f" на \"{ data['new_status']}\" виникла помилка.")
        
        result = False
    
    response_payload = {
        "request_id": data["request_id"],
        "result": result
    }

    reply_to = data['reply_to']

    await client.publish(data['reply_to'], json.dumps(response_payload), qos = 1)
    print(f"Відповідь на {reply_to} надіслана. Result: {result}.")


ROUTES = {
    "users/new": handle_add_user,
    "products/new": handle_add_product,
    "batches/new": handle_add_batch,
    "status/update_package": handle_change_status_for_package,
    "status/update_batch": handle_change_status_for_batch,
}

class Command(BaseCommand):
    help = 'Запуск MQTT підписника.'

    def handle(self, *args, **options):

        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        try:
            asyncio.run(self.start_subscriber())
        
        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS("Роботу завершено."))

    async def start_subscriber(self):
        print(f"Підключення до брокера {MQTT_BROKER}...")

        # context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        # context.load_verify_locations(str(CA_CERT_PATH))
        
        # context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        # context.check_hostname = False
        # context.verify_mode = ssl.CERT_NONE
        
        async with Client(MQTT_BROKER, MQTT_PORT) as client: 
        # async with Client(MQTT_BROKER, MQTT_PORT, username = MQTT_LOGIN, password = MQTT_PASSWORD, tls_context = context) as client:

            for topic, qos in TOPICS:
                await client.subscribe(topic, qos = qos)
            
            print("З'єднано з MQTT брокером. Очікування повідомлень...")

            async for message in client.messages:

                topic_name = str(message.topic)
                handler = ROUTES.get(topic_name)

                if handler:

                    try:

                        data = json.loads(message.payload.decode())
                        asyncio.create_task(handler(client, data))

                    except Exception as e:
                        print(f"Помилка при обробці повідомлення з {topic_name}: {e}")
                else:
                    print(f"Немає обробника для {topic_name}")

            


# def on_connect(client, userdata, flags, rc):
#     print("З'єднано з MQTT брокером.")
#     client.subscribe(TOPICS)

# def on_message(client, userdata, msg):
#     handler = ROUTES.get(msg.topic)

#     if not handler:
#         print(f"Немає обробника для {msg.topic}")
#         return

#     data = json.loads(msg.payload.decode())
#     handler(client, data)

# client = mqtt.Client()
# client.on_connect = on_connect
# client.on_message = on_message
# client.connect(MQTT_BROKER, 1883, 60)
# client.loop_forever()