from selenium import webdriver
import selenium
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common import desired_capabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time
import json



class Application:
    def __init__(self, request) -> None:

        self.__url__ = "https://www.youtube.com/results?search_query=" # ссылка для ввода запроса
        self.request = request.replace(" ", "+") # меняем пробелы на + для запроса

        self.options = webdriver.ChromeOptions() # Загружаем Хромиум
        self.options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36") # Подгружаем Юзер-Агент
        self.options.add_argument("--disable-blink-features=AutomationControlled") # предотвращает появление предупреждающего сообщения
        self.options.add_argument('--log-level=3') # Логирование | Записывать ошибки, предупреждения и информационные сообщения (по умолчанию)
        self.options.page_load_strategy = 'eager' # Делаем частичную подгрузку для ускорения процесса (Если убрать эту строчку будет ждать фулл подгрузку страницы)



        self.service = Service(ChromeDriverManager().install()) # Устанавливаем WebDriver под хром
        self.browser = webdriver.Chrome(options=self.options, service=self.service) # Запускаем наши настройки + загруженный хромиум
        self.browser.maximize_window() # Далем во все окно
    
    def run(self) -> None: # Функция запуска
        """
            Running the program
        """
        print('[!] Открываю youtube.com')
        self.__open_url() # Открывает ссылку с запросом
        time.sleep(1) # Спим 1 секунду
        
        print('[!] Начинаю подгрузку куков')
        self.__load_cookie() # Подгружаем куки
        time.sleep(5) # Спим 5 секунд
        
        print('[!] Проверяю авторизацию')
        status = self.__check_auth() # Проверяем авторицию | Возращает bool
        if not status:
            print('[-] Ваши куки невалидные')
            return
        print('[+] Авторизация прошла')

        print('[!] Собираю видео со страницы...')
        videos = self.__parse_videos() # Парсим видео | Возврощает list


        if not videos:
            print('[-] Не смог спарсить видео')
            return
        
        if len(videos) < 6:
            print('[!] Перехожу на последнее видео по запросу')
            video = videos[-1] # Берем последнее видео т.к длина videos меньше 6
        else:
            print('[!] Перехожу на 6 видео по запросу')
            video = videos[5] # Берем 5 индекс (6 видео)
        
        video.click() # Нажимаем на видео
        time.sleep(5) # Спим 5 секунд
        
        print('[!] Лайкаю видео')
        status_like = self.__set_like() # Ставим лайк | True - лайк поставлен | False - лайка нет
        if status_like: # Проверяем status лайка
            print('[+] Лайк отправлен')
        else:
            print('[-] Не смог поставить лайк')
        time.sleep(1) # Спим 1 секунду
        
        print('[!] Пытаюсь подписаться...')
        status_sub = self.__subscribe() # Подписываемся | True - подписан | False - подписки нет
        if status_sub:
            print('[+] Оформил подписку')
        else:
            print('[-] Не смог подписаться')

        input()

        



    def __load_cookie(self) -> None: # Загрузка куков
        """
            Cookie loading
        """
        with open('cookie.txt', "r", encoding="utf8") as f: # Открываем файл для чтения с кодировкой utf8
            try:
                lines = json.loads(f.read()) # Читаем файл + декодирования строки, содержащей данные в формате JSON
            except:
                print('[-] Неверный формат куков')
                raise
        
        for line in lines: # Идем циклом по каждому куку
            name = line['name'] # Имя кука
            value = line['value'] # Значение кука
            self.browser.add_cookie({'name': name, 'value': value}) # Подгружаем в куки селениума

        self.browser.refresh() # Обновляем страничку

    def __check_auth(self) -> bool: # Проверка авторизации | Возврощает bool
        """
            Authorization check

            :rtype: bool
        """
        element = self.browser.find_element(By.XPATH, "//div[@class='yt-spec-touch-feedback-shape__fill']").text # Проверяем на наличие кнопки "Войти" Если есть False иначе True
        if element:
            return False
        return True

    def __set_like(self) -> bool: # Ставим лайк | Возврощает bool
        """
            As function that puts like function that puts likes

            :rtype: bool
        """
        # Ищет элемент лайка <button class='...'>
        button_like = self.browser.find_element(By.XPATH, "//button[@class='yt-spec-button-shape-next yt-spec-button-shape-next--tonal yt-spec-button-shape-next--mono yt-spec-button-shape-next--size-m yt-spec-button-shape-next--icon-leading yt-spec-button-shape-next--segmented-start ']")
        button_like.click() # Нажимает по элементу
        # Ищет элемент лайка <button class='...'> + достает значение из атрибута чтобы проверить true или false
        status_like = self.browser.find_element(By.XPATH, "//button[@class='yt-spec-button-shape-next yt-spec-button-shape-next--tonal yt-spec-button-shape-next--mono yt-spec-button-shape-next--size-m yt-spec-button-shape-next--icon-leading yt-spec-button-shape-next--segmented-start ']").get_attribute('aria-pressed')
        return status_like == 'true'
    
    def __subscribe(self) -> bool: # Подписка | Возрощает bool
        """
            Function for subscribing to the channel

            :rtype: bool
        """
        # Ищет кнопку подписаться <button class='...'>
        button_sub = self.browser.find_element(By.XPATH, "//button[@class='yt-spec-button-shape-next yt-spec-button-shape-next--filled yt-spec-button-shape-next--mono yt-spec-button-shape-next--size-m ']")
        try:
            button_sub.click() # Нажимает на кнопку
            return True
        except:
            return False


        

    def __open_url(self) -> None: # Функция открытия ссылки (запроса)
        """
            Opening a link with request
        """
        self.browser.get(self.__url__+self.request) # гетаем ссылка_ютуба+наш_запрос

    
    def __parse_videos(self) -> list: # Парсинг видео | List
        # Ищет тег <ytd-video-renderer>
        """
            Video parser YT

            :rtype: list of WebElement
        """
        videos = self.browser.find_elements(By.XPATH, "//ytd-video-renderer[@bigger-thumbs-style='DEFAULT']")
        return videos
