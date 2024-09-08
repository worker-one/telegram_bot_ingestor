import logging
import os
import re
import requests


class YandexDisk:
    def __init__(self, token: str = None, email: str = None): 
        if token is None:
            self.token = os.getenv("YANDEX_API_TOKEN")
            if self.token is None:
                raise ValueError(f"Environment variable YANDEX_API_TOKEN is not set")
        else:
            self.token = token
        if email is None:
            self.email = os.getenv("YANDEX_EMAIL_ACCOUNT")
            if self.email is None:
                raise ValueError(f"Environment variable YANDEX_EMAIL_ACCOUNT is not set")
            logging.info(f"Connecting to yandex disk {self.email}")

    def _prepare_folder_name(self, input_string: str) -> str:
        result = re.sub(r'[^а-яA-Яa-zA-Z0-9]', '-', input_string)
        result = result.replace('--', '-')
        return result

    def create_folder(self, folder_name: str):
        base_url = "https://cloud-api.yandex.net/v1/disk/resources"
        folder_name = self._prepare_folder_name(folder_name)
        params = {
            "path": folder_name
        }
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/hal+json",
            "Authorization": f"OAuth {self.token}"
        }

        response = requests.put(base_url, headers=headers, params=params)

        return folder_name

    def upload_file(self, file_path: str, url: str):
      base_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
      params = {
          "path": file_path,
          "url": url
      }
      headers = {
          "Content-Type": "application/json",
          "Accept": "application/hal+json",
          "Authorization": f"OAuth {self.token}"
      }

      response = requests.post(base_url, headers=headers, params=params)

      return response
