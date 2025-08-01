#include <SoftwareSerial.h>
#include <SD.h> // Хотя библиотека SD не используется, но пусть будет.

SoftwareSerial BT(4, 7); // RX, TX для Bluetooth
#define IN1 5  // Должен быть PWM-пин
#define IN2 6  // Должен быть PWM-пин
#define IN3 9
#define IN4 10
char command; // Переменная для хранения команды

void setup() {
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  pinMode(13, OUTPUT);

  Serial.begin(9600); // Запускаем Serial Monitor
  BT.begin(9600);      // Запуск Bluetooth (HC-05/HC-06)
}

void loop() {
  if (BT.available() > 0) {
    command = BT.read(); // Считываем символ из Bluetooth
    digitalWrite(13, HIGH);  // Включаем светодиод

    switch (command) {
      case '0': // Остановка
        stopMotors();
        break;

      case '1': // Вперёд
        moveForward(100);
        break;

      case '2': // Назад
        moveBackward(100);
        break;

      case '3': // Влево
        turnLeft(100);
        break;

      case '4': // Вправо
        turnRight(100);
        break;

      default:
        Serial.print("Неизвестная команда: ");
        Serial.println(command); // Выводим в Serial Monitor код полученного символа
        break;
    }
    delay(50); // Задержка, чтобы увидеть светодиод
    digitalWrite(13, LOW); // Выключаем светодиод после обработки
  }
}

// Функции для движения машинки
void stopMotors() {
  analogWrite(IN1, 0);
  analogWrite(IN2, 0);
  analogWrite(IN3, 0);
  analogWrite(IN4, 0);
}

void moveForward(int speed) {
  analogWrite(IN1, speed);
  digitalWrite(IN2, LOW);
  analogWrite(IN3, speed);
  digitalWrite(IN4, LOW);
}

void moveBackward(int speed) {
  digitalWrite(IN1, LOW);
  analogWrite(IN2, speed);
  digitalWrite(IN3, LOW);
  analogWrite(IN4, speed);
}

void turnLeft(int speed) {
  digitalWrite(IN1, LOW);
  analogWrite(IN2, speed);
  analogWrite(IN3, speed);
  digitalWrite(IN4, speed);
}

void turnRight(int speed) {
  analogWrite(IN1, speed);
  digitalWrite(IN2, LOW);
  analogWrite(IN3, speed);
  digitalWrite(IN4, speed);
}