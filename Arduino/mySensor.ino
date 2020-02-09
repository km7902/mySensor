#include <DHT.h>

// Initializing DHT11 sensor
const int PIN_DHT = 8;
DHT dht(PIN_DHT, DHT11);

void setup() {

  //start serial connection
  Serial.begin(9600);

  //configure pin A3 as an input and enable the internal resistor
  pinMode(A3, INPUT);

  // start DHT11 sensor
  dht.begin();

}

void loop() {

  // Whether to display in Fahrenheit
  bool isFahrenheit = false;

  // Get humidity and temperature
  float percentHumidity = dht.readHumidity();
  float temperature = dht.readTemperature(isFahrenheit);

  // Do nothing if not available
  if (isnan(percentHumidity) || isnan(temperature)) {
    return;
  }

  // Get heat index
  float heatIndex = dht.computeHeatIndex(
    temperature,
    percentHumidity,
    isFahrenheit
  );

  //read the photocell value into a variable
  int photocell = analogRead(A3);

  //print out the sensor value in csv format
  String s = "";
  s += String(temperature, 1) + ",";
  s += String(percentHumidity, 1) + ",";
  s += String(heatIndex, 1) + ",";
  s += String(photocell);
  Serial.println(s);

  //delay 2000 ms
  delay(2000);

}
