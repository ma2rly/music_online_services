"""Собственные исключения предметной области"""


class MusicServiceError(Exception):
    """Базовое исключение музыкального сервиса"""


class ValidationError(MusicServiceError):
    """Ошибка проверки значений полей"""


class DuplicateError(MusicServiceError):
    """Попытка создать повторяющуюся запись"""


class NotFoundError(MusicServiceError):
    """Отсутствует объект по указанному идентификатору"""


class DataFormatError(MusicServiceError):
    """Неверный формат или структура JSON и XML"""
