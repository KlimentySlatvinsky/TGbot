import requests
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
from dotenv import load_dotenv
import os

# Загрузка переменных окружения из файла .env
load_dotenv()

# Получение значений API-ключа и токена бота из файла .env
api_key = os.getenv("API_KEY")  # API-ключ для OpenWeatherMap
bot_token = os.getenv("BOT_TOKEN")  # Токен для Telegram-бота

# Функция для получения данных о погоде с OpenWeatherMap
def get_weather(city: str, forecast_type="current"):
    """
    Получает данные о погоде для указанного города.
    :param city: Название города.
    :param forecast_type: Тип прогноза ('current', 'tomorrow', 'week').
    :return: Строка с информацией о погоде или сообщение об ошибке.
    """
    # Формирование URL для текущей погоды или прогноза
    if forecast_type == "current":
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=ru"
    elif forecast_type in ["tomorrow", "week"]:
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric&lang=ru"
    else:
        return "Неизвестный тип прогноза."

    # Запрос к OpenWeatherMap API
    response = requests.get(url)

    # Проверка успешности запроса
    if response.status_code == 200:
        data = response.json()

        # Обработка текущей погоды
        if forecast_type == "current":
            weather = data['weather'][0]['description']
            temp = data['main']['temp']
            humidity = data['main']['humidity']
            return f"Погода в {city} сейчас:\n{weather}\nТемпература: {temp}°C\nВлажность: {humidity}%"

        # Прогноз на завтра
        elif forecast_type == "tomorrow":
            tomorrow_data = data['list'][8]  # Прогноз через 24 часа
            weather = tomorrow_data['weather'][0]['description']
            temp = tomorrow_data['main']['temp']
            humidity = tomorrow_data['main']['humidity']
            return f"Погода в {city} завтра:\n{weather}\nТемпература: {temp}°C\nВлажность: {humidity}%"

        # Прогноз на неделю (примерный)
        elif forecast_type == "week":
            week_data = data['list'][16]  # Прогноз через ~7 дней
            weather = week_data['weather'][0]['description']
            temp = week_data['main']['temp']
            humidity = week_data['main']['humidity']
            return f"Погода в {city} через неделю:\n{weather}\nТемпература: {temp}°C\nВлажность: {humidity}%"

    else:
        # Сообщение об ошибке, если запрос не успешен
        return "Не удалось получить данные о погоде. Проверьте название города."

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обрабатывает команду /start. Отправляет приветственное сообщение и клавиатуру.
    """
    buttons = [
        [KeyboardButton("Топ-10 городов России")],
        [KeyboardButton("О боте")]
    ]
    keyboard = ReplyKeyboardMarkup(buttons, resize_keyboard=True)

    # Отправка сообщения с клавиатурой
    await update.message.reply_text("Привет! Выберите действие или введите название города:", reply_markup=keyboard)

# Обработка ввода города
async def handle_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обрабатывает ввод города пользователем. Выводит текущую погоду и предлагает прогноз.
    """
    city = update.message.text  # Получение текста сообщения (название города)

    weather_info = get_weather(city)  # Получение текущей погоды

    if weather_info:
        # Кнопки для прогноза на завтра и неделю
        buttons = [
            [InlineKeyboardButton(f"Погода в {city} завтра", callback_data=f"forecast_tomorrow|{city}")],
            [InlineKeyboardButton(f"Погода в {city} через неделю", callback_data=f"forecast_week|{city}")]
        ]
        keyboard = InlineKeyboardMarkup(buttons)

        # Отправка сообщения с текущей погодой и кнопками
        await update.message.reply_text(f"{weather_info}\n\nНе хотите ли узнать погоду на завтра или через неделю?", reply_markup=keyboard)
    else:
        # Сообщение об ошибке, если данные не получены
        await update.message.reply_text(f"Не удалось получить данные о погоде для города {city}. Попробуйте другой.")

# Обработка кнопки "Топ-10 городов России"
async def handle_top_cities(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обрабатывает выбор кнопки "Топ-10 городов России". Предлагает список популярных городов.
    """
    # Список популярных городов
    top_cities = ["Москва", "Санкт-Петербург", "Уфа", "Казань", "Екатеринбург",
                  "Новосибирск", "Челябинск", "Нижний Новгород", "Самара", "Ростов-на-Дону"]

    # Создание кнопок для каждого города
    buttons = [[InlineKeyboardButton(city, callback_data=f"top_city|{city}")] for city in top_cities]
    keyboard = InlineKeyboardMarkup(buttons)

    # Отправка сообщения с кнопками
    await update.message.reply_text("Выберите город из топ-10, чтобы узнать погоду:", reply_markup=keyboard)

# Обработка нажатий на кнопки
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обрабатывает нажатия на инлайн-кнопки.
    """
    query = update.callback_query  # Получение данных о запросе
    await query.answer()  # Подтверждение получения запроса

    data = query.data  # Получение данных из нажатой кнопки

    # Логика обработки кнопок
    if data.startswith("top_city"):
        # Если выбрали город из топ-10
        city = data.split("|")[1]
        weather_info = get_weather(city)

        buttons = [
            [InlineKeyboardButton(f"Погода в {city} завтра", callback_data=f"forecast_tomorrow|{city}")],
            [InlineKeyboardButton(f"Погода в {city} через неделю", callback_data=f"forecast_week|{city}")]
        ]
        keyboard = InlineKeyboardMarkup(buttons)

        if weather_info:
            await query.edit_message_text(f"{weather_info}\n\nНе хотите ли узнать погоду на завтра или через неделю?", reply_markup=keyboard)
        else:
            await query.edit_message_text(f"Не удалось получить данные о погоде для города {city}. Попробуйте выбрать другой город.")

    # Прогноз на завтра
    elif data.startswith("forecast_tomorrow"):
        city = data.split("|")[1]
        weather_info = get_weather(city, forecast_type="tomorrow")

        buttons = [
            [InlineKeyboardButton(f"Погода в {city} через неделю", callback_data=f"forecast_week|{city}")]
        ]
        keyboard = InlineKeyboardMarkup(buttons)

        if weather_info:
            await query.edit_message_text(f"{weather_info}\n\nХотите узнать погоду через неделю?", reply_markup=keyboard)
        else:
            await query.edit_message_text(f"Не удалось получить прогноз погоды на завтра для города {city}. Попробуйте позже.")

    # Прогноз на неделю
    elif data.startswith("forecast_week"):
        city = data.split("|")[1]
        weather_info = get_weather(city, forecast_type="week")

        buttons = [
            [InlineKeyboardButton(f"Погода в {city} завтра", callback_data=f"forecast_tomorrow|{city}")]
        ]
        keyboard = InlineKeyboardMarkup(buttons)

        if weather_info:
            await query.edit_message_text(f"{weather_info}\n\nХотите узнать погоду на завтра?", reply_markup=keyboard)
        else:
            await query.edit_message_text(f"Не удалось получить прогноз погоды на неделю для города {city}. Попробуйте позже.")

# Обработка кнопки "О боте"
async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обрабатывает выбор кнопки "О боте". Отправляет информацию о боте.
    """
    await update.message.reply_text("Этот бот предназначен для получения прогноза погоды в любом городе.\n\nКурсовая работа студента ЛЭТИ, Слатвинского К.В., гр. 3354.")

# Основная логика запуска
def main():
    """
    Главная функция запуска бота.
    """
    # Создаем приложение Telegram
    application = Application.builder().token(bot_token).build()

    # Регистрация обработчиков команд и событий
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Regex("^Топ-10 городов России$"), handle_top_cities))
    application.add_handler(MessageHandler(filters.Regex("^О боте$"), about))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_city))
    application.add_handler(CallbackQueryHandler(button_handler))

    # Запуск бота
    application.run_polling()

# Запуск программы
if __name__ == "__main__":
    main()
