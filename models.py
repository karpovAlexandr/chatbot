#!/usr/bin/env python3

from pony.orm import (
    Database,
    Required,
    Json,
)

try:
    from settings import DB_CONFIG
except ImportError:
    DB_CONFIG = None
    print(
        'для подключения БД в файле settings.py нужен словарь DB_CONFIG\n'
        'с ключами: provider, user, host, database, password (опционально)'
    )

db = Database()
db.bind(**DB_CONFIG)


class UserState(db.Entity):
    """Модель с user_state'ом пользователя"""
    user_id = Required(str, unique=True)
    scenario_name = Required(str)
    step_name = Required(str)
    context = Required(Json)


class Ticket(db.Entity):
    """Билеты"""
    departure = Required(str)
    arrival = Required(str)
    date = Required(str)
    flight_number = Required(int)
    seats_count = Required(int)
    comment = Required(str)


class Flights(db.Entity):
    """Модель рейсов"""
    departure = Required(str)
    arrival = Required(str)
    date = Required(str)
    flight_number = Required(int)


db.generate_mapping(create_tables=True)
