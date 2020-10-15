from copy import deepcopy
import datetime
from unittest import TestCase
from unittest.mock import Mock, patch

from pony.orm import db_session, select, rollback

from vk_api.bot_longpoll import VkBotEvent

from handlers import (
    action_print_available_air_flights,
    action_print_available_arrival_cities,
    action_print_available_departure_cities,
    action_print_context,
)
from generate_ticket import generate_ticket, TEST_ARGUMENTS
from models import Flights, flight_generator

try:
    from settings import (
        DEFAULT_ANSWER, INTENTS,
        SCENARIOS, RAW_EVENT,
        cities,
    )

    from bot import Bot
except ImportError:
    DEFAULT_ANSWER, INTENTS, SCENARIOS, RAW_EVENT = None, None, None, None
    bot = None
    Bot = None

    print('Для работы тестов:\n'
          'файл bot.py должен быть в одной директории с тестами\n'
          'в settings.py завести переменные: \n'
          'RAW_EVENT - полученное текстовое сообщение в формате json')
    exit()


def isolate_db(test_func):
    def wrapper(*args, **kwargs):
        with db_session:
            test_func(*args, **kwargs)
            rollback()

    return wrapper


@db_session
def get_context_data(date):
    """Готовим наш контекст"""
    context = dict()
    query = (select(item for item in Flights if item.date == date)[:1])

    if not query:
        flight_generator(cities)
        query = (select(item for item in Flights if item.date == date)[:1])

    for flight in query:
        cleaned_date = datetime.datetime.strftime(flight.date, '%d-%m-%Y')
        context.update({'departure': flight.departure})
        context.update({'arrival': flight.arrival})
        context.update({'date': cleaned_date})
        context.update({'flight_number': str(flight.flight_number)})
    return context


class TestBot(TestCase):
    RAW_EVENT = {
        'type': 'message_new',
        'object': {'date': 1595599261,
                   'from_id': 92443788,
                   'id': 154, 'out': 0,
                   'peer_id': 92443788,
                   'text': 'Прр',
                   'conversation_message_id': 148,
                   'fwd_messages': [],
                   'important': False,
                   'random_id': 0,
                   'attachments': [],
                   'is_hidden': False},
        'group_id': 197279836
    }
    TODAY = datetime.date.today()

    def test_run(self):
        count = 5
        test_obj = {'a': 1}
        events = [test_obj] * count

        long_poller_mock = Mock(return_value=events)
        long_poller_listen_mock = Mock()
        long_poller_listen_mock.listen = long_poller_mock

        with patch('bot.vk_api.VkApi'):
            with patch('bot.VkBotLongPoll', return_value=long_poller_listen_mock):
                test_bot = Bot('', '')
                test_bot.on_event = Mock()
                test_bot.send_image = Mock()
                test_bot.run()

                test_bot.on_event.assert_called()
                test_bot.on_event.assert_any_call(test_obj)
                assert test_bot.on_event.call_count == count

    CONTEXT = get_context_data(TODAY)

    INPUTS = [
        'привет',
        'ticket',  # 1
        CONTEXT['departure'],  # 2
        CONTEXT['arrival'],  # 3
        CONTEXT['date'],
        CONTEXT['flight_number'],  # 5
        '1',  # 6
        'коммент',  # 7
        'да',  # 8
        'Имя Пользователя',  # 9
        'ticket',  # 1
        CONTEXT['departure'],  # 2
        CONTEXT['arrival'],  # 3
        CONTEXT['date'],  # 4
        '100',  # 5
        CONTEXT['flight_number'],  # 6
        '1',  # 6
        'коммент',  # 7
        'нет',  # 8

    ]

    CONTEXT.update({
        'seats_count': INPUTS[6],
        'comment': INPUTS[7],
        'phone': INPUTS[9]
    })

    EXPECTED_OUTPUTS = [
        DEFAULT_ANSWER,
        SCENARIOS['ticket_order']['steps']["step_1"]['text'] + action_print_available_departure_cities(),
        SCENARIOS['ticket_order']['steps']["step_2"]['text'] + action_print_available_arrival_cities(CONTEXT),
        SCENARIOS['ticket_order']['steps']["step_3"]['text'],
        SCENARIOS['ticket_order']['steps']["step_4"]['text'] + action_print_available_air_flights(CONTEXT),
        SCENARIOS['ticket_order']['steps']["step_5"]['text'],
        SCENARIOS['ticket_order']['steps']["step_6"]['text'],
        SCENARIOS['ticket_order']['steps']["step_7"]['text'] + action_print_context(CONTEXT),
        SCENARIOS['ticket_order']['steps']["step_8"]['text'],
        SCENARIOS['ticket_order']['steps']["step_9"]['text'],
        SCENARIOS['ticket_order']['steps']["step_1"]['text'] + action_print_available_departure_cities(),
        SCENARIOS['ticket_order']['steps']["step_2"]['text'] + action_print_available_arrival_cities(CONTEXT),
        SCENARIOS['ticket_order']['steps']["step_3"]['text'],
        SCENARIOS['ticket_order']['steps']["step_4"]['text'] + action_print_available_air_flights(CONTEXT),
        SCENARIOS['ticket_order']['steps']["step_4"]['failure_text'],
        SCENARIOS['ticket_order']['steps']["step_5"]['text'],
        SCENARIOS['ticket_order']['steps']["step_6"]['text'],
        SCENARIOS['ticket_order']['steps']["step_7"]['text'] + action_print_context(CONTEXT),
        INTENTS[2]['answer'],
    ]

    @isolate_db
    def test_run_ok(self):
        send_mock = Mock()
        api_mock = Mock()
        api_mock.messages.send = send_mock

        events = []
        for input_text in self.INPUTS:
            event = deepcopy(self.RAW_EVENT)
            event['object']['text'] = input_text
            events.append(VkBotEvent(event))

        long_poller_mock = Mock()
        long_poller_mock.listen = Mock(return_value=events)

        with patch('bot.VkBotLongPoll', return_value=long_poller_mock):
            test_bot = Bot('', '')
            test_bot.api = api_mock
            test_bot.send_image = Mock()
            test_bot.run()
        assert send_mock.call_count == len(self.INPUTS)

        real_outputs = []
        for call in send_mock.call_args_list:
            args, kwargs = call
            real_outputs.append(kwargs['message'])
        # для удобной проверки
        # for real, expec in zip(real_outputs, self.EXPECTED_OUTPUTS):
        #     print(real)
        #     print('-' * 50)
        #     print(expec)
        #     print('-' * 50)
        #     print(real == expec)
        #     print('_' * 50)
        assert real_outputs == self.EXPECTED_OUTPUTS

    def test_image_generation(self):
        with open('files/sample@mail.png', 'rb') as avatar_file:
            avatar_mock = Mock()
            avatar_mock.content = avatar_file.read()

        with patch('requests.get', return_value=avatar_mock):
            ticket_file = generate_ticket(**TEST_ARGUMENTS)

        with open('files/ticket_for_tests.png', 'rb') as expected_file:
            expected_bytes = expected_file.read()

        assert ticket_file.read() == expected_bytes
