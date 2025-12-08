import pytest

from src.core.validators import (
    PathValidationError,
    validate_bucket_name,
)


class TestValidateBucketName:
    """Тесты для validate_bucket_name."""

    def test_valid_bucket_name(self):
        """Корректное имя бакета проходит валидацию."""
        result = validate_bucket_name("my-bucket-name")
        assert result == "my-bucket-name"

    def test_valid_bucket_with_numbers(self):
        """Имя бакета с цифрами проходит валидацию."""
        result = validate_bucket_name("my-bucket-123")
        assert result == "my-bucket-123"

    def test_empty_bucket_name_raises(self):
        """Пустое имя бакета вызывает ошибку."""
        with pytest.raises(PathValidationError, match="не может быть пустым"):
            validate_bucket_name("")

    def test_too_short_bucket_name_raises(self):
        """Слишком короткое имя бакета вызывает ошибку."""
        with pytest.raises(PathValidationError, match="от 3 до 63 символов"):
            validate_bucket_name("ab")

    def test_too_long_bucket_name_raises(self):
        """Слишком длинное имя бакета вызывает ошибку."""
        with pytest.raises(PathValidationError, match="от 3 до 63 символов"):
            validate_bucket_name("a" * 64)

    def test_uppercase_bucket_name_raises(self):
        """Имя с заглавными буквами вызывает ошибку."""
        with pytest.raises(PathValidationError, match="строчные буквы"):
            validate_bucket_name("My-Bucket")

    def test_consecutive_hyphens_raises(self):
        """Последовательные дефисы вызывают ошибку."""
        with pytest.raises(PathValidationError, match="последовательные дефисы"):
            validate_bucket_name("my--bucket")
