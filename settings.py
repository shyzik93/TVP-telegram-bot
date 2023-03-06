import os

import environ

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

env = environ.Env(
    DEBUG=(bool, True),
)
environ.Env.read_env(env_file=os.path.join(BASE_DIR, '.env'))

URL_KNOWLEDGE = env('URL_KNOWLEDGE')
TELEGRAM_TOKEN = env('TELEGRAM_TOKEN')