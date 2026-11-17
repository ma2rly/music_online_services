"""Абстрактный интерфейс хранилища, не зависящий от JSON и XML."""
from abc import ABC, abstractmethod
from domain.models import Catalog

class MusicRepository(ABC):
    @abstractmethod
    def load(self) -> Catalog:
        """Загрузить каталог."""

    @abstractmethod
    def save(self, catalog: Catalog) -> None:
        """Сохранить каталог."""
