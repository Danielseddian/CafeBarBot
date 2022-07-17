## Aiogram TG CafeBar bot
### Telegram bot based on aiogram and using sqlite for the simple database 

# Основа для бота небольшого кафе-бара.
## По запросу пользователя показывает меню. Админ чата может добавлять или удалять позиции в меню.
#### Доступные команды для пользователей:
- Меню ИЛИ /start — Покажет клавиатуру для взаимодействия с ботом
#### Доступные команды для администратора:
- Админ — доступ к клавиатуре для управления (только для из списка в .env)
#### Стек библиотек:
- aiogram==2.20
- python-dotenv==0.20.0
- python-environ==0.4.54
- openpyxl==3.0.10
- requests==2.28.0
- httpx==0.23.0

## Подготовка к запуску:
#### 1. [Создать и получить токен](https://habr.com/ru/post/262247/) телеграм [бота](https://tlgrm.ru/docs/bots). Сгенерировать qr-код со ссылкой на бота можно [здесь](http://qrcoder.ru/)
#### 2. Создать файл .env в папке source и добавить пары ключ=значение по примеру из .env.example
#### 3. Выполнить команды через консоль:
> python3 -m venv venv # (venv). название виртуального окружаения, обычно, venv

> . venv/bin/activate # для Windows: venv/Scripts/activate

> pip install -r requirements.txt 
## Запуск бота:
> python3 source/run_bot.py
