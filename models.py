#!/usr/bin/env python3
import datetime
import calendar
from itertools import combinations
from random import randint

from pony.orm import (
    Database,
    db_session,
    Json,
    Required,
    select,
)

try:
    from settings import DB_CONFIG, cities
except ImportError:
    DB_CONFIG = None
    cities = None
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
    date = Required(datetime.date)
    # по сути можно отдельным столбцом хранить время вылета
    flight_number = Required(int)


db.generate_mapping(create_tables=True)


def is_it_sub_list(list1, list2):
    """проверяем, является ли список подсписокм другого"""
    return True if [item for item in list1 if item not in list2] == [] else False


def list_dif(list1, list2):
    return [item for item in list1 if item not in list2]


def generate_dates(count):
    """
    генерируем список дат до конца текущего месяца и count -1 следующих месяцев
    count - число месяцев для генерации
    :return: list
    """
    date_list = list()
    for delta_month in range(count):
        today = datetime.datetime.now()
        start_date = datetime.date(today.year, today.month + delta_month, day=1)
        last_day_of_month = calendar.monthrange(start_date.year, start_date.month)[1]

        if start_date.month == today.month:
            start = today.day
        else:
            start = 1

        for day in range(start, last_day_of_month + 1):
            date_list.append(datetime.date(start_date.year, start_date.month, day))
    return date_list


def generate_flight_numbers():
    """Возвращаем случайное число от 1 до 1000"""
    number_of_flights = randint(1, 5)
    numbers = []
    for number in range(number_of_flights):
        numbers.append(randint(1, 1000))
    return numbers


def generate_city_pairs(list_of_cities):
    """Генерация списка кортежей из городов"""
    return [comb for comb in combinations(list_of_cities, 2)]


@db_session
def generate_flights(departure, arrival, date, flight_number):
    """
    Генерация записей рейсов в БД
    :param departure: город вылета
    :param arrival: город посадки
    :param date:дата
    :param flight_number: номер рейса
    :return:
    """
    Flights(
        departure=departure,
        arrival=arrival,
        date=date,
        flight_number=flight_number
    )


def generate_pass(pass_percent):
    """Генератор прописка шага"""
    random_number = randint(1, 100 // pass_percent)
    return True if random_number == 100 // pass_percent else False


@db_session
def get_dates_from_db():
    """Возвращаем все даты"""
    dates = []
    # query = db.select('date FROM Flights')
    query_ORM = select(item.date for item in Flights)
    for date in query_ORM:
        dates.append(date) if date not in dates else None
    return dates


def for_months(month_count):
    """Декоратор для проверки необходимости обновления"""

    def decorator(func):
        def wrapper(*args):
            print('проверяем, нужна ли проверка...')
            date_list = generate_dates(month_count)
            date_list_db = get_dates_from_db()
            if is_it_sub_list(date_list, date_list_db):
                print('обновлять не нужно!')
                return
            else:
                dif_date_list = list_dif(date_list, date_list_db)
                func(*args, date_list=dif_date_list)

        return wrapper

    return decorator


@for_months(2)
def flight_generator(list_of_cities, date_list):
    """Генерируем наши рейсы
        pass_probability - вероятность пропуска шага, чтоб немного радомизировать таблицу
    """
    city_pairs = generate_city_pairs(list_of_cities=list_of_cities)
    flight_numbers = generate_flight_numbers()
    pass_probability = 30
    count = 0
    for city_pair in city_pairs:
        if not generate_pass(pass_probability):
            for date in date_list:
                if not generate_pass(pass_probability):
                    for number in flight_numbers:
                        if not generate_pass(pass_probability):
                            generate_flights(departure=city_pair[0], arrival=city_pair[1], date=date,
                                             flight_number=number)
                            count += 1
    print(f'в базу {db} добавлено {count} записей')


if __name__ == '__main__':
    pass
