# MCP Object Storage Server

MCP сервер для работы с AWS S3 Object Storage. Позволяет AI-агентам загружать, скачивать, управлять файлами в облачном хранилище.

## Возможности

- **upload_file** — загрузка файлов в S3 (поддержка текста и base64)
- **download_file** — скачивание файлов из S3
- **list_files** — получение списка файлов с фильтрацией по префиксу
- **get_file_info** — получение метаданных файла без скачивания
- **delete_file** — удаление файлов

### Безопасность

- **Path Safety** — защита от directory traversal атак (запрет `..` и абсолютных путей)
- **Conflict Detection** — предотвращение случайной перезаписи файлов
- **File Validation** — валидация размера и расширений файлов

## Требования

- Python 3.11+
- AWS S3 или S3-совместимое хранилище (MinIO, Yandex Object Storage и т.д.)

## Установка

### 1. Клонирование и настройка окружения

```bash
cd ObjectStorageMCP

# Активация виртуального окружения
source .venv/bin/activate

# Установка зависимостей
uv sync
```

### 2. Настройка переменных окружения

Создайте файл `.env` в корне проекта:

```env
# Обязательные переменные
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
S3_BUCKET_NAME=your-bucket-name

# Опциональные переменные
AWS_REGION=us-east-1
S3_ENDPOINT_URL=https://storage.yandexcloud.net  # для S3-совместимых хранилищ
PORT=8000
HOST=0.0.0.0
LOG_LEVEL=INFO

# Лимиты безопасности
MAX_FILE_SIZE_MB=100
MAX_LIST_OBJECTS=1000
ALLOWED_EXTENSIONS=pdf,docx,xlsx,txt,json  # опционально, если не задано — все разрешены
```

## Запуск

### Локальный запуск

```bash
# Активация окружения
source .venv/bin/activate

# Запуск сервера
python -m src.entrypoints.server
```

Сервер будет доступен по адресу: `http://localhost:8000/mcp`

### Запуск через Docker

```bash
# Сборка образа
make build

# Запуск с переменными окружения из .env
make run
```

## Переменные окружения

| Переменная              | Обязательная | По умолчанию | Описание                                      |
| ----------------------- | ------------ | ------------ | --------------------------------------------- |
| `AWS_ACCESS_KEY_ID`     | Да           | —            | AWS Access Key ID                             |
| `AWS_SECRET_ACCESS_KEY` | Да           | —            | AWS Secret Access Key                         |
| `S3_BUCKET_NAME`        | Да           | —            | Имя бакета S3                                 |
| `AWS_REGION`            | Нет          | `us-east-1`  | AWS регион                                    |
| `S3_ENDPOINT_URL`       | Нет          | —            | Endpoint для S3-совместимых хранилищ          |
| `PORT`                  | Нет          | `8000`       | Порт сервера                                  |
| `HOST`                  | Нет          | `0.0.0.0`    | Хост сервера                                  |
| `LOG_LEVEL`             | Нет          | `INFO`       | Уровень логирования                           |
| `MAX_FILE_SIZE_MB`      | Нет          | `100`        | Максимальный размер файла (МБ)                |
| `MAX_LIST_OBJECTS`      | Нет          | `1000`       | Максимальное количество объектов при листинге |
| `ALLOWED_EXTENSIONS`    | Нет          | —            | Разрешённые расширения через запятую          |

## Использование инструментов

### upload_file

Загрузка файла в S3:

```json
{
  "key": "documents/report.pdf",
  "content": "base64_encoded_content_here",
  "content_type": "application/pdf",
  "is_base64": true,
  "overwrite": false
}
```

### download_file

Скачивание файла:

```json
{
  "key": "documents/report.pdf",
  "as_base64": true
}
```

### list_files

Получение списка файлов:

```json
{
  "prefix": "documents/",
  "max_keys": 100
}
```

### get_file_info

Получение информации о файле:

```json
{
  "key": "documents/report.pdf"
}
```

### delete_file

Удаление файла:

```json
{
  "key": "documents/old_report.pdf"
}
```

## Тестирование

```bash
# Активация окружения
source .venv/bin/activate

# Установка dev-зависимостей
uv sync --group dev

# Запуск тестов
make test

# Запуск с покрытием
make test-cov
```

## Docker

### Сборка

```bash
make build
```

### Push в registry

```bash
make push REGISTRY=your.registry.com VERSION=1.0.0
```
