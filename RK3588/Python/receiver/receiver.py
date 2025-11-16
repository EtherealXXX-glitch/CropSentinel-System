import sqlite3  # 用于操作 SQLite 数据库
import sys
import io
import time
from paho.mqtt import client as mqtt_client  # MQTT 客户端

# ===============================
# 设置标准输出为行缓冲 + UTF-8
# ===============================
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

# ===============================
# 创建/连接数据库
# ===============================
conn = sqlite3.connect("sensor.db")  # 连接到本地数据库
cursor = conn.cursor()               # 创建游标

# 创建表（如果不存在）
cursor.execute("""
CREATE TABLE IF NOT EXISTS sensor_data(
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    topic TEXT,                            
    payload TEXT,                          
    time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()  # 提交事务

# ===============================
# MQTT 配置
# ===============================
broker = "broker.emqx.io"      # Broker 地址
port = 1883                     # 端口
topic = "cropsentinel/data"     # 订阅主题
client_id = "python-subscriber" # MQTT 客户端 ID，必须唯一

# ===============================
# 接收到消息回调
# ===============================
def on_message(client, userdata, msg):
    payload_str = msg.payload.decode()
    print(f"[MQTT] 收到主题: {msg.topic}", flush=True)
    print(f"[MQTT] 内容: {payload_str}", flush=True)

    # 写入数据库
    cursor.execute(
        "INSERT INTO sensor_data(topic, payload) VALUES(?, ?)",
        (msg.topic, payload_str)
    )
    conn.commit()
    print("[DB] 数据已写入数据库\n", flush=True)

# ===============================
# 连接并订阅
# ===============================
def connect_mqtt():
    print("[MQTT] 正在连接到 Broker...", flush=True)
    client = mqtt_client.Client(client_id=client_id)  # ⚠️注意：不再使用 callback_api_version
    client.on_message = on_message

    # 尝试连接 Broker，最多重试 5 次
    for i in range(5):
        try:
            client.connect(broker, port)
            print("[MQTT] 已成功连接到 Broker", flush=True)
            return client
        except Exception as e:
            print(f"[MQTT] 连接失败，重试中 ({i+1}/5) 错误: {e}", flush=True)
            time.sleep(2)

    print("[MQTT] 无法连接 Broker，程序退出", flush=True)
    sys.exit(1)

def run():
    client = connect_mqtt()
    client.subscribe(topic)
    print(f"[MQTT] 已订阅主题: {topic}", flush=True)
    print("[INFO] Python MQTT 客户端已启动，等待 ESP8266 消息…", flush=True)
    client.loop_forever()  # 阻塞等待消息

if __name__ == "__main__":
    print("[INFO] 启动 receiver.py 脚本", flush=True)
    run()
