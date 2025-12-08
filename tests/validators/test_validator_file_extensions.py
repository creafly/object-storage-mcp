import pytest

from src.core.validators import (
    PathValidationError,
    validate_file_extension,
)


class TestValidateFileExtension:
    """Тесты для validate_file_extension."""

    def test_allowed_extension_passes(self):
        """Разрешённое расширение проходит валидацию."""
        validate_file_extension("report.pdf", ["pdf", "docx", "txt"])

    def test_allowed_extension_case_insensitive(self):
        """Проверка регистра расширения."""
        validate_file_extension("report.PDF", ["pdf", "docx", "txt"])

    def test_no_restrictions_passes(self):
        """Без ограничений любое расширение проходит."""
        validate_file_extension("report.exe", None)

    def test_disallowed_extension_raises(self):
        """Запрещённое расширение вызывает ошибку."""
        with pytest.raises(PathValidationError, match="не разрешено"):
            validate_file_extension("virus.exe", ["pdf", "docx", "txt"])

    def test_no_extension_with_restrictions_raises(self):
        """Файл без расширения при наличии ограничений вызывает ошибку."""
        with pytest.raises(PathValidationError, match="Файл без расширения"):
            validate_file_extension("noextension", ["pdf", "docx"])
