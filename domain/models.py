"""Основные сущности и каталог музыкального онлайн-сервиса"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, TypeVar

from domain.entities import (
    Album, Favorite, Genre, ListeningRecord, RecordLabel, Review,
    Subscription, SubscriptionPlan, nonempty_text, positive_id,
)
from domain.exceptions import DuplicateError, NotFoundError, ValidationError


@dataclass
class Artist:
    """Исполнитель музыкальных композиций"""

    id: int
    name: str

    def __post_init__(self) -> None:
        positive_id(self.id)
        nonempty_text(self.name, 'имя исполнителя')


@dataclass
class Track:
    """Музыкальная композиция с ссылкой на исполнителя и альбом"""

    id: int
    title: str
    artist_id: int
    duration_seconds: int
    genre: str
    album_id: int | None = None

    def __post_init__(self) -> None:
        positive_id(self.id)
        nonempty_text(self.title, 'название трека')
        positive_id(self.artist_id, 'ID исполнителя')
        positive_id(self.duration_seconds, 'Длительность')
        nonempty_text(self.genre, 'жанр')
        if self.album_id is not None:
            positive_id(self.album_id, 'ID альбома')


@dataclass
class Listener:
    """Зарегистрированный пользователь сервиса"""

    id: int
    username: str

    def __post_init__(self) -> None:
        positive_id(self.id)
        nonempty_text(self.username, 'имя пользователя')


@dataclass
class Playlist:
    """Подборка треков конкретного пользователя"""

    id: int
    name: str
    owner_id: int
    track_ids: list[int] = field(default_factory=list)

    def __post_init__(self) -> None:
        positive_id(self.id)
        nonempty_text(self.name, 'название плейлиста')
        positive_id(self.owner_id, 'ID владельца')
        if not isinstance(self.track_ids, list):
            raise ValidationError('Список треков плейлиста должен быть списком')
        for track_id in self.track_ids:
            positive_id(track_id, 'ID трека')
        if len(self.track_ids) != len(set(self.track_ids)):
            raise DuplicateError('В плейлисте не должно быть повторяющихся треков')

    def add_track(self, track_id: int) -> None:
        positive_id(track_id, 'ID трека')
        if track_id in self.track_ids:
            raise DuplicateError(f'Трек {track_id} уже добавлен в плейлист')
        self.track_ids.append(track_id)

    def remove_track(self, track_id: int) -> None:
        positive_id(track_id, 'ID трека')
        if track_id not in self.track_ids:
            raise NotFoundError(f'В плейлисте нет трека {track_id}')
        self.track_ids.remove(track_id)


T = TypeVar('T')


class Catalog:
    """Хранит объекты предметной области и поддерживает CRUD"""

    COLLECTIONS: dict[str, type[Any]] = {
        'artists': Artist,
        'tracks': Track,
        'listeners': Listener,
        'playlists': Playlist,
        'albums': Album,
        'genres': Genre,
        'labels': RecordLabel,
        'plans': SubscriptionPlan,
        'subscriptions': Subscription,
        'favorites': Favorite,
        'reviews': Review,
        'history': ListeningRecord,
    }

    def __init__(self) -> None:
        self.artists: dict[int, Artist] = {}
        self.tracks: dict[int, Track] = {}
        self.listeners: dict[int, Listener] = {}
        self.playlists: dict[int, Playlist] = {}
        self.albums: dict[int, Album] = {}
        self.genres: dict[int, Genre] = {}
        self.labels: dict[int, RecordLabel] = {}
        self.plans: dict[int, SubscriptionPlan] = {}
        self.subscriptions: dict[int, Subscription] = {}
        self.favorites: dict[int, Favorite] = {}
        self.reviews: dict[int, Review] = {}
        self.history: dict[int, ListeningRecord] = {}

    @staticmethod
    def _next_id(items: dict[int, Any]) -> int:
        return max(items, default=0) + 1

    @staticmethod
    def _get(items: dict[int, T], item_id: int, label: str) -> T:
        positive_id(item_id)
        if item_id not in items:
            raise NotFoundError(f'{label} с ID {item_id} не найден')
        return items[item_id]

    @staticmethod
    def _unique_name(items: dict[int, Any], name: str,
                     skip_id: int | None = None) -> None:
        nonempty_text(name, 'название')
        if any(item.name.strip().casefold() == name.strip().casefold()
               and item.id != skip_id for item in items.values()):
            raise DuplicateError('Запись с таким именем уже существует')

    def get_artist(self, artist_id: int) -> Artist:
        return self._get(self.artists, artist_id, 'Исполнитель')

    def add_artist(self, name: str) -> Artist:
        self._unique_name(self.artists, name)
        artist = Artist(self._next_id(self.artists), name.strip())
        self.artists[artist.id] = artist
        return artist

    def update_artist(self, artist_id: int, name: str) -> Artist:
        artist = self.get_artist(artist_id)
        self._unique_name(self.artists, name, artist_id)
        artist.name = name.strip()
        return artist

    def delete_artist(self, artist_id: int) -> None:
        self.get_artist(artist_id)
        if any(t.artist_id == artist_id for t in self.tracks.values()):
            raise ValidationError('Нельзя удалить исполнителя, у которого есть треки')
        if any(a.artist_id == artist_id for a in self.albums.values()):
            raise ValidationError('Нельзя удалить исполнителя, у которого есть альбомы')
        del self.artists[artist_id]

    def get_listener(self, listener_id: int) -> Listener:
        return self._get(self.listeners, listener_id, 'Пользователь')

    def register_listener(self, username: str) -> Listener:
        if any(u.username.strip().casefold() == username.strip().casefold()
               for u in self.listeners.values() if isinstance(username, str)):
            raise DuplicateError('Пользователь с таким именем уже существует')
        listener = Listener(self._next_id(self.listeners), username)
        self.listeners[listener.id] = listener
        return listener

    def update_listener(self, listener_id: int, username: str) -> Listener:
        listener = self.get_listener(listener_id)
        nonempty_text(username, 'имя пользователя')
        if any(u.id != listener_id and u.username.strip().casefold() ==
               username.strip().casefold() for u in self.listeners.values()):
            raise DuplicateError('Пользователь с таким именем уже существует')
        listener.username = username.strip()
        return listener

    def delete_listener(self, listener_id: int) -> None:
        self.get_listener(listener_id)
        references = (self.playlists, self.subscriptions, self.favorites,
                      self.reviews, self.history)
        if any(getattr(item, 'owner_id', getattr(item, 'listener_id', None)) ==
               listener_id for group in references for item in group.values()):
            raise ValidationError('Нельзя удалить пользователя со связанными записями')
        del self.listeners[listener_id]

    def get_track(self, track_id: int) -> Track:
        return self._get(self.tracks, track_id, 'Трек')

    def _check_album_artist(self, artist_id: int, album_id: int | None) -> None:
        self.get_artist(artist_id)
        if album_id is not None:
            album = self._get(self.albums, album_id, 'Альбом')
            if album.artist_id != artist_id:
                raise ValidationError(
                    'Исполнитель трека не совпадает с исполнителем альбома'
                )

    def add_track(self, title: str, artist_id: int,
                  duration_seconds: int, genre: str,
                  album_id: int | None = None) -> Track:
        self._check_album_artist(artist_id, album_id)
        track = Track(self._next_id(self.tracks), title, artist_id,
                      duration_seconds, genre, album_id)
        self.tracks[track.id] = track
        return track

    def update_track(self, track_id: int, title: str, artist_id: int,
                     duration_seconds: int, genre: str,
                     album_id: int | None = None) -> Track:
        old = self.get_track(track_id)
        self._check_album_artist(artist_id, album_id)
        replacement = Track(track_id, title, artist_id, duration_seconds,
                            genre, album_id)
        self.tracks[track_id] = replacement
        return replacement

    def delete_track(self, track_id: int) -> None:
        self.get_track(track_id)
        if any(track_id in p.track_ids for p in self.playlists.values()):
            raise ValidationError('Сначала удалите трек из плейлистов')
        references = (self.favorites, self.reviews, self.history)
        if any(item.track_id == track_id for group in references
               for item in group.values()):
            raise ValidationError('Нельзя удалить трек со связанными записями')
        del self.tracks[track_id]

    def get_playlist(self, playlist_id: int) -> Playlist:
        return self._get(self.playlists, playlist_id, 'Плейлист')

    def create_playlist(self, name: str, owner_id: int) -> Playlist:
        self.get_listener(owner_id)
        playlist = Playlist(self._next_id(self.playlists), name, owner_id)
        self.playlists[playlist.id] = playlist
        return playlist

    def update_playlist(self, playlist_id: int, name: str) -> Playlist:
        playlist = self.get_playlist(playlist_id)
        nonempty_text(name, 'название плейлиста')
        playlist.name = name.strip()
        return playlist

    def delete_playlist(self, playlist_id: int) -> None:
        self.get_playlist(playlist_id)
        del self.playlists[playlist_id]

    def add_track_to_playlist(self, playlist_id: int, track_id: int) -> None:
        self.get_track(track_id)
        self.get_playlist(playlist_id).add_track(track_id)

    def remove_track_from_playlist(self, playlist_id: int, track_id: int) -> None:
        self.get_playlist(playlist_id).remove_track(track_id)

    def playlist_tracks(self, playlist_id: int) -> list[Track]:
        return [self.get_track(track_id) for track_id
                in self.get_playlist(playlist_id).track_ids]

    def search_tracks(self, query: str) -> list[Track]:
        nonempty_text(query, 'поисковый запрос')
        return [t for t in self.tracks.values()
                if query.casefold() in t.title.casefold()]

    def add_label(self, name: str) -> RecordLabel:
        self._unique_name(self.labels, name)
        item = RecordLabel(self._next_id(self.labels), name.strip())
        self.labels[item.id] = item
        return item

    def add_genre(self, name: str) -> Genre:
        self._unique_name(self.genres, name)
        item = Genre(self._next_id(self.genres), name.strip())
        self.genres[item.id] = item
        return item

    def add_album(self, title: str, artist_id: int,
                  label_id: int | None = None) -> Album:
        self.get_artist(artist_id)
        if label_id is not None:
            self._get(self.labels, label_id, 'Лейбл')
        item = Album(self._next_id(self.albums), title, artist_id, label_id)
        self.albums[item.id] = item
        return item

    def add_plan(self, name: str, monthly_fee: int) -> SubscriptionPlan:
        self._unique_name(self.plans, name)
        item = SubscriptionPlan(self._next_id(self.plans), name, monthly_fee)
        self.plans[item.id] = item
        return item

    def delete_plan(self, plan_id: int) -> None:
        self._get(self.plans,plan_id, 'Тариф')
        if any(sub.plan_id == plan_id
               for sub in self.subscriptions.values()):
            raise ValidationError(
                'Сначала удалите подписки на этот тариф'
            )
        del self.plans[plan_id]

    def delete_subscription(self, subscription_id: int) -> None:
        self._get(self.subscriptions, subscription_id, 'Подписка')
        del self.subscriptions[subscription_id]

    def add_subscription(self, listener_id: int, plan_id: int,
                         active: bool = True) -> Subscription:
        self.get_listener(listener_id)
        self._get(self.plans, plan_id, 'Тариф')
        if any(s.listener_id == listener_id and s.active
               for s in self.subscriptions.values() if active):
            raise DuplicateError('У пользователя уже есть активная подписка')
        item = Subscription(self._next_id(self.subscriptions),
                            listener_id, plan_id, active)
        self.subscriptions[item.id] = item
        return item

    def add_favorite(self, listener_id: int, track_id: int) -> Favorite:
        self.get_listener(listener_id)
        self.get_track(track_id)
        if any(f.listener_id == listener_id and f.track_id == track_id
               for f in self.favorites.values()):
            raise DuplicateError('Этот трек уже в избранном')
        item = Favorite(self._next_id(self.favorites), listener_id, track_id)
        self.favorites[item.id] = item
        return item

    def add_review(self, listener_id: int, track_id: int,
                   rating: int, text: str) -> Review:
        self.get_listener(listener_id)
        self.get_track(track_id)
        item = Review(self._next_id(self.reviews), listener_id,
                      track_id, rating, text)
        self.reviews[item.id] = item
        return item

    def record_listen(self, listener_id: int, track_id: int,
                      listened_seconds: int) -> ListeningRecord:
        self.get_listener(listener_id)
        self.get_track(track_id)
        item = ListeningRecord(self._next_id(self.history),
                               listener_id, track_id, listened_seconds)
        self.history[item.id] = item
        return item

    def to_dict(self) -> dict[str, list[dict[str, Any]]]:
        """Подготавливает единый сериализуемый формат для JSON и XML"""
        return {
            name: [asdict(item) for item in getattr(self, name).values()]
            for name in self.COLLECTIONS
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Catalog:
        """Восстанавливает каталог и проверяет целостность всех ссылок"""
        if not isinstance(data, dict):
            raise ValidationError('Корень данных должен быть объектом')
        required = ('artists', 'tracks', 'listeners', 'playlists')
        if any(key not in data for key in required):
            raise ValidationError(
                'Необходимы разделы artists, tracks, listeners, playlists'
            )
        catalog = cls()
        for name, model in cls.COLLECTIONS.items():
            rows = data.get(name, [])
            if not isinstance(rows, list):
                raise ValidationError(f'Раздел {name} должен быть списком')
            collection = getattr(catalog, name)
            for row in rows:
                if not isinstance(row, dict):
                    raise ValidationError(f'Элементы {name} должны быть объектами')
                try:
                    item = model(**row)
                except TypeError as error:
                    raise ValidationError(
                        f'Некорректные поля в {name}: {error}'
                    ) from error
                if item.id in collection:
                    raise DuplicateError(f'Повтор ID {item.id} в {name}')
                collection[item.id] = item

        for album in catalog.albums.values():
            catalog.get_artist(album.artist_id)
            if album.label_id is not None:
                catalog._get(catalog.labels, album.label_id, 'Лейбл')
        for track in catalog.tracks.values():
            catalog._check_album_artist(track.artist_id, track.album_id)
        for playlist in catalog.playlists.values():
            catalog.get_listener(playlist.owner_id)
            for track_id in playlist.track_ids:
                catalog.get_track(track_id)
        for sub in catalog.subscriptions.values():
            catalog.get_listener(sub.listener_id)
            catalog._get(catalog.plans, sub.plan_id, 'Тариф')
        for name in ('favorites', 'reviews', 'history'):
            for record in getattr(catalog, name).values():
                catalog.get_listener(record.listener_id)
                catalog.get_track(record.track_id)
        return catalog
