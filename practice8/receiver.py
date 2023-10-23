from paho.mqtt import client as mqtt_client
import json
from datetime import datetime

HOST = "192.168.1.11"
PORT = 1883
KEEPALIVE = 60

SUB_TOPICS = {
    "/devices/wb-msw-v3_21/controls/Temperature": "temperature",
    "/devices/wb-msw-v3_21/controls/Current Motion": "motion",
    "/devices/wb-msw-v3_21/controls/Sound Level": "sound",
    "/devices/wb-mir_19/controls/Input Voltage": "voltage",
}

JSON_LIST = []

JSON_DICT = {}
for value in SUB_TOPICS.values():
    JSON_DICT[value] = 0


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

    param_name = SUB_TOPICS[topic]
    JSON_DICT["id"] = int(HOST.split(".")[-1])
    JSON_DICT["time"] = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    JSON_DICT[param_name] = float(payload)

    JSON_LIST.append(JSON_DICT.copy())

    print(topic + " " + payload)

    with open("data.json", "w") as file:
        json_string = json.dumps(JSON_LIST)
        file.write(json_string)


def main():
    client = mqtt_client.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(HOST, PORT, KEEPALIVE)

    client.loop_forever()


if __name__ == "__main__":
    main()
