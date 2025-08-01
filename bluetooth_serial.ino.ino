#include <SoftwareSerial.h>

// Bluetooth модуль
const int RX_PIN = 2;
const int TX_PIN = 3;
SoftwareSerial bluetoothSerial(RX_PIN, TX_PIN);

const int ledPin = 13; // Светодиод как индикатор

void setup() {
  Serial.begin(9600); // USB Serial
  bluetoothSerial.begin(9600); // Bluetooth Serial
  pinMode(ledPin, OUTPUT);
  Serial.println("Arduino готов к приему и отправке...");
}

void loop() {
  // Проверка, есть ли данные с USB Serial (от Python)
  if (Serial.available() > 0) {
    String receivedString = Serial.readStringUntil('\n'); // Читаем данные до символа новой строки
    receivedString.trim(); // Удаляем пробелы

    // Проверяем, что строка не пустая
    if (receivedString.length() > 0) {
      int receivedNumber = receivedString.toInt(); // Преобразуем строку в число

      Serial.print("Получено с USB: ");
      Serial.println(receivedNumber);

      // Проверяем, что преобразование прошло успешно
      if (receivedNumber != 0 || receivedString == "0") {
        digitalWrite(ledPin, HIGH); // Включаем светодиод (сигнал получен)

        // Отправляем число по Bluetooth
        bluetoothSerial.println(receivedNumber);
        Serial.print("Отправлено по Bluetooth: ");
        Serial.println(receivedNumber);
      } else {
        Serial.println("Не удалось преобразовать в число");
        digitalWrite(ledPin, LOW); // на всякий случай выключаем LED
      }
    } else {
      Serial.println("Получена пустая строка");
    }
    delay(50); // Небольшая задержка
    digitalWrite(ledPin, LOW); // Выключаем светодиод после обработки
  }
}