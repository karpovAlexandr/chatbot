#!/usr/bin/env python3
import logging

import requests
import vk_api
from pony.orm import db_session, CacheIndexError, OperationWithDeletedObjectError
from vk_api.bot_longpoll import VkBotLongPoll
from vk_api.bot_longpoll import VkBotEventType
from vk_api.utils import get_random_id

import handlers
from models import UserState, Ticket

try:
    from settings import TOKEN
    from settings import GROUP_ID
    from settings import SCENARIOS
    from settings import INTENTS
    from settings import DEFAULT_ANSWER
except ImportError:
    settings = None
    TOKEN = None
    GROUP_ID = None
    SCENARIOS = None
    INTENTS = None
    DEFAULT_ANSWER = None
    print('Для работы бота нужно:\n'
          'создать файл settings.py\n'
          'в settings.py завести переменные: \n'
          'TOKEN - токен от VK (с типом str) \n'
          'GROUP_ID - id группы в VK (с типом int)')
    exit()

log = logging.getLogger('bot')
date_format = '%d-%m-%Y %H:%M'


def conf_logging():
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt=date_format))
    stream_handler.setLevel(logging.INFO)
    log.addHandler(stream_handler)

    file_handler = logging.FileHandler(filename='bot_logs.log', encoding='utf-8')
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt=date_format))
    file_handler.setLevel(logging.DEBUG)
    log.addHandler(file_handler)

    log.setLevel(logging.DEBUG)


class Bot:
    """
    Бот для заказа авиабилетов для vk.com
    use python ver 3.8.2
    """

    def __init__(self, group, token_api):
        """
        :param group: group id из группы в vk
        :param token_api: токен для группы {group_id} из vk
        """
        self.group_id = group
        self.token = token_api
        self.vk = vk_api.VkApi(token=self.token)
        self.long_poller = VkBotLongPoll(self.vk, self.group_id)
        self.api = self.vk.get_api()

    def run(self):
        """Запуск бота."""
        for event in self.long_poller.listen():
            try:
                self.on_event(event)
            except Exception as err:
                log.exception('ошибка в обработке события', err)

    @db_session
    def on_event(self, event):
        """
        Отправляем сообщение назад, если оно текствое
        :param event: VkBotMessageEvent object
        :return: None
        """
        if event.type != VkBotEventType.MESSAGE_NEW:
            # log.info(f' неизвестное событие {event.type}')
            return

        user_id = event.object.peer_id
        text = event.object.text
        log.debug(f'пользователь {user_id} пишет: {text}')

        state = UserState.get(user_id=str(user_id))

        for intent in INTENTS:
            log.debug(f'User {user_id} get {intent}')
            if any(token in text.lower() for token in intent['tokens']):
                if intent['answer']:
                    self.clear_context(state)
                    text_to_send = intent['answer']
                    self.send_text(text_to_send, user_id)
                else:
                    self.clear_context(str(user_id))
                    self.start_scenario(scenario_name=intent['scenario'], user_id=user_id, text=text)

                break
        else:
            if state is not None:
                self.continue_scenario(text=text, state=state, user_id=user_id)
            else:
                text_to_send = DEFAULT_ANSWER
                self.send_text(text_to_send, user_id)

        # log.debug(f'бот отвечает {text_to_send}')

    def send_text(self, text_to_send, user_id):
        self.api.messages.send(
            message=text_to_send,
            random_id=get_random_id(),
            peer_id=user_id,
        )

    def send_image(self, image, user_id):
        upload_url = self.api.photos.getMessagesUploadServer()['upload_url']
        upload_data = requests.post(upload_url, files={'photo': ('image.png', image, 'image/png')}).json()
        image_data = self.api.photos.saveMessagesPhoto(**upload_data)
        owner_id = image_data[0]['owner_id']
        media_id = image_data[0]['id']
        attachment = f'photo{owner_id}_{media_id}'

        self.api.messages.send(
            attachment=attachment,
            random_id=get_random_id(),
            peer_id=user_id,
        )

    def send_step(self, step, user_id, text, context, text_to_send):
        if text_to_send:
            self.send_text(text_to_send, user_id)
        if 'image' in step:
            handler = getattr(handlers, step['image'])
            image = handler(text, context)
            self.send_image(image, user_id)

    def start_scenario(self, scenario_name, user_id, text):
        """Начинаем сценарий"""
        scenario = SCENARIOS[scenario_name]
        first_step = scenario['first_step']
        step = scenario['steps'][first_step]
        text_to_send = step['text']
        action = getattr(handlers, step['action'])
        text_to_send += action()
        self.send_step(step=step, user_id=user_id, text=text, context={}, text_to_send=text_to_send)
        # self.send_text(text_to_send, user_id)
        try:
            UserState(user_id=str(user_id), scenario_name=scenario_name, step_name=first_step, context={})
        except CacheIndexError:
            pass
        return text_to_send

    def continue_scenario(self, text, state, user_id):
        """Продолжаем сценарий"""
        # достаем шаги
        steps = SCENARIOS[state.scenario_name]['steps']
        step = steps[state.step_name]
        step_to_send = step
        # достаем хэндлер
        handler = getattr(handlers, step['handler'])

        if handler(text=text, context=state.context):
            # next step
            next_step = steps[step["next_step"]]
            text_to_send = next_step['text'].format(**state.context)
            step_to_send = next_step

            # проверяем что ввел пользоваетль на 7ом шаге
            if self.is_it_ok(state=state):
                self.clear_context(state)
                self.send_text(INTENTS[2]['answer'], user_id)
                return

            # Достаем экшен
            elif next_step['action']:
                action = getattr(handlers, next_step['action'])
                text_to_send += action(state.context)

            if next_step['next_step']:
                # переключаем на след шаг
                state.step_name = step['next_step']

            else:
                # после удаления из бд обратится к объекту не получится, отправляем прощание
                self.send_step(step=step_to_send, user_id=user_id, text=text, context=state.context,
                               text_to_send=text_to_send)
                Ticket(
                    departure=state.context['departure'],
                    arrival=state.context['arrival'],
                    date=state.context['date'],
                    flight_number=state.context['flight_number'],
                    seats_count=state.context['seats_count'],
                    comment=str(state.context['comment']),
                )
                state.delete()
                print('удалили из бд, проверь!')

                return
        else:
            # retry current step
            text_to_send = step['failure_text'].format(**state.context)

        text_to_send += self.print_extra_content(state)
        self.send_step(step=step_to_send, user_id=user_id, text=text, context=state.context, text_to_send=text_to_send)

    @staticmethod
    def is_it_ok(state):
        """
        проверяем не ввел ли пользователь на шаге 7 ответ "нет"
        :param state: state пользователя из бд
        :return: bool
        """
        try:
            if state.context['is_correct'] is False:
                return True
        except (KeyError, TypeError):
            return False

    @staticmethod
    def clear_context(state):
        """
        очищаем контекст пользователя
        :param state: состояние пользователя
        :return: None
        """
        try:
            state.delete()
        except (KeyError, AttributeError,):
            pass

    @staticmethod
    def print_extra_content(state):
        """
        проверяем наличие extra_content в context
        :type state: стейт пользователя
        :return: extra_content -> str
        """
        try:
            extra_content = state.context['extra_content']
            state.context.pop('extra_content')
            return extra_content
        except (KeyError, AttributeError, OperationWithDeletedObjectError):
            return ''


if __name__ == "__main__":
    conf_logging()
    bot = Bot(group=GROUP_ID, token_api=TOKEN)
    bot.run()

# Первая часть курсового проекта зачтена.
