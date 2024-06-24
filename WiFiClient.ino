#include <ESP8266WiFi.h>
#include <Servo.h>
#include <WiFiUdp.h>
#include <EEPROM.h>

const int EEPROM_SIZE = 96;
const int SSID_START = 0;
const int PASSWORD_START = 32;
const int MAX_SSID_LENGTH = 32;
const int MAX_PASSWORD_LENGTH = 64;

WiFiUDP udp;  // 创建一个UDP对象
Servo myServo;  // 创建Servo对象

const int servoPin = 5;  // 舵机信号引脚
const int rstPin = 0;    // RST引脚

unsigned long previousMillis = 0;  // 用于存储上一次引脚高电平的时间
const long interval = 200;  // 高电平维持的时间间隔
unsigned long ledPreviousMillis = 0;
const long ledInterval = 1000;  // LED闪烁间隔
bool ledState = false;

void smartConfig() {
  WiFi.mode(WIFI_STA);
  Serial.println("\r\nWait for Smartconfig...");
  WiFi.beginSmartConfig();  // 等待手机端发出的用户名与密码
  while (!WiFi.smartConfigDone()) {
    Serial.print(".");
    delay(1000);
  }
  Serial.println("SmartConfig Success");
  Serial.printf("SSID:%s\r\n", WiFi.SSID().c_str());
  Serial.printf("PSW:%s\r\n", WiFi.psk().c_str());
}

void setup() {
  Serial.begin(115200);
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(rstPin, INPUT);
  myServo.attach(servoPin);  // 将舵机连接到指定引脚
  myServo.write(0);
  WiFi.mode(WIFI_STA);

  EEPROM.begin(EEPROM_SIZE);

  Serial.println("\r\n正在连接");
  if (!connectToSavedWiFi()) {
    smartConfig();  // 微信智能配网
    saveCredentials(WiFi.SSID(), WiFi.psk());  // 保存凭据到EEPROM
  }

  Serial.println("连接成功");
  Serial.print("IP:");
  Serial.println(WiFi.localIP());

  udp.begin(5555);  // 启动UDP监听端口5555
}

void loop() {
  // 处理UDP广播请求
  handleUDP();

  // 检查是否需要将舵机恢复到初始位置
  if (millis() - previousMillis >= interval) {
    myServo.write(0);
  }
}

bool connectToSavedWiFi() {
  char ssid[MAX_SSID_LENGTH];
  char password[MAX_PASSWORD_LENGTH];

  if (readCredentials(ssid, password)) {
    return connectToWiFi(ssid, password);
  }
  return false;
}

bool readCredentials(char* ssid, char* password) {
  for (int i = SSID_START; i < SSID_START + MAX_SSID_LENGTH; ++i) {
    ssid[i - SSID_START] = EEPROM.read(i);
  }
  ssid[MAX_SSID_LENGTH - 1] = '\0';  // 确保字符串以NULL结尾

  for (int i = PASSWORD_START; i < PASSWORD_START + MAX_PASSWORD_LENGTH; ++i) {
    password[i - PASSWORD_START] = EEPROM.read(i);
  }
  password[MAX_PASSWORD_LENGTH - 1] = '\0';  // 确保字符串以NULL结尾

  return (strlen(ssid) > 0 && strlen(password) > 0);
}

bool connectToWiFi(const char* ssid, const char* password) {
  WiFi.begin(ssid, password);
  Serial.print("Connecting to ");
  Serial.println(ssid);

  uint8_t i = 0;
  while (WiFi.status() != WL_CONNECTED && i++ < 20) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");

  if (WiFi.status() == WL_CONNECTED) {
    Serial.print("Connected! IP address: ");
    Serial.println(WiFi.localIP());
    return true;
  } else {
    Serial.println("Connection failed.");
    return false;
  }
}

void saveCredentials(String ssid, String password) {
  for (int i = 0; i < MAX_SSID_LENGTH; ++i) {
    if (i < ssid.length()) {
      EEPROM.write(SSID_START + i, ssid[i]);
    } else {
      EEPROM.write(SSID_START + i, 0);
    }
  }

  for (int i = 0; i < MAX_PASSWORD_LENGTH; ++i) {
    if (i < password.length()) {
      EEPROM.write(PASSWORD_START + i, password[i]);
    } else {
      EEPROM.write(PASSWORD_START + i, 0);
    }
  }

  EEPROM.commit();
}

void handleUDP() {
  // 检查是否有UDP数据包到达
  int packetSize = udp.parsePacket();
  if (packetSize) {
    // 读取数据包内容
    char packetBuffer[UDP_TX_PACKET_MAX_SIZE];
    udp.read(packetBuffer, UDP_TX_PACKET_MAX_SIZE);
    String request = String(packetBuffer);

    // 判断是否收到特定的广播请求消息
    if (request.startsWith("ServerDiscoveryRequest")) {
      IPAddress remoteIP = udp.remoteIP();
      IPAddress localIP = WiFi.localIP();
      udp.beginPacket(remoteIP, udp.remotePort());
      udp.print(localIP.toString());
      udp.endPacket();
    } else if (request == "1") {
      myServo.write(90);
      previousMillis = millis();  // 记录当前时间
    }else if (request == "2"){
      clearEEPROM();
      delay(500);
      ESP.restart();
    }
  }
}

void clearEEPROM() {
  for (int i = 0; i < EEPROM_SIZE; ++i) {
    EEPROM.write(i, 0);
  }
  EEPROM.commit();
  Serial.println("EEPROM cleared");
}
