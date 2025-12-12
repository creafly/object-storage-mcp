import sys

from src.core.settings import get_settings
from src.services.s3_service import S3Service


def main():
    print("=" * 60)
    print("ТЕСТ ПОДКЛЮЧЕНИЯ К S3")
    print("=" * 60)

    settings = get_settings()

    print(f"AWS Region: {settings.AWS_REGION}")
    print(f"S3 Bucket: {settings.S3_BUCKET_NAME}")
    print(f"S3 Endpoint: {settings.S3_ENDPOINT_URL or 'AWS Default'}")
    print(f"Access Key ID: {settings.AWS_ACCESS_KEY_ID[:4]}...{settings.AWS_ACCESS_KEY_ID[-4:]}")
    print("=" * 60)

    try:
        settings.validate_required_fields()
        print("[OK] Все обязательные поля заполнены")
    except ValueError as e:
        print(f"[ERROR] Ошибка конфигурации: {e}")
        return 1

    s3_service = S3Service(settings)

    print("\n[TEST 1] Получение списка файлов...")
    try:
        result = s3_service.list_files(max_keys=10)
        print(f"  [OK] Найдено {result['total_count']} файлов")
        for f in result["files"][:5]:
            print(f"    - {f['key']} ({f['size_bytes']} bytes)")
        if result["total_count"] > 5:
            print(f"    ... и ещё {result['total_count'] - 5} файлов")
    except Exception as e:
        print(f"  [ERROR] Ошибка: {e}")
        return 1

    print("\n[TEST 2] Загрузка тестового файла...")
    test_key = "_test_connection_file.txt"
    test_content = "Hello from S3 connection test!"
    try:
        result = s3_service.upload_file(
            key=test_key,
            content=test_content,
            content_type="text/plain",
            overwrite=True,
        )
        print(f"  [OK] Файл загружен: {result['key']}")
        print(f"       Размер: {result['size_bytes']} bytes")
    except Exception as e:
        print(f"  [ERROR] Ошибка: {e}")
        return 1

    print("\n[TEST 3] Проверка существования файла...")
    try:
        exists = s3_service.check_file_exists(test_key)
        if exists:
            print(f"  [OK] Файл {test_key} существует")
        else:
            print(f"  [ERROR] Файл {test_key} не найден (но должен быть!)")
            return 1
    except Exception as e:
        print(f"  [ERROR] Ошибка: {e}")
        return 1

    print("\n[TEST 4] Скачивание файла...")
    try:
        result = s3_service.download_file(key=test_key)
        if result["content"] == test_content:
            print("  [OK] Содержимое файла совпадает")
        else:
            print("  [ERROR] Содержимое не совпадает!")
            print(f"    Ожидалось: {test_content}")
            print(f"    Получено: {result['content']}")
            return 1
    except Exception as e:
        print(f"  [ERROR] Ошибка: {e}")
        return 1

    print("\n[TEST 5] Удаление тестового файла...")
    try:
        result = s3_service.delete_file(key=test_key)
        print(f"  [OK] Файл удалён: {result['key']}")
    except Exception as e:
        print(f"  [ERROR] Ошибка: {e}")
        return 1

    print("\n" + "=" * 60)
    print("ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    print("S3 подключение работает корректно.")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
