"""Реализация MusicRepository для JSON."""
import json
from pathlib import Path

from domain.exceptions import DataFormatError, MusicServiceError
from domain.models import Catalog
from domain.repository import MusicRepository

class JsonMusicRepository(MusicRepository):
    def __init__(self, path: Path):
        self.path = Path(path)

    def load(self) -> Catalog:
        try:
            with self.path.open('r', encoding='utf-8') as stream:
                data = json.load(stream)
        except (json.JSONDecodeError, UnicodeError) as error:
            raise DataFormatError(f'Некорректный JSON: {error}') from error
        try:
            return Catalog.from_dict(data)
        except (MusicServiceError, TypeError, ValueError) as error:
            raise DataFormatError(f'Неверные данные JSON: {error}') from error

    def save(self, catalog: Catalog) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open('w', encoding='utf-8') as stream:
            json.dump(catalog.to_dict(), stream, ensure_ascii=False, indent=2)
            stream.write('\n')
