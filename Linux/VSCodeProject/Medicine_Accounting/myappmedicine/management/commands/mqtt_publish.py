import asyncio
import json
from pathlib import Path
import ssl
import uuid
from aiomqtt import Client

MQTT_BROKER = "192.168.1.108"
MQTT_PORT = 8883
MQTT_LOGIN = "scherbina-knt125m"
MQTT_PASSWORD = "tjMC54%@"

BASE_DIR = Path(__file__).resolve().parents[3]
CA_CERT_PATH = BASE_DIR / "ca.crt"

async def mqtt_request(topic, payload, timeout = 5):
    
    request_id = payload["request_id"]
    reply_topic = payload["reply_to"]

    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.load_verify_locations(str(CA_CERT_PATH))


    async with Client(MQTT_BROKER, MQTT_PORT, username = MQTT_LOGIN, password = MQTT_PASSWORD, tls_context = context) as client:

        await client.subscribe(reply_topic, qos = 1)
        
        await client.publish(topic, json.dumps(payload), qos = 1)

        try:

            async with asyncio.timeout(timeout):

                async for message in client.messages:

                    data = json.loads(message.payload.decode())
                    
                    if data["request_id"] == request_id:
                        return data["result"]
        
        except asyncio.TimeoutError:

            print(f"Час очікування відповіді вичерпано. Topic: {topic} - {request_id}")
            return None



async def publish_new_user(login, password, address):

    request_id = str(uuid.uuid4())
    reply_topic = f"users/responses/{request_id}"

    payload = {
        "login": login,
        "password": password,
        "address": address,
        "reply_to": reply_topic,
        "request_id": request_id
    }

    return await mqtt_request("users/new", payload)

async def publish_new_product(product_name, manufacturer_name):
    
    request_id = str(uuid.uuid4())
    reply_topic = f"products/responses/{request_id}"

    payload = {
        "product_name": product_name,
        "manufacturer_name": manufacturer_name,
        "reply_to": reply_topic,
        "request_id": request_id
    }

    return await mqtt_request("products/new", payload)

async def publish_new_batch(product_id, user_id, package_size, expiration_date_1, expiration_date_2, number_of_packages):
    
    request_id = str(uuid.uuid4())
    reply_topic = f"batches/responses/{request_id}"

    payload = {
        "product_id": product_id,
        "user_id": user_id,
        "package_size": package_size,
        "expiration_date_1": expiration_date_1,
        "expiration_date_2": expiration_date_2,
        "number_of_packages": number_of_packages,
        "reply_to": reply_topic,
        "request_id": request_id
    }

    return await mqtt_request("batches/new", payload)

async def publish_change_status_for_package(selected_package_id, selected_batch_id, selected_product_id, selected_expiration_date_1,
                                    selected_expiration_date_2, new_status):
    
    request_id = str(uuid.uuid4())
    reply_topic = f"statuses/responses/{request_id}"

    payload = {
        "selected_package_id": selected_package_id,
        "selected_batch_id": selected_batch_id,
        "selected_product_id": selected_product_id,
        "selected_expiration_date_1": selected_expiration_date_1,
        "selected_expiration_date_2": selected_expiration_date_2,
        "new_status": new_status,
        "reply_to": reply_topic,
        "request_id": request_id
    }

    return await mqtt_request("status/update_package", payload)

async def publish_change_status_for_batch(selected_batch_id, selected_product_id, selected_expiration_date_1,
                                    selected_expiration_date_2, new_status):
    
    request_id = str(uuid.uuid4())
    reply_topic = f"statuses/responses/{request_id}"

    payload = {
        "selected_batch_id": selected_batch_id,
        "selected_product_id": selected_product_id,
        "selected_expiration_date_1": selected_expiration_date_1,
        "selected_expiration_date_2": selected_expiration_date_2,
        "new_status": new_status,
        "reply_to": reply_topic,
        "request_id": request_id
    }

    return await mqtt_request("status/update_batch", payload)


# Синхронні версії запитів
# def publish_new_user(login, password, address, timeout = 5):

#     request_id = str(uuid.uuid4())
#     reply_topic = f"users/responses/{request_id}"

#     result = None

#     def on_message(client, userdata, msg):

#         data = json.loads(msg.payload.decode())

#         if data["request_id"] == request_id:

#             result = data["result"]
#             client.disconnect()

#     client = mqtt.Client()
#     client.on_message = on_message
#     client.connect(MQTT_BROKER, 1883, 60)
#     client.subscribe(reply_topic, qos = 1)
#     client.loop_start()

#     payload = {
#         "login": login,
#         "password": password,
#         "address": address,
#         "reply_to": reply_topic,
#         "request_id": request_id
#     }

#     client.publish("users/new", json.dumps(payload), qos = 1)

#     start_time = time.time()
#     while result is None and time.time() - start_time < timeout:
#         time.sleep(0.1)

#     client.loop_stop()
#     client.disconnect()

#     return result

# def publish_new_product(product_name, manufacturer_name, timeout = 5):
    
#     request_id = str(uuid.uuid4())
#     reply_topic = f"products/responses/{request_id}"

#     result = None

#     def on_message(client, userdata, msg):

#         data = json.loads(msg.payload.decode())

#         if data["request_id"] == request_id:

#             result = data["result"]
#             client.disconnect()

#     client = mqtt.Client()
#     client.on_message = on_message
#     client.connect("MQTT_BROKER", 1883, 60)
#     client.subscribe(reply_topic, qos = 1)
#     client.loop_start()

#     payload = {
#         "product_name": product_name,
#         "manufacturer_name": manufacturer_name,
#         "reply_to": reply_topic,
#         "request_id": request_id
#     }

#     client.publish("products/new", json.dumps(payload), qos = 1)

#     start_time = time.time()
#     while result is None and time.time() - start_time < timeout:
#         time.sleep(0.1)

#     client.loop_stop()
#     client.disconnect()

#     return result

# def publish_change_status_for_package(selected_package_id, selected_batch_id, selected_product_id, selected_expiration_date_1,
#                                     selected_expiration_date_2, new_status, timeout = 5):
    
#     request_id = str(uuid.uuid4())
#     reply_topic = f"statuses/responses/{request_id}"

#     result = None

#     def on_message(client, userdata, msg):

#         data = json.loads(msg.payload.decode())

#         if data["request_id"] == request_id:

#             result = data["result"]
#             client.disconnect()

#     client = mqtt.Client()
#     client.on_message = on_message
#     client.connect("MQTT_BROKER", 1883, 60)
#     client.subscribe(reply_topic, qos = 1)
#     client.loop_start()

#     payload = {
#         "selected_package_id": selected_package_id,
#         "selected_batch_id": selected_batch_id,
#         "selected_product_id": selected_product_id,
#         "selected_expiration_date_1": selected_expiration_date_1,
#         "selected_expiration_date_2": selected_expiration_date_2,
#         "new_status": new_status,
#         "reply_to": reply_topic,
#         "request_id": request_id
#     }

#     client.publish("status/update_package", json.dumps(payload), qos = 1)

#     start_time = time.time()
#     while result is None and time.time() - start_time < timeout:
#         time.sleep(0.1)

#     client.loop_stop()
#     client.disconnect()

#     return result

# def publish_change_status_for_batch(selected_batch_id, selected_product_id, selected_expiration_date_1,
#                                     selected_expiration_date_2, new_status, timeout = 5):
    
#     request_id = str(uuid.uuid4())
#     reply_topic = f"statuses/responses/{request_id}"

#     result = None

#     def on_message(client, userdata, msg):

#         data = json.loads(msg.payload.decode())

#         if data["request_id"] == request_id:

#             result = data["result"]
#             client.disconnect()

#     client = mqtt.Client()
#     client.on_message = on_message
#     client.connect("MQTT_BROKER", 1883, 60)
#     client.subscribe(reply_topic, qos = 1)
#     client.loop_start()

#     payload = {
#         "selected_batch_id": selected_batch_id,
#         "selected_product_id": selected_product_id,
#         "selected_expiration_date_1": selected_expiration_date_1,
#         "selected_expiration_date_2": selected_expiration_date_2,
#         "new_status": new_status,
#         "reply_to": reply_topic,
#         "request_id": request_id
#     }

#     client.publish("status/update_batch", json.dumps(payload), qos = 1)

#     start_time = time.time()
#     while result is None and time.time() - start_time < timeout:
#         time.sleep(0.1)

#     client.loop_stop()
#     client.disconnect()

#     return result