import pytest

from src.core.validators import (
    PathValidationError,
    validate_path_safety,
)


class TestValidatePathSafety:
    """Тесты для validate_path_safety."""

    def test_valid_simple_path(self):
        """Простой путь проходит валидацию."""
        result = validate_path_safety("documents/report.pdf")
        assert result == "documents/report.pdf"

    def test_valid_nested_path(self):
        """Вложенный путь проходит валидацию."""
        result = validate_path_safety("documents/2024/january/report.pdf")
        assert result == "documents/2024/january/report.pdf"

    def test_valid_filename_only(self):
        """Просто имя файла проходит валидацию."""
        result = validate_path_safety("report.pdf")
        assert result == "report.pdf"

    def test_empty_path_raises(self):
        """Пустой путь вызывает ошибку."""
        with pytest.raises(PathValidationError, match="не может быть пустым"):
            validate_path_safety("")

    def test_null_byte_raises(self):
        """Null-байт в пути вызывает ошибку."""
        with pytest.raises(PathValidationError, match="null-байт"):
            validate_path_safety("documents/report\x00.pdf")

    def test_absolute_path_raises(self):
        """Абсолютный путь вызывает ошибку."""
        with pytest.raises(PathValidationError, match="Абсолютные пути не разрешены"):
            validate_path_safety("/etc/passwd")

    def test_windows_absolute_path_raises(self):
        """Windows-style абсолютный путь вызывает ошибку."""
        with pytest.raises(PathValidationError, match="Абсолютные пути не разрешены"):
            validate_path_safety("\\Windows\\System32")

    def test_directory_traversal_raises(self):
        """Directory traversal вызывает ошибку."""
        with pytest.raises(PathValidationError, match="Directory traversal"):
            validate_path_safety("../../../etc/passwd")

    def test_directory_traversal_middle_raises(self):
        """Directory traversal в середине пути вызывает ошибку."""
        with pytest.raises(PathValidationError, match="Directory traversal"):
            validate_path_safety("documents/../../../etc/passwd")

    def test_too_long_path_raises(self):
        """Слишком длинный путь вызывает ошибку."""
        long_path = "a" * 1025
        with pytest.raises(PathValidationError, match="слишком длинный"):
            validate_path_safety(long_path)
