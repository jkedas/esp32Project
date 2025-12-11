#define LIGHT_ANALOG_IN 34
#define SOUND_ANALOG_IN 35
#include "DHTesp.h"
#include <WiFi.h>
#include <WebServer.h>

const char* ssid = "breadboi";     
const char* password = "test1234";

WebServer server(80);

DHTesp dht;     //Define the DHT object
int dhtPin = 13;//Define the dht pin

float light = 0.0;
float temp = 0.0;
float humidity = 0.0;
float sound = 0.0;

void handleData() {
  String response = "{\"light\": " + String(light) + ", \"temp\": " + String(temp) + ", \"humidity\": " + String(humidity) + ", \"sound\": " + String(sound) + "}";
  server.send(200, "text/plain", response);
}

void setup() {
  pinMode(LIGHT_ANALOG_IN, INPUT);
  pinMode(SOUND_ANALOG_IN, INPUT);
  dht.setup(dhtPin, DHTesp::DHT11);
  Serial.begin(115200);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(200);
    Serial.print(".");
  }
  Serial.println("\nConnected!");
  Serial.print("ESP32 IP: ");
  Serial.println(WiFi.localIP());  
  server.on("/data", handleData);
  server.begin();
}

void loop() {
  Serial.println();
  if (WiFi.status() != WL_CONNECTED){
    Serial.println("Wifi Not Connected.");
  } else{
    Serial.println(WiFi.localIP());  
  }
  //light
  int lightAdcVal = analogRead(LIGHT_ANALOG_IN); //read adc 0 to 4095 which is 0 to 3.3V
  Serial.println("Light Sensor Value: " + String(lightAdcVal));
  if (lightAdcVal != 0) {
    light = (150000.0 / (lightAdcVal+76))-36; //aprox equation for lux reading
    Serial.println("Adjusted Light Value: " + String(light) + " Lux (Estimated)");
  } else {
    light = (150000.0 / (0.01+76))-40;
    Serial.println("Light Sensor out of Range.");
  }

  //temp and humidity
  flag:TempAndHumidity newValues = dht.getTempAndHumidity();//Get the Temperature and humidity
  if (dht.getStatus() != 0) {//Judge if the correct value is read
    Serial.println("No Temp Data");
    goto flag;               //If there is an error, go back to the flag and re-read the data
  }
  temp = (1.8*newValues.temperature+32);
  humidity = (newValues.humidity);
  Serial.println("Temperature: " + String(temp) + " F\nHumidity: " + String(humidity) + "%");

  // sound
  sound = analogRead(SOUND_ANALOG_IN)*3.3/4095; //outputs sound as 0-3.3V
  Serial.println("Sound Value: " + String(sound));

  server.handleClient();
  delay(500);
}
