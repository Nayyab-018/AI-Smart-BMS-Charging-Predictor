#include <math.h>

const int PIN_BATTERY_POT = A0;  // Potentiometer (0-100% Battery)
const int PIN_TEMP_SENSOR = A1;  // 10k NTC Thermistor
const int PIN_LED_NORMAL  = 8;   // Green LED (Safe Charging)
const int PIN_LED_ALERT   = 9;   // Red LED (Overheat Alert)
const int PIN_BUZZER      = 10;  // Piezo Buzzer

const float TEMP_THRESHOLD_C = 42.0; // Thermal throttling threshold (°C)

void setup() {
  Serial.begin(9600);
  pinMode(PIN_LED_NORMAL, OUTPUT);
  pinMode(PIN_LED_ALERT, OUTPUT);
  pinMode(PIN_BUZZER, OUTPUT);
  Serial.println("Battery_Pct,Voltage_V,Temp_C,Current_A,Charging_Mode,Est_Mins_Left");
}

void loop() {
  int rawPot = analogRead(PIN_BATTERY_POT);
  int batteryPct = map(rawPot, 0, 1023, 0, 100);
  float batteryVoltage = 3.20 + (batteryPct / 100.0) * 1.00;

  int rawTemp = constrain(analogRead(PIN_TEMP_SENSOR), 1, 1022);
  float resistance = 10000.0 * ((1023.0 / rawTemp) - 1.0);
  float tempK = 1.0 / (1.0 / 298.15 + (1.0 / 3950.0) * log(resistance / 10000.0));
  float tempC = tempK - 273.15;

  float chargingCurrentA = 0.0;
  String chargingMode = "IDLE";

  if (batteryPct >= 100) {
    chargingCurrentA = 0.0;
    chargingMode = "FULL_CUTOFF";
    digitalWrite(PIN_LED_NORMAL, LOW);
    digitalWrite(PIN_LED_ALERT, LOW);
    noTone(PIN_BUZZER);
  } else if (tempC >= TEMP_THRESHOLD_C) {
    chargingCurrentA = 0.5;
    chargingMode = "THERMAL_THROTTLE";
    digitalWrite(PIN_LED_NORMAL, LOW);
    digitalWrite(PIN_LED_ALERT, HIGH);
    tone(PIN_BUZZER, 1000, 150);
  } else if (batteryPct < 80) {
    chargingCurrentA = 3.0;
    chargingMode = "FAST_CC_25W";
    digitalWrite(PIN_LED_NORMAL, HIGH);
    digitalWrite(PIN_LED_ALERT, LOW);
    noTone(PIN_BUZZER);
  } else {
    chargingCurrentA = 1.2;
    chargingMode = "TRICKLE_CV";
    digitalWrite(PIN_LED_NORMAL, HIGH);
    digitalWrite(PIN_LED_ALERT, LOW);
    noTone(PIN_BUZZER);
  }

  float remainingAh = 5.0 * ((100.0 - batteryPct) / 100.0);
  int estMinutesLeft = (chargingCurrentA > 0.0) ? (int)((remainingAh / chargingCurrentA) * 60.0) : 0;

  Serial.print(batteryPct); Serial.print(",");
  Serial.print(batteryVoltage, 2); Serial.print(",");
  Serial.print(tempC, 1); Serial.print(",");
  Serial.print(chargingCurrentA, 1); Serial.print(",");
  Serial.print(chargingMode); Serial.print(",");
  Serial.println(estMinutesLeft);

  delay(1000);
}
