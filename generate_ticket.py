import requests
from six import BytesIO

from PIL import Image, ImageDraw, ImageFont


def generate_ticket(name, departure, arrival, date, email):
    """
    генерация картинки png
    :param email: электронная почта для генерации аватара
    :param name: имя пользователя
    :param departure: город вылета
    :param arrival:  город посадки
    :param date: дата рейса
    :return: BytesIO object
    """
    COORDINATES = {
        'name': (50, 122),
        'departure': (50, 192),
        'arrival': (50, 257),
        'date': (275, 257),
        'avatar': (400, 110),
    }

    TEMPLATE_PATH = 'templates/ticket_template.png'
    FONT_PATH = 'fonts/Roboto.ttf'
    BLACK_COLOR = (0, 0, 0, 255)

    AVATAR_SIZE = 100

    template = Image.open(TEMPLATE_PATH).convert("RGBA")
    font = ImageFont.truetype(FONT_PATH, 15)
    draw = ImageDraw.Draw(template)

    draw.text(xy=COORDINATES['name'], text=name, font=font, fill=BLACK_COLOR)
    draw.text(xy=COORDINATES['departure'], text=departure, font=font, fill=BLACK_COLOR)
    draw.text(xy=COORDINATES['arrival'], text=arrival, font=font, fill=BLACK_COLOR)
    draw.text(xy=COORDINATES['date'], text=date, font=font, fill=BLACK_COLOR)

    response = requests.get(url=f"https://api.adorable.io/avatars/{AVATAR_SIZE}/{email}")
    # print(f"https://api.adorable.io/avatars/{AVATAR_SIZE}/{email}")
    avatar_file_like = BytesIO(response.content)
    avatar = Image.open(avatar_file_like)

    template.paste(avatar, COORDINATES['avatar'])

    # with open('files/ticket_for_tests.png', 'wb') as f:
    #     template.save(f, 'png')
    temp_file = BytesIO()
    template.save(temp_file, 'png')
    temp_file.seek(0)

    return temp_file


TEST_ARGUMENTS = {
    'name': 'Пользователь',
    'departure': 'Москва',
    'arrival': 'Берлин',
    'date': '01-01-2020',
    'email': 'sample@mail.ri'
}

if __name__ == '__main__':
    generate_ticket(**TEST_ARGUMENTS)
