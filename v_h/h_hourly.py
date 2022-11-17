import logging
from datetime import datetime, timezone

import undetected_chromedriver as uc
from time import sleep

import os, sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))

from utils import telegram, gsheets
from driver.base_page import BasePage
from selenium import webdriver


class Hungary(BasePage):
    pass


gs = gsheets.GoogleSheets('hungary')
id_email, email, password, name, date, phone, passport = gs.ws.get_all_values()[104]


def register(thread):
    try:
        time = datetime.strptime(
            f'{datetime.utcnow().date().strftime("%m/%d/%Y")}/{datetime.utcnow().hour+1}/00', '%m/%d/%Y/%H/%M')
        options = webdriver.ChromeOptions()
        options.headless = True
        options.add_argument('--blink-settings=imagesEnabled=false')
        driver = uc.Chrome(options=options)
        driver.delete_all_cookies()

        driver.get(sys.argv[3])
        f = Hungary(driver)
        logging.warning('Создали драйвер. Открыли сайт')
        for i in range(3):
            if not f.is_element_displayed('//button[@id="langSelector"]') or not f.is_element_displayed('//input[@id="birthDate"]'):
                driver.refresh()
                sleep(3)
            else:
                break
        else:
            telegram.send_doc(caption=f'{name} Не прогрузился язык или дата', html=driver.page_source)
            raise  RuntimeError(f'Не прогрузился язык или дата {name}')

        f.click_on_while('//button[@id="langSelector"]')
        while True:
            if f.is_element_displayed('//div[@class="dropdown-menu language show"]//img[@alt="Русский"]'):
                f.click_on('//img[@alt="Русский"]')
                logging.warning('Выбрали язык')
                break
            else:
                logging.warning('Глюк селектора выбора языка.Еще заход')
                f.click_on('//button[@id="langSelector"]')

        while True:
            try:
                f.click_on('//label[text()="Место предоставления услуги"]/..//button[text()="Выбор места"]')
                break
            except Exception as e:
                sleep(0.1)
        while True:
            try:
                f.type_in('//input[@placeholder="Поиск"]', 'Беларусь')
                break
            except Exception as e:
                sleep(0.1)
        f.click_on_while('//label[text()="Беларусь - Минск"]')
        logging.warning('Выбрали Беларусь')
        f.click_on_while('//label[text()="Тип дела"]/..//button[text()="Добавление типа услуги"]')
        f.type_in('//h5[text()="Типы дел"]/../..//input[@placeholder="Поиск"]', 'типа С')
        f.click_on_while('//label[contains(text(),"Заявление о выдаче визы (краткосрочная шенгенская виза типа С)")]')
        f.click_on_while('Сохранить')
        logging.warning('Выбрали Тип услуги')
        f.type_in('//input[@id="label4"]', name)
        logging.warning(f'Ввод имя: {name}')
        f.type_in('//input[@id="birthDate"]', date.replace('.','/'))
        logging.warning('Ввод рождение')
        f.type_in('//input[@id="label9"]', phone)
        logging.warning('Ввод телефон')
        f.type_in('//input[@id="label10"]', email)
        logging.warning('Ввод почта')
        f.type_in('//input[@id="label1000"]', passport)
        logging.warning('Ввод паспорт')
        sleep(2)
        while True:
            try:
                f.click_on('//input[@id="slabel13"]')
                break
            except Exception as e:
                sleep(0.1)
        try:
            f.click_on('//button[text()="Перейти  к выбору времени"]')
        except Exception:
            pass
        while True:
            try:
                f.click_on('//input[@id="label13"]')
                break
            except Exception as e:
                sleep(0.1)
        logging.warning('Поставили галки')
        logging.warning('Жду время')
        while True:
            dt = datetime.strptime(datetime.now(tz=timezone.utc).strftime('%m/%d/%Y/%H/%M'), '%m/%d/%Y/%H/%M')
            if time <= dt:
                logging.warning(f'dt:{dt}')
                break
        while True:
            try:
                f.click_on('//button[text()="Перейти  к выбору времени"]')
                break
            except Exception as e:
                sleep(0.1)
        dt = datetime.strptime(datetime.now(tz=timezone.utc).strftime('%m/%d/%Y/%H/%M'), '%m/%d/%Y/%H/%M')
        logging.warning(f'Нажали выбор даты:{dt}')
        telegram.send_image('В неизвестная ошибка', driver)
        if f.is_element_displayed('//span[text()="Свободно"]'):
            logging.warning(f'Есть даты')
            while True:
                try:
                    f.click_on('(//span[text()="Свободно"])[last()]')
                    break
                except Exception as e:
                    logging.warning('click')
                    sleep(0.1)
            # тут похоже начинает работать бан, кнопка не всегда работает, нужно переключать ip
            # может попробовать рандомом кликать по элементам, перемотка вроде помогает немного
            # element3 = driver.find_element(By.ID, 'nextTo3')
            # driver.execute_script("arguments[0].scrollIntoView();", element3)
            logging.warning('Выбрали дату')
            while True:
                try:
                    f.click_on('//button[@id="nextTo3"]')
                    break
                except Exception as e:
                    sleep(0.1)
            logging.warning('Нажали далее')
            # telegram.send_message(f'{thread}: {datetime.now()}')
            telegram.send_doc(f'🟢В. Перед завершением бронирования {name}',driver.page_source)
            sleep(90)
            f.click_on_while('Завершение бронирования')
            dt = datetime.strptime(datetime.now(tz=timezone.utc).strftime('%m/%d/%Y/%H/%M'), '%m/%d/%Y/%H/%M')
            logging.warning(f'ЗАПИСАН:({name}): {dt}')
            sleep(10)
            telegram.send_doc(f'🟢В: в {dt} успешно зарегистрирован({name})', driver.page_source)
        else:
            logging.warning(f'Нет дат')
            if f.is_element_displayed('//div[text()="Обращаем Ваше внимание, что у Вас уже есть действующая запись для решения данного вопроса."]'):
                telegram.send_doc(f'В {name} уже зареген другим сеансом', driver.page_source)
                logging.warning('Уже зареген')
                driver.close()
            else:
                logging.warning('Нет дат2')
                telegram.send_doc(f'🔴 В для:{name} нет дат', driver.page_source)
                if f.is_element_displayed('//button[text()="Хорошо"]'):
                    while True:
                        try:
                            f.click_on('//button[text()="Хорошо"]')
                            break
                        except Exception as e:
                            sleep(0.1)
    except Exception as e:
        try:
            telegram.send_image(driver, f'В неизвестная ошибка {str(e)}')
        except Exception as e:
            telegram.send_message(f'В Driver убит {str(e)}')


if __name__ == "__main__":
    register('1')
