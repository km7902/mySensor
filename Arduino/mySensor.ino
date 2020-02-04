
void setup() {

  //start serial connection
  Serial.begin(9600);

  //configure pin A3 as an input and enable the internal resistor
  pinMode(A3, INPUT);

}

void loop() {

  //read the photocell value into a variable
  int sensorVal = analogRead(A3);

  //print out the value of the photocell
  Serial.println(sensorVal);

  //delay 1000 ms
  delay(1000);

}
