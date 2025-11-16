#define _CRT_SECURE_NO_WARNINGS
#include <ESP8266WiFi.h>
#include <PubSubClient.h>

// ===== WiFi 信息 =====
const char* ssid = "leon";
const char* password = "00001111";

// ===== MQTT Broker 信息 =====
const char* mqtt_server = "broker.emqx.io";  // 免费 Broker
const int mqtt_port = 1883;
const char* mqtt_topic = "cropsentinel/data";

WiFiClient espClient;
PubSubClient client(espClient);

// ========== 连接 WiFi ==========
void setup_wifi() {
  delay(10);
  Serial.println("连接 WiFi...");
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi 连接成功");
}

// ========== 连接 MQTT ==========
void reconnect() {
  while (!client.connected()) {
    Serial.println("尝试连接 MQTT...");
    if (client.connect("ESP8266_Client")) {
      Serial.println("MQTT 连接成功");
    } else {
      Serial.print("MQTT 连接失败,状态:");
      Serial.println(client.state());
      delay(2000);
    }
  }
}

void setup() {
  Serial.begin(115200);   // 用于接收电脑数据
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  // 如果串口有收到数据
  if (Serial.available()) {
    String data = Serial.readStringUntil('\n'); // 接收一行数据
    Serial.print("收到串口数据:");
    Serial.println(data);

    // 发布到 MQTT
    client.publish(mqtt_topic, data.c_str());
    Serial.println("已发布到 MQTT");
  }
}
