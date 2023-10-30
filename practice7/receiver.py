from concurrent.futures import ThreadPoolExecutor
import copy
import time
from paho.mqtt import client as mqtt_client  # type: ignore
from datetime import datetime
import json
import dict2xml
import pandas as pd


# Параметры подключения к MQTT-брокеру
HOST = "192.168.1.12"  # IP чемодана
PORT = 1883  # Стандартный порт подключения для Mosquitto
KEEPALIVE = 60
# Время ожидания доставки сообщения, если при отправке оно будет прeвышено,
# брокер будет считаться недоступным

# Словарь с топиками и собираемыми из них параметрами
# SUB_TOPICS = {
#     "/devices/wb-msw-v3_21/controls/Temperature": "temperature",
#     "/devices/wb-msw-v3_21/controls/Current Motion": "motion",
#     "/devices/wb-msw-v3_21/controls/Sound Level": "sound",
#     "/devices/wb-ms_11/controls/Illuminance": "illuminance",
# }

SUB_TOPICS = {
    "/devices/wb-msw-v3_21/controls/Temperature": "temperature",
    "/devices/wb-msw-v3_21/controls/Current Motion": "motion",
    "/devices/wb-map12e_23/controls/Ch 1 P L2": "power",
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

all_data = []


def save_to_json():
    with open("data.json", "w") as file:
        file.write(json.dumps(all_data))


def save_to_csv():
    with open("data.json", encoding="utf-8") as inputfile:
        df = pd.read_json(inputfile)
    df.to_csv("data.csv", index=False)


def save_to_xml():
    xml_string = dict2xml.dict2xml(all_data, wrap="item", indent="   ")
    with open("data.xml", "w") as file:
        file.write(xml_string)


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
    data["id"] = int(HOST.split(".")[-1])
    data[SUB_TOPICS[topic]] = float(payload)


def output_loop():
    while True:
        time.sleep(1)
        new_data = copy.deepcopy(data)
        new_data["time"] = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        print(new_data)
        all_data.append(new_data)
        save_to_json()
        save_to_csv()
        save_to_xml()


def main():
    client = mqtt_client.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(HOST, PORT, KEEPALIVE)
    with ThreadPoolExecutor(max_workers=2) as pool:
        pool.submit(client.loop_forever)
        pool.submit(output_loop)


if __name__ == "__main__":
    main()
