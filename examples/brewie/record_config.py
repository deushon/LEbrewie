#!/usr/bin/env python

"""
Конфигурационный файл для записи датасета Brewie.

Этот файл содержит все настройки для записи датасета.
Измените значения в этом файле перед запуском record.py
"""

from dataclasses import dataclass
from typing import Optional

@dataclass
class RecordingConfig:
    """Конфигурация для записи датасета Brewie."""
    
    # =============================================================================
    # НАСТРОЙКИ HUGGINGFACE
    # =============================================================================
    
    # Ваши учетные данные HuggingFace
    hf_username: str = "your_username"  # Замените на ваш username
    hf_token: str = "your_token"        # Замените на ваш token
    
    # Название датасета (будет создан как username/dataset_name)
    dataset_name: str = "brewie_demo_001"
    
    # =============================================================================
    # НАСТРОЙКИ ЗАПИСИ
    # =============================================================================
    
    # Количество эпизодов для записи
    num_episodes: int = 5
    
    # Частота записи (кадров в секунду)
    fps: int = 30
    
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
    
    # =============================================================================
    # ПРЕДУСТАНОВЛЕННЫЕ КОНФИГУРАЦИИ
    # =============================================================================
    
    @classmethod
    def quick_demo(cls) -> "RecordingConfig":
        """Быстрая демонстрация - 2 коротких эпизода."""
        return cls(
            hf_username="forroot",  # ОБЯЗАТЕЛЬНО: замените на ваш username
            hf_token="",       
            ros_master_ip="192.168.20.21",
            ros_master_port=9090,
            num_episodes=2,
            episode_time_sec=15,
            reset_time_sec=3,
            task_description="Fast demo of robot movements",
            task_category="demo",
            difficulty_level="beginner"
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

# =============================================================================
# ВЫБОР КОНФИГУРАЦИИ
# =============================================================================

# Выберите одну из предустановленных конфигураций или создайте свою
config = RecordingConfig.quick_demo()
# config = RecordingConfig.full_dataset()
# config = RecordingConfig.pick_place_task()
# config = RecordingConfig.assembly_task()

# Или создайте свою конфигурацию
'''
config = RecordingConfig(
    hf_username="your_username",  # ОБЯЗАТЕЛЬНО: замените на ваш username
    hf_token="your_token",        # ОБЯЗАТЕЛЬНО: замените на ваш token
    dataset_name="brewie_my_task",
    num_episodes=5,
    episode_time_sec=30,
    task_description="Моя задача для робота Brewie"
)
'''