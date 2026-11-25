"""Тесты предметной области: python -m unittest discover -s tests -v"""
import unittest

from application.music_service import MusicService
from domain.exceptions import DuplicateError, NotFoundError, ValidationError
from domain.models import Artist, Catalog, Playlist


class ServiceTests(unittest.TestCase):
    def setUp(self):
        self.service = MusicService()
        self.artist = self.service.add_artist('Muse')
        self.user = self.service.register_listener('anna')
        self.track = self.service.add_track('Uprising', self.artist.id, 305, 'Rock')
        self.playlist = self.service.create_playlist('Любимое', self.user.id)

    def test_create_artist(self):
        self.assertEqual(self.artist.id, 1)

    def test_register_user(self):
        self.assertEqual(self.user.username, 'anna')

    def test_create_track(self):
        self.assertEqual(self.track.artist_id, self.artist.id)

    def test_add_track_to_playlist(self):
        self.service.add_track_to_playlist(self.playlist.id, self.track.id)
        self.assertEqual(self.service.playlist_tracks(self.playlist.id), [self.track])

    def test_remove_track_from_playlist(self):
        self.service.add_track_to_playlist(self.playlist.id, self.track.id)
        self.service.remove_track_from_playlist(self.playlist.id, self.track.id)
        self.assertEqual(self.service.playlist_tracks(self.playlist.id), [])

    def test_search_case_insensitive(self):
        self.assertEqual(self.service.search_tracks('UPRI'), [self.track])

    def test_empty_title_rejected(self):
        with self.assertRaises(ValidationError):
            self.service.add_track('   ', self.artist.id, 200, 'Pop')

    def test_negative_duration_rejected(self):
        with self.assertRaises(ValidationError):
            self.service.add_track('New', self.artist.id, -1, 'Pop')

    def test_missing_artist_rejected(self):
        with self.assertRaises(NotFoundError):
            self.service.add_track('New', 999, 200, 'Pop')

    def test_missing_user_rejected(self):
        with self.assertRaises(NotFoundError):
            self.service.create_playlist('New', 999)

    def test_duplicate_artist_rejected(self):
        with self.assertRaises(DuplicateError):
            self.service.add_artist('mUSE')

    def test_duplicate_username_rejected(self):
        with self.assertRaises(DuplicateError):
            self.service.register_listener('ANNA')

    def test_duplicate_track_rejected(self):
        self.service.add_track_to_playlist(1, 1)
        with self.assertRaises(DuplicateError):
            self.service.add_track_to_playlist(1, 1)

    def test_missing_playlist_rejected(self):
        with self.assertRaises(NotFoundError):
            self.service.playlist_tracks(999)

    def test_invalid_id_type_rejected(self):
        with self.assertRaises(ValidationError):
            Artist(True, 'Bad')

    def test_duplicate_playlist_ids_rejected(self):
        with self.assertRaises(DuplicateError):
            Playlist(1, 'Bad', 1, [1, 1])

    def test_invalid_reference_in_file(self):
        data = self.service.catalog.to_dict()
        data['tracks'][0]['artist_id'] = 999
        with self.assertRaises(NotFoundError):
            Catalog.from_dict(data)

    def test_duplicate_entity_ids_in_file(self):
        data = self.service.catalog.to_dict()
        data['artists'].append({'id': 1, 'name': 'Other'})
        with self.assertRaises(DuplicateError):
            Catalog.from_dict(data)

    def test_missing_entity_field_in_file(self):
        data = self.service.catalog.to_dict()
        del data['tracks'][0]['genre']
        with self.assertRaises(ValidationError):
            Catalog.from_dict(data)


if __name__ == '__main__':
    unittest.main()
