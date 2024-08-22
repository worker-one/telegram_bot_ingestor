import os
import telebot
import logging
import logging.config
from dotenv import load_dotenv, find_dotenv
from omegaconf import OmegaConf

from telegram_bot_ingestor.service.yandex_disk import YandexDisk
from telegram_bot_ingestor.service.google_sheets import GoogleSheets
from telegram_bot_ingestor.db.database import log_message, add_user

# Load logging configuration with OmegaConf
logging_config = OmegaConf.to_container(OmegaConf.load("./src/telegram_bot_ingestor/conf/logging_config.yaml"), resolve=True)

# Apply the logging configuration
logging.config.dictConfig(logging_config)

# Configure logging
logger = logging.getLogger(__name__)

load_dotenv(find_dotenv(usecwd=True))  # Load environment variables from .env file
BOT_TOKEN = os.getenv("BOT_TOKEN")
YANDEX_API_TOKEN = os.getenv("YANDEX_API_TOKEN")

if BOT_TOKEN is None:
    logger.error("BOT_TOKEN is not set in the environment variables.")
    exit(1)

if YANDEX_API_TOKEN is None:
    logger.error("YANDEX_API_TOKEN is not set in the environment variables.")
    exit(1)

BASE_URL = f"https://api.telegram.org/file/bot{BOT_TOKEN}/"

cfg = OmegaConf.load("./src/telegram_bot_ingestor/conf/config.yaml")
bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)

yandex_disk = YandexDisk(YANDEX_API_TOKEN)
google_sheets = GoogleSheets()

google_sheets.set_sheet(config.google_sheets.sheet_name)
table_names = google_sheets.get_table_names()

@bot.message_handler(content_types=['text', 'document', 'photo'])
def process_user_input(message):
    username = message.from_user.username

    # Determine the type of file received
    file_id = None
    user_input_text = None
    if message.content_type == 'document':
        file_id = message.document.file_id
    elif message.content_type == 'photo':
        # Get the highest resolution photo
        file_id = message.photo[-1].file_id

    # If file_id was determined, get the file path
    if file_id:
        file_info = bot.get_file(file_id)
        file_path = file_info.file_path

        # Construct the full URL
        file_url = BASE_URL + file_path

        response = yandex_disk.upload_file(file_path.split('/')[-1], file_url)
        if response.status_code == 202:
            response_json = response.json()
            bot.send_message(message.chat.id, f"Файл загружен: {response_json['href']}")

    try:
        if user_input_text is None:
            user_input_text = message.text
    except:
        pass

    logger.info(f"User input text: {user_input_text}")
    logger.info(f"Document type: {message.content_type}")
    logger.info(f"User input image path: {file_id}")


def start_bot():
    logger.info(f"bot `{str(bot.get_me().username)}` has started")
    bot.polling()
