from domain.models import Artist, Catalog, Listener, Playlist, Track
from domain.repository import MusicRepository

class MusicService:
    def __init__(self, catalog: Catalog | None = None):
        self.catalog = catalog if catalog is not None else Catalog()

    def add_artist(self, name: str) -> Artist:
        return self.catalog.add_artist(name)

    def register_listener(self, username: str) -> Listener:
        return self.catalog.register_listener(username)

    def add_track(self, title: str, artist_id: int, duration_seconds: int, genre: str) -> Track:
        return self.catalog.add_track(title, artist_id, duration_seconds, genre)

    def create_playlist(self, name: str, owner_id: int) -> Playlist:
        return self.catalog.create_playlist(name, owner_id)

    def add_track_to_playlist(self, playlist_id: int, track_id: int) -> None:
        self.catalog.add_track_to_playlist(playlist_id, track_id)

    def remove_track_from_playlist(self, playlist_id: int, track_id: int) -> None:
        self.catalog.remove_track_from_playlist(playlist_id, track_id)

    def playlist_tracks(self, playlist_id: int) -> list[Track]:
        return self.catalog.playlist_tracks(playlist_id)

    def search_tracks(self, query: str) -> list[Track]:
        return self.catalog.search_tracks(query)

    def save_to(self, repository: MusicRepository) -> None:
        repository.save(self.catalog)

    def load_from(self, repository: MusicRepository) -> None:
        loaded = repository.load()
        self.catalog = loaded
