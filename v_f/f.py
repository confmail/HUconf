from datetime import datetime, timezone
import logging
import random

import undetected_chromedriver as uc
from time import sleep

import os, sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))

from utils import telegram
from driver.base_page import BasePage

from selenium import webdriver


class France(BasePage):
    pass


if __name__ == "__main__":
    options = webdriver.ChromeOptions()
    options.headless = True
    driver = uc.Chrome(options=options)
    for i in range(4):
        try:

            start_time_dict = {'0': '59/59.5', '1': '00/00.0', '2': '00/00.0', '3': '00/00.0'}

            time = datetime.strptime(
                f'{datetime.now(tz=timezone.utc).strftime("%m/%d/%Y/%H")}/{start_time_dict[str(i)]}',
                '%m/%d/%Y/%H/%M/%S.%f')

            logging.warning(i)
            driver.delete_all_cookies()
            driver.get(sys.argv[1])
            f = France(driver)
            if 'Bad Gateway' not in driver.page_source:
                f.click_on('Доступ к услугам')
                if f.is_element_displayed('//button[text()="Нет"]'):
                    f.click_on('//button[text()="Нет"]')
                f.click_on('Подтвердить')
                f.click_on('Я прочитал')
                logging.warning('Жду время')
                while True:
                    dt = datetime.strptime(datetime.now(tz=timezone.utc).strftime('%m/%d/%Y/%H/%M/%S.%f'),
                                           '%m/%d/%Y/%H/%M/%S.%f')
                    if time <= dt:
                        logging.warning(f'dt:{dt}')
                        break
                f.click_on('Назначить встречу')
                if f.is_element_displayed('//section/div'):
                    telegram.send_doc('🇫🇷 Ф появилась дата', driver.page_source)
                    f.click_on('//section/div')
                    while True:
                        if f.is_element_displayed(
                                '//p[contains(text(),"К сожалению, все наши слоты зарезервированы")]'):
                            sleep(5)
                            driver.refresh()
                            if f.is_element_displayed('//section/div'):
                                f.click_on('//section/div')
                        else:
                            telegram.send_doc('🟢 🇫🇷 Ф появился слот', driver.page_source, debug=False)
                            sleep(random.randint(100, 120))
                            driver.quit()
                            break
                elif not f.is_element_displayed('На сегодня нет свободных мест.'):
                    telegram.send_doc(f'Ф({i}): Есть даты!', driver.page_source, debug=False)
                    sleep(random.randint(100, 120))
                else:
                    sleep(random.randint(100, 120))
                logging.warning('Ф нет дат')
                telegram.send_doc(f'Ф({i}): Нет дат!', driver.page_source, debug=False)
            else:
                telegram.send_doc(f'Ф({i}): Ошибка 502', driver.page_source, debug=False)
                sleep(random.randint(10, 20))
        except Exception as e:
            try:
                telegram.send_doc(f'Ф({i}): Неизвестная ошибка', driver.page_source, debug=False)
                sleep(random.randint(100, 120))
            except Exception as e:
                telegram.send_message(f'Ф({i}): Неизвестная ошибка\n{str(e)}', debug=False)
                sleep(random.randint(100, 120))
