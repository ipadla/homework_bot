import logging
import sys
import time
from http import HTTPStatus
from typing import Optional

import requests
import telegram

from exceptions import APIResponseError
from settings import (ENDPOINT, ENDPOINT_TIMEOUT, ENVLIST, HEADERS,
                      HOMEWORK_STATUSES, PRACTICUM_TOKEN, RETRY_TIME,
                      TELEGRAM_CHAT_ID, TELEGRAM_TOKEN)

logging.basicConfig(
    level=logging.DEBUG,
    handlers=[logging.StreamHandler(stream=sys.stdout)],
    format='%(asctime)s %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)

PRACTICUM_TOKEN


def send_message(bot: telegram.Bot, message: str) -> None:
    """Отправка Telegram сообщения.

    Пробуем отправить сообщение ботом, в случае исключения - логируем его,
    если получится - записываем в лог.INFO строку сообщения
    """
    try:
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message
        )
    except telegram.error.TelegramError:
        logger.error(f'Не удалось отправить сообщение в Telegram: {message}')
    else:
        logger.info(f'Бот отправил сообщение: {message}')


def get_api_answer(current_timestamp: Optional[int] = None) -> dict:
    """Получение ответа APIи преобразование в тип данных Python.

    На входе получаем epoch или устанавливаем его в сейчас.
    Пробеум получить ответ от эндпоинта.
    В случае недоступности - кидаем исключение
    По заданию если ответ эндпоинта не 200 - тоже кидаем исключение
    """
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
        raise Exception(f'Эндпоинт не доступен: {error}')
    else:
        if response.status_code != HTTPStatus.OK:
            raise APIResponseError(
                f'Ошибка доступа к эндпоинту, HTTP: {response.status_code}'
            )

    try:
        response.json()
    except requests.exceptions.JSONDecodeError:
        logger.error('Ошибка в формате json')
        raise requests.exceptions.JSONDecodeError('Ошибка в формате json')
    else:
        return response.json()


def check_response(response: dict) -> list:
    """Проверяем ответ на наличие необходимых ключей и типов данных."""
    if type(response) is not dict:
        raise TypeError('Ответ API не словарь')

    try:
        homeworks = response['homeworks']
    except KeyError as error:
        raise KeyError(f'В ответе API нет ключа {error}')

    if type(homeworks) is not list:
        raise TypeError(
            'В ответе API ключ homeworks - не список!'
        )

    return homeworks


def parse_status(homework: dict) -> str:
    """Проверка наличия необходимых для уведомления пользователя данных."""
    try:
        homework_name = homework['homework_name']
        homework_status = homework['status']
    except KeyError as error:
        raise KeyError(f'В ответе API нет ключа {error}')

    try:
        verdict = HOMEWORK_STATUSES[homework_status]
    except KeyError as error:
        raise KeyError(f'Неизвестный статус работы {error}')

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens() -> bool:
    """Проверяем все ли переменные окружения установлены.

    Проходим по списку необходимых переменных окружения, если какая-то одна не
    установлена - возвращаем False и записываем в лог.CRITICAL
    """
    for env in ENVLIST:
        if not globals()[env]:
            logger.critical(
                f'Отсутствует обязательная переменная окружения: {env}'
            )

    return all([bool(globals()[env]) for env in ENVLIST])


def main() -> None:
    """Основная логика работы бота."""
    if not check_tokens():
        raise SystemExit('Нужно установить все переменные окружения')

    bot = telegram.Bot(token=str(TELEGRAM_TOKEN))
    current_timestamp = int(time.time())
    last_exception_msg = ""

    while True:
        try:
            response = get_api_answer(current_timestamp=current_timestamp)

            homeworks = check_response(response)

            if len(homeworks) == 0:
                logger.debug('Отсутствуют новые статусы в ответе API')
            else:
                for homework in homeworks:
                    send_message(bot=bot, message=parse_status(homework))

            current_timestamp = response.get(
                'current_date', int(time.time()) - RETRY_TIME
            )
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
            if last_exception_msg != message:
                send_message(bot=bot, message=message)
                last_exception_msg = message
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
