from http import HTTPStatus
import logging
import os
import sys
import time
from typing import Optional

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    handlers=[logging.StreamHandler(stream=sys.stdout)],
    format='%(asctime)s %(levelname)s %(message)s'
)


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
    response = bot.send_message(
        chat_id=TELEGRAM_CHAT_ID,
        text=message
    )

    if response != message:
        logging.error("Не удалось отправить сообщение в Telegram")
    else:
        logging.info(f"Бот отправил сообщение: {message}")


def get_api_answer(current_timestamp: Optional[int] = None) -> dict:
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}

    response = requests.get(ENDPOINT, headers=HEADERS, params=params)

    if response.status_code == HTTPStatus.OK:
        return response.json()

    return {'homeworks': [], 'current_date': timestamp}


def check_response(response: dict):

    print(response)


def parse_status(homework):
    homework_name = ...
    homework_status = ...

    ...

    verdict = ...

    ...

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens() -> bool:
    envlist = ['PRACTICUM_TOKEN', 'TELEGRAM_TOKEN', 'TELEGRAM_CHAT_ID']
    result = [False] * len(envlist)

    for index, env in enumerate(envlist):
        if globals()[env] is not None:
            result[index] = True
        else:
            result[index] = False
            logging.critical(
                f"Отсутствует обязательная переменная окружения: {env}"
            )

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
            response = get_api_answer(current_timestamp=current_timestamp)

            check_response(response)

            current_timestamp = response.get('current_date')
            time.sleep(RETRY_TIME)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            ...
            time.sleep(RETRY_TIME)
        else:
            ...


if __name__ == '__main__':
    main()
