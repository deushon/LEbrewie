#!/usr/bin/env python

"""
Диагностический скрипт для измерения производительности получения наблюдений.

Этот скрипт поможет определить, сколько времени занимает получение данных
с каждого датчика и общее время получения наблюдений.
"""

import sys
import time
import statistics
from pathlib import Path

# Добавляем путь к модулям lerobot
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from lerobot.robots.brewie.config_Brewie import BrewieConfig
from lerobot.robots.brewie.Brewie_base import BrewieBase

def measure_observation_performance(robot, num_samples=100):
    """Измеряет производительность получения наблюдений."""
    
    print(f"Измерение производительности получения наблюдений...")
    print(f"Количество образцов: {num_samples}")
    print()
    
    times = []
    
    for i in range(num_samples):
        start_time = time.perf_counter()
        obs = robot.get_observation()
        end_time = time.perf_counter()
        
        dt_ms = (end_time - start_time) * 1000
        times.append(dt_ms)
        
        if i % 10 == 0:
            print(f"Образец {i+1}/{num_samples}: {dt_ms:.1f}ms")
    
    # Статистика
    mean_time = statistics.mean(times)
    median_time = statistics.median(times)
    min_time = min(times)
    max_time = max(times)
    std_time = statistics.stdev(times) if len(times) > 1 else 0
    
    print()
    print("=" * 50)
    print("РЕЗУЛЬТАТЫ ИЗМЕРЕНИЯ ПРОИЗВОДИТЕЛЬНОСТИ")
    print("=" * 50)
    print(f"Среднее время: {mean_time:.1f}ms")
    print(f"Медианное время: {median_time:.1f}ms")
    print(f"Минимальное время: {min_time:.1f}ms")
    print(f"Максимальное время: {max_time:.1f}ms")
    print(f"Стандартное отклонение: {std_time:.1f}ms")
    print()
    
    # Анализ FPS
    print("АНАЛИЗ FPS:")
    print(f"Фактический FPS (средний): {1000/mean_time:.1f}")
    print(f"Фактический FPS (медианный): {1000/median_time:.1f}")
    print(f"Фактический FPS (минимальный): {1000/max_time:.1f}")
    print(f"Фактический FPS (максимальный): {1000/min_time:.1f}")
    print()
    
    # Рекомендации
    print("РЕКОМЕНДАЦИИ:")
    if mean_time > 33.33:  # Больше 30 FPS
        print("⚠️  ВНИМАНИЕ: Время получения наблюдений превышает 33.33ms")
        print("   Это означает, что фактический FPS будет ниже 30")
        print("   Рекомендуется снизить целевую частоту записи")
        
        recommended_fps = int(1000 / mean_time)
        print(f"   Рекомендуемая частота записи: {recommended_fps} FPS")
    else:
        print("✅ Время получения наблюдений в пределах нормы")
        print(f"   Можно поддерживать частоту записи до {int(1000/mean_time)} FPS")
    
    return {
        'mean_time': mean_time,
        'median_time': median_time,
        'min_time': min_time,
        'max_time': max_time,
        'std_time': std_time,
        'actual_fps': 1000/mean_time
    }

def test_individual_sensors(robot):
    """Тестирует производительность отдельных датчиков."""
    
    print("=" * 50)
    print("ТЕСТИРОВАНИЕ ОТДЕЛЬНЫХ ДАТЧИКОВ")
    print("=" * 50)
    
    # Тест моторов
    print("Тестирование моторов...")
    motor_times = []
    for i in range(20):
        start = time.perf_counter()
        obs = robot.get_observation()
        # Извлекаем только данные моторов
        motor_data = {k: v for k, v in obs.items() if k.endswith('.pos')}
        end = time.perf_counter()
        motor_times.append((end - start) * 1000)
    
    print(f"Моторы: {statistics.mean(motor_times):.1f}ms ± {statistics.stdev(motor_times):.1f}ms")
    
    # Тест джойстика
    print("Тестирование джойстика...")
    joy_times = []
    for i in range(20):
        start = time.perf_counter()
        obs = robot.get_observation()
        # Извлекаем только данные джойстика
        joy_data = {k: v for k, v in obs.items() if k.startswith('joystick.')}
        end = time.perf_counter()
        joy_times.append((end - start) * 1000)
    
    print(f"Джойстик: {statistics.mean(joy_times):.1f}ms ± {statistics.stdev(joy_times):.1f}ms")
    
    # Тест IMU
    print("Тестирование IMU...")
    imu_times = []
    for i in range(20):
        start = time.perf_counter()
        obs = robot.get_observation()
        # Извлекаем только данные IMU
        imu_data = {k: v for k, v in obs.items() if k.startswith('imu.')}
        end = time.perf_counter()
        imu_times.append((end - start) * 1000)
    
    print(f"IMU: {statistics.mean(imu_times):.1f}ms ± {statistics.stdev(imu_times):.1f}ms")
    
    # Тест камеры
    print("Тестирование камеры...")
    camera_times = []
    for i in range(20):
        start = time.perf_counter()
        obs = robot.get_observation()
        # Извлекаем только данные камеры
        camera_data = {k: v for k, v in obs.items() if k == 'camera'}
        end = time.perf_counter()
        camera_times.append((end - start) * 1000)
    
    print(f"Камера: {statistics.mean(camera_times):.1f}ms ± {statistics.stdev(camera_times):.1f}ms")

def main():
    """Основная функция тестирования производительности."""
    
    print("Диагностика производительности робота Brewie")
    print("Убедитесь, что ROS master запущен и доступен")
    print()
    
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
        
        # Тестируем отдельные датчики
        test_individual_sensors(robot)
        print()
        
        # Измеряем общую производительность
        results = measure_observation_performance(robot, num_samples=50)
        
        # Дополнительные рекомендации
        print()
        print("ДОПОЛНИТЕЛЬНЫЕ РЕКОМЕНДАЦИИ:")
        if results['actual_fps'] < 20:
            print("🔴 КРИТИЧНО: Очень низкая производительность!")
            print("   Рекомендуется:")
            print("   - Проверить подключение к ROS")
            print("   - Уменьшить количество датчиков")
            print("   - Использовать частоту записи 10-15 FPS")
        elif results['actual_fps'] < 25:
            print("🟡 ПРЕДУПРЕЖДЕНИЕ: Производительность ниже оптимальной")
            print("   Рекомендуется использовать частоту записи 20-25 FPS")
        else:
            print("🟢 ХОРОШО: Производительность в норме")
            print("   Можно использовать стандартную частоту записи 30 FPS")
        
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

if __name__ == "__main__":
    main()
