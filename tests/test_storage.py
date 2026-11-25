"""Тесты работы с JSON и XML"""
import tempfile
import unittest
from pathlib import Path

from application.music_service import MusicService
from domain.exceptions import DataFormatError
from infrastructure.json_repository import JsonMusicRepository
from infrastructure.xml_repository import XmlMusicRepository


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.service = MusicService()
        artist = self.service.add_artist('Кино')
        user = self.service.register_listener('test')
        track = self.service.add_track('Группа крови', artist.id, 287, 'Рок')
        playlist = self.service.create_playlist('Любимое', user.id)
        self.service.add_track_to_playlist(playlist.id, track.id)

    def test_json_roundtrip(self):
        repository = JsonMusicRepository(self.folder / 'nested' / 'catalog.json')
        self.service.save_to(repository)
        other = MusicService()
        other.load_from(repository)
        self.assertEqual(other.catalog.to_dict(), self.service.catalog.to_dict())

    def test_xml_roundtrip(self):
        repository = XmlMusicRepository(self.folder / 'nested' / 'catalog.xml')
        self.service.save_to(repository)
        other = MusicService()
        other.load_from(repository)
        self.assertEqual(other.catalog.to_dict(), self.service.catalog.to_dict())

    def test_json_invalid_syntax(self):
        file = self.folder / 'broken.json'
        file.write_text('{broken', encoding='utf-8')
        with self.assertRaises(DataFormatError):
            self.service.load_from(JsonMusicRepository(file))

    def test_xml_invalid_syntax(self):
        file = self.folder / 'broken.xml'
        file.write_text('<music_service>', encoding='utf-8')
        with self.assertRaises(DataFormatError):
            self.service.load_from(XmlMusicRepository(file))

    def test_json_wrong_structure(self):
        file = self.folder / 'broken.json'
        file.write_text('{"artists": []}', encoding='utf-8')
        with self.assertRaises(DataFormatError):
            self.service.load_from(JsonMusicRepository(file))

    def test_xml_missing_section(self):
        file = self.folder / 'broken.xml'
        file.write_text(
            '<music_service version="1"><artists/></music_service>',
            encoding='utf-8',
        )
        with self.assertRaises(DataFormatError):
            self.service.load_from(XmlMusicRepository(file))

    def test_xml_invalid_integer(self):
        file = self.folder / 'broken.xml'
        file.write_text('''<music_service version="1"><artists>
            <artist id="x"><name>Test</name></artist></artists>
            <tracks/><listeners/><playlists/></music_service>''', encoding='utf-8')
        with self.assertRaises(DataFormatError):
            self.service.load_from(XmlMusicRepository(file))

    def test_missing_file_raises_builtin_error(self):
        with self.assertRaises(FileNotFoundError):
            self.service.load_from(JsonMusicRepository(self.folder / 'absent.json'))

    def test_invalid_load_does_not_delete_current_catalog(self):
        previous = self.service.catalog.to_dict()
        file = self.folder / 'bad.json'
        file.write_text('bad', encoding='utf-8')
        with self.assertRaises(DataFormatError):
            self.service.load_from(JsonMusicRepository(file))
        self.assertEqual(self.service.catalog.to_dict(), previous)


if __name__ == '__main__':
    unittest.main()
