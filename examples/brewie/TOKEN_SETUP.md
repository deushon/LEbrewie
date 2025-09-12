# Настройка HuggingFace Token для Brewie

## Обзор

HuggingFace токен теперь получается безопасным способом из переменных окружения или командной строки, а не хранится в коде.

## Способы установки токена

### 1. Переменная окружения (рекомендуется)

```bash
# Установка переменной окружения
export HUGGINGFACE_TOKEN=your_token_here

# Запуск скрипта
python examples/brewie/record_with_config.py
```

### 2. Альтернативная переменная окружения

```bash
# Использование стандартной переменной HF_TOKEN
export HF_TOKEN=your_token_here

# Запуск скрипта
python examples/brewie/record_with_config.py
```

### 3. Аргумент командной строки

```bash
# Передача токена через аргумент
python examples/brewie/record_with_config.py --hf-token your_token_here
```

### 4. Интерактивный ввод

```bash
# Токен будет запрошен при запуске (скрытый ввод)
python examples/brewie/record_with_config.py
```

## Получение токена

1. Зайдите на [HuggingFace](https://huggingface.co/)
2. Перейдите в Settings → Access Tokens
3. Создайте новый токен с правами "Write"
4. Скопируйте токен (начинается с `hf_`)

## Тестирование

Для проверки работы токена используйте тестовый скрипт:

```bash
# С переменной окружения
export HUGGINGFACE_TOKEN=your_token_here
python examples/brewie/test_token_handling.py

# С аргументом командной строки
python examples/brewie/test_token_handling.py --hf-token your_token_here
```

## Безопасность

- ✅ Никогда не коммитьте токены в код
- ✅ Используйте переменные окружения для продакшена
- ✅ Токены вводятся скрыто (не отображаются в терминале)
- ✅ Токены валидируются на корректность формата

## Порядок приоритета

1. `HUGGINGFACE_TOKEN` (переменная окружения)
2. `HF_TOKEN` (переменная окружения)
3. `--hf-token` (аргумент командной строки)
4. Интерактивный ввод (скрытый)

## Ошибки

Если токен не найден, скрипт покажет подробные инструкции по его установке.
