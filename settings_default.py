#!/usr/bin/env python3
# TOKEN - токен от VK (с типом str)
# GROUP_ID - id группы в VK (с типом int)


TOKEN = ''
GROUP_ID = 0

RAW_EVENT = {
    'type': 'message_new',
    'object': {'date': 1595599261,
               'from_id': int,
               'id': 154, 'out': 0,
               'peer_id': int,
               'text': 'Прр',
               'conversation_message_id': 148,
               'fwd_messages': [],
               'important': False,
               'random_id': 0,
               'attachments': [],
               'is_hidden': False},
    'group_id': int
}

DEFAULT_ANSWER = "Добрый день!\n" \
                 "список доступных команд:\n" \
                 "/ticket - заказать авиабилет \n" \
                 "/help - вызов справки \n" \
                 "/exit - завершить работу "

INTENTS = [

    {
        "name": "Помощь",
        "tokens": ("/help", "help", "start", "/start"),
        "scenario": None,
        "answer": DEFAULT_ANSWER
    },

    {
        "name": "Заказать Билет",
        "tokens": ("/ticket", "ticket", "билет"),
        "scenario": "ticket_order",
        "answer": None
    },

    {
        "name": "Завершить",
        "tokens": ("/end", "end", "/exit", "exit", "закончи", "выйт"),
        "scenario": None,
        "answer": "Вы выбрали завершить\n"
                  "Всего доброго!"
    },
]

cities = ['ПРАГА', 'АМСТЕРДАМ', 'МОСКВА', 'МАДРИД', 'РИМ', 'ВЕНА', 'ВАРШАВА', 'БЕРЛИН', 'САНКТ-ПЕТЕРБУРГ', 'ЛОНДОН',
          'БУДАПЕШТ', 'ПАРИЖ']

SCENARIOS = {
    "ticket_order": {
        "first_step": "step_1",
        "steps": {
            "step_1": {
                "text": f"Введите город вылета",
                "action": "action_print_available_departure_cities",
                "failure_text": "Нет вылетов из данного города",
                "handler": "handle_departure_city",
                "next_step": "step_2"
            },
            "step_2": {
                "text": "Введите город прилета",
                "action": "action_print_available_arrival_cities",
                "failure_text": "Нет рейсов в этот город",
                "handler": "handle_arrival_city",
                "next_step": "step_3"
            },
            "step_3": {
                "text": "Введите дату в формате \"dd-mm-yyyy\"",
                "action": "action_pass",
                "failure_text": "Нет рейсов в эту дату",
                "handler": "handle_flight_date",
                "next_step": "step_4"
            },
            "step_4": {
                "text": "Выберите номер рейса",
                "action": "action_print_available_air_flights",
                "failure_text": "Нет такого рейса",
                "handler": "handle_flight_number",
                "next_step": "step_5"
            },
            "step_5": {
                "text": "Выберите количество мест (от 1 до 5)",
                "action": 'action_pass',
                "failure_text": "доступное количесто для заказа от 1 до 5",
                "handler": "handle_seats",
                "next_step": "step_6"
            },
            "step_6": {
                "text": "Вы можете написать комментарий (до 100 сим.)",
                "action": 'action_pass',
                "failure_text": "Ваше сообщение больше 100 символов",
                "handler": "handle_comment",
                "next_step": "step_7"
            },
            "step_7": {
                "text": "Ваш заказ верен? (да/нет)",
                "action": 'action_print_context',
                "failure_text": "введите \"да\" или \"нет\"",
                "handler": "handle_confirm",
                "next_step": "step_8"
            },
            "step_8": {
                "text": "Введите Ваше имя и фамилию через пробел",
                "action": 'action_pass',
                "failure_text": "Введите Ваше имя и фамилию через пробел",
                "handler": 'handle_name',
                "next_step": "step_9"
            },
            "step_9": {
                "text": "Хорошие новости!\n"
                        "Ожидайте Ваше билет на данном чате",
                "image": 'generate_ticket_handler',
                "action": None,
                "failure_text": None,
                "handler": 'handle_pass',
                "next_step": None
            },
        }
    },
}

DB_CONFIG = {
    'provider': 'postgres',
    'user': 'postgres',
    'password': '',
    'host': 'localhost',
    'database': 'vk_chat_bot',
}
