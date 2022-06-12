#include <WiFi.h>
#include <NeoPixelBus.h>
#include <WiFiUdp.h>

#define INPUT_DELAY 50
#define SCORE_COLOR  RgbColor(128, 0, 255)
#define EMPTY_COLOR   RgbColor(0) 
#define RESTART_DELAY 10000
#define DEFAULT_RESTART_DELAY 10000

const uint16_t PIXEL_COUNT = 8;
const uint8_t P1_PIXEL_PIN = 7;  
const uint8_t P2_PIXEL_PIN = 8;  

const int P1_UP = 2;
const int P1_DOWN = 4;

const char* SSID = "DTM";
const char* PASSWORD = "atiradeon21";

const char* HOST = "192.168.0.104";
const uint16_t P1_PORT = 65432;

const String UP_COMMAND = "U";
const String DOWN_COMMAND = "D";

byte buffer[11];
WiFiUDP udp;
uint8_t score[11];
NeoPixelBus<NeoGrbFeature, NeoEsp32BitBang800KbpsMethod> scoreP1(PIXEL_COUNT, P1_PIXEL_PIN);

TaskHandle_t p1Handler;

int p1ScoreCounter = 0;

//---------------- Restart -----------------------

//---------------- PINOUTS -----------------------
void initPins() {
  pinMode(P1_UP, INPUT_PULLUP);
  pinMode(P1_DOWN, INPUT_PULLUP);
}

//---------------- Wifi -----------------------
void initWifi() {
  Serial.println("Begin wifi connection ");
  WiFi.begin(SSID,PASSWORD);

  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(1000);
  }
  Serial.println("Wifi connection established");
}



WiFiClient p1_client;


void initSockets() {

  Serial.println("Connecting to socket");
  if(!p1_client.connect(HOST, P1_PORT)){
    Serial.println("Connection failed for player 1");
    delay(1000);

  }
}
//---------------- Setup -----------------------
void setup() {

  Serial.begin(115200L);
  while (!Serial); // wait for serial attach  

  delay(max(DEFAULT_RESTART_DELAY, RESTART_DELAY));

  initPins();
  initWifi();
  initSockets();
  xTaskCreatePinnedToCore(
                    Task1code,   /* Task function. */
                    "Player1",     /* name of task. */
                    10000,       /* Stack size of task */
                    NULL,        /* parameter of the task */
                    1,           /* priority of the task */
                    &p1Handler,      /* Task handle to keep track of created task */
                    0);          /* pin task to core 0 */     
  
}

void  Task1code(void * pvParameters) {
   while (p1_client.connected()) {
 
      while (p1_client.available()>0) {
        String line = p1_client.readString();
        Serial.println("Line is " + line);
      }
      delay(10);
    }
}

//---------------- Main -----------------------
void loop() {

  if(digitalRead(P1_UP) == LOW) {
    p1_client.println(UP_COMMAND);
    Serial.println(UP_COMMAND);
    delay(INPUT_DELAY);

  }else if(digitalRead(P1_DOWN) == LOW) {
    p1_client.println(DOWN_COMMAND);
    Serial.println(DOWN_COMMAND);
    delay(INPUT_DELAY);
  }
}
