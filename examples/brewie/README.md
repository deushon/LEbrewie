# Brewie Robot ROS Integration

Этот пример демонстрирует использование робота Brewie с интеграцией ROS через roslibpy.

## Требования

1. **Python зависимости:**
   ```bash
   pip install roslibpy opencv-python numpy
   ```

2. **ROS окружение:**
   - ROS master должен быть запущен
   - Должны быть доступны следующие сервисы и топики:
     - Сервис: `/ros_robot_controller/bus_servo/get_position`
     - Топик: `/ros_robot_controller/bus_servo/set_position`
     - Топик: `/camera/image_raw/compressed` (опционально)

## Конфигурация

### Параметры подключения

В файле конфигурации `BrewieConfig` можно настроить:

- `master_ip`: IP адрес ROS master (по умолчанию "localhost")
- `master_port`: Порт ROS master (по умолчанию 9090)
- `servo_duration`: Время выполнения движения сервоприводов (по умолчанию 0.1 сек)

### Маппинг сервоприводов

По умолчанию используется следующее соответствие ID сервоприводов и названий суставов:

```python
servo_mapping = {
    13: "left_shoulder_pan",
    14: "right_shoulder_pan", 
    15: "left_shoulder_lift",
    16: "right_shoulder_lift",
    17: "left_forearm_roll",
    18: "right_forearm_roll",
    19: "left_forearm_pitch",
    20: "right_forearm_pitch",
    21: "left_gripper",
    22: "right_gripper"
}
```

## Использование

### Базовый пример

```python
from lerobot.robots.brewie import BrewieBase, BrewieConfig

# Создание конфигурации
config = BrewieConfig(
    master_ip="192.168.1.100",  # IP вашего ROS master
    master_port=9090,
    servo_duration=0.1
)

# Создание экземпляра робота
robot = BrewieBase(config)

# Подключение
robot.connect()

# Получение наблюдений
obs = robot.get_observation()
print(f"Текущие позиции: {obs}")

# Отправка команды движения
action = {
    "left_shoulder_pan.pos": 500,
    "right_shoulder_pan.pos": 500,
    # ... другие суставы
}
robot.send_action(action)

# Отключение
robot.disconnect()
```

### Получение наблюдений

Метод `get_observation()` возвращает словарь с:
- Позициями всех сервоприводов (ключи вида `"joint_name.pos"`)
- Изображением с камеры (ключ `"camera"`)

### Отправка команд

Метод `send_action()` принимает словарь с целевыми позициями:
- Ключи: `"joint_name.pos"`
- Значения: позиции в диапазоне 0-1000

## ROS Сервисы и Топики

### Сервис получения позиций
- **Название:** `/ros_robot_controller/bus_servo/get_position`
- **Тип:** `ros_robot_controller/GetBusServosPosition`
- **Запрос:** `{'id': [13, 14, 15, 16, 17, 18, 19, 20, 21, 22]}`
- **Ответ:** `{'success': True, 'position': [{'id': 13, 'position': 872}, ...]}`

### Топик установки позиций
- **Название:** `/ros_robot_controller/bus_servo/set_position`
- **Тип:** `ros_robot_controller/SetBusServosPosition`
- **Сообщение:** `{'duration': 0.1, 'position': [{'id': 13, 'position': 500}, ...]}`

### Топик камеры
- **Название:** `/camera/image_raw/compressed`
- **Тип:** `sensor_msgs/CompressedImage`

## Совместимость с LeRobot

Реализация полностью совместима со стандартом LeRobot:
- Поддерживает сбор датасетов
- Совместима с политиками обучения
- Сохраняет интерфейс `Robot` класса

## Устранение неполадок

1. **Ошибка подключения к ROS:**
   - Проверьте, что ROS master запущен
   - Убедитесь в правильности IP и порта
   - Проверьте сетевое соединение

2. **Ошибки сервисов:**
   - Убедитесь, что ROS контроллер робота запущен
   - Проверьте доступность сервисов командой `rosservice list`

3. **Проблемы с камерой:**
   - Проверьте, что топик камеры публикуется
   - Убедитесь в правильности формата изображения
