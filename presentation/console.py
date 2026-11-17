"""Ввод/вывод: меню, преобразование типов и обработка исключений."""
from application.music_service import MusicService
from domain.exceptions import MusicServiceError, DataFormatError
from infrastructure.json_repository import JsonMusicRepository
from infrastructure.xml_repository import XmlMusicRepository

class ConsoleApp:
    def __init__(self, service: MusicService, json_repo: JsonMusicRepository,
                 xml_repo: XmlMusicRepository):
        self.service = service
        self.json_repo = json_repo
        self.xml_repo = xml_repo

    def show_catalog(self) -> None:
        catalog = self.service.catalog
        print('\nИСПОЛНИТЕЛИ:')
        for artist in catalog.artists.values():
            print(f'  #{artist.id}: {artist.name}')
        print('ТРЕКИ:')
        for track in catalog.tracks.values():
            print(f'  #{track.id}: {track.title} — '
                  f'{catalog.artists[track.artist_id].name}, {track.genre}, '
                  f'{track.duration_seconds} сек.')
        print('ПОЛЬЗОВАТЕЛИ:')
        for listener in catalog.listeners.values():
            print(f'  #{listener.id}: {listener.username}')
        print('ПЛЕЙЛИСТЫ:')
        for playlist in catalog.playlists.values():
            print(f'  #{playlist.id}: {playlist.name} '
                  f'(владелец #{playlist.owner_id}, треков: {len(playlist.track_ids)})')
        if not any((catalog.artists, catalog.tracks, catalog.listeners, catalog.playlists)):
            print('  Каталог пуст')

    def run(self) -> None:
        menu = """
МУЗЫКАЛЬНЫЙ СЕРВИС 
1. Показать каталог
2. Добавить исполнителя
3. Зарегистрировать пользователя
4. Добавить трек
5. Создать плейлист
6. Добавить трек в плейлист
7. Показать треки плейлиста
8. Поиск треков
9. Удалить трек из плейлиста
10. Сохранить в JSON
11. Загрузить из JSON
12. Сохранить в XML
13. Загрузить из XML
0.  Выход
"""
        while True:
            print(menu)
            try:
                choice = input('Выберите пункт: ').strip()
                if choice == '0':
                    print('Программа завершена')
                    return
                if choice == '1':
                    self.show_catalog()
                elif choice == '2':
                    artist = self.service.add_artist(input('Имя исполнителя: '))
                    print(f'Добавлен исполнитель #{artist.id}')
                elif choice == '3':
                    user = self.service.register_listener(input('Логин пользователя: '))
                    print(f'Зарегистрирован пользователь #{user.id}')
                elif choice == '4':
                    title = input('Название трека: ')
                    artist_id = int(input('ID исполнителя: '))
                    duration = int(input('Длительность в секундах: '))
                    genre = input('Жанр: ')
                    track = self.service.add_track(title, artist_id, duration, genre)
                    print(f'Добавлен трек #{track.id}')
                elif choice == '5':
                    name = input('Название плейлиста: ')
                    owner_id = int(input('ID пользователя: '))
                    playlist = self.service.create_playlist(name, owner_id)
                    print(f'Создан плейлист #{playlist.id}')
                elif choice == '6':
                    playlist_id = int(input('ID плейлиста: '))
                    track_id = int(input('ID трека: '))
                    self.service.add_track_to_playlist(playlist_id, track_id)
                    print('Трек добавлен')
                elif choice == '7':
                    playlist_id = int(input('ID плейлиста: '))
                    tracks = self.service.playlist_tracks(playlist_id)
                    print('Треки:', ', '.join(t.title for t in tracks) or 'плейлист пуст')
                elif choice == '8':
                    tracks = self.service.search_tracks(input('Часть названия: '))
                    print('Найдено:', ', '.join(t.title for t in tracks) or 'ничего')
                elif choice == '9':
                    playlist_id = int(input('ID плейлиста: '))
                    track_id = int(input('ID трека: '))
                    self.service.remove_track_from_playlist(playlist_id, track_id)
                    print('Трек удалён')
                elif choice == '10':
                    self.service.save_to(self.json_repo)
                    print('Сохранено в JSON')
                elif choice == '11':
                    self.service.load_from(self.json_repo)
                    print('Загружено из JSON')
                elif choice == '12':
                    self.service.save_to(self.xml_repo)
                    print('Сохранено в XML')
                elif choice == '13':
                    self.service.load_from(self.xml_repo)
                    print('Загружено из XML')
                else:
                    print('Нет такого пункта меню')
            except ValueError:
                print('Ошибка ввода: ID и длительность должны быть целыми числами')
            except DataFormatError as error:
                print(f'Ошибка формата файла: {error}')
            except MusicServiceError as error:
                print(f'Ошибка: {error}')
            except FileNotFoundError:
                print('Файл не найден. Сначала сохраните данные')
            except PermissionError:
                print('Недостаточно прав для записи или чтения файла')
            except OSError as error:
                print(f'Ошибка работы с файлом: {error}')
            except (EOFError, KeyboardInterrupt):
                print('\nВыход из программы')
                return
