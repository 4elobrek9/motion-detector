import logging
import time
import pygetwindow as gw
import numpy as np
import cv2
from PIL import ImageGrab
import threading
import keyboard
import os

# Настройка логирования с кодировкой UTF-8
logging.basicConfig(filename='system_monitor.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s', encoding='utf-8')

exit_program = False
# Значения чувствительности
sensitivity_map = {
    1: 1000,
    2: 15000,
    3: 40000
}

# Ввод чувствительности от пользователя
while True:
    try:
        sensitivity_choice = int(input("Выберите чувствительность (1, 2 или 3): "))
        if sensitivity_choice in sensitivity_map:
            break
        else:
            print("Пожалуйста, выберите 1, 2 или 3.")
    except ValueError:
        print("Введите целое число.")

trigger_pixel_count = sensitivity_map[sensitivity_choice]  # Получаем значение чувствительности
last_trigger_time = time.time()  
consecutive_triggers = 0  # Счетчик последовательных срабатываний
grouped_triggers = 0  # Счетчик групп из 4 срабатываний

def detect_motion():
    while not exit_program:
        time.sleep(1)

def clear_console():
    """Функция для очистки консоли."""
    os.system('cls' if os.name == 'nt' else 'clear')

def on_trigger(changed_pixels):
    global consecutive_triggers, grouped_triggers  # Используем глобальные переменные
    consecutive_triggers += 1  # Увеличиваем счетчик срабатываний

    if consecutive_triggers == 4:  # Если счетчик достиг 4
        clear_console()  # Очищаем консоль
        grouped_triggers += 1  # Увеличиваем счетчик групп
        logging.info(f"Кол ср: {grouped_triggers}. Изменено пикселей: {changed_pixels}")  # Записываем в лог
        print(f"Количество срабатываний: {grouped_triggers}. Изменено пикселей: {changed_pixels}")  # Выводим сообщение в консоль
        consecutive_triggers = 0  # Сбрасываем счетчик

def main():
    global exit_program, last_trigger_time, consecutive_triggers, grouped_triggers
    last_image = None
    last_window = None

    while not exit_program:
        try:
            # Проверяем наличие окна Iriun
            windows = gw.getWindowsWithTitle("Iriun")
            if windows:
                current_window = windows[0]  # Используем первое найденное окно
                bbox = (current_window.left, current_window.top, current_window.right, current_window.bottom)

                # Захватываем содержимое окна Iriun
                current_image = ImageGrab.grab(bbox)
                current_image_np = np.array(current_image)
                current_image_gray = cv2.cvtColor(current_image_np, cv2.COLOR_BGR2GRAY)

                if last_image is None:
                    last_image = current_image_gray
                    logging.info("Сохранено начальное изображение.")
                else:
                    difference = cv2.absdiff(last_image, current_image_gray)
                    _, thresh = cv2.threshold(difference, 30, 255, cv2.THRESH_BINARY)
                    non_zero_count = cv2.countNonZero(thresh)

                    if non_zero_count >= trigger_pixel_count:
                        on_trigger(non_zero_count)  # Передаем количество изменённых пикселей
                        last_trigger_time = time.time()
                        last_image = current_image_gray

            if keyboard.is_pressed('e'):
                logging.info("Выход из программы по нажатию клавиши 'E'.")
                print("Выход из программы...")
                exit_program = True

            time.sleep(1)

        except Exception as e:
            logging.error(f"Произошла ошибка: {e}")
            print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    print("Запуск системы обнаружения изменений пикселей в окне...")
    detect_motion_thread = threading.Thread(target=detect_motion)
    detect_motion_thread.start()
    main()
    detect_motion_thread.join()
