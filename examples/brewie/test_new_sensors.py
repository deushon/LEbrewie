#!/usr/bin/env python

"""
Тестовый скрипт для проверки интеграции новых датчиков в робота Brewie.

Этот скрипт тестирует:
1. Новые моторы головы (23 - поворот, 24 - наклон)
2. Подписку на топик /joy (джойстик)
3. Подписку на топик /imu (гироскоп и акселерометр)

Использование:
    python examples/brewie/test_new_sensors.py
"""

import sys
import time
from pathlib import Path

# Добавляем путь к модулям lerobot
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from lerobot.robots.brewie.config_Brewie import BrewieConfig
from lerobot.robots.brewie.Brewie_base import BrewieBase

def test_robot_connection():
    """Тестирует подключение к роботу и получение данных с новых датчиков."""
    
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ НОВЫХ ДАТЧИКОВ BREWIE")
    print("=" * 60)
    
    # Создаем конфигурацию робота
    config = BrewieConfig(
        master_ip="192.168.20.21",
        master_port=9090,
    )
    
    print(f"Конфигурация робота:")
    print(f"  - ROS Master: {config.master_ip}:{config.master_port}")
    print(f"  - Моторы: {config.servo_ids}")
    print(f"  - Маппинг моторов: {config.servo_mapping}")
    print(f"  - Топик джойстика: {config.joy_topic}")
    print(f"  - Топик IMU: {config.imu_topic}")
    print()
    
    # Создаем экземпляр робота
    robot = BrewieBase(config)
    
    print("Признаки наблюдения:")
    for key, value in robot.observation_features.items():
        print(f"  - {key}: {value}")
    print()
    
    try:
        # Подключаемся к роботу
        print("Подключение к роботу...")
        robot.connect()
        print("✓ Подключение успешно!")
        print()
        
        # Тестируем получение данных
        print("Тестирование получения данных с датчиков...")
        print("Нажмите Ctrl+C для остановки")
        print()
        
        test_count = 0
        while test_count < 10:  # Тестируем 10 итераций
            try:
                # Получаем наблюдения
                obs = robot.get_observation()
                
                print(f"--- Итерация {test_count + 1} ---")
                
                # Проверяем моторы головы
                head_pan = obs.get("head_pan.pos", "N/A")
                head_tilt = obs.get("head_tilt.pos", "N/A")
                print(f"Моторы головы: pan={head_pan}, tilt={head_tilt}")
                
                # Проверяем джойстик
                joy_axes = [obs.get(f"joystick.axis_{i}", 0.0) for i in range(8)]
                joy_buttons = [obs.get(f"joystick.button_{i}", 0.0) for i in range(15)]
                print(f"Джойстик: axes={joy_axes[:4]}... (первые 4), buttons={joy_buttons[:4]}... (первые 4)")
                
                # Проверяем IMU
                imu_orientation = {
                    'x': obs.get("imu.orientation.x", 0.0),
                    'y': obs.get("imu.orientation.y", 0.0),
                    'z': obs.get("imu.orientation.z", 0.0),
                    'w': obs.get("imu.orientation.w", 0.0)
                }
                imu_angular_velocity = {
                    'x': obs.get("imu.angular_velocity.x", 0.0),
                    'y': obs.get("imu.angular_velocity.y", 0.0),
                    'z': obs.get("imu.angular_velocity.z", 0.0)
                }
                imu_linear_acceleration = {
                    'x': obs.get("imu.linear_acceleration.x", 0.0),
                    'y': obs.get("imu.linear_acceleration.y", 0.0),
                    'z': obs.get("imu.linear_acceleration.z", 0.0)
                }
                
                print(f"IMU ориентация: x={imu_orientation['x']:.3f}, y={imu_orientation['y']:.3f}, z={imu_orientation['z']:.3f}, w={imu_orientation['w']:.3f}")
                print(f"IMU угловая скорость: x={imu_angular_velocity['x']:.3f}, y={imu_angular_velocity['y']:.3f}, z={imu_angular_velocity['z']:.3f}")
                print(f"IMU линейное ускорение: x={imu_linear_acceleration['x']:.3f}, y={imu_linear_acceleration['y']:.3f}, z={imu_linear_acceleration['z']:.3f}")
                
                # Проверяем камеру
                if "camera" in obs:
                    camera_shape = obs["camera"].shape if hasattr(obs["camera"], 'shape') else "N/A"
                    print(f"Камера: shape={camera_shape}")
                
                print()
                test_count += 1
                time.sleep(1)
                
            except KeyboardInterrupt:
                print("\nТестирование прервано пользователем")
                break
            except Exception as e:
                print(f"Ошибка при получении данных: {e}")
                time.sleep(1)
        
        print("Тестирование завершено!")
        
    except Exception as e:
        print(f"Ошибка подключения: {e}")
        return False
    
    finally:
        # Отключаемся от робота
        try:
            print("Отключение от робота...")
            robot.disconnect()
            print("✓ Отключение успешно!")
        except Exception as e:
            print(f"Ошибка при отключении: {e}")
    
    return True

def test_sensor_subscribers():
    """Тестирует подписчики на датчики напрямую."""
    
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ ПОДПИСЧИКОВ НА ДАТЧИКИ")
    print("=" * 60)
    
    # Создаем конфигурацию робота
    config = BrewieConfig(
        master_ip="192.168.20.21",
        master_port=9090,
    )
    
    # Создаем экземпляр робота
    robot = BrewieBase(config)
    
    try:
        # Подключаемся к роботу
        print("Подключение к роботу...")
        robot.connect()
        print("✓ Подключение успешно!")
        print()
        
        # Тестируем подписчики
        print("Тестирование подписчиков...")
        
        # Тест джойстика
        if robot.joystick_subscriber:
            joy_data = robot.joystick_subscriber.get_last_joy_data()
            if joy_data:
                print(f"✓ Джойстик: получены данные - {len(joy_data['axes'])} осей, {len(joy_data['buttons'])} кнопок")
            else:
                print("⚠ Джойстик: данные не получены")
        else:
            print("✗ Джойстик: подписчик не инициализирован")
        
        # Тест IMU
        if robot.imu_subscriber:
            imu_data = robot.imu_subscriber.get_last_imu_data()
            if imu_data:
                print(f"✓ IMU: получены данные - ориентация, угловая скорость, линейное ускорение")
            else:
                print("⚠ IMU: данные не получены")
        else:
            print("✗ IMU: подписчик не инициализирован")
        
        # Тест камеры
        if robot.camera_subscriber:
            camera_data = robot.camera_subscriber.get_last_image()
            if camera_data is not None:
                print(f"✓ Камера: получено изображение размером {camera_data.shape}")
            else:
                print("⚠ Камера: изображение не получено")
        else:
            print("✗ Камера: подписчик не инициализирован")
        
        print()
        
    except Exception as e:
        print(f"Ошибка: {e}")
        return False
    
    finally:
        # Отключаемся от робота
        try:
            robot.disconnect()
        except Exception as e:
            print(f"Ошибка при отключении: {e}")
    
    return True

def main():
    """Основная функция тестирования."""
    
    print("Тестирование новых датчиков для робота Brewie")
    print("Убедитесь, что ROS master запущен и доступен по адресу 192.168.20.21:9090")
    print()
    
    # Выбор типа тестирования
    print("Выберите тип тестирования:")
    print("1. Полное тестирование (подключение + получение данных)")
    print("2. Тестирование только подписчиков")
    print("3. Оба теста")
    
    try:
        choice = input("Введите номер (1-3): ").strip()
        
        if choice == "1":
            test_robot_connection()
        elif choice == "2":
            test_sensor_subscribers()
        elif choice == "3":
            test_sensor_subscribers()
            print("\n" + "="*60 + "\n")
            test_robot_connection()
        else:
            print("Неверный выбор. Запуск полного тестирования...")
            test_robot_connection()
            
    except KeyboardInterrupt:
        print("\nТестирование прервано пользователем")
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()
