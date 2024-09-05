import logging
import os
from io import BytesIO

import telebot
from dotenv import find_dotenv, load_dotenv
from fastapi import UploadFile
from omegaconf import OmegaConf

from telegram_bot_ingestor.service.file_parser import FileParser
from telegram_bot_ingestor.service.fireworksai import FireworksLLM
from telegram_bot_ingestor.service.google_sheets import GoogleSheets
from telegram_bot_ingestor.service.utils import extract_json, extract_json_list
from telegram_bot_ingestor.service.yandex_disk import YandexDisk

config = OmegaConf.load("src/telegram_bot_ingestor/conf/config.yaml")

load_dotenv(find_dotenv(usecwd=True))  # Load environment variables from .env file
BOT_TOKEN = os.getenv("BOT_TOKEN")
YANDEX_API_TOKEN = os.getenv("YANDEX_API_TOKEN")

if BOT_TOKEN is None:
    logging.error("BOT_TOKEN is not set in the environment variables.")
    exit(1)

if YANDEX_API_TOKEN is None:
    logging.error("YANDEX_API_TOKEN is not set in the environment variables.")
    exit(1)

BASE_URL = f"https://api.telegram.org/file/bot{BOT_TOKEN}/"

cfg = OmegaConf.load("./src/telegram_bot_ingestor/conf/config.yaml")
bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)

yandex_disk = YandexDisk(YANDEX_API_TOKEN)
google_sheets = GoogleSheets(share_emails=cfg.google_sheets.share_emails)
file_parser = FileParser(max_file_size_mb=10, allowed_file_types={"txt", "doc", "docx", "pdf"})

if cfg.llm.provider == "fireworks":
    llm = FireworksLLM(cfg.llm.model_name, cfg.llm.prompt_template.ru)
else:
    logging.error("Invalid LLM provider in the configuration file.")
    exit(1)

try:
    google_sheets.set_sheet(config.google_sheets.sheet_name)
except:
    google_sheets.create_sheet(config.google_sheets.sheet_name)

import pandas as pd
df = pd.DataFrame({
	"Дата" : [],
	"Регион" : [],
	"Адрес" : [],
	"Кадастровый номер" : [],
	"Площадь ( ГА )" : [],
	"Цена" : [],
	"Под что участок (жилье, апарты, ижс, коммерция)" : [],
	"Описание (документы, ври, рнс, и прочее)": []
})

google_sheets.import_dataframe(df, "участки")

table_names = google_sheets.get_table_names()
worksheet_name = cfg.google_sheets.worksheet_name

logging.info(f"Table names: {table_names}")

@bot.message_handler(commands=['tables'])
def get_table_list(message: str) -> None:
    """
    Get the list of tables in the Google Sheet
    """
    table_names = google_sheets.get_table_names()
    if table_names:
        for table_name in table_names:
            table_columns = google_sheets.get_header(table_name)
            table_columns_str = "\n-".join(table_columns)
            bot.send_message(message.chat.id, f"{table_name}:\n -{table_columns_str}")
    else:
        bot.send_message(message.chat.id, "Таблиц не найдено")

@bot.message_handler(content_types=['text', 'document', 'photo'])
def process_user_input(message):

    # Determine the type of file received
    file_info = None
    text_content = None
    file_content = None

    if message.content_type == 'text':
        text_content = message.text

    if message.content_type == 'document':
        text_content = message.caption

        file = message.document
        file_info = bot.get_file(file.file_id)
        file_name = file.file_name
        downloaded_file = bot.download_file(file_info.file_path)

        # Extract content from the file
        try:
            upload_file = UploadFile(
                filename=file_name,
                file=BytesIO(downloaded_file),
                size=len(downloaded_file),
                headers={"content-type": file.mime_type}
            )

            file_content = file_parser.extract_content(upload_file)
            bot.send_message(message.chat.id, f"File content: {file_content}")
        except Exception as e:
            bot.send_message(message.chat.id, f"Error extracting file content: {str(e)}")


    if message.content_type == 'photo':
        # Get the highest resolution photo
        file = message.photo[-1]
        file_info = bot.get_file(message.photo[-1].file_id)
        file_name = file.file_id + ".jpg"

    # If file_id was determined, get the file path
    if file_info:
        # Construct the full URL
        file_url = BASE_URL + file_info.file_path

        response = yandex_disk.upload_file(file_name, file_url)
        if response.status_code == 202:
            response_json = response.json()
            bot.send_message(message.chat.id, f"Файл загружен: {response_json['href']}")
        else:
            bot.send_message(message.chat.id, f"Ошибка загрузки файла: {response.text}")

    if text_content or file_content:
        column_names = google_sheets.get_header(worksheet_name)
        response = llm.run(text_content=text_content, file_content=file_content, column_names=column_names)
        print(response)
        try:
            json_data = extract_json(response)
        except:
            json_data = extract_json_list(response)


        if isinstance(json_data, dict):
            bot.send_message(message.chat.id, str(json_data))
            google_sheets.add_row(worksheet_name, list(json_data.values()))

        if isinstance(json_data, list):
            bot.send_message(message.chat.id, str(json_data))
            for row in json_data:
                google_sheets.add_row(worksheet_name, list(row.values()))

        logging.info(f"User input text: {text_content}")
        logging.info(f"Document type: {message.content_type}")


def start_bot():
    logging.info(f"bot `{str(bot.get_me().username)}` has started")
    bot.polling()
