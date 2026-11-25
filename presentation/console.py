"""Консольный интерфейс и обработка пользовательских ошибок"""

from application.music_service import MusicService
from domain.exceptions import DataFormatError, MusicServiceError
from infrastructure.json_repository import JsonMusicRepository
from infrastructure.xml_repository import XmlMusicRepository


class ConsoleApp:
    """Запускает меню и предотвращает аварийный выход при ошибках"""

    def __init__(self, service: MusicService,
                 json_repo: JsonMusicRepository,
                 xml_repo: XmlMusicRepository) -> None:
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
                  f'(владелец #{playlist.owner_id}, '
                  f'треков: {len(playlist.track_ids)})')
        if not any((catalog.artists, catalog.tracks,
                    catalog.listeners, catalog.playlists)):
            print('  Каталог пуст')

    def show_extra(self) -> None:
        """Отображает дополнительные коллекции предметной области"""
        catalog = self.service.catalog
        groups = (
            ('АЛЬБОМЫ', 'albums'),
            ('ЖАНРЫ', 'genres'),
            ('ЛЕЙБЛЫ', 'labels'),
            ('ТАРИФЫ', 'plans'),
            ('ПОДПИСКИ', 'subscriptions'),
            ('ИЗБРАННОЕ', 'favorites'),
            ('ОТЗЫВЫ', 'reviews'),
            ('ИСТОРИЯ ПРОСЛУШИВАНИЯ', 'history'),
        )
        for title, name in groups:
            print(title + ':')
            collection = getattr(catalog, name)
            for obj in collection.values():
                print(f'  #{obj.id}: {obj}')
            if not collection:
                print('  Пока нет записей')

    @staticmethod
    def read_int(prompt: str) -> int:
        """Запрашивает целое число с сообщением о допустимом типе"""
        return int(input(prompt))

    def run(self) -> None:
        menu = """
========== МУЗЫКАЛЬНЫЙ СЕРВИС ==========
 1  — Показать каталог
 2  — Добавить исполнителя
 3  — Зарегистрировать пользователя
 4  — Добавить трек
 5  — Создать плейлист
 6  — Добавить трек в плейлист
 7  — Показать треки плейлиста
 8  — Поиск треков
 9  — Удалить трек из плейлиста
10  — Сохранить в JSON
11  — Загрузить из JSON
12  — Сохранить в XML
13  — Загрузить из XML
--- CRUD: изменение и удаление ---
14  — Переименовать исполнителя
15  — Удалить исполнителя
16  — Изменить пользователя
17  — Удалить пользователя
18  — Изменить трек
19  — Удалить трек
20  — Переименовать плейлист
21  — Удалить плейлист
--- Дополнительные классы ---
22  — Создать альбом
23  — Добавить жанр
24  — Добавить лейбл
25  — Создать тариф
26  — Оформить подписку
27  — Добавить трек в избранное
28  — Оставить отзыв
29  — Записать прослушивание
30  — Показать дополнительные коллекции
 0  — Выход
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
                    artist_id = self.read_int('ID исполнителя: ')
                    duration = self.read_int('Длительность в секундах: ')
                    genre = input('Жанр: ')
                    track = self.service.add_track(title, artist_id, duration, genre)
                    print(f'Добавлен трек #{track.id}')
                elif choice == '5':
                    name = input('Название плейлиста: ')
                    owner_id = self.read_int('ID пользователя: ')
                    playlist = self.service.create_playlist(name, owner_id)
                    print(f'Создан плейлист #{playlist.id}')
                elif choice == '6':
                    playlist_id = self.read_int('ID плейлиста: ')
                    track_id = self.read_int('ID трека: ')
                    self.service.add_track_to_playlist(playlist_id, track_id)
                    print('Трек добавлен')
                elif choice == '7':
                    playlist_id = self.read_int('ID плейлиста: ')
                    tracks = self.service.playlist_tracks(playlist_id)
                    print('Треки:', ', '.join(t.title for t in tracks)
                          or 'плейлист пуст')
                elif choice == '8':
                    tracks = self.service.search_tracks(input('Часть названия: '))
                    print('Найдено:', ', '.join(t.title for t in tracks)
                          or 'ничего')
                elif choice == '9':
                    playlist_id = self.read_int('ID плейлиста: ')
                    track_id = self.read_int('ID трека: ')
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
                elif choice == '14':
                    artist_id = self.read_int('ID исполнителя: ')
                    self.service.update_artist(artist_id, input('Новое имя: '))
                    print('Исполнитель обновлён')
                elif choice == '15':
                    self.service.delete_artist(self.read_int('ID исполнителя: '))
                    print('Исполнитель удалён')
                elif choice == '16':
                    listener_id = self.read_int('ID пользователя: ')
                    self.service.update_listener(listener_id,
                                                 input('Новый логин: '))
                    print('Пользователь обновлён')
                elif choice == '17':
                    self.service.delete_listener(self.read_int('ID пользователя: '))
                    print('Пользователь удалён')
                elif choice == '18':
                    track_id = self.read_int('ID трека: ')
                    title = input('Новое название трека: ')
                    artist_id = self.read_int('ID исполнителя: ')
                    duration = self.read_int('Новая длительность: ')
                    genre = input('Жанр: ')
                    self.service.update_track(track_id, title, artist_id,
                                              duration, genre)
                    print('Трек обновлён')
                elif choice == '19':
                    self.service.delete_track(self.read_int('ID трека: '))
                    print('Трек удалён')
                elif choice == '20':
                    playlist_id = self.read_int('ID плейлиста: ')
                    self.service.update_playlist(playlist_id,
                                                 input('Новое название: '))
                    print('Плейлист обновлён')
                elif choice == '21':
                    self.service.delete_playlist(self.read_int('ID плейлиста: '))
                    print('Плейлист удалён')
                elif choice == '22':
                    title = input('Название альбома: ')
                    artist_id = self.read_int('ID исполнителя: ')
                    album = self.service.add_album(title, artist_id)
                    print(f'Добавлен альбом #{album.id}')
                elif choice == '23':
                    genre = self.service.add_genre(input('Название жанра: '))
                    print(f'Добавлен жанр #{genre.id}')
                elif choice == '24':
                    label = self.service.add_label(input('Название лейбла: '))
                    print(f'Добавлен лейбл #{label.id}')
                elif choice == '25':
                    name = input('Название тарифа: ')
                    fee = self.read_int('Стоимость в условных единицах: ')
                    plan = self.service.add_plan(name, fee)
                    print(f'Создан тариф #{plan.id}')
                elif choice == '26':
                    listener_id = self.read_int('ID пользователя: ')
                    plan_id = self.read_int('ID тарифа: ')
                    sub = self.service.add_subscription(listener_id, plan_id)
                    print(f'Оформлена подписка #{sub.id}')
                elif choice == '27':
                    listener_id = self.read_int('ID пользователя: ')
                    track_id = self.read_int('ID трека: ')
                    self.service.add_favorite(listener_id, track_id)
                    print('Трек добавлен в избранное')
                elif choice == '28':
                    listener_id = self.read_int('ID пользователя: ')
                    track_id = self.read_int('ID трека: ')
                    rating = self.read_int('Оценка от 1 до 5: ')
                    text = input('Текст отзыва: ')
                    self.service.add_review(listener_id, track_id, rating, text)
                    print('Отзыв сохранён')
                elif choice == '29':
                    listener_id = self.read_int('ID пользователя: ')
                    track_id = self.read_int('ID трека: ')
                    seconds = self.read_int('Прослушано секунд: ')
                    self.service.record_listen(listener_id, track_id, seconds)
                    print('Прослушивание записано')
                elif choice == '30':
                    self.show_extra()
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
