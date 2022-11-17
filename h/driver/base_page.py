import random
from time import sleep

from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait


class BasePage:

    def __init__(self, driver):
        self.driver = driver
        self._verify_page()

    def _verify_page(self):
        pass

    def on_this_page(self, *args):
        for element_name in args:
            self.get_element(element_name)

    def hover_element(self, locator):
        element = self.get_clickable_element(locator)
        hover = ActionChains(self.driver).move_to_element(element)
        hover.perform()

    def click_on(self, element_name, section=None):
        try:
            # self.hover_element(element_name)
            self.get_clickable_element(element_name).click()
        except StaleElementReferenceException:
            sleep(0.1)
            self.get_clickable_element(element_name).click()

    def click_on_while(self, element_name, section=None):
        element=self.get_clickable_element(element_name)
        for i in range(10):
            try:
                # self.hover_element(element_name)
                element.click()
                break
            except Exception:
                sleep(0.1)


    def type_in(self, element_name, text):
        self.click_on_while(element_name)
        # self.get_element(element_name).clear()
        self.get_element(element_name).send_keys(text)

    def type_in_clear(self, element_name, text):
        self.click_on_while(element_name)
        self.get_element(element_name).clear()
        self.get_element(element_name).send_keys(text)

    def select_by_text(self, element_name, text):
        select = Select(self.get_element(element_name))
        try:
            select.select_by_visible_text(text)
        except (TimeoutException, NoSuchElementException):
            select.select_by_value(text)

    def get_text(self, element_name):
        return self.get_element(element_name).text

    def get_element_by_name(self, element):
        if type(element) is str:
            if element.startswith('//') or element.startswith('(//'):
                return (By.XPATH, element)
            else:
                return (By.XPATH, f'//*[contains(text(),"{element}")]|//*[contains(@value,"{element}")]')
        return element

    def switch_to_frame(self, frame):
        return WebDriverWait(self.driver, 10).until(ec.frame_to_be_available_and_switch_to_it(frame))

    def get_element(self, element_name, timeout=5):
        # sleep(random.randint(1,2))
        locator = self.get_element_by_name(element_name)
        expected_condition = ec.presence_of_element_located(locator)
        result = WebDriverWait(self.driver, timeout).until(
            expected_condition,
            message=f'Не могу найти {element_name} в течение {timeout} сек')
        return result

    def get_elements(self, element_name, timeout=50):
        locator = self.get_element_by_name(element_name)
        expected_condition = ec.presence_of_all_elements_located(locator)
        return WebDriverWait(self.driver, timeout).until(
            expected_condition,
            message=f'Не могу найти ни одного элемента {element_name} в течение {timeout} сек')

    def get_clickable_element(self, element_name, timeout=50):
        locator = self.get_element_by_name(element_name)
        expected_condition = ec.element_to_be_clickable(locator)
        return WebDriverWait(self.driver, timeout).until(
            expected_condition,
            message=f'Не могу найти {element_name} в течение {timeout} сек')

    def get_element_in_section(self, locator_name, section_name):
        section_name = section_name if section_name.endswith('section') else f'{section_name} section'
        section_element = self.get_element(section_name)
        if self.get_element_by_name(locator_name)[0] == 'xpath':
            try:
                return section_element.find_element_by_xpath(
                    f'.{self.get_element_by_name(locator_name)[1]}')
            except NoSuchElementException:
                raise RuntimeError(f'Unable to locate {locator_name} in {section_name}')
        else:
            raise RuntimeError('Use XPATH locator only for section element')

    def is_element_displayed(self, element_name, timeout=5):
        try:
            self.get_element(element_name, timeout=timeout)
            return True
        except TimeoutException:
            return False

    def is_element_invisible(self, element_name, timeout=5):
        locator = self.get_element_by_name(element_name)
        try:
            expected_condition = ec.invisibility_of_element_located(locator)
            WebDriverWait(self.driver, timeout).until(
                expected_condition,
                message=f'Элемент {element_name} отображается в течение {timeout} сек"')
            return True
        except TimeoutException:
            return False
