#!/usr/bin/env python

"""
Пример записи датасета для робота Brewie с использованием конфигурационного файла.

Этот скрипт использует record_config.py для настройки всех параметров записи.
Измените настройки в record_config.py перед запуском этого скрипта.

ОСОБЕННОСТИ:
- Автоматическое определение существующих датасетов
- Возможность продолжения записи в существующий датасет (добавление новых эпизодов)
- Интерактивный выбор режима записи
- Поддержка всех стандартных функций LeRobot
- Безопасное получение HuggingFace токена из переменных окружения

Использование:
    # С переменной окружения
    export HUGGINGFACE_TOKEN=your_token_here
    python examples/brewie/record_with_config.py
    
    # С аргументом командной строки
    python examples/brewie/record_with_config.py --hf-token your_token_here
    
    # Интерактивный ввод (токен запросится при запуске)
    python examples/brewie/record_with_config.py

Режимы работы:
1. Создание нового датасета (по умолчанию)
2. Продолжение записи в существующий датасет (автоматически предлагается при обнаружении)
3. Принудительное продолжение записи (через resume_existing_dataset=True в конфиге)
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

def check_dataset_exists(dataset_repo_id: str) -> bool:
    """Проверяет, существует ли датасет локально или на Hub."""
    try:
        # Попытка загрузить существующий датасет
        existing_dataset = LeRobotDataset(dataset_repo_id)
        return True
    except Exception:
        return False

def get_existing_dataset_info(dataset_repo_id: str) -> dict:
    """Получает информацию о существующем датасете."""
    try:
        existing_dataset = LeRobotDataset(dataset_repo_id)
        return {
            "exists": True,
            "num_episodes": existing_dataset.num_episodes,
            "fps": existing_dataset.fps,
            "robot_type": existing_dataset.meta.robot_type,
            "features": list(existing_dataset.features.keys())
        }
    except Exception as e:
        return {
            "exists": False,
            "error": str(e)
        }

def validate_config():
    """Проверка корректности конфигурации."""
    errors = []
    
    if config.hf_username == "your_username":
        errors.append("Необходимо указать ваш HuggingFace username в config.hf_username")
    
    # Проверяем токен через новый метод
    try:
        hf_token = config.get_hf_token()
        if not hf_token or hf_token.strip() == "":
            errors.append("Не удалось получить HuggingFace token")
    except ValueError as e:
        errors.append(f"Ошибка получения HuggingFace token: {e}")
    
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
        print("\nДля установки HuggingFace token используйте:")
        print("  export HUGGINGFACE_TOKEN=your_token_here")
        print("или передайте токен через аргумент командной строки:")
        print("  python record_with_config.py --hf-token your_token_here")
        return False
    
    return True

def print_config_summary(dataset_repo_id: str, existing_dataset_info: dict = None):
    """Вывод сводки конфигурации."""
    print("=" * 60)
    print("КОНФИГУРАЦИЯ ЗАПИСИ ДАТАСЕТА BREWIE")
    print("=" * 60)
    print(f"Датасет: {dataset_repo_id}")
    
    if existing_dataset_info and existing_dataset_info.get("exists"):
        print(f"РЕЖИМ: Продолжение записи в существующий датасет")
        print(f"Существующих эпизодов: {existing_dataset_info['num_episodes']}")
        print(f"Будет добавлено эпизодов: {config.num_episodes}")
        print(f"Итого эпизодов: {existing_dataset_info['num_episodes'] + config.num_episodes}")
    else:
        print(f"РЕЖИМ: Создание нового датасета")
        print(f"Эпизодов: {config.num_episodes}")
    
    print(f"Задача: {config.task_description}")
    print(f"Категория: {config.task_category}")
    print(f"Сложность: {config.difficulty_level}")
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
    
    # Создание ID датасета
    dataset_repo_id = f"{config.hf_username}/{config.dataset_name}"
    
    # Проверка существования датасета
    existing_dataset_info = get_existing_dataset_info(dataset_repo_id)
    
    # Автоматическое определение режима resume, если не задан явно
    should_resume = config.resume_existing_dataset
    if existing_dataset_info.get("exists") and not config.resume_existing_dataset:
        print(f"\nОбнаружен существующий датасет: {dataset_repo_id}")
        print(f"Существующих эпизодов: {existing_dataset_info['num_episodes']}")
        print(f"FPS: {existing_dataset_info['fps']}")
        print(f"Тип робота: {existing_dataset_info['robot_type']}")
        
        response = input("\nПродолжить запись в существующий датасет? (y/N): ").strip().lower()
        if response in ['y', 'yes', 'да']:
            should_resume = True
            print("Режим: Продолжение записи в существующий датасет")
        else:
            print("Режим: Создание нового датасета (существующий будет перезаписан)")
    
    # Вывод сводки конфигурации
    if should_resume and existing_dataset_info.get("exists"):
        print_config_summary(dataset_repo_id, existing_dataset_info)
    else:
        print_config_summary(dataset_repo_id)
    
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
    
    # Создание или загрузка датасета
    if should_resume and existing_dataset_info.get("exists"):
        log_say("Загрузка существующего датасета для продолжения записи...")
        dataset = LeRobotDataset(
            repo_id=dataset_repo_id,
            batch_encoding_size=1,  # Используем значение по умолчанию
        )
        
        # Запуск image writer для существующего датасета
        if hasattr(robot, "cameras") and len(robot.cameras) > 0:
            dataset.start_image_writer(
                num_processes=0,  # Используем значение по умолчанию
                num_threads=config.image_writer_threads,
            )
        
        log_say(f"Датасет загружен. Существующих эпизодов: {dataset.num_episodes}")
    else:
        log_say("Создание нового датасета...")
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
    
    # Определяем начальный номер эпизода
    start_episode = dataset.num_episodes if should_resume else 0
    total_episodes_to_record = config.num_episodes
    recorded_episodes = 0
    
    log_say(f"Начало записи. Будет записано {total_episodes_to_record} эпизодов")
    if should_resume:
        log_say(f"Продолжение с эпизода {start_episode}")
    
    try:
        while recorded_episodes < total_episodes_to_record and not events["stop_recording"]:
            current_episode_num = start_episode + recorded_episodes + 1
            log_say(f"Запись эпизода {current_episode_num} ({recorded_episodes + 1}/{total_episodes_to_record})")
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
                (recorded_episodes < total_episodes_to_record - 1) or events["rerecord_episode"]
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
            current_episode_num = start_episode + recorded_episodes
            log_say(f"Эпизод {current_episode_num} сохранен")
            
    except KeyboardInterrupt:
        log_say("Запись прервана пользователем")
    except Exception as e:
        log_say(f"Ошибка во время записи: {e}")
    
    # =============================================================================
    # ЗАВЕРШЕНИЕ И ОТПРАВКА НА HUB
    # =============================================================================
    
    total_episodes_in_dataset = dataset.num_episodes
    if should_resume:
        log_say(f"Запись завершена! Добавлено {recorded_episodes} новых эпизодов")
        log_say(f"Всего эпизодов в датасете: {total_episodes_in_dataset}")
    else:
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
