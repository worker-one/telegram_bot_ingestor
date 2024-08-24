""" Application that provides functionality for the Telegram bot. """
import logging.config
import os

from dotenv import find_dotenv, load_dotenv
from omegaconf import OmegaConf

load_dotenv(find_dotenv(usecwd=True))  # Load environment variables from .env file

# Load logging configuration with OmegaConf
logging_config = OmegaConf.to_container(OmegaConf.load("./src/telegram_bot_ingestor/conf/logging_config.yaml"), resolve=True)

# Apply the logging configuration
logging.config.dictConfig(logging_config)

# Configure logging
logger = logging.getLogger(__name__)

class FireworksLLM:
    def __init__(self, model_name: str, prompt_template: str):
        import fireworks.client
        API_KEY = os.getenv("FIREWORKS_API_KEY")
        if API_KEY is None:
            logger.error("FIREWORKS_API_KEY is not set in the environment variables.")
            raise ValueError("FIREWORKS_API_KEY is not set in the environment variables.")
        self.client = fireworks.client
        self.model_name = model_name
        fireworks.client.api_key = API_KEY
        self.prompt_template = prompt_template

    def run(
            self,
            text_content: str,
            file_content: str,
            column_names: list[str]):
        """Run the LLM model with the given query and document."""
        completion = self.client.ChatCompletion.create(
            model=self.model_name,
            messages=[
                {
                    "role": "user",
                    "content": self.prompt_template.format(
                        text_content=text_content,
                        file_content=file_content,
                        column_names=','.join(column_names)
                    )
                }
            ],
            max_tokens=500,
            temperature=0.5,
            presence_penalty=0,
            frequency_penalty=0,
            top_p=1,
            top_k=40
        )
        return completion.choices[0].message.content