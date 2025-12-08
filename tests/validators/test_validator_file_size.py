import pytest

from src.core.validators import (
    PathValidationError,
    validate_file_size,
)


class TestValidateFileSize:
    """Тесты для validate_file_size."""

    def test_valid_size_passes(self):
        """Допустимый размер проходит валидацию."""
        validate_file_size(1024 * 1024, 100 * 1024 * 1024)  # 1MB при лимите 100MB

    def test_zero_size_raises(self):
        """Нулевой размер вызывает ошибку."""
        with pytest.raises(PathValidationError, match="положительным числом"):
            validate_file_size(0, 100 * 1024 * 1024)

    def test_negative_size_raises(self):
        """Отрицательный размер вызывает ошибку."""
        with pytest.raises(PathValidationError, match="положительным числом"):
            validate_file_size(-1, 100 * 1024 * 1024)

    def test_exceeds_limit_raises(self):
        """Превышение лимита вызывает ошибку."""
        with pytest.raises(
            PathValidationError, match="превышает максимально допустимый"
        ):
            validate_file_size(200 * 1024 * 1024, 100 * 1024 * 1024)
