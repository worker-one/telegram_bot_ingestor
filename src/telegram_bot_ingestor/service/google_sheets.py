import os
from typing import List

import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials


def create_keyfile_dict() -> dict[str, str]:
    """ Create a dictionary with keys for the Google Sheets API from environment variables

    Returns:
        Dictionary with keys for the Google Sheets API
    Raises:
        ValueError: If any of the environment variables is not set
    """
    variables_keys = {
        "type": os.getenv("TYPE"),
        "project_id": os.getenv("PROJECT_ID"),
        "private_key_id": os.getenv("PRIVATE_KEY_ID"),
        "private_key": os.getenv("PRIVATE_KEY").replace('\\n', '\n'),
        "client_email": os.getenv("CLIENT_EMAIL"),
        "client_id": os.getenv("CLIENT_ID"),
        "auth_uri": os.getenv("AUTH_URI"),
        "token_uri": os.getenv("TOKEN_URI"),
        "auth_provider_x509_cert_url": os.getenv("AUTH_PROVIDER_X509_CERT_URL"),
        "client_x509_cert_url": os.getenv("CLIENT_X509_CERT_URL")
    }
    for key in variables_keys:
        if variables_keys[key] is None:
            raise ValueError(f"Environment variable {key} is not set")
    return variables_keys


class GoogleSheets:
    def __init__(self, share_emails: List[str] = None):
        self.keyfile_dict = create_keyfile_dict()
        self.scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        self.creds = ServiceAccountCredentials.from_json_keyfile_dict(keyfile_dict=self.keyfile_dict, scopes=self.scope)
        self.client = gspread.authorize(self.creds)
        self.share_emails = share_emails

    def _prepare_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """ Convert not JSON serializable columns into string """
        for column in df.columns:
            df[column] = df[column].astype(str)
        return df

    def set_sheet(self, sheet_name: str):
        try:
            self.sheet = self.client.open(sheet_name)
        except:
            raise Exception(f"Sheet {sheet_name} not found")

    def get_table_names(self) -> List[str]:
        """ Get the names of the worksheets in the Google Sheet """
        return [worksheet.title for worksheet in self.sheet.worksheets()]
    
    def get_header(self, table_name: str) -> List[str]:
        """ Get the headers of a specific worksheet """
        worksheet = self.sheet.worksheet(table_name)
        df = pd.DataFrame(worksheet.get_all_records())
        return df.columns.tolist()

    def import_dataframe(self, df: pd.DataFrame, worksheet_name: str) -> None:
        """
        Import a pandas DataFrame into a Google Sheet
        """
        try:
            worksheet = self.sheet.worksheet(worksheet_name)
        except gspread.WorksheetNotFound:
            worksheet = self.sheet.add_worksheet(worksheet_name, rows=1, cols=1)

        df = self._prepare_dataframe(df)

        worksheet.clear()
        worksheet.update([df.columns.values.tolist()] + df.values.tolist())

    def export_dataframe(self, worksheet_name: str) -> pd.DataFrame:
        """
        Export a Google Sheet into a pandas DataFrame
        """
        worksheet = self.sheet.worksheet(worksheet_name)
        df = pd.DataFrame(worksheet.get_all_records())
        return df

    def add_row(self, worksheet_name: str, row_data: List[Any]) -> None:
        """
        Add a row to the specified worksheet in the Google Sheet

        :param worksheet_name: The name of the worksheet to add the row to
        :param row_data: The data for the new row as a list
        """
        worksheet = self.sheet.worksheet(worksheet_name)
        worksheet.append_row(row_data, value_input_option="USER_ENTERED")
    