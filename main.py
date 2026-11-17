from pathlib import Path

from application.music_service import MusicService
from domain.exceptions import MusicServiceError
from infrastructure.json_repository import JsonMusicRepository
from infrastructure.xml_repository import XmlMusicRepository
from presentation.console import ConsoleApp


def main() -> None:
    root = Path(__file__).resolve().parent
    json_repo = JsonMusicRepository(root / 'data' / 'catalog.json')
    xml_repo = XmlMusicRepository(root / 'data' / 'catalog.xml')
    service = MusicService()
    if json_repo.path.exists():
        try:
            service.load_from(json_repo)
            print('Пример каталога загружен из data/catalog.json')
        except (OSError, MusicServiceError) as error:
            print(f'Не удалось загрузить пример, создан пустой каталог: {error}')
    ConsoleApp(service, json_repo, xml_repo).run()


if __name__ == '__main__':
    main()
