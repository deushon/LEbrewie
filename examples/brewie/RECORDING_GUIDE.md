# Руководство по записи датасетов для робота Brewie

Это руководство описывает, как записывать демонстрационные данные с робота Brewie для обучения политик в стандарте LeRobot.

## Требования

### 1. Оборудование
- Робот Brewie с подключенными сервоприводами
- ROS master запущен и доступен
- Камера (опционально)

### 2. Программное обеспечение
- Python 3.8+
- ROS (Robot Operating System)
- roslibpy для Python
- LeRobot библиотека

### 3. Учетные данные
- HuggingFace аккаунт
- HuggingFace token с правами на создание датасетов

## Установка зависимостей

```bash
pip install roslibpy opencv-python numpy
pip install -e .  # Установка LeRobot из исходного кода
```

## Настройка HuggingFace

1. Создайте аккаунт на [HuggingFace](https://huggingface.co)
2. Создайте token в настройках аккаунта
3. Убедитесь, что у вас есть права на создание датасетов

## Быстрый старт

### Вариант 1: Интерактивная настройка

Запустите скрипт с интерактивным вводом параметров:

```bash
python examples/brewie/record.py
```

Скрипт попросит ввести:
- HuggingFace username
- HuggingFace token
- Название датасета
- Количество эпизодов
- Длительность эпизодов
- Описание задачи
- Настройки ROS

### Вариант 2: Конфигурационный файл

1. Отредактируйте `record_config.py`:

```python
config = RecordingConfig(
    hf_username="your_username",     # Ваш HuggingFace username
    hf_token="your_token",           # Ваш HuggingFace token
    dataset_name="brewie_my_task",   # Название датасета
    num_episodes=5,                  # Количество эпизодов
    episode_time_sec=30,             # Длительность эпизода
    task_description="Моя задача"    # Описание задачи
)
```

2. Запустите скрипт:

```bash
python examples/brewie/record_with_config.py
```

## Предустановленные конфигурации

В `record_config.py` доступны готовые конфигурации:

### Быстрая демонстрация
```python
config = RecordingConfig.quick_demo()
# 2 эпизода по 15 секунд
```

### Полный датасет
```python
config = RecordingConfig.full_dataset()
# 20 эпизодов по 60 секунд
```

### Задача pick and place
```python
config = RecordingConfig.pick_place_task()
# 10 эпизодов по 45 секунд
```

### Задача сборки
```python
config = RecordingConfig.assembly_task()
# 15 эпизодов по 90 секунд
```

## Параметры конфигурации

### Основные настройки
- `hf_username`: Ваш HuggingFace username
- `hf_token`: Ваш HuggingFace token
- `dataset_name`: Название датасета
- `num_episodes`: Количество эпизодов
- `episode_time_sec`: Длительность эпизода в секундах
- `fps`: Частота записи (кадров в секунду)

### Настройки робота
- `ros_master_ip`: IP адрес ROS master
- `ros_master_port`: Порт ROS master
- `max_relative_target`: Максимальное движение за шаг
- `servo_duration`: Время выполнения движения сервоприводов

### Настройки задачи
- `task_description`: Описание задачи
- `task_category`: Категория задачи (manipulation, pick_place, assembly)
- `difficulty_level`: Уровень сложности (beginner, intermediate, advanced)

## Управление во время записи

- **ENTER**: Начать/продолжить запись эпизода
- **ESC**: Остановить запись
- **R**: Перезаписать текущий эпизод

## Структура датасета

Созданный датасет будет содержать:

### Наблюдения (observations)
- Позиции всех сервоприводов: `joint_name.pos`
- Изображения с камеры: `camera`

### Действия (actions)
- Целевые позиции сервоприводов: `joint_name.pos`

### Метаданные
- Описание задачи
- Категория и сложность
- Информация о роботе
- Временные метки

## Проверка ROS подключения

Перед записью убедитесь, что ROS работает корректно:

```bash
# Проверка ROS master
rosnode list

# Проверка сервисов
rosservice list | grep bus_servo

# Проверка топиков
rostopic list | grep bus_servo
```

## Устранение неполадок

### Ошибка подключения к ROS
- Проверьте, что ROS master запущен
- Убедитесь в правильности IP и порта
- Проверьте сетевое соединение

### Ошибки сервоприводов
- Убедитесь, что все сервоприводы подключены
- Проверьте правильность маппинга ID сервоприводов
- Убедитесь, что ROS контроллер робота запущен

### Проблемы с камерой
- Проверьте, что топик камеры публикуется
- Убедитесь в правильности формата изображения

### Ошибки HuggingFace
- Проверьте правильность username и token
- Убедитесь, что у вас есть права на создание датасетов
- Проверьте интернет соединение

## Примеры использования

### Запись простой демонстрации
```python
config = RecordingConfig(
    hf_username="myusername",
    hf_token="hf_...",
    dataset_name="brewie_simple_demo",
    num_episodes=3,
    episode_time_sec=20,
    task_description="Простое движение рук робота"
)
```

### Запись сложной задачи
```python
config = RecordingConfig(
    hf_username="myusername", 
    hf_token="hf_...",
    dataset_name="brewie_complex_task",
    num_episodes=15,
    episode_time_sec=60,
    task_description="Сложная манипуляция с объектами",
    task_category="manipulation",
    difficulty_level="advanced"
)
```

## Следующие шаги

После записи датасета вы можете:

1. **Просмотреть датасет**: Используйте `examples/1_load_lerobot_dataset.py`
2. **Обучить политику**: Используйте `examples/3_train_policy.py`
3. **Оценить политику**: Используйте `examples/2_evaluate_pretrained_policy.py`

## Поддержка

При возникновении проблем:
1. Проверьте логи ROS
2. Убедитесь в правильности конфигурации
3. Проверьте подключение всех устройств
4. Обратитесь к документации LeRobot
