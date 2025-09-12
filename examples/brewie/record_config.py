#!/usr/bin/env python

"""
Конфигурационный файл для записи датасета Brewie.

Этот файл содержит все настройки для записи датасета.
Измените значения в этом файле перед запуском record.py

ВАЖНО: hf_token теперь получается из переменной окружения HUGGINGFACE_TOKEN
или из командной строки. Не храните токены в коде!

ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ:

1. С переменной окружения (рекомендуется):
   export HUGGINGFACE_TOKEN=your_token_here
   python examples/brewie/record_with_config.py

2. С аргументом командной строки:
   python examples/brewie/record_with_config.py --hf-token your_token_here

3. Интерактивный ввод (токен запросится при запуске):
   python examples/brewie/record_with_config.py

4. Альтернативная переменная окружения:
   export HF_TOKEN=your_token_here
   python examples/brewie/record_with_config.py

БЕЗОПАСНОСТЬ:
- Никогда не коммитьте токены в код
- Используйте переменные окружения для продакшена
- Токены вводятся скрыто (не отображаются в терминале)
"""

import os
import sys
import getpass
from dataclasses import dataclass
from typing import Optional

def get_hf_token() -> str:
    """
    Получает HuggingFace токен из переменной окружения или запрашивает у пользователя.
    
    Порядок получения токена:
    1. Переменная окружения HUGGINGFACE_TOKEN
    2. Переменная окружения HF_TOKEN
    3. Аргумент командной строки --hf-token
    4. Интерактивный ввод (скрытый)
    
    Returns:
        str: HuggingFace токен
        
    Raises:
        ValueError: Если токен не найден и пользователь отменил ввод
    """
    def validate_token(token: str) -> str:
        """Валидирует формат HuggingFace токена."""
        if not token or not token.strip():
            raise ValueError("Токен не может быть пустым")
        
        token = token.strip()
        
        # Базовая валидация формата токена HuggingFace
        if not token.startswith("hf_"):
            print("Предупреждение: Токен не начинается с 'hf_'. Убедитесь, что это правильный HuggingFace токен.")
        
        if len(token) < 10:
            raise ValueError("Токен слишком короткий. Проверьте правильность токена.")
        
        return token
    
    # 1. Проверяем переменные окружения
    token = os.getenv("HUGGINGFACE_TOKEN") or os.getenv("HF_TOKEN")
    if token:
        return validate_token(token)
    
    # 2. Проверяем аргументы командной строки
    if "--hf-token" in sys.argv:
        try:
            token_index = sys.argv.index("--hf-token")
            if token_index + 1 < len(sys.argv):
                token = sys.argv[token_index + 1]
                return validate_token(token)
        except (ValueError, IndexError):
            pass
    
    # 3. Запрашиваем у пользователя
    print("HuggingFace токен не найден в переменных окружения.")
    print("Установите переменную окружения HUGGINGFACE_TOKEN или введите токен:")
    print("  export HUGGINGFACE_TOKEN=your_token_here")
    print()
    
    try:
        token = getpass.getpass("Введите ваш HuggingFace токен (скрытый ввод): ")
        return validate_token(token)
    except KeyboardInterrupt:
        print("\nВвод отменен пользователем")
        raise ValueError("Токен не предоставлен")

@dataclass
class RecordingConfig:
    """Конфигурация для записи датасета Brewie."""
    
    # =============================================================================
    # НАСТРОЙКИ HUGGINGFACE
    # =============================================================================
    
    # Ваши учетные данные HuggingFace
    hf_username: str = "your_username"  # Замените на ваш username
    # hf_token теперь получается динамически из переменных окружения или ввода
    
    # Название датасета (будет создан как username/dataset_name)
    dataset_name: str = "hit_detection"
    
    # =============================================================================
    # НАСТРОЙКИ ЗАПИСИ
    # =============================================================================
    
    # Количество эпизодов для записи
    num_episodes: int = 5
    
    # Частота записи (кадров в секунду)
    # ВНИМАНИЕ: После добавления новых датчиков рекомендуется снизить FPS
    # для предотвращения проблем с синхронизацией видео
    fps: int = 20  # Снижено с 30 до 20 для стабильности
    
    # Длительность каждого эпизода в секундах
    episode_time_sec: int = 30
    
    # Время сброса между эпизодами в секундах
    reset_time_sec: int = 5
    
    # =============================================================================
    # ОПИСАНИЕ ЗАДАЧИ
    # =============================================================================
    
    # Описание задачи, которую будет выполнять робот
    task_description: str = "Демонстрация манипуляций робота Brewie"
    
    # Дополнительные метаданные
    task_category: str = "manipulation"  # manipulation, pick_place, assembly, etc.
    difficulty_level: str = "beginner"   # beginner, intermediate, advanced
    
    # =============================================================================
    # НАСТРОЙКИ РОБОТА
    # =============================================================================
    
    # Параметры подключения к ROS
    ros_master_ip: str = "localhost"
    ros_master_port: int = 9090
    
    # Настройки безопасности
    max_relative_target: float = 50.0  # Максимальное относительное движение за шаг
    servo_duration: float = 0.1        # Время выполнения движения сервоприводов
    
    # =============================================================================
    # НАСТРОЙКИ ДАТАСЕТА
    # =============================================================================
    
    # Использовать видео в датасете
    use_videos: bool = True
    
    # Количество потоков для записи изображений
    image_writer_threads: int = 4
    
    # =============================================================================
    # ДОПОЛНИТЕЛЬНЫЕ НАСТРОЙКИ
    # =============================================================================
    
    # Показывать данные во время записи
    display_data: bool = True 
    
    # Название сессии для визуализации
    session_name: str = "brewie_record"
    
    # Автоматически отправлять на Hub после записи
    auto_push_to_hub: bool = True
    
    # Продолжить запись в существующий датасет (добавить новые эпизоды)
    resume_existing_dataset: bool = False
    
    def get_hf_token(self) -> str:
        """
        Получает HuggingFace токен для этой конфигурации.
        
        Returns:
            str: HuggingFace токен
        """
        return get_hf_token()
    
    # =============================================================================
    # ПРЕДУСТАНОВЛЕННЫЕ КОНФИГУРАЦИИ
    # =============================================================================
    
    @classmethod
    def quick_demo(cls) -> "RecordingConfig":
        """Быстрая демонстрация - 2 коротких эпизода."""
        return cls(
            hf_username="forroot",  # ОБЯЗАТЕЛЬНО: замените на ваш username
            # hf_token получается динамически из переменных окружения
            ros_master_ip="192.168.20.21",
            ros_master_port=9090,
            num_episodes=2,
            fps=20, 
            episode_time_sec=15,
            reset_time_sec=3,
            task_description="Fast demo of robot movements",
            task_category="demo",
            difficulty_level="beginner",
            resume_existing_dataset=True
        )
    
    @classmethod
    def detection_aim(cls) -> "RecordingConfig":
        """racking and aiming at an enemy robot for fire. FAST MODE"""
        return cls(
            hf_username="forroot",  # ОБЯЗАТЕЛЬНО: замените на ваш username
            dataset_name ="detection_aim",
            ros_master_ip="192.168.20.21",
            ros_master_port=9090,
            num_episodes=2,
            fps=20, 
            episode_time_sec=15,
            reset_time_sec=3,
            task_description="Tracking and aiming at an enemy robot for fire",
            task_category="aim",
            difficulty_level="beginner",
            resume_existing_dataset=True
        )
    @classmethod
    def hit_detection(cls) -> "RecordingConfig":
        return cls(
            hf_username="forroot",  # ОБЯЗАТЕЛЬНО: замените на ваш username
            dataset_name ="hit_detection",
            ros_master_ip="192.168.20.21",
            ros_master_port=9090,
            num_episodes=2,
            fps=20, 
            episode_time_sec=20,
            reset_time_sec=3,
            task_description="Testing observation of hit data FIRE button True = human hit verification",
            task_category="hit",
            difficulty_level="beginner",
            resume_existing_dataset=False
        )

    @classmethod
    def resume_demo(cls) -> "RecordingConfig":
        """Демонстрация продолжения записи в существующий датасет."""
        return cls(
            hf_username="forroot",  # ОБЯЗАТЕЛЬНО: замените на ваш username
            # hf_token получается динамически из переменных окружения
            ros_master_ip="192.168.20.21",
            ros_master_port=9090,
            num_episodes=3,
            episode_time_sec=20,
            reset_time_sec=5,
            task_description="Additional episodes for existing dataset",
            task_category="demo",
            difficulty_level="beginner",
            resume_existing_dataset=True  # Включить режим продолжения записи
        )
    
    @classmethod
    def full_dataset(cls) -> "RecordingConfig":
        """Полный датасет - много эпизодов для обучения."""
        return cls(
            num_episodes=20,
            episode_time_sec=60,
            reset_time_sec=10,
            task_description="Полный набор демонстраций для обучения",
            task_category="manipulation",
            difficulty_level="intermediate"
        )
    
    @classmethod
    def pick_place_task(cls) -> "RecordingConfig":
        """Конфигурация для задачи pick and place."""
        return cls(
            num_episodes=10,
            episode_time_sec=45,
            reset_time_sec=8,
            task_description="Захват и размещение объектов",
            task_category="pick_place",
            difficulty_level="intermediate"
        )
    
    @classmethod
    def assembly_task(cls) -> "RecordingConfig":
        """Конфигурация для задачи сборки."""
        return cls(
            num_episodes=15,
            episode_time_sec=90,
            reset_time_sec=15,
            task_description="Сборка деталей роботом",
            task_category="assembly",
            difficulty_level="advanced"
        )
    
    @classmethod
    def optimized_with_sensors(cls) -> "RecordingConfig":
        """Оптимизированная конфигурация для работы с новыми датчиками."""
        return cls(
            hf_username="forroot",  # ОБЯЗАТЕЛЬНО: замените на ваш username
            ros_master_ip="192.168.20.21",
            ros_master_port=9090,
            num_episodes=5,
            episode_time_sec=30,
            reset_time_sec=5,
            fps=15,  # Сниженная частота для стабильности
            task_description="Оптимизированная запись с новыми датчиками",
            task_category="demo",
            difficulty_level="beginner",
            resume_existing_dataset=True,
            image_writer_threads=2,  # Меньше потоков для стабильности
            use_videos=True
        )

# =============================================================================
# ВЫБОР КОНФИГУРАЦИИ
# =============================================================================

# Выберите одну из предустановленных конфигураций или создайте свою
#config = RecordingConfig.optimized_with_sensors()  # Рекомендуется для новых датчиков
config = RecordingConfig.hit_detection()
# config = RecordingConfig.resume_demo()  # Для продолжения записи в существующий датасет
# config = RecordingConfig.full_dataset()
# config = RecordingConfig.pick_place_task()
# config = RecordingConfig.assembly_task()

# Или создайте свою конфигурацию
'''
config = RecordingConfig(
    hf_username="your_username",  # ОБЯЗАТЕЛЬНО: замените на ваш username
    # hf_token получается автоматически из переменных окружения
    dataset_name="brewie_my_task",
    num_episodes=5,
    episode_time_sec=30,
    task_description="Моя задача для робота Brewie",
    resume_existing_dataset=False  # True для продолжения записи в существующий датасет
)
'''