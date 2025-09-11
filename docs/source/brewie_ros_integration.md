# Brewie Robot ROS Integration

## Обзор

Реализация робота Brewie была переработана для использования ROS (Robot Operating System) через библиотеку `roslibpy` вместо прямого управления моторами через `lerobot.motors`.

## Основные изменения

### 1. Конфигурация (`config_Brewie.py`)

Добавлены новые параметры конфигурации:

- `master_ip`: IP адрес ROS master (по умолчанию "localhost")
- `master_port`: Порт ROS master (по умолчанию 9090)
- `servo_ids`: Список ID сервоприводов
- `servo_duration`: Время выполнения движения сервоприводов
- `servo_mapping`: Соответствие ID сервоприводов и названий суставов
- `position_service`: Название ROS сервиса для получения позиций
- `set_position_topic`: Название ROS топика для установки позиций
- `camera_topic`: Название ROS топика камеры

### 2. Основной класс (`Brewie_base.py`)

#### Удалены зависимости:
- `lerobot.motors` - прямое управление моторами
- `FeetechMotorsBus` - шина моторов

#### Добавлены зависимости:
- `roslibpy` - для работы с ROS
- `numpy`, `cv2` - для обработки изображений
- `threading` - для потокобезопасности

#### Новые методы:
- `_setup_ros_services()` - настройка ROS сервисов
- `_setup_ros_topics()` - настройка ROS топиков
- `_camera_callback()` - обработка изображений с камеры

#### Измененные методы:
- `connect()` - подключение к ROS вместо моторов
- `get_observation()` - получение данных через ROS сервисы
- `send_action()` - отправка команд через ROS топики
- `disconnect()` - отключение от ROS

## ROS Интерфейс

### Сервисы

#### Получение позиций сервоприводов
- **Название:** `/ros_robot_controller/bus_servo/get_position`
- **Тип:** `ros_robot_controller/GetBusServosPosition`
- **Запрос:** `{'id': [13, 14, 15, 16, 17, 18, 19, 20, 21, 22]}`
- **Ответ:** `{'success': True, 'position': [{'id': 13, 'position': 872}, ...]}`

### Топики

#### Установка позиций сервоприводов
- **Название:** `/ros_robot_controller/bus_servo/set_position`
- **Тип:** `ros_robot_controller/SetBusServosPosition`
- **Сообщение:** `{'duration': 0.1, 'position': [{'id': 13, 'position': 500}, ...]}`

#### Изображение с камеры
- **Название:** `/camera/image_raw/compressed`
- **Тип:** `sensor_msgs/CompressedImage`

## Маппинг сервоприводов

По умолчанию используется следующее соответствие:

| ID | Название сустава |
|----|------------------|
| 13 | left_shoulder_pan |
| 14 | right_shoulder_pan |
| 15 | left_shoulder_lift |
| 16 | right_shoulder_lift |
| 17 | left_forearm_roll |
| 18 | right_forearm_roll |
| 19 | left_forearm_pitch |
| 20 | right_forearm_pitch |
| 21 | left_gripper |
| 22 | right_gripper |

## Совместимость

Реализация полностью совместима со стандартом LeRobot:
- Сохраняет интерфейс класса `Robot`
- Поддерживает сбор датасетов
- Совместима с политиками обучения
- Сохраняет формат наблюдений и действий

## Примеры использования

См. файлы в `examples/brewie/`:
- `ros_brewie_example.py` - базовый пример использования
- `README.md` - подробная документация

## Тестирование

Созданы тесты в `tests/robots/test_brewie_ros.py` для проверки:
- Инициализации робота
- Подключения к ROS
- Получения наблюдений
- Отправки команд
- Отключения

## Требования

- `roslibpy` - для работы с ROS
- `opencv-python` - для обработки изображений
- `numpy` - для работы с массивами
- ROS master должен быть запущен и доступен
