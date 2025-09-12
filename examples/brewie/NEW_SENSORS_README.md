# Новые датчики для робота Brewie

Этот документ описывает новые датчики и устройства, добавленные в систему сбора датасетов для робота Brewie.

## Добавленные компоненты

### 1. Моторы головы

Добавлены два новых мотора для управления головой робота:

- **Мотор 23** (`head_pan`) - поворот головы влево/вправо
- **Мотор 24** (`head_tilt`) - наклон головы вверх/вниз

#### Конфигурация

Моторы автоматически добавлены в конфигурацию `BrewieConfig`:

```python
servo_ids: list[int] = [13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]

servo_mapping: dict[int, str] = {
    # ... существующие моторы ...
    23: "head_pan",      # поворот головы
    24: "head_tilt"      # наклон головы
}
```

#### Использование

Моторы головы доступны как обычные суставы робота:

```python
# Получение текущих позиций
obs = robot.get_observation()
head_pan_pos = obs["head_pan.pos"]
head_tilt_pos = obs["head_tilt.pos"]

# Управление моторами головы
action = {
    "head_pan.pos": 500.0,    # Средняя позиция
    "head_tilt.pos": 300.0    # Наклон вниз
}
robot.send_action(action)
```

### 2. Джойстик (/joy)

Добавлена подписка на топик `/joy` для получения данных джойстика.

#### Структура данных

Джойстик предоставляет:
- **8 осей** (`joystick.axis_0` - `joystick.axis_7`) - значения от -1.0 до 1.0
- **15 кнопок** (`joystick.button_0` - `joystick.button_14`) - 0.0 (не нажата) или 1.0 (нажата)

#### Пример ROS сообщения

```yaml
header:
  seq: 533703
  stamp:
    secs: 1757659234
    nsecs: 709816240
  frame_id: "/dev/input/js0"
axes: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
buttons: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
```

#### Использование

```python
# Получение данных джойстика
obs = robot.get_observation()

# Оси джойстика
left_stick_x = obs["joystick.axis_0"]  # Левая ручка X
left_stick_y = obs["joystick.axis_1"]  # Левая ручка Y
right_stick_x = obs["joystick.axis_2"] # Правая ручка X
right_stick_y = obs["joystick.axis_3"] # Правая ручка Y

# Кнопки джойстика
button_a = obs["joystick.button_0"]    # Кнопка A
button_b = obs["joystick.button_1"]    # Кнопка B
# ... и так далее
```

### 3. IMU (/imu)

Добавлена подписка на топик `/imu` для получения данных инерциального измерительного блока.

#### Структура данных

IMU предоставляет:
- **Ориентация** (кватернион): `imu.orientation.x/y/z/w`
- **Угловая скорость**: `imu.angular_velocity.x/y/z`
- **Линейное ускорение**: `imu.linear_acceleration.x/y/z`

#### Пример ROS сообщения

```yaml
header:
  seq: 2697385
  stamp:
    secs: 1757659497
    nsecs: 428191184
  frame_id: "imu_link"
orientation:
  x: 0.0
  y: 0.0
  z: 0.0
  w: 0.0
orientation_covariance: [0.01, 0.0, 0.0, 0.0, 0.01, 0.0, 0.0, 0.0, 0.01]
angular_velocity:
  x: -0.26622066131445543
  y: 0.030051706288538295
  z: -0.0036658731984271367
angular_velocity_covariance: [0.01, 0.0, 0.0, 0.0, 0.01, 0.0, 0.0, 0.0, 0.01]
linear_acceleration:
  x: -1.1101805222019543
  y: 9.209895210186303
  z: 2.875961428403373
linear_acceleration_covariance: [0.0004, 0.0, 0.0, 0.0, 0.0004, 0.0, 0.0, 0.0, 0.004]
```

#### Использование

```python
# Получение данных IMU
obs = robot.get_observation()

# Ориентация (кватернион)
orientation_x = obs["imu.orientation.x"]
orientation_y = obs["imu.orientation.y"]
orientation_z = obs["imu.orientation.z"]
orientation_w = obs["imu.orientation.w"]

# Угловая скорость (рад/с)
angular_vel_x = obs["imu.angular_velocity.x"]
angular_vel_y = obs["imu.angular_velocity.y"]
angular_vel_z = obs["imu.angular_velocity.z"]

# Линейное ускорение (м/с²)
linear_acc_x = obs["imu.linear_acceleration.x"]
linear_acc_y = obs["imu.linear_acceleration.y"]
linear_acc_z = obs["imu.linear_acceleration.z"]
```

## Обновленные признаки наблюдения

Теперь `robot.observation_features` включает:

### Моторы (включая новые моторы головы)
- `left_shoulder_pan.pos`, `right_shoulder_pan.pos`
- `left_shoulder_lift.pos`, `right_shoulder_lift.pos`
- `left_forearm_roll.pos`, `right_forearm_roll.pos`
- `left_forearm_pitch.pos`, `right_forearm_pitch.pos`
- `left_gripper.pos`, `right_gripper.pos`
- **`head_pan.pos`** (новый)
- **`head_tilt.pos`** (новый)

### Камера
- `camera` (изображение)

### Джойстик (новый)
- `joystick.axis_0` - `joystick.axis_7` (8 осей, float)
- `joystick.button_0` - `joystick.button_14` (15 кнопок, float)

### IMU (новый)
- `imu.orientation.x/y/z/w` (ориентация)
- `imu.angular_velocity.x/y/z` (угловая скорость)
- `imu.linear_acceleration.x/y/z` (линейное ускорение)

## Тестирование

Для тестирования новых датчиков используйте:

```bash
python examples/brewie/test_new_sensors.py
```

Этот скрипт:
1. Подключается к роботу
2. Тестирует получение данных с всех датчиков
3. Выводит информацию о состоянии каждого датчика
4. Позволяет проверить корректность работы новых компонентов

## Требования

- ROS master должен быть запущен и доступен
- Топики `/joy` и `/imu` должны публиковать данные
- Моторы 23 и 24 должны быть подключены и настроены в ROS контроллере

## Совместимость

Все изменения обратно совместимы:
- Существующие датасеты продолжат работать
- Старые конфигурации будут работать с нулевыми значениями для новых датчиков
- Новые датчики автоматически добавляются в новые датасеты

## Логирование

Новые компоненты используют подробное логирование:
- `[JoystickSubscriber]` - логи подписчика джойстика
- `[IMUSubscriber]` - логи подписчика IMU
- `[Joystick]` - логи получения данных джойстика
- `[IMU]` - логи получения данных IMU

Уровень логирования можно настроить через стандартные механизмы Python logging.
