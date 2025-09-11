#!/usr/bin/env python

"""
Пример использования скриптов записи датасета для робота Brewie.

Этот файл демонстрирует различные способы настройки и запуска записи датасетов.
"""

from record_config import RecordingConfig, config

def example_quick_demo():
    """Пример быстрой демонстрации."""
    print("=== ПРИМЕР: Быстрая демонстрация ===")
    
    # Создание конфигурации для быстрой демонстрации
    demo_config = RecordingConfig.quick_demo()
    
    # Настройка учетных данных (ОБЯЗАТЕЛЬНО!)
    demo_config.hf_username = "your_username"  # Замените на ваш username
    demo_config.hf_token = "your_token"        # Замените на ваш token
    demo_config.dataset_name = "brewie_quick_demo"
    
    print(f"Конфигурация: {demo_config.num_episodes} эпизодов по {demo_config.episode_time_sec}с")
    print(f"Датасет: {demo_config.hf_username}/{demo_config.dataset_name}")
    print(f"Задача: {demo_config.task_description}")
    
    # Для запуска записи раскомментируйте следующую строку:
    # from record_with_config import main; main()

def example_pick_place_task():
    """Пример задачи pick and place."""
    print("\n=== ПРИМЕР: Задача Pick and Place ===")
    
    # Создание конфигурации для задачи pick and place
    pick_place_config = RecordingConfig.pick_place_task()
    
    # Настройка учетных данных
    pick_place_config.hf_username = "your_username"
    pick_place_config.hf_token = "your_token"
    pick_place_config.dataset_name = "brewie_pick_place"
    
    # Дополнительные настройки
    pick_place_config.ros_master_ip = "192.168.1.100"  # IP вашего ROS master
    pick_place_config.max_relative_target = 30.0       # Более точные движения
    
    print(f"Конфигурация: {pick_place_config.num_episodes} эпизодов по {pick_place_config.episode_time_sec}с")
    print(f"Датасет: {pick_place_config.hf_username}/{pick_place_config.dataset_name}")
    print(f"Задача: {pick_place_config.task_description}")
    print(f"Категория: {pick_place_config.task_category}")
    print(f"Сложность: {pick_place_config.difficulty_level}")

def example_custom_config():
    """Пример пользовательской конфигурации."""
    print("\n=== ПРИМЕР: Пользовательская конфигурация ===")
    
    # Создание полностью пользовательской конфигурации
    custom_config = RecordingConfig(
        # Учетные данные HuggingFace
        hf_username="your_username",
        hf_token="your_token",
        dataset_name="brewie_custom_task",
        
        # Настройки записи
        num_episodes=8,
        fps=25,
        episode_time_sec=45,
        reset_time_sec=7,
        
        # Описание задачи
        task_description="Сложная манипуляция с несколькими объектами",
        task_category="manipulation",
        difficulty_level="advanced",
        
        # Настройки робота
        ros_master_ip="192.168.1.50",
        ros_master_port=9090,
        max_relative_target=25.0,  # Очень точные движения
        servo_duration=0.05,       # Быстрые движения
        
        # Дополнительные настройки
        use_videos=True,
        image_writer_threads=6,
        display_data=True,
        auto_push_to_hub=True
    )
    
    print(f"Конфигурация: {custom_config.num_episodes} эпизодов по {custom_config.episode_time_sec}с")
    print(f"Частота записи: {custom_config.fps} FPS")
    print(f"Датасет: {custom_config.hf_username}/{custom_config.dataset_name}")
    print(f"Задача: {custom_config.task_description}")
    print(f"ROS Master: {custom_config.ros_master_ip}:{custom_config.ros_master_port}")
    print(f"Максимальное движение: {custom_config.max_relative_target}")

def example_assembly_task():
    """Пример задачи сборки."""
    print("\n=== ПРИМЕР: Задача сборки ===")
    
    # Создание конфигурации для задачи сборки
    assembly_config = RecordingConfig.assembly_task()
    
    # Настройка учетных данных
    assembly_config.hf_username = "your_username"
    assembly_config.hf_token = "your_token"
    assembly_config.dataset_name = "brewie_assembly"
    
    # Специальные настройки для сборки
    assembly_config.max_relative_target = 20.0  # Очень точные движения
    assembly_config.servo_duration = 0.2        # Медленные, точные движения
    assembly_config.reset_time_sec = 20         # Больше времени на сброс
    
    print(f"Конфигурация: {assembly_config.num_episodes} эпизодов по {assembly_config.episode_time_sec}с")
    print(f"Датасет: {assembly_config.hf_username}/{assembly_config.dataset_name}")
    print(f"Задача: {assembly_config.task_description}")
    print(f"Категория: {assembly_config.task_category}")
    print(f"Сложность: {assembly_config.difficulty_level}")
    print(f"Время сброса: {assembly_config.reset_time_sec}с")

def show_available_configurations():
    """Показать все доступные конфигурации."""
    print("\n=== ДОСТУПНЫЕ КОНФИГУРАЦИИ ===")
    
    configs = [
        ("quick_demo", RecordingConfig.quick_demo(), "Быстрая демонстрация"),
        ("full_dataset", RecordingConfig.full_dataset(), "Полный датасет"),
        ("pick_place_task", RecordingConfig.pick_place_task(), "Задача pick and place"),
        ("assembly_task", RecordingConfig.assembly_task(), "Задача сборки")
    ]
    
    for name, cfg, description in configs:
        print(f"\n{name}:")
        print(f"  Описание: {description}")
        print(f"  Эпизоды: {cfg.num_episodes}")
        print(f"  Длительность: {cfg.episode_time_sec}с")
        print(f"  Сброс: {cfg.reset_time_sec}с")
        print(f"  Категория: {cfg.task_category}")
        print(f"  Сложность: {cfg.difficulty_level}")

def main():
    """Основная функция с примерами."""
    print("ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ СКРИПТОВ ЗАПИСИ ДАТАСЕТА BREWIE")
    print("=" * 70)
    
    # Показать доступные конфигурации
    show_available_configurations()
    
    # Примеры использования
    example_quick_demo()
    example_pick_place_task()
    example_custom_config()
    example_assembly_task()
    
    print("\n" + "=" * 70)
    print("ИНСТРУКЦИИ ПО ИСПОЛЬЗОВАНИЮ:")
    print("=" * 70)
    print("1. Выберите подходящую конфигурацию из примеров выше")
    print("2. Отредактируйте record_config.py с вашими настройками")
    print("3. Обязательно укажите ваши HuggingFace учетные данные")
    print("4. Убедитесь, что ROS master запущен и доступен")
    print("5. Запустите: python record_with_config.py")
    print("\nАльтернативно:")
    print("- Для интерактивной настройки: python record.py")
    print("- Для тестирования: python test_imports.py")
    print("=" * 70)

if __name__ == "__main__":
    main()
