"""Абстрактный интерфейс хранилища без привязки к формату"""

from abc import ABC, abstractmethod

from domain.models import Catalog


class MusicRepository(ABC):
    """Единый контракт чтения и записи данных"""

    @abstractmethod
    def load(self) -> Catalog:
        """Загружает данные из файла"""

    @abstractmethod
    def save(self, catalog: Catalog) -> None:
        """Записывает данные в файл"""
