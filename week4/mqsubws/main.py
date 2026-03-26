"""MQ Subscriber WebSocket: ZeroMQ/MQTT 수신 → WebSocket 브로드캐스트."""

import asyncio
import json
import threading
from datetime import datetime, timezone

import paho.mqtt.client as mqtt
import zmq
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

ZMQ_BIND = "tcp://0.0.0.0:5555"
MQTT_BROKER = "mqbroker"
MQTT_PORT = 1883
MQTT_TOPIC = "week4/hello"

# 연결된 WebSocket 클라이언트 목록
clients: list[WebSocket] = []
# asyncio 이벤트 루프 (스레드 간 통신용)
loop: asyncio.AbstractEventLoop | None = None


async def broadcast(message: dict):
    """모든 WebSocket 클라이언트에 메시지 전송."""
    data = json.dumps(message)
    disconnected = []
    for ws in clients:
        try:
            await ws.send_text(data)
        except Exception:
            disconnected.append(ws)
    for ws in disconnected:
        clients.remove(ws)


def zmq_listener():
    """ZeroMQ PULL 소켓으로 메시지 수신 (별도 스레드)."""
    ctx = zmq.Context()
    pull_sock = ctx.socket(zmq.PULL)
    pull_sock.bind(ZMQ_BIND)
    print(f"ZeroMQ PULL bound on {ZMQ_BIND}")

    while True:
        msg = pull_sock.recv_string()
        timestamp = datetime.now(timezone.utc).isoformat()
        data = {"protocol": "ZeroMQ", "message": msg, "timestamp": timestamp}
        if loop is not None:
            asyncio.run_coroutine_threadsafe(broadcast(data), loop)


def mqtt_listener():
    """MQTT 구독으로 메시지 수신 (별도 스레드)."""
    def on_message(_client, _userdata, msg):
        timestamp = datetime.now(timezone.utc).isoformat()
        payload = msg.payload.decode("utf-8", errors="replace")
        data = {
            "protocol": "MQTT",
            "topic": msg.topic,
            "message": payload,
            "timestamp": timestamp,
        }
        if loop is not None:
            asyncio.run_coroutine_threadsafe(broadcast(data), loop)

    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id="mqsubws",
    )
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT)
    client.subscribe(MQTT_TOPIC)
    print(f"MQTT subscribed to {MQTT_TOPIC}")
    client.loop_forever()


@app.on_event("startup")
async def startup():
    """서버 시작 시 ZeroMQ/MQTT 리스너 스레드 실행."""
    global loop
    loop = asyncio.get_event_loop()

    zmq_thread = threading.Thread(target=zmq_listener, daemon=True)
    zmq_thread.start()

    mqtt_thread = threading.Thread(target=mqtt_listener, daemon=True)
    mqtt_thread.start()

    print("mqsubws started")


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    """WebSocket 연결 처리."""
    await ws.accept()
    clients.append(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        clients.remove(ws)
