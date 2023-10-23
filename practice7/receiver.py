from paho.mqtt import client as mqtt_client  # type: ignore
from datetime import datetime
import json
import xml


# Параметры подключения к MQTT-брокеру
HOST = "192.168.1.11"  # IP чемодана
PORT = 1883  # Стандартный порт подключения для Mosquitto
KEEPALIVE = 60
# Время ожидания доставки сообщения, если при отправке оно будет прeвышено,
# брокер будет считаться недоступным

# Словарь с топиками и собираемыми из них параметрами
SUB_TOPICS = {
    "/devices/wb-msw-v3_21/controls/Temperature": "temperature",
    "/devices/wb-msw-v3_21/controls/Current Motion": "motion",
    "/devices/wb-msw-v3_21/controls/Sound Level": "sound",
    "/devices/wb-ms_11/controls/Illuminance": "illuminance",
}
try:
    all_data = json.load(open("data.json", "r"))
except Exception:
    all_data = []


def on_connect(client, userdata, flags, rc):
    """Функция, вызываемая при подключении к брокеру

    Arguments:
    client - Экземпляр класса Client, управляющий подключением к брокеру
    userdata - Приватные данные пользователя, передаваемые при подключениии
    flags - Флаги ответа, возвращаемые брокером
    rc - Результат подключения, если 0, всё хорошо
    """
    print("Connected with result code " + str(rc))

    # Подключение ко всем заданным выше топикам
    for topic in SUB_TOPICS.keys():
        client.subscribe(topic)


data = {}


def save_to_json(json_data):
    with open("data.json", "w") as file:
        file.write(json.dumps(json_data))


def save_to_xml(json_data):
    pass


last_time = None


def on_message(client, userdata, msg):
    """Функция, вызываемая при получении сообщения от брокера
    по одному из отслеживаемых топиков

    Arguments:
    client - Экземпляр класса Client, управляющий подключением к брокеру
    userdata - Приватные данные пользователя, передаваемые при подключениии
    msg - Сообщение, приходящее от брокера, со всей информацией
    """
    payload = msg.payload.decode()
    topic = msg.topic

    global data
    global last_time
    data["id"] = int(HOST.split(".")[-1])
    current_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    data["time"] = current_time
    data[SUB_TOPICS[topic]] = float(payload)
    if last_time != current_time:
        print(data)
        all_data.append(data)
        save_to_json(all_data)
        save_to_xml(all_data)
        data = {}


def main():
    client = mqtt_client.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(HOST, PORT, KEEPALIVE)

    client.loop_forever()


if __name__ == "__main__":
    main()
