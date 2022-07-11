# homework_bot
Телеграм бот сообщающий о статусе проверки домашней работы в Яндекс.Практикуме.

# Запуск проекта
Необходимо создать .env файл:
```
PRACTICUM_TOKEN=Токен от ЯндексюПрактикума
TELEGRAM_TOKEN=Токен Телеграм бота
TELEGRAM_CHAT_ID=ChatID в который отправляются сообщения
```
Cоздать и активировать виртуальное окружение:
```
python3 -m venv venv
source venv/bin/activate
```
Установить зависимости из файла requirements.txt:
```
pip install requirements.txt
```
Запустить бота
```
python3 ./homework.py
```
