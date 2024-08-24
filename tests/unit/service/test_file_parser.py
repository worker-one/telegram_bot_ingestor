import pytest
from fastapi import UploadFile
from telegram_bot_ingestor.service.file_parser import FileParser

@pytest.fixture
def file_parser():
    return FileParser(max_file_size_mb=10, allowed_file_types={"txt", "doc", "docx", "pdf"})

def test_extract_txt_content(file_parser):
    with open("tests/unit/mock/shoes.txt", "rb") as f:
        upload_file = UploadFile(
            filename="shoes.txt",
            file=f,
            size=len(f.read()),
            headers={"content-type": "text/plain"}
        )

        content = file_parser.extract_txt_content(upload_file)
        assert "Kiprun" in content

def test_extract_word_content(file_parser):
    with open("tests/unit/mock/shoes.docx", "rb") as f:
        file = UploadFile("shoes.docx", file=f)
        content = file_parser.extract_word_content(file)
        assert "Kiprun" in content

def test_extract_pdf_content(file_parser):
    with open("tests/unit/mock/shoes.pdf", "rb") as f:
        file = UploadFile("shoes.pdf", file=f)
        content = file_parser.extract_pdf_content(file)
        assert "Kiprun" in content

def test_extract_content(file_parser):
    with open("tests/unit/mock/shoes.docx", "rb") as f:
        file = UploadFile("shoes.docx", file=f)
        content = file_parser.extract_content(file)
        assert "Kiprun" in content