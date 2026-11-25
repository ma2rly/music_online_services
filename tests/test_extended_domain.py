"""Дополнительные сущности, связи и сохранение в обоих форматах"""

import tempfile
import unittest
from pathlib import Path

from application.music_service import MusicService
from domain.exceptions import (
    DataFormatError, DuplicateError, NotFoundError, ValidationError,
)
from domain.models import Catalog
from infrastructure.json_repository import JsonMusicRepository
from infrastructure.xml_repository import XmlMusicRepository


class ExtendedDomainTests(unittest.TestCase):
    def setUp(self) -> None:
        self.s = MusicService()
        self.artist = self.s.add_artist('Muse')
        self.listener = self.s.register_listener('student')
        self.label = self.s.add_label('Example Records')
        self.album = self.s.add_album('Collection', self.artist.id,
                                      self.label.id)
        self.track = self.s.add_track('One', self.artist.id,
                                      170, 'Rock', self.album.id)
        self.s.add_genre('Rock')
        self.plan = self.s.add_plan('Premium', 200)
        self.sub = self.s.add_subscription(self.listener.id, self.plan.id)
        self.fav = self.s.add_favorite(self.listener.id, self.track.id)
        self.review = self.s.add_review(self.listener.id, self.track.id,
                                        5, 'Отлично')
        self.listen = self.s.record_listen(self.listener.id, self.track.id, 125)

    def test_extra_entities_exist(self) -> None:
        data = self.s.catalog.to_dict()
        self.assertEqual(len(Catalog.COLLECTIONS), 12)
        self.assertEqual(len(data['albums']), 1)
        self.assertEqual(len(data['genres']), 1)
        self.assertEqual(len(data['labels']), 1)
        self.assertEqual(len(data['subscriptions']), 1)
        self.assertEqual(len(data['favorites']), 1)
        self.assertEqual(len(data['reviews']), 1)
        self.assertEqual(len(data['history']), 1)

    def test_duplicate_favorite(self) -> None:
        with self.assertRaises(DuplicateError):
            self.s.add_favorite(self.listener.id, self.track.id)

    def test_subscription_duplicate(self) -> None:
        with self.assertRaises(DuplicateError):
            self.s.add_subscription(self.listener.id, self.plan.id)

    def test_invalid_rating(self) -> None:
        with self.assertRaises(ValidationError):
            self.s.add_review(self.listener.id, self.track.id, 8, 'Неверно')

    def test_track_album_artist_must_match(self) -> None:
        other = self.s.add_artist('Other')
        with self.assertRaises(ValidationError):
            self.s.add_track('Wrong', other.id, 100, 'Rock', self.album.id)

    def test_json_extended_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            repo = JsonMusicRepository(Path(folder) / 'catalog.json')
            self.s.save_to(repo)
            restored = MusicService()
            restored.load_from(repo)
            self.assertEqual(self.s.catalog.to_dict(), restored.catalog.to_dict())

    def test_xml_extended_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            repo = XmlMusicRepository(Path(folder) / 'catalog.xml')
            self.s.save_to(repo)
            restored = MusicService()
            restored.load_from(repo)
            self.assertEqual(self.s.catalog.to_dict(), restored.catalog.to_dict())

    def test_undeclared_reference_is_rejected(self) -> None:
        data = self.s.catalog.to_dict()
        data['subscriptions'][0]['plan_id'] = 999
        with self.assertRaises(NotFoundError):
            Catalog.from_dict(data)

    def test_xml_wrong_boolean_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            repo = XmlMusicRepository(Path(folder) / 'catalog.xml')
            self.s.save_to(repo)
            text = repo.path.read_text(encoding='utf-8')
            repo.path.write_text(text.replace('active="true"',
                                              'active="maybe"'), encoding='utf-8')
            with self.assertRaises(DataFormatError):
                MusicService().load_from(repo)


if __name__ == '__main__':
    unittest.main()
