import os
from dotenv import load_dotenv

# Load .env file from parent directory
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

# Get the parent directory (where .env is located)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

class Config:
    # PDF_FOLDER_PATH = os.environ.get('PDF_FOLDER_PATH', 'pdf')
    # CSV_FOLDER_PATH = os.environ.get('CSV_FOLDER_PATH', 'csv')
    # TEMP_FOLDER = os.environ.get('TEMP_FOLDER', 'temp')
    # PORT = int(os.environ.get('PORT', 5000))
    # DEBUG = os.environ.get('DEBUG', 'False') == 'True'
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DB_URI', 'sqlite:///web.db')
    # SQLALCHEMY_TRACK_MODIFICATIONS = False
    # USER = os.environ.get("USER", "Oline")
    # TESSERACT_CMD_PATH = os.path.join(project_root, 'Tesseract-OCR', 'tesseract.exe')
    PDF_FOLDER_PATH = 'pdf'
    CSV_FOLDER_PATH = 'csv'
    TEMP_FOLDER = 'temp'
    EXCEL_FOLDER_PATH = 'excel'
    PORT = '9090'
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///web.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    USER = "Olineee"
    TESSERACT_CMD_PATH = os.path.join(project_root, 'Tesseract-OCR', 'tesseract.exe')