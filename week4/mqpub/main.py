"""MQ Publisher: 5초 간격으로 ZeroMQ PUSH + MQTT publish."""

import time

import paho.mqtt.client as mqtt
import zmq

ZMQ_ENDPOINT = "tcp://mqsubws:5555"
MQTT_BROKER = "mqbroker"
MQTT_PORT = 1883
MQTT_TOPIC = "week4/hello"
INTERVAL_SEC = 5


def main():
    """ZeroMQ PUSH, MQTT publish를 5초 간격으로 실행."""
    # ZeroMQ PUSH 소켓
    ctx = zmq.Context()
    push_sock = ctx.socket(zmq.PUSH)
    push_sock.connect(ZMQ_ENDPOINT)

    # MQTT 클라이언트
    mqtt_client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id="mqpub",
    )
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
    mqtt_client.loop_start()

    print("mqpub started")

    try:
        while True:
            push_sock.send_string("Hello ZeroMQ")
            print("ZeroMQ PUSH: Hello ZeroMQ")

            mqtt_client.publish(MQTT_TOPIC, "Hello MQTT")
            print(f"MQTT PUBLISH [{MQTT_TOPIC}]: Hello MQTT")

            time.sleep(INTERVAL_SEC)
    except KeyboardInterrupt:
        pass
    finally:
        push_sock.close()
        ctx.term()
        mqtt_client.loop_stop()
        mqtt_client.disconnect()


if __name__ == "__main__":
    main()
