import base64
import logging
import sys
from datetime import datetime
from time import sleep

from bs4 import BeautifulSoup
from twocaptcha import TwoCaptcha

from utils import telegram


def get_code(html: str, page='not set') -> str:
    logging.warning(f'{datetime.now().strftime("%H:%M:%S")}: captcha page {page}')
    soup = BeautifulSoup(html, "lxml")
    image = soup.select("captcha > div")
    image = image[0]['style'].split("url('")[1].split("')")[0]
    errors = []
    try:
        return str(TwoCaptcha(sys.argv[6]).normal(image)['code'])
        # ref.push().set({'code': code, 'image': image_base64})
    except Exception as e:
        logging.warning(f'captcha error: {str(e)}')
        if 'ERROR_ZERO_BALANCE' in str(e):
            telegram.send_message(f'Ошибка TwoCaptcha: Timeout 5 минут: {str(e)}')
            sleep(300)
            print(f'{datetime.now()} error: ERROR_ZERO_BALANCE')
            return None
        elif 'ERROR_CAPTCHA_UNSOLVABLE' in str(e):
            print(f'{datetime.now()} error: ERROR_CAPTCHA_UNSOLVABLE')
            return None
        else:
            telegram.send_message(f'Неизвестная Ошибка TwoCaptcha: {str(e)}')
            errors.append(str(e))


def get_code_selenium(context, image_name: str, page='not set'):
    try:
        code = str(TwoCaptcha(context.api_key).normal(image_name)['code'])
    except Exception as e:
        logging.warning(f'captcha error')
        if 'ERROR_ZERO_BALANCE' in str(e):
            telegram.send_message(f'Ошибка TwoCaptcha: Timeout 5 минут: {str(e)}')
            sleep(300)
        elif 'ERROR_CAPTCHA_UNSOLVABLE' in str(e):
            return None
        else:
            telegram.send_message(f'Ошибка TwoCaptcha: {str(e)}')
        code = None
    return code


def is_captcha_displayed(html: str):
    soup = BeautifulSoup(html, "lxml")
    image = soup.select("captcha > div")
    if image:
        try:
            image = image[0]['style'].split("url('")[1].split("')")[0]
            base64.b64decode(image.split(',')[1])
            return True
        except Exception:
            result = False
    else:
        result = False
    return result
