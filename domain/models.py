"""Сущности и агрегат Catalog предметной области."""
from __future__ import annotations

from dataclasses import dataclass, field


from domain.exceptions import MusicServiceError, ValidationError, DuplicateError, NotFoundError


def _positive_id(value: int, label: str = "Идентификатор") -> None:
    if type(value) is not int or value <= 0:
        raise ValidationError(f"{label} должен быть положительным целым числом.")


def _nonempty_text(value: str, label: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"Поле «{label}» не должно быть пустым.")


@dataclass
class Artist:
    id: int
    name: str

    def __post_init__(self) -> None:
        _positive_id(self.id)
        _nonempty_text(self.name, "имя исполнителя")


@dataclass
class Track:
    id: int
    title: str
    artist_id: int
    duration_seconds: int
    genre: str

    def __post_init__(self) -> None:
        _positive_id(self.id)
        _nonempty_text(self.title, "название трека")
        _positive_id(self.artist_id, "ID исполнителя")
        _positive_id(self.duration_seconds, "Длительность")
        _nonempty_text(self.genre, "жанр")


@dataclass
class Listener:
    id: int
    username: str

    def __post_init__(self) -> None:
        _positive_id(self.id)
        _nonempty_text(self.username, "имя пользователя")


@dataclass
class Playlist:
    id: int
    name: str
    owner_id: int
    track_ids: list[int] = field(default_factory=list)

    def __post_init__(self) -> None:
        _positive_id(self.id)
        _nonempty_text(self.name, "название плейлиста")
        _positive_id(self.owner_id, "ID владельца")
        if not isinstance(self.track_ids, list):
            raise ValidationError("Список треков плейлиста должен быть списком.")
        for track_id in self.track_ids:
            _positive_id(track_id, "ID трека")
        if len(self.track_ids) != len(set(self.track_ids)):
            raise DuplicateError("В плейлисте не должно быть повторяющихся треков.")

    def add_track(self, track_id: int) -> None:
        _positive_id(track_id, "ID трека")
        if track_id in self.track_ids:
            raise DuplicateError(f"Трек {track_id} уже добавлен в плейлист.")
        self.track_ids.append(track_id)

    def remove_track(self, track_id: int) -> None:
        _positive_id(track_id, "ID трека")
        if track_id not in self.track_ids:
            raise NotFoundError(f"В плейлисте нет трека {track_id}.")
        self.track_ids.remove(track_id)


class Catalog:
    """Каталог пользователей, исполнителей, треков и плейлистов."""

    def __init__(self) -> None:
        self.artists: dict[int, Artist] = {}
        self.tracks: dict[int, Track] = {}
        self.listeners: dict[int, Listener] = {}
        self.playlists: dict[int, Playlist] = {}

    @staticmethod
    def _next_id(items: dict) -> int:
        return max(items, default=0) + 1

    def add_artist(self, name: str) -> Artist:
        artist = Artist(self._next_id(self.artists), name)
        if any(a.name.casefold() == name.strip().casefold() for a in self.artists.values()):
            raise DuplicateError("Исполнитель с таким именем уже существует.")
        self.artists[artist.id] = artist
        return artist

    def register_listener(self, username: str) -> Listener:
        listener = Listener(self._next_id(self.listeners), username)
        if any(u.username.casefold() == username.strip().casefold() for u in self.listeners.values()):
            raise DuplicateError("Пользователь с таким именем уже существует.")
        self.listeners[listener.id] = listener
        return listener

    def add_track(self, title: str, artist_id: int, duration_seconds: int, genre: str) -> Track:
        if artist_id not in self.artists:
            raise NotFoundError(f"Исполнитель с ID {artist_id} не найден.")
        track = Track(self._next_id(self.tracks), title, artist_id, duration_seconds, genre)
        self.tracks[track.id] = track
        return track

    def create_playlist(self, name: str, owner_id: int) -> Playlist:
        if owner_id not in self.listeners:
            raise NotFoundError(f"Пользователь с ID {owner_id} не найден.")
        playlist = Playlist(self._next_id(self.playlists), name, owner_id)
        self.playlists[playlist.id] = playlist
        return playlist

    def add_track_to_playlist(self, playlist_id: int, track_id: int) -> None:
        if playlist_id not in self.playlists:
            raise NotFoundError(f"Плейлист с ID {playlist_id} не найден.")
        if track_id not in self.tracks:
            raise NotFoundError(f"Трек с ID {track_id} не найден.")
        self.playlists[playlist_id].add_track(track_id)

    def remove_track_from_playlist(self, playlist_id: int, track_id: int) -> None:
        if playlist_id not in self.playlists:
            raise NotFoundError(f"Плейлист с ID {playlist_id} не найден.")
        self.playlists[playlist_id].remove_track(track_id)

    def search_tracks(self, query: str) -> list[Track]:
        _nonempty_text(query, "поисковый запрос")
        return [t for t in self.tracks.values() if query.casefold() in t.title.casefold()]

    def playlist_tracks(self, playlist_id: int) -> list[Track]:
        if playlist_id not in self.playlists:
            raise NotFoundError(f"Плейлист с ID {playlist_id} не найден.")
        return [self.tracks[id_] for id_ in self.playlists[playlist_id].track_ids]

    def to_dict(self) -> dict:
        """Общая структура для JSON и XML; порядок элементов стабилен."""
        return {
            "artists": [{"id": a.id, "name": a.name} for a in self.artists.values()],
            "tracks": [
                {"id": t.id, "title": t.title, "artist_id": t.artist_id,
                 "duration_seconds": t.duration_seconds, "genre": t.genre}
                for t in self.tracks.values()
            ],
            "listeners": [{"id": u.id, "username": u.username} for u in self.listeners.values()],
            "playlists": [
                {"id": p.id, "name": p.name, "owner_id": p.owner_id, "track_ids": list(p.track_ids)}
                for p in self.playlists.values()
            ],
        }

    @classmethod
    def from_dict(cls, data: dict) -> Catalog:
        """Восстановление с проверкой типов, уникальности ID и связей."""
        if not isinstance(data, dict):
            raise ValidationError("Корень данных должен быть объектом.")
        keys = ("artists", "tracks", "listeners", "playlists")
        if any(key not in data or not isinstance(data[key], list) for key in keys):
            raise ValidationError("Необходимы списки: artists, tracks, listeners, playlists.")
        service = cls()

        def read_items(collection: str, factory, destination: dict):
            for row in data[collection]:
                if not isinstance(row, dict):
                    raise ValidationError(f"Элементы {collection} должны быть объектами.")
                try:
                    item = factory(**row)
                except TypeError as exc:
                    raise ValidationError(f"Некорректные поля в {collection}: {exc}") from exc
                if item.id in destination:
                    raise DuplicateError(f"Повтор ID {item.id} в {collection}.")
                destination[item.id] = item

        read_items("artists", Artist, service.artists)
        read_items("listeners", Listener, service.listeners)
        read_items("tracks", Track, service.tracks)
        read_items("playlists", Playlist, service.playlists)
        for track in service.tracks.values():
            if track.artist_id not in service.artists:
                raise NotFoundError(f"В файле нет исполнителя {track.artist_id} для трека {track.id}.")
        for playlist in service.playlists.values():
            if playlist.owner_id not in service.listeners:
                raise NotFoundError(f"В файле нет владельца {playlist.owner_id} плейлиста {playlist.id}.")
            for track_id in playlist.track_ids:
                if track_id not in service.tracks:
                    raise NotFoundError(f"В файле нет трека {track_id} плейлиста {playlist.id}.")
        return service
