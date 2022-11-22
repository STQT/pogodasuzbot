import os

from pathlib import Path
from dotenv import load_dotenv
from aiogram.contrib.middlewares.i18n import I18nMiddleware

load_dotenv()


BASE_DIR = Path(__file__).parent
LOCALES_DIR = BASE_DIR / 'locales'
I18N_DOMAIN = 'mybot'
i18n = I18nMiddleware(I18N_DOMAIN, LOCALES_DIR)
TOKEN = os.getenv('TOKEN')
OWM_TOKEN = os.getenv('OWM_TOKEN')
