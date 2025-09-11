#!/usr/bin/env python

"""
Пример записи датасета для робота Brewie в стандарте LeRobot.

Этот скрипт демонстрирует, как записывать демонстрационные данные
с робота Brewie для последующего обучения политик.

Требования:
- ROS master должен быть запущен
- Робот Brewie должен быть подключен и готов к работе
- Учетные данные HuggingFace должны быть настроены

Использование:
    python examples/brewie/record.py
"""

import os
import getpass
from typing import Optional

from lerobot.datasets.lerobot_dataset import LeRobotDataset
from lerobot.datasets.utils import hw_to_dataset_features
from lerobot.record import record_loop
from lerobot.robots.brewie.config_Brewie import BrewieConfig
from lerobot.robots.brewie.Brewie_base import BrewieBase
from lerobot.teleoperators.keyboard import KeyboardTeleop, KeyboardTeleopConfig
from lerobot.utils.control_utils import init_keyboard_listener
from lerobot.utils.utils import log_say
from lerobot.utils.visualization_utils import _init_rerun

# =============================================================================
# КОНФИГУРАЦИЯ ЗАПИСИ ДАТАСЕТА
# =============================================================================

# Настройки HuggingFace
HF_USERNAME = input("Введите ваш HuggingFace username: ").strip()
HF_TOKEN = getpass.getpass("Введите ваш HuggingFace token: ").strip()
DATASET_NAME = input("Введите название датасета (например: brewie_demo_001): ").strip()

# Настройки записи
NUM_EPISODES = int(input("Количество эпизодов для записи (по умолчанию 5): ") or "5")
FPS = int(input("Частота записи FPS (по умолчанию 30): ") or "30")
EPISODE_TIME_SEC = int(input("Длительность эпизода в секундах (по умолчанию 30): ") or "30")
RESET_TIME_SEC = int(input("Время сброса между эпизодами в секундах (по умолчанию 5): ") or "5")

# Описание задачи
TASK_DESCRIPTION = input("Опишите задачу, которую будет выполнять робот: ").strip()
if not TASK_DESCRIPTION:
    TASK_DESCRIPTION = "Демонстрация манипуляций робота Brewie"

# Настройки робота
ROS_MASTER_IP = input("IP адрес ROS master (по умолчанию localhost): ").strip() or "localhost"
ROS_MASTER_PORT = int(input("Порт ROS master (по умолчанию 9090): ") or "9090")

# =============================================================================
# СОЗДАНИЕ КОНФИГУРАЦИЙ
# =============================================================================

# Конфигурация робота
robot_config = BrewieConfig(
    master_ip=ROS_MASTER_IP,
    master_port=ROS_MASTER_PORT,
    servo_duration=0.1,
    max_relative_target=50.0,  # Ограничение максимального движения за шаг
)

# Конфигурация телеоператора (клавиатура)
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
action_features = hw_to_dataset_features(robot.action_features, "action") 
obs_features = hw_to_dataset_features(robot.observation_features, "observation")
dataset_features = {**action_features, **obs_features}

# Создание датасета
dataset_repo_id = f"{HF_USERNAME}/{DATASET_NAME}"
dataset = LeRobotDataset.create(
    repo_id=dataset_repo_id,
    fps=FPS,
    features=dataset_features,
    robot_type=robot.name,
    use_videos=True,
    image_writer_threads=4,
)

# =============================================================================
# ПОДКЛЮЧЕНИЕ К УСТРОЙСТВАМ
# =============================================================================

log_say("Подключение к роботу Brewie...")
robot.connect()

log_say("Подключение к телеоператору...")
keyboard.connect()

# Инициализация визуализации
_init_rerun(session_name="brewie_record")

# Инициализация слушателя клавиатуры
listener, events = init_keyboard_listener()

# Проверка подключений
if not robot.is_connected:
    raise ValueError("Робот Brewie не подключен!")
if not keyboard.is_connected:
    raise ValueError("Телеоператор не подключен!")

log_say(f"Все устройства подключены. Начинаем запись датасета '{dataset_repo_id}'")
log_say(f"Задача: {TASK_DESCRIPTION}")
log_say(f"Параметры: {NUM_EPISODES} эпизодов, {EPISODE_TIME_SEC}с каждый, {FPS} FPS")

# =============================================================================
# ЦИКЛ ЗАПИСИ ЭПИЗОДОВ
# =============================================================================

recorded_episodes = 0
while recorded_episodes < NUM_EPISODES and not events["stop_recording"]:
    log_say(f"Запись эпизода {recorded_episodes + 1}/{NUM_EPISODES}")
    log_say("Нажмите ENTER для начала записи эпизода...")
    input()

    # Запуск цикла записи
    record_loop(
        robot=robot,
        events=events,
        fps=FPS,
        dataset=dataset,
        teleop=[keyboard],
        control_time_s=EPISODE_TIME_SEC,
        single_task=TASK_DESCRIPTION,
        display_data=True,
    )

    # Логика сброса окружения
    if not events["stop_recording"] and (
        (recorded_episodes < NUM_EPISODES - 1) or events["rerecord_episode"]
    ):
        log_say("Сброс окружения...")
        record_loop(
            robot=robot,
            events=events,
            fps=FPS,
            teleop=[keyboard],
            control_time_s=RESET_TIME_SEC,
            single_task="Сброс позиции робота",
            display_data=True,
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

# =============================================================================
# ЗАВЕРШЕНИЕ И ОТПРАВКА НА HUB
# =============================================================================

log_say(f"Запись завершена! Сохранено {recorded_episodes} эпизодов")
log_say("Отправка датасета на HuggingFace Hub...")

# Отправка на HuggingFace Hub
try:
    dataset.push_to_hub()
    log_say(f"Датасет успешно отправлен на: https://huggingface.co/datasets/{dataset_repo_id}")
except Exception as e:
    log_say(f"Ошибка при отправке на Hub: {e}")
    log_say("Датасет сохранен локально")

# Отключение устройств
log_say("Отключение устройств...")
robot.disconnect()
keyboard.disconnect()
listener.stop()

log_say("Запись датасета завершена!")
