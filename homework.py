import os
import time
from typing import Optional

import requests
from requests.models import Response
import telegram
from dotenv import load_dotenv

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot: telegram.Bot, message: str) -> None:
    bot.send_message(
        chat_id=TELEGRAM_CHAT_ID,
        text=message
    )


def get_api_answer(current_timestamp: Optional[int] = None) -> Response:
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}

    return requests.get(ENDPOINT, headers=HEADERS, params=params).json()


def check_response(response: Response):

    print(response)


def parse_status(homework):
    homework_name = ...
    homework_status = ...

    ...

    verdict = ...

    ...

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    envlist = [PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]
    result = [False] * len(envlist)

    for index, env in enumerate(envlist):
        result[index] = True if env is not None else False

    return all(result)


def main() -> None:
    """Основная логика работы бота."""
    if not check_tokens():
        raise SystemExit('You need to set all Environment variables')

    bot = telegram.Bot(token=str(TELEGRAM_TOKEN))
    current_timestamp = int(time.time())

    ...

    while True:
        try:
            response = get_api_answer()

            check_response(response)

            current_timestamp = ...
            time.sleep(RETRY_TIME)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            ...
            time.sleep(RETRY_TIME)
        else:
            ...


if __name__ == '__main__':
    main()
