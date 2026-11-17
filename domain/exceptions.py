"""Иерархия собственных исключений предметной области."""

class MusicServiceError(Exception):
    """Общее пользовательское исключение сервиса."""

class ValidationError(MusicServiceError):
    """Неверное значение поля."""

class DuplicateError(MusicServiceError):
    """Повторяющийся объект."""

class NotFoundError(MusicServiceError):
    """Объект не найден."""

class DataFormatError(MusicServiceError):
    """Файл JSON или XML имеет неверную структуру."""
