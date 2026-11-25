"""Дополнительные сущности музыкального онлайн-сервиса"""

from __future__ import annotations

from dataclasses import dataclass

from domain.exceptions import ValidationError


def positive_id(value: int, label: str = 'ID') -> None:
    """Проверяет положительный целочисленный идентификатор"""
    if type(value) is not int or value <= 0:
        raise ValidationError(f'{label} должен быть положительным целым числом')


def nonempty_text(value: str, label: str) -> None:
    """Проверяет обязательное текстовое поле"""
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f'Поле «{label}» не должно быть пустым')


@dataclass
class Album:
    """Музыкальный альбом определённого исполнителя"""

    id: int
    title: str
    artist_id: int
    label_id: int | None = None

    def __post_init__(self) -> None:
        positive_id(self.id)
        nonempty_text(self.title, 'название альбома')
        positive_id(self.artist_id, 'ID исполнителя')
        if self.label_id is not None:
            positive_id(self.label_id, 'ID лейбла')


@dataclass
class Genre:
    """Музыкальный жанр"""

    id: int
    name: str

    def __post_init__(self) -> None:
        positive_id(self.id)
        nonempty_text(self.name, 'жанр')


@dataclass
class RecordLabel:
    """Звукозаписывающая компания"""

    id: int
    name: str

    def __post_init__(self) -> None:
        positive_id(self.id)
        nonempty_text(self.name, 'лейбл')


@dataclass
class SubscriptionPlan:
    """Тарифный план сервиса"""

    id: int
    name: str
    monthly_fee: int

    def __post_init__(self) -> None:
        positive_id(self.id)
        nonempty_text(self.name, 'тариф')
        if type(self.monthly_fee) is not int or self.monthly_fee < 0:
            raise ValidationError('Стоимость тарифа не может быть отрицательной')


@dataclass
class Subscription:
    """Подписка пользователя на тариф"""

    id: int
    listener_id: int
    plan_id: int
    active: bool = True

    def __post_init__(self) -> None:
        positive_id(self.id)
        positive_id(self.listener_id, 'ID пользователя')
        positive_id(self.plan_id, 'ID тарифа')
        if type(self.active) is not bool:
            raise ValidationError('Статус подписки должен быть логическим значением')


@dataclass
class Favorite:
    """Отметка понравившегося трека"""

    id: int
    listener_id: int
    track_id: int

    def __post_init__(self) -> None:
        positive_id(self.id)
        positive_id(self.listener_id, 'ID пользователя')
        positive_id(self.track_id, 'ID трека')


@dataclass
class Review:
    """Оценка и текстовый отзыв пользователя о треке"""

    id: int
    listener_id: int
    track_id: int
    rating: int
    text: str

    def __post_init__(self) -> None:
        positive_id(self.id)
        positive_id(self.listener_id, 'ID пользователя')
        positive_id(self.track_id, 'ID трека')
        if type(self.rating) is not int or not 1 <= self.rating <= 5:
            raise ValidationError('Оценка должна быть целым числом от 1 до 5')
        nonempty_text(self.text, 'отзыв')


@dataclass
class ListeningRecord:
    """Запись о прослушивании композиции"""

    id: int
    listener_id: int
    track_id: int
    listened_seconds: int

    def __post_init__(self) -> None:
        positive_id(self.id)
        positive_id(self.listener_id, 'ID пользователя')
        positive_id(self.track_id, 'ID трека')
        positive_id(self.listened_seconds, 'Прослушанные секунды')
