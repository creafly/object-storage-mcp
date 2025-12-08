import pytest

from src.core.settings import Settings


@pytest.fixture
def settings():
    """Настройки для тестов."""
    return Settings(
        AWS_ACCESS_KEY_ID="testing",
        AWS_SECRET_ACCESS_KEY="testing",
        AWS_REGION="us-east-1",
        S3_BUCKET_NAME="test-bucket",
        MAX_FILE_SIZE_MB=10,
        MAX_LIST_OBJECTS=100,
    )
