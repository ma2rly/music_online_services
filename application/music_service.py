"""Прикладной сервис для работы с каталогом и репозиториями"""

from domain.entities import (
    Album, Favorite, Genre, ListeningRecord, RecordLabel, Review,
    Subscription, SubscriptionPlan,
)
from domain.models import Artist, Catalog, Listener, Playlist, Track
from domain.repository import MusicRepository


class MusicService:
    """Предоставляет операции предметной области интерфейсу пользователя"""

    def __init__(self, catalog: Catalog | None = None) -> None:
        self.catalog = catalog if catalog is not None else Catalog()

    def get_artist(self, artist_id: int) -> Artist:
        return self.catalog.get_artist(artist_id)

    def add_artist(self, name: str) -> Artist:
        return self.catalog.add_artist(name)

    def update_artist(self, artist_id: int, name: str) -> Artist:
        return self.catalog.update_artist(artist_id, name)

    def delete_artist(self, artist_id: int) -> None:
        self.catalog.delete_artist(artist_id)

    def get_listener(self, listener_id: int) -> Listener:
        return self.catalog.get_listener(listener_id)

    def register_listener(self, username: str) -> Listener:
        return self.catalog.register_listener(username)

    def update_listener(self, listener_id: int, username: str) -> Listener:
        return self.catalog.update_listener(listener_id, username)

    def delete_listener(self, listener_id: int) -> None:
        self.catalog.delete_listener(listener_id)

    def get_track(self, track_id: int) -> Track:
        return self.catalog.get_track(track_id)

    def add_track(self, title: str, artist_id: int,
                  duration_seconds: int, genre: str,
                  album_id: int | None = None) -> Track:
        return self.catalog.add_track(title, artist_id, duration_seconds,
                                      genre, album_id)

    def update_track(self, track_id: int, title: str, artist_id: int,
                     duration_seconds: int, genre: str,
                     album_id: int | None = None) -> Track:
        return self.catalog.update_track(track_id, title, artist_id,
                                         duration_seconds, genre, album_id)

    def delete_track(self, track_id: int) -> None:
        self.catalog.delete_track(track_id)

    def get_playlist(self, playlist_id: int) -> Playlist:
        return self.catalog.get_playlist(playlist_id)

    def create_playlist(self, name: str, owner_id: int) -> Playlist:
        return self.catalog.create_playlist(name, owner_id)

    def update_playlist(self, playlist_id: int, name: str) -> Playlist:
        return self.catalog.update_playlist(playlist_id, name)

    def delete_playlist(self, playlist_id: int) -> None:
        self.catalog.delete_playlist(playlist_id)

    def add_track_to_playlist(self, playlist_id: int, track_id: int) -> None:
        self.catalog.add_track_to_playlist(playlist_id, track_id)

    def remove_track_from_playlist(self, playlist_id: int, track_id: int) -> None:
        self.catalog.remove_track_from_playlist(playlist_id, track_id)

    def playlist_tracks(self, playlist_id: int) -> list[Track]:
        return self.catalog.playlist_tracks(playlist_id)

    def search_tracks(self, query: str) -> list[Track]:
        return self.catalog.search_tracks(query)

    def add_album(self, title: str, artist_id: int,
                  label_id: int | None = None) -> Album:
        return self.catalog.add_album(title, artist_id, label_id)

    def add_genre(self, name: str) -> Genre:
        return self.catalog.add_genre(name)

    def add_label(self, name: str) -> RecordLabel:
        return self.catalog.add_label(name)

    def add_plan(self, name: str, monthly_fee: int) -> SubscriptionPlan:
        return self.catalog.add_plan(name, monthly_fee)

    def add_subscription(self, listener_id: int, plan_id: int,
                         active: bool = True) -> Subscription:
        return self.catalog.add_subscription(listener_id, plan_id, active)

    def add_favorite(self, listener_id: int, track_id: int) -> Favorite:
        return self.catalog.add_favorite(listener_id, track_id)

    def add_review(self, listener_id: int, track_id: int,
                   rating: int, text: str) -> Review:
        return self.catalog.add_review(listener_id, track_id, rating, text)

    def record_listen(self, listener_id: int, track_id: int,
                      listened_seconds: int) -> ListeningRecord:
        return self.catalog.record_listen(listener_id, track_id,
                                          listened_seconds)

    def save_to(self, repository: MusicRepository) -> None:
        repository.save(self.catalog)

    def load_from(self, repository: MusicRepository) -> None:
        # Меняем каталог только после успешного чтения и проверки данных
        loaded = repository.load()
        self.catalog = loaded
