#!/usr/bin/env python

"""
Пример записи датасета для робота Brewie с использованием конфигурационного файла.

Этот скрипт использует record_config.py для настройки всех параметров записи.
Измените настройки в record_config.py перед запуском этого скрипта.

Использование:
    python examples/brewie/record_with_config.py
"""

import os
import sys
from pathlib import Path

# Добавляем путь к модулям lerobot
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from lerobot.datasets.lerobot_dataset import LeRobotDataset
from lerobot.datasets.utils import hw_to_dataset_features
from lerobot.record import record_loop
from lerobot.robots.brewie.config_Brewie import BrewieConfig
from lerobot.robots.brewie.Brewie_base import BrewieBase
from lerobot.teleoperators.keyboard import KeyboardTeleop, KeyboardTeleopConfig
from lerobot.utils.control_utils import init_keyboard_listener
from lerobot.utils.utils import log_say as _log_say
from lerobot.utils.visualization_utils import _init_rerun

# Импорт конфигурации
from record_config import config

def log_say(text: str, play_sounds: bool = True, blocking: bool = False):
    """
    Обертка для log_say, которая дублирует информацию в консоль.
    
    Args:
        text: Текст для вывода
        play_sounds: Воспроизводить ли звук (передается в оригинальную log_say)
        blocking: Блокирующий режим (передается в оригинальную log_say)
    """
    # Выводим в консоль
    print(f"[LOG] {text}")
    
    # Вызываем оригинальную функцию log_say
    _log_say(text, play_sounds, blocking)

def validate_config():
    """Проверка корректности конфигурации."""
    errors = []
    
    if config.hf_username == "your_username":
        errors.append("Необходимо указать ваш HuggingFace username в config.hf_username")
    
    if config.hf_token == "your_token":
        errors.append("Необходимо указать ваш HuggingFace token в config.hf_token")
    
    if not config.dataset_name:
        errors.append("Необходимо указать название датасета в config.dataset_name")
    
    if config.num_episodes <= 0:
        errors.append("Количество эпизодов должно быть больше 0")
    
    if config.episode_time_sec <= 0:
        errors.append("Длительность эпизода должна быть больше 0")
    
    if errors:
        print("Ошибки в конфигурации:")
        for error in errors:
            print(f"  - {error}")
        print("\nИсправьте ошибки в файле record_config.py и запустите скрипт снова.")
        return False
    
    return True

def print_config_summary():
    """Вывод сводки конфигурации."""
    print("=" * 60)
    print("КОНФИГУРАЦИЯ ЗАПИСИ ДАТАСЕТА BREWIE")
    print("=" * 60)
    print(f"Датасет: {config.hf_username}/{config.dataset_name}")
    print(f"Задача: {config.task_description}")
    print(f"Категория: {config.task_category}")
    print(f"Сложность: {config.difficulty_level}")
    print(f"Эпизоды: {config.num_episodes}")
    print(f"Длительность эпизода: {config.episode_time_sec}с")
    print(f"Время сброса: {config.reset_time_sec}с")
    print(f"Частота записи: {config.fps} FPS")
    print(f"ROS Master: {config.ros_master_ip}:{config.ros_master_port}")
    print("=" * 60)

def main():
    """Основная функция записи датасета."""
    
    # Проверка конфигурации
    if not validate_config():
        return
    
    # Вывод сводки конфигурации
    print_config_summary()
    
    # Подтверждение запуска
    response = input("Продолжить запись с этими настройками? (y/N): ").strip().lower()
    if response not in ['y', 'yes', 'да']:
        print("Запись отменена.")
        return
    
    # =============================================================================
    # СОЗДАНИЕ КОНФИГУРАЦИЙ
    # =============================================================================
    
    # Конфигурация робота
    robot_config = BrewieConfig(
        master_ip=config.ros_master_ip,
        master_port=config.ros_master_port,
        servo_duration=config.servo_duration,
        max_relative_target=config.max_relative_target,
    )
    
    # Конфигурация телеоператора
    keyboard_config = KeyboardTeleopConfig()
    
    # =============================================================================
    # ИНИЦИАЛИЗАЦИЯ УСТРОЙСТВ
    # =============================================================================
    
    robot = BrewieBase(robot_config)
    keyboard = KeyboardTeleop(keyboard_config)
    
    # =============================================================================
    # НАСТРОЙКА ДАТАСЕТА
    # =============================================================================
    
    # Конфигурация признаков датасета
    #action_features = hw_to_dataset_features(robot.action_features, "action") 
    obs_features = hw_to_dataset_features(robot.observation_features, "observation")
    dataset_features = {**obs_features}
    #**action_features,
    
    # Создание датасета
    dataset_repo_id = f"{config.hf_username}/{config.dataset_name}"
    dataset = LeRobotDataset.create(
        repo_id=dataset_repo_id,
        fps=config.fps,
        features=dataset_features,
        robot_type=robot.name,
        use_videos=config.use_videos,
        image_writer_threads=config.image_writer_threads,
    )
    
    # =============================================================================
    # ПОДКЛЮЧЕНИЕ К УСТРОЙСТВАМ
    # =============================================================================
    
    log_say("Подключение к роботу Brewie...")
    try:
        robot.connect()
    except Exception as e:
        log_say(f"Ошибка подключения к роботу: {e}")
        return
    
    log_say("Подключение к телеоператору...")
    try:
        keyboard.connect()
    except Exception as e:
        log_say(f"Ошибка подключения к телеоператору: {e}")
        robot.disconnect()
        return
    
    # Инициализация визуализации
    _init_rerun(session_name=config.session_name)
    
    # Инициализация слушателя клавиатуры
    listener, events = init_keyboard_listener()
    
    # Проверка подключений
    if not robot.is_connected:
        log_say("ОШИБКА: Робот Brewie не подключен!")
        keyboard.disconnect()
        listener.stop()
        return
        
    if not keyboard.is_connected:
        log_say("ОШИБКА: Телеоператор не подключен!")
        robot.disconnect()
        listener.stop()
        return
    
    log_say("Все устройства подключены успешно!")
    log_say("Управление:")
    log_say("  - ENTER: Начать/продолжить запись эпизода")
    log_say("  - ESC: Остановить запись")
    log_say("  - R: Перезаписать текущий эпизод")
    
    # =============================================================================
    # ЦИКЛ ЗАПИСИ ЭПИЗОДОВ
    # =============================================================================
    
    recorded_episodes = 0
    try:
        while recorded_episodes < config.num_episodes and not events["stop_recording"]:
            log_say(f"Запись эпизода {recorded_episodes + 1}/{config.num_episodes}")
            log_say("Нажмите ENTER для начала записи эпизода...")
            input()
            
            # Запуск цикла записи
            record_loop(
                robot=robot,
                events=events,
                fps=config.fps,
                dataset=dataset,
                teleop=keyboard,
                control_time_s=config.episode_time_sec,
                single_task=config.task_description,
                display_data=config.display_data,
            )
            
            # Логика сброса окружения
            if not events["stop_recording"] and (
                (recorded_episodes < config.num_episodes - 1) or events["rerecord_episode"]
            ):
                log_say("Сброс окружения...")
                record_loop(
                    robot=robot,
                    events=events,
                    fps=config.fps,
                    teleop=keyboard,
                    control_time_s=config.reset_time_sec,
                    single_task="Сброс позиции робота",
                    display_data=config.display_data,
                )
            
            # Обработка перезаписи эпизода
            if events["rerecord_episode"]:
                log_say("Перезапись эпизода...")
                events["rerecord_episode"] = False
                events["exit_early"] = False
                dataset.clear_episode_buffer()
                continue
            
            # Сохранение эпизода
            dataset.save_episode()
            recorded_episodes += 1
            log_say(f"Эпизод {recorded_episodes} сохранен")
            
    except KeyboardInterrupt:
        log_say("Запись прервана пользователем")
    except Exception as e:
        log_say(f"Ошибка во время записи: {e}")
    
    # =============================================================================
    # ЗАВЕРШЕНИЕ И ОТПРАВКА НА HUB
    # =============================================================================
    
    log_say(f"Запись завершена! Сохранено {recorded_episodes} эпизодов")
    
    if recorded_episodes > 0 and config.auto_push_to_hub:
        log_say("Отправка датасета на HuggingFace Hub...")
        try:
            dataset.push_to_hub()
            log_say(f"Датасет успешно отправлен на: https://huggingface.co/datasets/{dataset_repo_id}")
        except Exception as e:
            log_say(f"Ошибка при отправке на Hub: {e}")
            log_say("Датасет сохранен локально")
    elif recorded_episodes > 0:
        log_say("Датасет сохранен локально (auto_push_to_hub = False)")
    
    # Отключение устройств
    log_say("Отключение устройств...")
    try:
        robot.disconnect()
        keyboard.disconnect()
        listener.stop()
    except Exception as e:
        log_say(f"Ошибка при отключении: {e}")
    
    log_say("Запись датасета завершена!")

if __name__ == "__main__":
    main()
