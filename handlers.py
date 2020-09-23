import operator
import re
from datetime import datetime

from generate_ticket import generate_ticket
from models import Flights


try:
    from settings import flights
except ImportError:
    settings = None
    flights = None

    print('Для работы бота нужно:\n'
          'создать файл settings.py\n'
          'в settings.py завести переменные: \n'
          'flights - словарь словарей (структура будет описана позже)')
    exit()

re_date = re.compile(r"([0-3][0-9])-([0-1][0-9])-(20\d\d)")

re_name = re.compile(r"(\w{2,}) (\w{2,})")


def find_city_by_patterns(user_input):
    """
    делаем из инпута пользователя шаблон и сравниваем, с нашим списком городов
    :param user_input: город введенный пользователем
    :return: подходящий город str или bool
    """
    cities = [key for key in flights.keys()]
    slicer = int(len(user_input) // 1.4)

    pattern = f'{user_input[:slicer]}'
    re_city_pattern = re.compile(pattern)

    for city in cities:
        if re.findall(re_city_pattern, city):
            return city
    else:
        return False


def handle_departure_city(text, context):
    """
    проверяем введенный город в списке доступных и добавляем в контекст
    :param text: ввод от пользоваетля
    :param context: для прохождения сценария
    :return: bool
    """
    text = text.upper()
    if text in flights.keys():
        context['departure'] = text
        return True
    else:
        text = find_city_by_patterns(text)
        if text:
            context['departure'] = text
            return True
        else:
            return False


def handle_arrival_city(text, context):
    """
    проверяем введенный город в списке доступных и добавляем в контекст
    :param text: ввод от пользоваетля
    :param context: для прохождения сценария
    :return: bool
    """
    text = text.upper()
    if text in flights[context['departure']].keys():
        context['arrival'] = text
        return True
    else:
        text = find_city_by_patterns(text)
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


def nearest_departure_date(dict_path, users_date, count=5):
    """
    если введенной пользователем даты нет, то предлагаем count ближайших
    :param dict_path: пусть в flights
    :param users_date: введенная пользователем дата
    :param count: число ближайших дат
    :return: готовый текст для печати состоящий из count дат
    """
    dateset_list = [datetime.strptime(date, '%d-%m-%Y') for date in dict_path.keys()]
    users_date = datetime.strptime(users_date, '%d-%m-%Y')

    count = len(dict_path.keys()) if len(dict_path.keys()) < count else count

    dates = sorted(
        [(date_from_list, abs((date_from_list - users_date)).days) for date_from_list in dateset_list],
        key=operator.itemgetter(1), reverse=False)[:count]

    result = '\nБлижайшие даты:\n'
    for date in dates:
        result += f'{date[0].strftime("%d-%m-%Y")}\n'
    return result


def handle_flight_date(text, context):
    """
    проверяем введенную дату в списке доступных и добавляем в контекст
    :param text: ввод от пользоваетля
    :param context: для прохождения сценария
    :return: bool
    """
    if not date_format(text):
        return False
    if text in flights[context['departure']][context['arrival']].keys():
        context['date'] = text
        return True
    else:
        # здесь явно костыль, но другого способа не придумал
        context['extra_content'] = nearest_departure_date(
            dict_path=flights[context['departure']][context['arrival']], users_date=text)
        return False


def handle_flight_number(text, context):
    """
    проверяем номер рейса и добавляем в контекст
    :param text: ввод от пользоваетля
    :param context: для прохождения сценария
    :return: bool
    """
    if text in flights[context['departure']][context['arrival']][context['date']]:
        context['flight_number'] = text
        return True
    else:
        return False


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

def popular_cities(dict_path, count=5):
    """
    возвращаем список городов с самым большим числом авиасообщений
    :param dict_path: путь в flights
    :param count: число городов
    :return: list of tuples (city_name, count_of_flights)
    """
    if len(dict_path.keys()) < count:
        count = len(dict_path.keys())

    return sorted(
        [(key, len(dict_path[key])) for key in dict_path.keys()],
        key=operator.itemgetter(1), reverse=True)[:count]


def action_print_available_departure_cities():
    """
    выводим пользователю достпные города для вылета
    :return: строка с названиями городов -> str
    """
    result = ''
    cities = popular_cities(flights)
    for city in cities:
        result += f'{city[0]} - вылеты в {city[1]} городов\n'
    return f"\nБольше всего рейсов из:\n{result}"


def action_print_available_arrival_cities(context):
    """
    выводим пользователю достпные города для прилета
    :param context: ввод от пользователя
    :return: строка с названиями городов -> str
    """
    result = ''
    cities = popular_cities(flights[context['departure']], count=3)
    for city in cities:
        result += f'В {city[0]} - {city[1]} рейсов\n'
    return f"\nиз {context['departure']} больше всего рейсов в :\n{result}"


def action_print_available_dates(context):
    """
    выводим пользователю 5 ближайших дат
    :param context: ввод от пользователя
    :return: список дат -> str
    """
    result = ''
    for date in flights[context['departure']][context['arrival']]:
        result += date + '\n'
    return f'\nДоступные даты:\n{result}'


def action_print_available_air_flights(context):
    """
     выводим пользователю 5 рейсов на выбранную дату
    :param context: ввод от пользователя
    :return: список рейсов -> str
    """
    result = ''
    for air_flight in flights[context['departure']][context['arrival']][context['date']]:
        result += air_flight + '\n'
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
            email='sample@mail.com'
        )
    except KeyError:
        print('что не так с контекстом')


if __name__ == "__main__":
    pass
