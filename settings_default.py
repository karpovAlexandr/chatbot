#!/usr/bin/env python3
# TOKEN - токен от VK (с типом str)
# GROUP_ID - id группы в VK (с типом int)

# Сделал копию файла setting пайтон файлом, помоему так удобнее для проверки, поскольку, в файле есть довольно
# большие структуры не поддающиеся чтению в развернутом виде


TOKEN = ''
GROUP_ID = 0

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

print(INTENTS[2]['answer'])



flights = {
    'МОСКВА': {
        'САНКТ-ПЕТЕРБУРГ': {
            # ежедневное авиасообщение
            '28-09-2020': ['1', ],
            '29-09-2020': ['3', ],
            '30-09-2020': ['5', '6'],
            '01-10-2020': ['7', ],
            '02-10-2020': ['7', ],
            '03-10-2020': ['1', ],
            '04-10-2020': ['3', ],

        },
        'БЕРЛИН': {

            # пример авиасообщения по числам месяца: 1,8,15,22
            '22-09-2020': ['8', ],
            '01-10-2020': ['18', ],
            '08-10-2020': ['19', ],
            '15-10-2020': ['19', ],

        },
        'ЛОНДОН': {

            # пример
            '28-09-2020': ['8', ],  # каждый понедельник и пятницу
            '02-10-2020': ['19', ],  # каждую пятницу

        },
        'ПРАГА': {

            '28-09-2020': ['8', ],
            '29-09-2020': ['9', ],
            '30-09-2020': ['2', '18'],
            '01-10-2020': ['18', ],
            '02-10-2020': ['19', ],
        },
        'РИМ': {
            '28-09-2020': ['8', ],
            '29-09-2020': ['9', ],
            '30-09-2020': ['2', '18'],
            '01-10-2020': ['18', ],
            '02-10-2020': ['19', ],
        },
    },
    'БУДАПЕШТ': {
        'МОСКВА': {
            # ежедневное авиасообщение
            '28-09-2020': ['1', ],
            '29-09-2020': ['3', ],
            '30-09-2020': ['5', '6'],
            '01-10-2020': ['7', ],
            '02-10-2020': ['7', ],
            '03-10-2020': ['1', ],
            '04-10-2020': ['3', ],
        },
        'БЕРЛИН': {
            # пример авиасообщения по числам месяца: 1,8,15,22
            '22-09-2020': ['8', ],
            '01-10-2020': ['18', ],
            '08-10-2020': ['19', ],
            '15-10-2020': ['19', ],

        },
        'РИМ': {
            '28-09-2020': ['8', ],
            '29-09-2020': ['9', ],
            '30-09-2020': ['2', '18'],
            '01-10-2020': ['18', ],
            '02-10-2020': ['19', ],
        },
    },
    'АМСТЕРДАМ': {
        'ПРАГА': {
            '28-09-2020': ['8', ],
            '29-09-2020': ['9', ],
            '30-09-2020': ['2', '18'],
            '01-10-2020': ['18', ],
            '02-10-2020': ['19', ],
        },
        'РИМ': {
            '28-09-2020': ['8', ],
            '29-09-2020': ['9', ],
            '30-09-2020': ['2', '18'],
            '01-10-2020': ['18', ],
            '02-10-2020': ['19', ],
        },
        'МИНСК': {
            # ежедневное авиасообщение
            '28-09-2020': ['1', ],
            '29-09-2020': ['3', ],
            '30-09-2020': ['5', '6'],
            '01-10-2020': ['7', ],
            '02-10-2020': ['7', ],
            '03-10-2020': ['1', ],
            '04-10-2020': ['3', ],
        },
        'ПАРИЖ': {
            # пример авиасообщения по числам месяца: 1,8,15,22
            '22-09-2020': ['8', ],
            '01-10-2020': ['18', ],
            '08-10-2020': ['19', ],
            '15-10-2020': ['19', ],

        },
    },
    'ПРАГА': {
        'ВАРШАВА': {
            '28-09-2020': ['8', ],
            '29-09-2020': ['9', ],
            '30-09-2020': ['2', '18'],
            '01-10-2020': ['18', ],
            '02-10-2020': ['19', ],
        },
        'РИМ': {
            '28-09-2020': ['8', ],
            '29-09-2020': ['9', ],
            '30-09-2020': ['2', '18'],
            '01-10-2020': ['18', ],
            '02-10-2020': ['19', ],
        },
        'МИНСК': {
            # ежедневное авиасообщение
            '28-09-2020': ['1', ],
            '29-09-2020': ['3', ],
            '30-09-2020': ['5', '6'],
            '01-10-2020': ['7', ],
            '02-10-2020': ['7', ],
            '03-10-2020': ['1', ],
            '04-10-2020': ['3', ],
        },
        'ПАРИЖ': {
            # пример авиасообщения по числам месяца: 1,8,15,22
            '22-09-2020': ['8', ],
            '01-10-2020': ['18', ],
            '08-10-2020': ['19', ],
            '15-10-2020': ['19', ],

        },
    },
    'РИМ': {
        'МОСКВА': {
            # ежедневное авиасообщение
            '28-09-2020': ['1', ],
            '29-09-2020': ['3', ],
            '30-09-2020': ['5', '6'],
            '01-10-2020': ['7', ],
            '02-10-2020': ['7', ],
            '03-10-2020': ['1', ],
            '04-10-2020': ['3', ],
        },
        'БЕРЛИН': {
            # пример авиасообщения по числам месяца: 1,8,15,22
            '22-09-2020': ['8', ],
            '01-10-2020': ['18', ],
            '08-10-2020': ['19', ],
            '15-10-2020': ['19', ],

        },
        'ПАРИЖ': {
            # пример авиасообщения по числам месяца: 1,8,15,22
            '22-09-2020': ['8', ],
            '01-10-2020': ['18', ],
            '08-10-2020': ['19', ],
            '15-10-2020': ['19', ],

        },
    },
    'САНКТ-ПЕТЕРБУРГ': {
        'МОСКВА': {
            # ежедневное авиасообщение
            '28-09-2020': ['1', ],
            '29-09-2020': ['3', ],
            '30-09-2020': ['5', '6'],
            '01-10-2020': ['7', ],
            '02-10-2020': ['7', ],
            '03-10-2020': ['1', ],
            '04-10-2020': ['3', ],
        },
        'ПРАГА': {
            '28-09-2020': ['8', ],
            '29-09-2020': ['9', ],
            '30-09-2020': ['2', '18'],
            '01-10-2020': ['18', ],
            '02-10-2020': ['19', ],
        },
    },
    'ЛОНДОН': {
        'ПРАГА': {
            '28-09-2020': ['8', ],
            '29-09-2020': ['9', ],
            '30-09-2020': ['2', '18'],
            '01-10-2020': ['18', ],
            '02-10-2020': ['19', ],
        },
        'РИМ': {
            '28-09-2020': ['8', ],
            '29-09-2020': ['9', ],
            '30-09-2020': ['2', '18'],
            '01-10-2020': ['18', ],
            '02-10-2020': ['19', ],
        },
        'ПАРИЖ': {
            # ежедневное авиасообщение
            '28-09-2020': ['1', ],
            '29-09-2020': ['3', ],
            '30-09-2020': ['5', '6'],
            '01-10-2020': ['7', ],
            '02-10-2020': ['7', ],
            '03-10-2020': ['1', ],
            '04-10-2020': ['3', ],
        },
        'БУДАПЕШТ': {
            # ежедневное авиасообщение
            '28-09-2020': ['1', ],
            '29-09-2020': ['3', ],
            '30-09-2020': ['5', '6'],
            '01-10-2020': ['7', ],
            '02-10-2020': ['7', ],
            '03-10-2020': ['1', ],
            '04-10-2020': ['3', ],
        },
        'АМСТЕРДАМ': {
            # ежедневное авиасообщение
            '28-09-2020': ['1', ],
            '29-09-2020': ['3', ],
            '30-09-2020': ['5', '6'],
            '01-10-2020': ['7', ],
            '02-10-2020': ['7', ],
            '03-10-2020': ['1', ],
            '04-10-2020': ['3', ],
        },
    },
    'БЕРЛИН': {
        'ПАРИЖ': {
            # пример авиасообщения по числам месяца: 1,8,15,22
            '22-09-2020': ['8', ],
            '01-10-2020': ['18', ],
            '08-10-2020': ['19', ],
            '15-10-2020': ['19', ],

        },
        'ВАРШАВА': {
            '28-09-2020': ['8', ],
            '29-09-2020': ['9', ],
            '30-09-2020': ['2', '18'],
            '01-10-2020': ['18', ],
            '02-10-2020': ['19', ],
        },
        'РИМ': {
            '28-09-2020': ['8', ],
            '29-09-2020': ['9', ],
            '30-09-2020': ['2', '18'],
            '01-10-2020': ['18', ],
            '02-10-2020': ['19', ],
        },
        'МИНСК': {
            # ежедневное авиасообщение
            '28-09-2020': ['1', ],
            '29-09-2020': ['3', ],
            '30-09-2020': ['5', '6'],
            '01-10-2020': ['7', ],
            '02-10-2020': ['7', ],
            '03-10-2020': ['1', ],
            '04-10-2020': ['3', ],
        },
    },
    'ПАРИЖ': {
        'ВАРШАВА': {
            '28-09-2020': ['8', ],
            '29-09-2020': ['9', ],
            '30-09-2020': ['2', '18'],
            '01-10-2020': ['18', ],
            '02-10-2020': ['19', ],
        },
        'РИМ': {
            '28-09-2020': ['8', ],
            '29-09-2020': ['9', ],
            '30-09-2020': ['2', '18'],
            '01-10-2020': ['18', ],
            '02-10-2020': ['19', ],
        },
        'МИНСК': {
            # ежедневное авиасообщение
            '28-09-2020': ['1', ],
            '29-09-2020': ['3', ],
            '30-09-2020': ['5', '6'],
            '01-10-2020': ['7', ],
            '02-10-2020': ['7', ],
            '03-10-2020': ['1', ],
            '04-10-2020': ['3', ],
        },
        'МОСКВА': {
            # ежедневное авиасообщение
            '28-09-2020': ['1', ],
            '29-09-2020': ['3', ],
            '30-09-2020': ['5', '6'],
            '01-10-2020': ['7', ],
            '02-10-2020': ['7', ],
            '03-10-2020': ['1', ],
            '04-10-2020': ['3', ],
        },
        'БЕРЛИН': {
            # пример авиасообщения по числам месяца: 1,8,15,22
            '22-09-2020': ['8', ],
            '01-10-2020': ['18', ],
            '08-10-2020': ['19', ],
            '15-10-2020': ['19', ],

        },

    },
    'ВАРШАВА': {
        'МОСКВА': {
            # ежедневное авиасообщение
            '28-09-2020': ['1', ],
            '29-09-2020': ['3', ],
            '30-09-2020': ['5', '6'],
            '01-10-2020': ['7', ],
            '02-10-2020': ['7', ],
            '03-10-2020': ['1', ],
            '04-10-2020': ['3', ],
        },
        'БЕРЛИН': {
            # пример авиасообщения по числам месяца: 1,8,15,22
            '22-09-2020': ['8', ],
            '01-10-2020': ['18', ],
            '08-10-2020': ['19', ],
            '15-10-2020': ['19', ],
        },
        'РИМ': {
            '28-09-2020': ['8', ],
            '29-09-2020': ['9', ],
            '30-09-2020': ['2', '18'],
            '01-10-2020': ['18', ],
            '02-10-2020': ['19', ],
        },
        'МИНСК': {
            # ежедневное авиасообщение
            '28-09-2020': ['1', ],
            '29-09-2020': ['3', ],
            '30-09-2020': ['5', '6'],
            '01-10-2020': ['7', ],
            '02-10-2020': ['7', ],
            '03-10-2020': ['1', ],
            '04-10-2020': ['3', ],
        },
        'ПАРИЖ': {
            # пример авиасообщения по числам месяца: 1,8,15,22
            '22-09-2020': ['8', ],
            '01-10-2020': ['18', ],
            '08-10-2020': ['19', ],
            '15-10-2020': ['19', ],

        },
    },
    'ВЕНА': {
        'ПРАГА': {
            '28-09-2020': ['8', ],
            '29-09-2020': ['9', ],
            '30-09-2020': ['2', '18'],
            '01-10-2020': ['18', ],
            '02-10-2020': ['19', ],
        },
        'РИМ': {
            '28-09-2020': ['8', ],
            '29-09-2020': ['9', ],
            '30-09-2020': ['2', '18'],
            '01-10-2020': ['18', ],
            '02-10-2020': ['19', ],
        },
        'МИНСК': {
            # ежедневное авиасообщение
            '28-09-2020': ['1', ],
            '29-09-2020': ['3', ],
            '30-09-2020': ['5', '6'],
            '01-10-2020': ['7', ],
            '02-10-2020': ['7', ],
            '03-10-2020': ['1', ],
            '04-10-2020': ['3', ],
        },
        'ПАРИЖ': {
            # пример авиасообщения по числам месяца: 1,8,15,22
            '22-09-2020': ['8', ],
            '01-10-2020': ['18', ],
            '08-10-2020': ['19', ],
            '15-10-2020': ['19', ],

        },
    },
    'МАДРИД': {
        'МОСКВА': {
            # ежедневное авиасообщение
            '28-09-2020': ['1', ],
            '29-09-2020': ['3', ],
            '30-09-2020': ['5', '6'],
            '01-10-2020': ['7', ],
            '02-10-2020': ['7', ],
            '03-10-2020': ['1', ],
            '04-10-2020': ['3', ],
        },
        'БЕРЛИН': {
            # пример авиасообщения по числам месяца: 1,8,15,22
            '22-09-2020': ['8', ],
            '01-10-2020': ['18', ],
            '08-10-2020': ['19', ],
            '15-10-2020': ['19', ],

        },
        'ПАРИЖ': {
            # пример авиасообщения по числам месяца: 1,8,15,22
            '22-09-2020': ['8', ],
            '01-10-2020': ['18', ],
            '08-10-2020': ['19', ],
            '15-10-2020': ['19', ],

        },
    },
    'КИЕВ': {
        'ВАРШАВА': {
            '28-09-2020': ['8', ],
            '29-09-2020': ['9', ],
            '30-09-2020': ['2', '18'],
            '01-10-2020': ['18', ],
            '02-10-2020': ['19', ],
        },
        'РИМ': {
            '28-09-2020': ['8', ],
            '29-09-2020': ['9', ],
            '30-09-2020': ['2', '18'],
            '01-10-2020': ['18', ],
            '02-10-2020': ['19', ],
        },
        'МИНСК': {
            # ежедневное авиасообщение
            '28-09-2020': ['1', ],
            '29-09-2020': ['3', ],
            '30-09-2020': ['5', '6'],
            '01-10-2020': ['7', ],
            '02-10-2020': ['7', ],
            '03-10-2020': ['1', ],
            '04-10-2020': ['3', ],
        },
        'ПАРИЖ': {
            # пример авиасообщения по числам месяца: 1,8,15,22
            '22-09-2020': ['8', ],
            '01-10-2020': ['18', ],
            '08-10-2020': ['19', ],
            '15-10-2020': ['19', ],

        },
    },
    'МИНСК': {
        'МОСКВА': {
            # ежедневное авиасообщение
            '28-09-2020': ['1', ],
            '29-09-2020': ['3', ],
            '30-09-2020': ['5', '6'],
            '01-10-2020': ['7', ],
            '02-10-2020': ['7', ],
            '03-10-2020': ['1', ],
            '04-10-2020': ['3', ],
        },
        'БЕРЛИН': {
            # пример авиасообщения по числам месяца: 1,8,15,22
            '22-09-2020': ['8', ],
            '01-10-2020': ['18', ],
            '08-10-2020': ['19', ],
            '15-10-2020': ['19', ],

        },
        'ПАРИЖ': {
            # пример авиасообщения по числам месяца: 1,8,15,22
            '22-09-2020': ['8', ],
            '01-10-2020': ['18', ],
            '08-10-2020': ['19', ],
            '15-10-2020': ['19', ],

        },
        'БУДАПЕШТ': {
            # ежедневное авиасообщение
            '28-09-2020': ['1', ],
            '29-09-2020': ['3', ],
            '30-09-2020': ['5', '6'],
            '01-10-2020': ['7', ],
            '02-10-2020': ['7', ],
            '03-10-2020': ['1', ],
            '04-10-2020': ['3', ],
        },
        'АМСТЕРДАМ': {
            # ежедневное авиасообщение
            '28-09-2020': ['1', ],
            '29-09-2020': ['3', ],
            '30-09-2020': ['5', '6'],
            '01-10-2020': ['7', ],
            '02-10-2020': ['7', ],
            '03-10-2020': ['1', ],
            '04-10-2020': ['3', ],
        },

    }
}

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