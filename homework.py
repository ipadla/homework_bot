import logging
import os
import sys
import time
from http import HTTPStatus
from typing import Optional

import requests
import telegram
from dotenv import load_dotenv

from exceptions import APIAccessError, APIResponseError, CheckResponseError

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    handlers=[logging.StreamHandler(stream=sys.stdout)],
    format='%(asctime)s %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
ENDPOINT_TIMEOUT = 10
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot: telegram.Bot, message: str) -> None:
    try:
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message
        )
    except Exception as error:
        logger.error(f"Не удалось отправить сообщение в Telegram: {error}")
    else:
        logger.info(f"Бот отправил сообщение: {message}")


def get_api_answer(current_timestamp: Optional[int] = None) -> dict:
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}

    try:
        response = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=params,
            timeout=ENDPOINT_TIMEOUT
        )
    except Exception as error:
        raise APIAccessError(f"Эндпоинт не доступен: {error}")
    else:
        if response.status_code != HTTPStatus.OK:
            raise APIResponseError(
                f"Ошибка доступа к эндпоинту, HTTP: {response.status_code}"
            )
        else:
            return response.json()


def check_response(response: dict) -> list:
    if type(response) is not dict:
        raise TypeError('В ответе API нет dict')

    homeworks = response.get('homeworks')

    if homeworks is None:
        raise CheckResponseError('В ответе API нет ключа homeworks')

    if type(homeworks) is not list:
        raise CheckResponseError('В ответе API ключ homeworks - не список!')

    return homeworks


def parse_status(homework: list) -> str:
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
            logger.critical(
                f"Отсутствует обязательная переменная окружения: {env}"
            )

    return all(result)


def main() -> None:
    """Основная логика работы бота."""
    if not check_tokens():
        raise SystemExit('You need to set all Environment variables')

    bot = telegram.Bot(token=str(TELEGRAM_TOKEN))
    current_timestamp = int(time.time())
    # current_timestamp = 1
    last_exception = ""

    ...

    while True:
        try:
            response = get_api_answer(current_timestamp=current_timestamp)

            homeworks = check_response(response)

            current_timestamp = response.get('current_date')
        except Exception as error:
            # print(str(error))
            error_name = error.__class__.__name__
            # message = f'Сбой в работе программы: {error}'

            if error_name in [
                    'APIAccessError',
                    'APIResponseError',
                    'CheckResponseError',
                    'TypeError']:
                logger.error(str(error))
                if last_exception != error_name:
                    send_message(bot=bot, message=str(error))
                    last_exception = error_name
        else:
            ...
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
