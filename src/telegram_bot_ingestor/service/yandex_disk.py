import os
import requests


class YandexDisk:
    def __init__(self, token: str = None): 
        if token is None:
            self.token = os.getenv("YANDEX_API_TOKEN")
            if self.token is None:
                raise ValueError(f"Environment variable YANDEX_API_TOKEN is not set")
        else:
            self.token = token
      
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