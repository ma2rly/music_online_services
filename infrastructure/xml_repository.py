"""Репозиторий для сериализации и десериализации XML"""

from __future__ import annotations

from pathlib import Path
from typing import Any
import xml.etree.ElementTree as ET

from domain.exceptions import DataFormatError, MusicServiceError, ValidationError
from domain.models import Catalog
from domain.repository import MusicRepository


# Поля чисел и логических значений хранятся в атрибутах XML
# Остальные поля помещаются в отдельные текстовые элементы
XML_FIELDS: dict[str, tuple[str, dict[str, type[Any]], tuple[str, ...]]] = {
    'artists': ('artist', {'id': int}, ('name',)),
    'tracks': ('track', {'id': int, 'artist_id': int,
                       'duration_seconds': int, 'album_id': int},
               ('title', 'genre')),
    'listeners': ('listener', {'id': int}, ('username',)),
    'playlists': ('playlist', {'id': int, 'owner_id': int}, ('name',)),
    'albums': ('album', {'id': int, 'artist_id': int, 'label_id': int}, ('title',)),
    'genres': ('genre', {'id': int}, ('name',)),
    'labels': ('label', {'id': int}, ('name',)),
    'plans': ('plan', {'id': int, 'monthly_fee': int}, ('name',)),
    'subscriptions': ('subscription', {'id': int, 'listener_id': int,
                                     'plan_id': int, 'active': bool}, ()),
    'favorites': ('favorite', {'id': int, 'listener_id': int,
                             'track_id': int}, ()),
    'reviews': ('review', {'id': int, 'listener_id': int, 'track_id': int,
                         'rating': int}, ('text',)),
    'history': ('record', {'id': int, 'listener_id': int, 'track_id': int,
                         'listened_seconds': int}, ()),
}

OPTIONAL_FIELDS = frozenset(('album_id', 'label_id'))


class XmlMusicRepository(MusicRepository):
    """Читает и записывает каталог в XML с проверкой структуры"""

    def __init__(self, path: Path) -> None:
        self.path = Path(path)

    def save(self, catalog: Catalog) -> None:
        root = ET.Element('music_service', {'version': '2'})
        data = catalog.to_dict()
        for section_name, (tag, attributes, text_fields) in XML_FIELDS.items():
            section = ET.SubElement(root, section_name)
            for row in data[section_name]:
                attrs = {
                    name: ('true' if row[name] else 'false')
                    if kind is bool else str(row[name])
                    for name, kind in attributes.items()
                    if row.get(name) is not None
                }
                element = ET.SubElement(section, tag, attrs)
                for name in text_fields:
                    ET.SubElement(element, name).text = row[name]
                if section_name == 'playlists':
                    tracks = ET.SubElement(element, 'track_ids')
                    for track_id in row['track_ids']:
                        ET.SubElement(tracks, 'track', {'id': str(track_id)})
        ET.indent(root, space='  ')
        self.path.parent.mkdir(parents=True, exist_ok=True)
        ET.ElementTree(root).write(self.path, encoding='utf-8',
                                   xml_declaration=True)

    def load(self) -> Catalog:
        try:
            root = ET.parse(self.path).getroot()
        except (ET.ParseError, UnicodeError) as error:
            raise DataFormatError(f'Некорректный XML: {error}') from error
        if root.tag != 'music_service' or root.get('version') not in ('1', '2'):
            raise DataFormatError('Неподдерживаемый корень или версия XML')
        data: dict[str, list[dict[str, Any]]] = {}
        try:
            for section_name, (tag, attributes, text_fields) in XML_FIELDS.items():
                section = root.find(section_name)
                if section is None:
                    if root.get('version') == '1' and section_name not in (
                        'artists', 'tracks', 'listeners', 'playlists'
                    ):
                        data[section_name] = []
                        continue
                    raise DataFormatError(f'Отсутствует раздел XML: {section_name}')
                rows: list[dict[str, Any]] = []
                for element in section.findall(tag):
                    row: dict[str, Any] = {}
                    for name, kind in attributes.items():
                        raw = element.get(name)
                        if raw is None:
                            if name in OPTIONAL_FIELDS:
                                row[name] = None
                                continue
                            if name == 'active' and root.get('version') == '1':
                                row[name] = True
                                continue
                            raise DataFormatError(f'Отсутствует атрибут {name}')
                        if kind is bool:
                            if raw not in ('true', 'false'):
                                raise DataFormatError('Некорректный статус подписки')
                            row[name] = raw == 'true'
                        else:
                            row[name] = int(raw)
                    for name in text_fields:
                        row[name] = _required_text(element, name)
                    if section_name == 'playlists':
                        if element.find('track_ids') is None:
                            raise DataFormatError(
                                'У плейлиста отсутствует раздел track_ids'
                            )
                        row['track_ids'] = [int(x.attrib['id']) for x in
                                            element.findall('./track_ids/track')]
                    rows.append(row)
                data[section_name] = rows
            return Catalog.from_dict(data)
        except (KeyError, ValueError, TypeError, MusicServiceError) as error:
            raise DataFormatError(f'Неверные данные XML: {error}') from error


def _required_text(element: ET.Element, name: str) -> str:
    child = element.find(name)
    if child is None or child.text is None or not child.text.strip():
        raise ValidationError(f'Отсутствует поле <{name}>')
    return child.text
