# bot.py

import logging
import requests
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from telegram.ext import Updater, CommandHandler, CallbackContext
import os
from dotenv import load_dotenv

load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получение переменных окружения
TELEGRAM_API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')
WEB_APP_URL = os.getenv('WEB_APP_URL')  # Например, https://your-project.railway.app/web_app/index.html

def start(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    logger.info("User %s started the bot.", user.first_name)
    
    # Кнопка для открытия Web App
    button = KeyboardButton(
        text="Открыть HelpCoin",
        web_app=WebAppInfo(url=WEB_APP_URL)
    )
    keyboard = [[button]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    update.message.reply_text(
        "Добро пожаловать в HelpCoin! Нажмите кнопку ниже, чтобы начать.",
        reply_markup=reply_markup
    )

def help_command(update: Update, context: CallbackContext) -> None:
    help_text = (
        "/start - Начало работы и регистрация\n"
        "/help - Список команд\n"
        "/tasks - Просмотр доступных задач\n"
        "/mytasks - Мои задачи\n"
        "/profile - Мой профиль\n"
        "/accept_task [task_id] - Принять задачу\n"
        "/complete_task [task_id] - Завершить задачу\n"
    )
    update.message.reply_text(help_text)

def main():
    updater = Updater(TELEGRAM_API_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Обработчики команд
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    # Запуск бота
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()