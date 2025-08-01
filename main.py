import cv2  # Импорт библиотеки OpenCV для работы с изображениями и видео
import mediapipe as mp  # Импорт библиотеки MediaPipe для отслеживания движений рук
import numpy as np  # Импорт библиотеки NumPy для работы с массивами и матрицами
import serial.tools.list_ports  # Импорт модуля serial.tools.list_ports для поиска доступных COM-портов
import time  # Импорт модуля time для работы со временем

# --- Настройка последовательного порта ---
ser = serial.Serial("COM7", 9600, timeout=1)
if ser is None:  # Проверка, удалось ли открыть COM-порт
    print("Error")  # Вывод сообщения об ошибке в случае неудачи
    exit()  # Завершение программы

time.sleep(2)  # Задержка 2 секунды (необходима для инициализации COM-порта Arduino)
# --- Настройка MediaPipe Hands ---
mp_hands = mp.solutions.hands  # Получение модуля hands из библиотеки MediaPipe
mp_drawing = mp.solutions.drawing_utils  # Получение модуля drawing_utils для рисования линий на изображении
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7)

tip_ids = [4, 8, 12, 16, 20]
base_ids = [0, 5, 9, 13, 17]
# --- Настройка захвата видео с камеры ---
cap = cv2.VideoCapture(0)

# --- Пороговые значения для определения выпрямленности пальцев ---
extension_threshold = 0.17  # Порог для определения, является ли палец выпрямленным (больше - палец должен быть более выпрямленным)
thumb_extension_threshold = 0.1 # Порог для определения, является ли большой палец выпрямленным (больше - палец должен быть более выпрямленным)

# --- Функции для анализа положения рук ---
def get_vector(p1, p2):
    return np.array([p2.x - p1.x, p2.y - p1.y, p2.z - p1.z])  # Возвращает вектор в виде NumPy массив
def is_finger_extended(base, tip, is_thumb=False):
    # Функция для определения, выпрямлен ли палец (is_thumb - True для большого пальца, False для остальных)
    base_to_tip = get_vector(base, tip)  # Вычисление вектора от основания пальца к кончику
    base_to_tip_norm = np.linalg.norm(base_to_tip)  # Вычисление длины вектора (нормы)
    if is_thumb:
        # Если это большой палец, используем другой порог
        return base_to_tip_norm > thumb_extension_threshold  # Возвращает True, если палец выпрямлен
    else:
        return base_to_tip_norm > extension_threshold  # Возвращает True, если палец выпрямлен
def count_fingers(hand_landmarks):
    # Функция для подсчета выпрямленных пальцев на руке
    finger_count = 0  # Инициализация счетчика выпрямленных пальцев
    extended_fingers = []  # Список для хранения индексов выпрямленных пальцев
    finger_states = [0, 0, 0, 0, 0] # Список для хранения состояния пальцев (0 - согнут, 1 - выпрямлен).
    if hand_landmarks:  # Проверка, обнаружены ли landmark'и руки
        landmarks = hand_landmarks.landmark  # Получение списка landmark'ов
        for i in range(1, 5):  # Цикл по пальцам (начиная с указательного и заканчивая мизинцем)
            if is_finger_extended(landmarks[base_ids[i]], landmarks[tip_ids[i]]):  # Проверка, выпрямлен ли палец
                finger_count += 1  # Увеличение счетчика выпрямленных пальцев
                extended_fingers.append(tip_ids[i])  # Добавление индекса кончика пальца в список выпрямленных пальцев
                finger_states[i] = 1 # Записываем, что палец выпрямлен
    return finger_count, extended_fingers, finger_states

while True:  # Бесконечный цикл для обработки видеопотока
    ret, frame = cap.read()  # Чтение кадра из видеопотока
    if not ret:  # Проверка, успешно ли прочитан кадр
        continue  # Если кадр не прочитан, переходим к следующей итерации цикла

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Преобразование цветового пространства из BGR (используется в OpenCV) в RGB (используется в MediaPipe)
    results = hands.process(frame)  # Обработка кадра с помощью MediaPipe Hands (получение результатов отслеживания рук)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # Преобразование обратно в BGR для отображения с помощью OpenCV

    value_to_send = -1  # Инициализация переменной для хранения значения, которое будет отправлено на Arduino (-1 - значение по умолчанию, означает "жест не распознан")

    if results.multi_hand_landmarks:  # Проверка, обнаружены ли руки на кадре
        for hand_landmarks in results.multi_hand_landmarks:  # Цикл по всем обнаруженным рукам (в данном случае, должна быть только одна)
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)  # Рисование ключевых точек и соединительных линий на изображении

            fingers_counted, extended_fingers, finger_states = count_fingers(hand_landmarks)  # Вызов функции для подсчета выпрямленных пальцев и определения их состояния

            # Отображение кругов на кончиках выпрямленных пальцев
            for tip_index in extended_fingers:  # Цикл по индексам выпрямленных пальцев
                tip_landmark = hand_landmarks.landmark[tip_index]  # Получение координат кончика пальца
                x, y = int(tip_landmark.x * frame.shape[1]), int(tip_landmark.y * frame.shape[0])  # Преобразование относительных координат в абсолютные (пиксельные)
                cv2.circle(frame, (x, y), 10, (0, 255, 0), cv2.FILLED)  # Рисование круга на кончике пальца

            # Создание строки, отображающей состояние пальцев
            finger_state_text = ' '.join(['1' if state else '0' for state in finger_states])  # Преобразование списка состояний пальцев в строку (1 - выпрямлен, 0 - согнут)
            cv2.putText(frame, f'Fingers: {finger_state_text}', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2,
                        cv2.LINE_AA)  # Вывод текста с состоянием пальцев на изображение

            # Сопоставление состояний пальцев с командами управления роботом
            match finger_state_text:
                case "0 0 0 0 0":  # Все пальцы согнуты
                    value_to_send = 0  # Соответствует команде "Стоп"
                case "0 1 1 1 0":  # Три пальца выпрямлены (указательный, средний, безымянный)
                    value_to_send = 1  # Соответствует команде "Вперед"
                case "0 1 1 1 1":  # Четыре пальца выпрямлены (указательный, средний, безымянный, мизинец)
                    value_to_send = 2  # Соответствует команде "Вперед с ускорением"
                case "0 0 0 0 1":  # Только мизинец выпрямлен
                    value_to_send = 3  # Соответствует команде "Влево"
                case "0 1 0 0 0":  # Только указательный палец выпрямлен
                    value_to_send = 4  # Соответствует команде "Вправо"
                case _:  # Жест не распознан
                    value_to_send = -1  # Оставляем значение по умолчанию "-1"

            # Отправка команды управления на Arduino
            if value_to_send != -1:  # Проверка, был ли распознан жест
                # Отправляем int как строку с символом новой строки по USB Serial
                ser.write((str(value_to_send) + '\n').encode('utf-8'))  # Отправка значения на Arduino в виде строки, закодированной в UTF-8, с добавлением символа новой строки
                time.sleep(0.05)  # Небольшая задержка

    cv2.imshow('Fingers Count', frame)  # Отображение изображения с распознанными жестами в окне

    if cv2.waitKey(10) & 0xFF == 27:  # Ожидание нажатия клавиши (10 мс), проверка, не нажата ли клавиша "Esc" (код 27)
        break  # Выход из цикла, если нажата клавиша "Esc"

cap.release()  # Освобождение ресурсов камеры
cv2.destroyAllWindows()  # Закрытие всех окон OpenCV

