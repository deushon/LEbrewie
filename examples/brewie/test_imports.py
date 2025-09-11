#!/usr/bin/env python

"""
Тестовый скрипт для проверки корректности импортов и конфигурации.

Этот скрипт проверяет, что все необходимые модули могут быть импортированы
и что конфигурация корректна.

Использование:
    python examples/brewie/test_imports.py
"""

import sys
from pathlib import Path

def test_imports():
    """Тест импортов всех необходимых модулей."""
    print("Проверка импортов...")
    
    try:
        # Добавляем путь к модулям lerobot
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
        
        # Тест импорта LeRobot модулей
        from lerobot.datasets.lerobot_dataset import LeRobotDataset
        print("✓ LeRobotDataset импортирован")
        
        from lerobot.datasets.utils import hw_to_dataset_features
        print("✓ hw_to_dataset_features импортирован")
        
        from lerobot.record import record_loop
        print("✓ record_loop импортирован")
        
        from lerobot.robots.brewie.config_Brewie import BrewieConfig
        print("✓ BrewieConfig импортирован")
        
        from lerobot.robots.brewie.Brewie_base import BrewieBase
        print("✓ BrewieBase импортирован")
        
        from lerobot.teleoperators.keyboard import KeyboardTeleop, KeyboardTeleopConfig
        print("✓ KeyboardTeleop импортирован")
        
        from lerobot.utils.control_utils import init_keyboard_listener
        print("✓ init_keyboard_listener импортирован")
        
        from lerobot.utils.utils import log_say
        print("✓ log_say импортирован")
        
        from lerobot.utils.visualization_utils import _init_rerun
        print("✓ _init_rerun импортирован")
        
        # Тест импорта конфигурации
        from record_config import config, RecordingConfig
        print("✓ record_config импортирован")
        
        return True
        
    except ImportError as e:
        print(f"✗ Ошибка импорта: {e}")
        return False
    except Exception as e:
        print(f"✗ Неожиданная ошибка: {e}")
        return False

def test_config():
    """Тест конфигурации."""
    print("\nПроверка конфигурации...")
    
    try:
        from record_config import config, RecordingConfig
        
        # Проверка базовых параметров
        assert hasattr(config, 'hf_username'), "Отсутствует hf_username"
        assert hasattr(config, 'hf_token'), "Отсутствует hf_token"
        assert hasattr(config, 'dataset_name'), "Отсутствует dataset_name"
        assert hasattr(config, 'num_episodes'), "Отсутствует num_episodes"
        assert hasattr(config, 'episode_time_sec'), "Отсутствует episode_time_sec"
        assert hasattr(config, 'task_description'), "Отсутствует task_description"
        
        print("✓ Все необходимые параметры конфигурации присутствуют")
        
        # Проверка предустановленных конфигураций
        quick_demo = RecordingConfig.quick_demo()
        assert quick_demo.num_episodes == 2, "Неправильная конфигурация quick_demo"
        print("✓ Конфигурация quick_demo корректна")
        
        full_dataset = RecordingConfig.full_dataset()
        assert full_dataset.num_episodes == 20, "Неправильная конфигурация full_dataset"
        print("✓ Конфигурация full_dataset корректна")
        
        pick_place = RecordingConfig.pick_place_task()
        assert pick_place.task_category == "pick_place", "Неправильная конфигурация pick_place"
        print("✓ Конфигурация pick_place_task корректна")
        
        assembly = RecordingConfig.assembly_task()
        assert assembly.task_category == "assembly", "Неправильная конфигурация assembly"
        print("✓ Конфигурация assembly_task корректна")
        
        return True
        
    except Exception as e:
        print(f"✗ Ошибка конфигурации: {e}")
        return False

def test_robot_config():
    """Тест создания конфигурации робота."""
    print("\nПроверка конфигурации робота...")
    
    try:
        from lerobot.robots.brewie.config_Brewie import BrewieConfig
        
        # Создание тестовой конфигурации
        robot_config = BrewieConfig(
            master_ip="localhost",
            master_port=9090,
            servo_duration=0.1,
            max_relative_target=50.0,
        )
        
        # Проверка параметров
        assert robot_config.master_ip == "localhost"
        assert robot_config.master_port == 9090
        assert robot_config.servo_duration == 0.1
        assert robot_config.max_relative_target == 50.0
        assert len(robot_config.servo_ids) == 10  # 10 сервоприводов по умолчанию
        assert len(robot_config.servo_mapping) == 10
        
        print("✓ Конфигурация робота создана корректно")
        
        return True
        
    except Exception as e:
        print(f"✗ Ошибка конфигурации робота: {e}")
        return False

def main():
    """Основная функция тестирования."""
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ СКРИПТОВ ЗАПИСИ ДАТАСЕТА BREWIE")
    print("=" * 60)
    
    success = True
    
    # Тест импортов
    if not test_imports():
        success = False
    
    # Тест конфигурации
    if not test_config():
        success = False
    
    # Тест конфигурации робота
    if not test_robot_config():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("✓ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("Скрипты готовы к использованию.")
    else:
        print("✗ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ!")
        print("Исправьте ошибки перед использованием.")
    print("=" * 60)
    
    return success

if __name__ == "__main__":
    main()
