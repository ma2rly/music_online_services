"""Проверки CRUD для четырёх основных видов хранимых объектов"""

import unittest

from application.music_service import MusicService
from domain.exceptions import DuplicateError, NotFoundError, ValidationError


class CrudTests(unittest.TestCase):
    def setUp(self) -> None:
        self.s = MusicService()
        self.artist = self.s.add_artist('Alpha')
        self.listener = self.s.register_listener('visitor')
        self.track = self.s.add_track('Morning', self.artist.id, 140, 'Pop')
        self.playlist = self.s.create_playlist('First', self.listener.id)

    def test_artist_read_update_and_delete(self) -> None:
        self.assertEqual(self.s.get_artist(self.artist.id).name, 'Alpha')
        self.s.update_artist(self.artist.id, 'New Alpha')
        self.assertEqual(self.s.get_artist(self.artist.id).name, 'New Alpha')
        with self.assertRaises(ValidationError):
            self.s.delete_artist(self.artist.id)
        self.s.delete_track(self.track.id)
        self.s.delete_artist(self.artist.id)
        with self.assertRaises(NotFoundError):
            self.s.get_artist(self.artist.id)

    def test_listener_read_update_and_delete(self) -> None:
        self.assertEqual(self.s.get_listener(self.listener.id).username, 'visitor')
        self.s.update_listener(self.listener.id, 'new-visitor')
        self.assertEqual(self.s.get_listener(self.listener.id).username, 'new-visitor')
        with self.assertRaises(ValidationError):
            self.s.delete_listener(self.listener.id)
        self.s.delete_playlist(self.playlist.id)
        self.s.delete_listener(self.listener.id)
        with self.assertRaises(NotFoundError):
            self.s.get_listener(self.listener.id)

    def test_track_read_update_and_delete(self) -> None:
        self.assertEqual(self.s.get_track(self.track.id).title, 'Morning')
        changed = self.s.update_track(self.track.id, 'Evening',
                                      self.artist.id, 155, 'Rock')
        self.assertEqual(changed.title, 'Evening')
        self.s.delete_track(self.track.id)
        with self.assertRaises(NotFoundError):
            self.s.get_track(self.track.id)

    def test_playlist_read_update_and_delete(self) -> None:
        self.assertEqual(self.s.get_playlist(self.playlist.id).name, 'First')
        self.s.update_playlist(self.playlist.id, 'Updated')
        self.assertEqual(self.s.get_playlist(self.playlist.id).name, 'Updated')
        self.s.delete_playlist(self.playlist.id)
        with self.assertRaises(NotFoundError):
            self.s.get_playlist(self.playlist.id)

    def test_block_delete_track_from_playlist(self) -> None:
        self.s.add_track_to_playlist(self.playlist.id, self.track.id)
        with self.assertRaises(ValidationError):
            self.s.delete_track(self.track.id)
        self.s.remove_track_from_playlist(self.playlist.id, self.track.id)
        self.s.delete_track(self.track.id)

    def test_update_artist_duplicate_protected(self) -> None:
        self.s.add_artist('Beta')
        with self.assertRaises(DuplicateError):
            self.s.update_artist(self.artist.id, 'beta')
        self.assertEqual(self.s.get_artist(self.artist.id).name, 'Alpha')

    def test_update_track_invalid_input_preserves_old_data(self) -> None:
        with self.assertRaises(ValidationError):
            self.s.update_track(self.track.id, '', self.artist.id, 1, 'Rock')
        self.assertEqual(self.s.get_track(self.track.id).title, 'Morning')

    def test_get_noninteger_id_raises_custom_error(self) -> None:
        with self.assertRaises(ValidationError):
            self.s.get_artist('invalid')  # type: ignore[arg-type]


if __name__ == '__main__':
    unittest.main()
