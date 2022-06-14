#include <WiFi.h>
#include <NeoPixelBus.h>
#include <WiFiUdp.h>
#include <LiquidCrystal_I2C.h>

#define INPUT_DELAY 70
#define SCORE_COLOR  RgbColor(128, 0, 255)
#define EMPTY_COLOR   RgbColor(0) 
#define RESTART_DELAY 10000
#define DEFAULT_RESTART_DELAY 10000
#define BUFFER_SIZE 4
int lcdColumns = 16;
int lcdRows = 2;

const uint16_t PIXEL_COUNT = 8;
const uint8_t P1_PIXEL_PIN = 7;  
const uint8_t P2_PIXEL_PIN = 8;  

const int P1_UP = 2;
const int P1_DOWN = 4;

const char* SSID = "DTM";
const char* PASSWORD = "atiradeon21";

const char* HOST = "192.168.0.104";
const uint16_t PORT = 65432;

const uint8_t UP_COMMAND[3] = "U1";
const uint8_t DOWN_COMMAND[3] = "U2";

byte buffer[11];
WiFiUDP udp;
uint8_t score[11];
NeoPixelBus<NeoGrbFeature, NeoEsp32BitBang800KbpsMethod> scoreP1(PIXEL_COUNT, P1_PIXEL_PIN);

TaskHandle_t p1Handler;
LiquidCrystal_I2C lcd(0x27, lcdColumns, lcdRows);  

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
  if(!p1_client.connect(HOST, PORT)){
    Serial.println("Connection failed for player 1");
    delay(1000);

  }
}
//---------------- Setup -----------------------
void setup() {

  Serial.begin(115200L);
  while (!Serial); // wait for serial attach  

  delay(max(DEFAULT_RESTART_DELAY, RESTART_DELAY));
  lcd.init();
  // turn on LCD backlight                      
  lcd.backlight();
  initPins();
  initWifi();
  //initSockets();
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
    uint8_t buffer[BUFFER_SIZE];
    String line = "";
    for(;;) {
      udp.parsePacket();
      if(udp.read(buffer,BUFFER_SIZE) > 0)
      {
        line = String((char*)buffer);
        if(line.indexOf(':') > 0) 
        {
             lcd.clear();
             lcd.setCursor(0, 0);
             lcd.print(line);
             Serial.println(line);
             memset(buffer,0,BUFFER_SIZE);
        }
       
      }
      delay(INPUT_DELAY);
    }
    vTaskDelete(NULL);
}

//---------------- Main -----------------------
void loop() {

  if(digitalRead(P1_UP) == LOW) {
     udp.beginPacket(HOST,PORT);
     udp.write(UP_COMMAND, 3);
     udp.endPacket();
     delay(INPUT_DELAY);

  }else if(digitalRead(P1_DOWN) == LOW) {
      udp.beginPacket(HOST, PORT);
     udp.write(DOWN_COMMAND, 3);
     udp.endPacket();
    delay(INPUT_DELAY);
  }
  
}
