// Copyright © 2019 Tom Aubier
// This program is free software: you can redistribute it and/or modify it

int TTLinPin = 4; // Jack Right
int TTLoutPin = 2; // Jack Left

void setup() {
  // Setup the input and output pins
  pinMode(TTLinPin, INPUT);
  pinMode(TTLoutPin, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  // This program generates a 10ms pulse whenever a '0' is received through its serial input.
  // A pulse comming from the turn table is then expected in order to confirm the rotation with a '2' in the serial port.
  while (Serial.available()) {
    if (Serial.read() == 0) { // If a '0' is received in the serial port
      // Sets the output pin to high for 10ms
      digitalWrite(TTLoutPin, HIGH);
      delay(10);
      digitalWrite(TTLoutPin, LOW);
      Serial.println("1"); // Confirms the reception of the message
      // Waits for the pulse comming from the table
      while (digitalRead(TTLinPin) == 0);
      while (digitalRead(TTLinPin) == 1);
      Serial.println("2"); // Confirms the rotation of the table
    }
  }
}
