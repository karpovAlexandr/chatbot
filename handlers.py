import operator
import re
import datetime

from pony.orm import count, db_session, select

from chatbot.generate_ticket import generate_ticket
from chatbot.models import Flights


re_date = re.compile(r"([0-3][0-9])-([0-1][0-9])-(20\d\d)")

re_name = re.compile(r"(\w{2,}) (\w{2,})")


def find_city_by_patterns(user_input, cities):
    """
    делаем из инпута пользователя шаблон и сравниваем, с нашим списком городов
    :param cities: список городов
    :param user_input: город введенный пользователем
    :return: подходящий город str или bool
    """

    slicer = int(len(user_input) // 1.4)
    pattern = f'{user_input[:slicer]}'
    re_city_pattern = re.compile(pattern)

    for city in cities:
        if re.findall(re_city_pattern, city):
            return city
    else:
        return False


@db_session
def handle_departure_city(text, context):
    """
    проверяем введенный город в списке доступных и добавляем в контекст
    :param text: ввод от пользоваетля
    :param context: для прохождения сценария
    :return: bool
    """

    # SQL
    # SELECT DISTINCT departure
    # FROM flights;

    cities_queryset = select((item.departure,) for item in Flights)[:]

    text = text.upper()
    if text in cities_queryset:
        context['departure'] = text
        return True
    else:
        text = find_city_by_patterns(text, cities_queryset)
        if text:
            context['departure'] = text
            return True
        else:
            return False


@db_session
def handle_arrival_city(text, context):
    """
    проверяем введенный город в списке доступных и добавляем в контекст
    :param text: ввод от пользоваетля
    :param context: для прохождения сценария
    :return: bool
    """

    # SQL
    # SELECT DISTINCT arrival
    # FROM flights
    # WHERE departure = context['departure'];

    cities_queryset = select((item.arrival,) for item in Flights if item.departure == context['departure'])[:]

    text = text.upper()
    if text in cities_queryset:
        context['arrival'] = text
        return True
    else:
        text = find_city_by_patterns(text, cities_queryset)
        if text:
            context['arrival'] = text
            return True
        else:
            return False


def date_format(text):
    """
    проверяем формат введенной даты и добавляем в контекст
    :param text: ввод от пользоваетля
    :return: bool
    """
    match = re.match(re_date, text)
    if match:
        return True
    else:
        return False


def nearest_departure_date(dates, users_date, date_count=5):
    """
    генерируем строку из дат, близжайших к user_date и состоящий из date_count элементов
    :param dates: список дат
    :param users_date: введенная пользователем дата -> datetime.date
    :param date_count: число ближайших дат
    :return: строка с датами
    """

    date_count = len(dates) if len(dates) < date_count else date_count

    dates_sorted = sorted(
        [(date_from_list, abs((date_from_list - users_date)).days) for date_from_list in dates],
        key=operator.itemgetter(1), reverse=False)[:date_count]
    dates_sorted.sort()
    result = '\nБлижайшие даты:\n'
    for date in dates_sorted:
        result += f'{date[0].strftime("%d-%m-%Y")}\n'
    return result


def handle_flight_date(text, context):
    """
    проверяем введенную дату в списке доступных и добавляем в контекст
    :param text: ввод от пользоваетля
    :param context: для прохождения сценария
    :return: bool
    """

    # SQL
    # SELECT date
    # FROM flights
    # WHERE departure = context['departure']
    # and arrival = context['arrival']
    # and date >= CURDATE();

    today = datetime.date.today()
    if not date_format(text):
        return False

    user_date = date_to_string(text)

    if user_date < today:
        context['extra_content'] = '\nнельзя улететь в прошлое :/'
        return False

    date_queryset = select(
        (item.date,) for item in Flights if
        item.departure == context['departure']
        and item.arrival == context['arrival']
        and item.date >= today)[:]

    if user_date in date_queryset:
        context['date'] = text
        return True
    else:
        # здесь явно костыль, но другого способа не придумал
        context['extra_content'] = nearest_departure_date(
            dates=date_queryset, users_date=user_date)
        return False


def date_to_string(text):
    """Превращаем строку с дату"""
    date = datetime.datetime.strptime(text, '%d-%m-%Y')
    date = datetime.date(year=date.year, month=date.month, day=date.day)
    return date


def handle_flight_number(text, context):
    """
    проверяем номер рейса и добавляем в контекст
    :param text: ввод от пользоваетля
    :param context: для прохождения сценария
    :return: bool
    """

    # SQL
    # SELECT date
    # FROM flights
    # WHERE departure = context['departure']
    # and arrival = context['arrival']
    # and date = context['date'];

    user_date = date_to_string(context['date'])
    seats_query_set = select(
        (item.flight_number,) for item in Flights if item.departure == context['departure']
        and item.arrival == context['arrival']
        and item.date == user_date
    )[:]
    try:
        if int(text) in seats_query_set:
            context['flight_number'] = text
            return True
        else:
            return False
    except ValueError:
        pass


def handle_seats(text, context):
    """
    проверяем количество мест (от 1 до 5 включительно) и добавляем в контекст
    :param text: ввод от пользоваетля
    :param context: для прохождения сценария
    :return: bool
    """
    try:
        text = int(text)
    except ValueError:
        return False

    if text in range(1, 6):
        context['seats_count'] = text
        return True
    else:
        return False


def handle_comment(text, context):
    """
    проверяем длинну комментария и добавляем в контекст
    :param text: ввод от пользоваетля
    :param context: для прохождения сценария
    :return: bool
    """
    if len(text) < 100:
        context['comment'] = text
        return True
    else:
        return False


def handle_confirm(text, context):
    """
    проверяем ответ от пользователя и добавляем в контекст
    :param text: ввод от пользоваетля
    :param context: для прохождения сценария
    :return: bool
    """
    if text.lower() == 'да':
        context['is_correct'] = True
        return True
    elif text.lower() == 'нет':
        context['is_correct'] = False
        return True
    else:
        return False


def handle_name(text, context):
    """
    проверяем имя
    :param text: ввод от пользоваетля
    :param context: для прохождения сценария
    :return: bool
    """
    name = re.findall(re_name, text)
    if name:
        context['name'] = f'{name[0][0]} {name[0][1]}'.upper()
        return True
    else:
        return False


def handle_phone(text, context):
    """
    записываем телефон в контекст, без какой либо проверки
    :param text: ввод от пользоваетля
    :param context: для прохождения сценария
    :return: bool
    """
    if text:
        context['phone'] = text
        return True
    else:
        return False


# по аналогии с хэндлерами сделал в сценарии "действие" перед каждым шагом
# в основном это вывод информации на экран, скорее всего можно реализовать практичнее и проще

def popular_cities(dict_path, city_count=5):
    """
    возвращаем список городов с самым большим числом авиасообщений
    :param dict_path: путь в flights
    :param city_count: число городов
    :return: list of tuples (city_name, count_of_flights)
    """
    if len(dict_path.keys()) < city_count:
        city_count = len(dict_path.keys())

    return sorted(
        [(key, len(dict_path[key])) for key in dict_path.keys()],
        key=operator.itemgetter(1), reverse=True)[:city_count]


@db_session
def action_print_available_departure_cities():
    """
    выводим пользователю достпные города для вылета
    :return: строка с названиями городов -> str
    """

    # SQL:
    # SELECT departure, count(DISTINCT arrival)
    # FROM flights
    # GROUP BY departure
    # ORDER BY count(DISTINCT arrival) DESC
    # LIMIT 5;

    queryset = select(
        (item.departure, count(item.arrival))
        for item in Flights).order_by(-2)[:5]
    result = ''
    for city in queryset:
        result += f'{city[0]} - вылеты в {city[1]} городов\n'
    return f"\nБольше всего рейсов из:\n{result}"


@db_session
def action_print_available_arrival_cities(context):
    """
    выводим пользователю достпные города для прилета
    :param context: ввод от пользователя
    :return: строка с названиями городов -> str
    """

    # SQL:
    # SELECT arrival, count(arrival)
    # FROM flights
    # WHERE departure = '{context['departure']}'
    # GROUP BY arrival
    # ORDER BY count(arrival)
    # DESC LIMIT 5;

    query = select((item.arrival, count(item))
                   for item in Flights
                   if item.departure == context['departure']).order_by(-2)[:3]
    result = ''
    for city in query:
        result += f'В {city[0]} - {city[1]} рейсов\n'
    return f"\nиз {context['departure']} больше всего рейсов в :\n{result}"


@db_session
def action_print_available_dates(context):
    """
    выводим пользователю 5 ближайших дат
    :param context: ввод от пользователя
    :return: список дат -> str
    """

    # SQL:
    # SELECT date
    # FROM flights
    # WHERE departure = 'context['departure']'
    # AND arrival = context['arrival]
    # ORDER BY date DESC
    # LIMIT 5;

    dates_query = select((item.date,)
                         for item in Flights
                         if item.departure == context['departure']
                         and item.arrival == context['arrival'])[:5]
    dates_query.sort()
    result = ''
    for date in dates_query:
        date = date.strftime('%d-%m-%Y')
        result += date + '\n'
    return f'\nДоступные даты:\n{result}'


@db_session
def action_print_available_air_flights(context):
    """
     выводим пользователю 5 рейсов на выбранную дату
    :param context: ввод от пользователя
    :return: список рейсов -> str
    """

    # SQL
    # SELECT date
    # FROM flights
    # WHERE departure = context['departure']
    # and arrival = context['arrival']
    # and date = context['date'];

    user_date = date_to_string(context['date'])
    query_flight_numbers = select((item.flight_number,) for item in Flights
                                  if item.departure == context['departure']
                                  and item.arrival == context['arrival']
                                  and item.date == user_date)[:5]

    result = ''
    for air_flight in query_flight_numbers:
        result += str(air_flight) + '\n'
    return f'\nДоступные рейсы:\n{result}'


def action_print_context(context):
    """
    Выводим пользователю контекст
    :param context: ввод от пользователя
    :return: список -> str
    """
    result = f'\nВылет: {context["departure"]}\n' \
             f'Прибытие: {context["arrival"]}\n' \
             f'Дата: {context["date"]}\n' \
             f'Номер рейса: {context["flight_number"]}\n' \
             f'Количество мест: {context["seats_count"]}\n' \
             f'Комментарий: {context["comment"]}'
    return result


def action_pass(context):
    """
    экшен - заглушка
    :return: пустую строку
    """
    return ""


def action_exit():
    """
    экшен - для выхода
    :return: пустую строку
    """
    return ""


def generate_ticket_handler(text, context):
    """
    Ренерируем билет из контекста
    :param text: ввод от пользователя
    :param context: контекст
    :return: generate_ticket
    """
    try:
        return generate_ticket(
            name=context['name'],
            departure=context['departure'],
            arrival=context['arrival'],
            date=context['date'],
            email='sample@mail.com',
            flight_number=context['flight_number'],
        )
    except KeyError:
        print('что не так с контекстом', text)


if __name__ == "__main__":
    pass
