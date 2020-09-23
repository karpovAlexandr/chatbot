from copy import deepcopy
from unittest import TestCase
from unittest.mock import patch, Mock

from pony.orm import db_session, rollback

from generate_ticket import generate_ticket, TEST_ARGUMENTS

from handlers import (
    action_print_available_departure_cities,
    action_print_available_arrival_cities,
    action_print_available_air_flights,
    action_print_context,
    action_print_available_dates,
)

from vk_api.bot_longpoll import VkBotEvent

try:
    import settings
    from bot import Bot
except ImportError:
    settings = None
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

    INPUTS = [
        'привет',
        'ticket',  # 1
        'МОСКВА',  # 2
        'САНКТ-ПЕТЕРБУРГ',  # 3
        '03-10-2020',  # 4  TODO Дату хорошо было бы задавать относительную, чтобы со временем она не стала
        # TODO датой из прошлого (но тут проблема и с расписанием, обсудим её в лмс)
        '1',  # 5
        '1',  # 6
        'коммент',  # 7
        'да',  # 8
        'Имя Пользователя',  # 9
        'ticket',  # 1
        'МОСКВА',  # 2
        'САНКТ-ПЕТЕРБУРГ',  # 3
        '03-10-2020',  # 4
        '100',  # 5
        '1',  # 6
        '1',  # 6
        'коммент',  # 7
        'нет',  # 8

    ]

    CONTEXT = {
        'departure': INPUTS[2],
        'arrival': INPUTS[3],
        'date': INPUTS[4],
        'flight_number': INPUTS[5],
        'seats_count': INPUTS[6],
        'comment': INPUTS[7],
        'phone': INPUTS[9]

    }

    EXPECTED_OUTPUTS = [
        settings.DEFAULT_ANSWER,
        settings.SCENARIOS['ticket_order']['steps']["step_1"]['text'] + action_print_available_departure_cities(),
        settings.SCENARIOS['ticket_order']['steps']["step_2"]['text'] + action_print_available_arrival_cities(CONTEXT),
        settings.SCENARIOS['ticket_order']['steps']["step_3"]['text'],
        settings.SCENARIOS['ticket_order']['steps']["step_4"]['text'] + action_print_available_air_flights(CONTEXT),
        settings.SCENARIOS['ticket_order']['steps']["step_5"]['text'],
        settings.SCENARIOS['ticket_order']['steps']["step_6"]['text'],
        settings.SCENARIOS['ticket_order']['steps']["step_7"]['text'] + action_print_context(CONTEXT),
        settings.SCENARIOS['ticket_order']['steps']["step_8"]['text'],
        settings.SCENARIOS['ticket_order']['steps']["step_9"]['text'],
        # TODO Тут несовпадение начинается
        # TODO
        # Хорошие новости!
        # с Вами свяжутся по номеру Имя Пользователя
        # --------------------------------------------------
        # Хорошие новости!
        # с Вами свяжутся по номеру {phone}  TODO Надо вот эту переменную заполнить при помощи format
        # --------------------------------------------------
        # False
        settings.SCENARIOS['ticket_order']['steps']["step_1"]['text'] + action_print_available_departure_cities(),
        settings.SCENARIOS['ticket_order']['steps']["step_2"]['text'] + action_print_available_arrival_cities(CONTEXT),
        settings.SCENARIOS['ticket_order']['steps']["step_3"]['text'],
        settings.SCENARIOS['ticket_order']['steps']["step_4"]['text'] + action_print_available_air_flights(CONTEXT),
        settings.SCENARIOS['ticket_order']['steps']["step_4"]['failure_text'],
        settings.SCENARIOS['ticket_order']['steps']["step_5"]['text'],
        settings.SCENARIOS['ticket_order']['steps']["step_6"]['text'],
        settings.SCENARIOS['ticket_order']['steps']["step_7"]['text'] + action_print_context(CONTEXT),
        settings.INTENTS[2]['answer'],
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
        for real, expec in zip(real_outputs, self.EXPECTED_OUTPUTS):
            print(real)
            print('-' * 50)
            print(expec)
            print('-' * 50)
            print(real == expec)
            print('_' * 50)
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
