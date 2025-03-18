import time
import pygetwindow as gw
import numpy as np
import cv2
from PIL import ImageGrab
import threading
import keyboard
import os

exit_program = False
sensitivity_map = {
    1: 1000,
    2: 15000,
    3: 40000
}

while True:
    try:
        sensitivity_choice = int(input("Выберите чувствительность (1, 2 или 3): "))
        if sensitivity_choice in sensitivity_map:
            break
        else:
            print("Пожалуйста, выберите 1, 2 или 3.")
    except ValueError:
        print("Введите целое число.")

trigger_pixel_count = sensitivity_map[sensitivity_choice]
last_trigger_time = time.time()  
consecutive_triggers = 0  
grouped_triggers = 0  

def detect_motion():
    while not exit_program:
        time.sleep(1)

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def write_to_file(value):
    with open(r'C:\Users\aboby\motion-detector\value.txt', 'w') as f:
        f.write(f"check = {value}\n")

def on_trigger(changed_pixels):
    global consecutive_triggers, grouped_triggers
    consecutive_triggers += 1  

    if consecutive_triggers == 4:  
        clear_console()  
        grouped_triggers += 1  
        print(f"Количество срабатываний: {grouped_triggers}. Изменено пикселей: {changed_pixels}")  
        write_to_file(grouped_triggers)
        consecutive_triggers = 0  

def main():
    global exit_program, last_trigger_time, consecutive_triggers, grouped_triggers
    last_image = None

    while not exit_program:
        try:
            windows = gw.getWindowsWithTitle("Iriun")
            if windows:
                current_window = windows[0]
                bbox = (current_window.left, current_window.top, current_window.right, current_window.bottom)

                current_image = ImageGrab.grab(bbox)
                current_image_np = np.array(current_image)
                current_image_gray = cv2.cvtColor(current_image_np, cv2.COLOR_BGR2GRAY)

                if last_image is None:
                    last_image = current_image_gray
                else:
                    difference = cv2.absdiff(last_image, current_image_gray)
                    _, thresh = cv2.threshold(difference, 30, 255, cv2.THRESH_BINARY)
                    non_zero_count = cv2.countNonZero(thresh)

                    if non_zero_count >= trigger_pixel_count:
                        on_trigger(non_zero_count)  
                        last_trigger_time = time.time()
                        last_image = current_image_gray

            if keyboard.is_pressed('e'):
                print("Выход из программы...")
                grouped_triggers = 0
                write_to_file(grouped_triggers)
                exit_program = True

            time.sleep(1)

        except Exception as e:
            print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    print("Запуск системы обнаружения изменений пикселей в окне...")
    detect_motion_thread = threading.Thread(target=detect_motion)
    detect_motion_thread.start()
    main()
    detect_motion_thread.join()
