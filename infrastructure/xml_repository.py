"""Реализация MusicRepository для XML."""
from pathlib import Path
import xml.etree.ElementTree as ET

from domain.exceptions import DataFormatError, MusicServiceError, ValidationError
from domain.models import Catalog
from domain.repository import MusicRepository

class XmlMusicRepository(MusicRepository):
    def __init__(self, path: Path):
        self.path = Path(path)

    def save(self, catalog: Catalog) -> None:
        data = catalog.to_dict()
        root = ET.Element('music_service', {'version': '1'})
        for section_name, tag_name, fields in (
            ('artists', 'artist', ('name',)),
            ('tracks', 'track', ('title', 'genre')),
            ('listeners', 'listener', ('username',)),
            ('playlists', 'playlist', ('name',)),
        ):
            section = ET.SubElement(root, section_name)
            for row in data[section_name]:
                attrs = {'id': str(row['id'])}
                if tag_name == 'track':
                    attrs.update({'artist_id': str(row['artist_id']),
                                  'duration_seconds': str(row['duration_seconds'])})
                if tag_name == 'playlist':
                    attrs['owner_id'] = str(row['owner_id'])
                element = ET.SubElement(section, tag_name, attrs)
                for field_name in fields:
                    ET.SubElement(element, field_name).text = row[field_name]
                if tag_name == 'playlist':
                    tracks = ET.SubElement(element, 'track_ids')
                    for track_id in row['track_ids']:
                        ET.SubElement(tracks, 'track', {'id': str(track_id)})
        ET.indent(root, space='  ')
        self.path.parent.mkdir(parents=True, exist_ok=True)
        ET.ElementTree(root).write(self.path, encoding='utf-8', xml_declaration=True)

    def load(self) -> Catalog:
        try:
            root = ET.parse(self.path).getroot()
        except (ET.ParseError, UnicodeError) as error:
            raise DataFormatError(f'Некорректный XML: {error}') from error
        if root.tag != 'music_service' or root.get('version') != '1':
            raise DataFormatError("Требуется тег <music_service version='1'>")
        try:
            for name in ('artists', 'tracks', 'listeners', 'playlists'):
                if root.find(name) is None:
                    raise DataFormatError(f'Отсутствует раздел XML: {name}')
            data = {'artists': [], 'tracks': [], 'listeners': [], 'playlists': []}
            for element in root.findall('./artists/artist'):
                data['artists'].append({'id': int(element.attrib['id']),
                                        'name': _required_text(element, 'name')})
            for element in root.findall('./tracks/track'):
                data['tracks'].append({'id': int(element.attrib['id']),
                                       'artist_id': int(element.attrib['artist_id']),
                                       'duration_seconds': int(element.attrib['duration_seconds']),
                                       'title': _required_text(element, 'title'),
                                       'genre': _required_text(element, 'genre')})
            for element in root.findall('./listeners/listener'):
                data['listeners'].append({'id': int(element.attrib['id']),
                                          'username': _required_text(element, 'username')})
            for element in root.findall('./playlists/playlist'):
                if element.find('track_ids') is None:
                    raise DataFormatError('У плейлиста отсутствует раздел track_ids')
                data['playlists'].append({'id': int(element.attrib['id']),
                                          'owner_id': int(element.attrib['owner_id']),
                                          'name': _required_text(element, 'name'),
                                          'track_ids': [int(t.attrib['id']) for t in
                                                        element.findall('./track_ids/track')]})
            return Catalog.from_dict(data)
        except (KeyError, ValueError, TypeError, MusicServiceError) as error:
            raise DataFormatError(f'Неверные данные XML: {error}') from error


def _required_text(element: ET.Element, name: str) -> str:
    child = element.find(name)
    if child is None or child.text is None or not child.text.strip():
        raise ValidationError(f'Отсутствует поле <{name}>')
    return child.text
