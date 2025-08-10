import json
import os.path
import pickle
import platform
import socket
import time
from typing import Dict, List, Any
from urllib.parse import urlparse

from loguru import logger
from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class ATrustLoginStorage(BaseModel):
    cookies: List[Dict[str, Any]]
    local_storage: Dict[str, Any]

class ATrustLogin:
    def __init__(self, portal_address, driver_path=None, browser_path=None, driver_type=None, data_dir="data", interactive=False, input_delay=0.5, loading_delay=5):
        self.initialized = False
        if not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)
        self.data_dir = data_dir
        self.interactive = interactive
        self.portal_address = portal_address
        self.input_delay = input_delay
        self.loading_delay = loading_delay

        self.must_be_logged_keywords = ['app_center', 'user_info', 'app_apply', 'device_manage']
        self.must_not_logged_keywords = ['login', 'captcha']

        if driver_type is None:
            system = platform.system()
            if system == "Windows":
                driver_type = "edge"
            else:
                driver_type = "chrome"

        logger.debug(f"Driver: {driver_type}: {driver_path}")

        if driver_type == "edge":
            from selenium.webdriver.edge.options import Options
            from selenium.webdriver.edge.service import Service
        else :
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.chrome.options import Options

        # 配置Edge Driver选项
        self.options = Options()

        # self.options.add_argument(f'--user-data-dir="{data_dir}"')
        self.options.add_argument(f'--profile-directory=ATrustLogin')
        # options.add_argument("--start-maximized")
        self.options.add_argument("--ignore-certificate-errors")
        self.options.add_argument("--ignore-ssl-errors")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--lang=zh-CN")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--disable-extensions")
        self.options.add_argument("--window-size=896,672")

        self.options.add_experimental_option("prefs", {"intl.accept_languages": "zh-CN"})

        if browser_path is not None:
            self.options.binary_location = browser_path

        # 初始化Edge Driver
        service = Service(driver_path)

        if driver_type == "edge":
            self.driver = webdriver.Edge(service=service, options=self.options)
        else :
            self.driver = webdriver.Chrome(service=service, options=self.options)

        self.wait = WebDriverWait(self.driver, 10)

    # 打开默认的portal地址
    def open_portal(self):
        self.driver.get(self.portal_address)

    def wait_login_page(self):
        self.wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

    def delay_input(self):
        time.sleep(self.input_delay)

    def delay_loading(self):
        time.sleep(self.loading_delay)

    # 输入用户名和密码
    def enter_credentials(self, username, password):
        try:
            element = self.driver.find_element(By.XPATH, "//div[contains(@class, 'server-name') and contains(text(), '本地密码')]")
            if element.is_displayed():
                self.delay_input()
                self.scroll_and_click(element)
        except:
            pass

        self.wait.until(EC.element_to_be_clickable((By.ID, "userName")))
        username_input = self.driver.find_element(By.ID, "userName")

        self.wait.until(EC.element_to_be_clickable((By.ID, "password")))
        password_input = self.driver.find_element(By.ID, "password")

        # 输入用户名和密码
        self.scroll_and_click(username_input)
        self.delay_input()
        username_input.clear()
        username_input.send_keys(username)

        self.scroll_and_click(password_input)
        self.delay_input()
        password_input.clear()
        password_input.send_keys(password)

        logger.debug("Filled username and password")

    # 查找并点击登录按钮
    def click_login_button(self):
        self.scroll_and_click(self.driver.find_element(By.ID, "loginBtn"))

    def load_storage(self):
        # 从pickle文件中加载存储的数据
        try:
            if os.path.exists(os.path.join(self.data_dir, "ATrustLoginStorage.pkl")):
                with open(os.path.join(self.data_dir, "ATrustLoginStorage.pkl"), "rb") as f:
                    data = pickle.load(f)
                    # 从cookies中加载cookie
                    for cookie in data.cookies:
                        self.driver.delete_cookie(cookie['name'])
                        self.driver.add_cookie(cookie)
                    # 从local_storage中加载local storage
                    for key, value in data.local_storage.items():
                        key_js = json.dumps(key)
                        value_js = json.dumps(value)
                        self.driver.execute_script(f"window.localStorage.setItem({key_js}, {value_js});")
                    logger.info("Loaded storage data")
        except FileNotFoundError:
            logger.info("未找到存储的数据")

    def scroll_to(self, element):
        self.driver.execute_script("arguments[0].scrollIntoView();", element)

    def scroll_and_click(self, element):
        self.driver.execute_script("arguments[0].scrollIntoView();", element)
        element.click()
        return element

    def require_interact(self):
        if self.interactive:
            input("Press any key to continue")
        else:
            raise Exception("User Interact required")

    def init(self):
        if not self.initialized:
            self.open_portal()
            self.wait_login_page()
            self.delay_loading()
            self.load_storage()
            self.initialized = True

    def login(self, username, password):
        self.init()

        if self.is_logged():
            logger.info("Already logged in")
            return True

        self.enter_credentials(username=username, password=password)
        self.delay_input()
        self.click_login_button()

        logger.info("Performed basic login action")

        self.delay_loading()

        if self.is_logged():
            logger.info("Login Success")
            self.update_storage()
            return True

    def is_logged(self):
        """
        检查是否已经登录
        :return: None if not sure, True if logged, False if not logged
        """

        if self.driver.current_url.startswith('about:'):
            return None

        url = urlparse(self.driver.current_url)

        if any(keyword in url.fragment for keyword in self.must_be_logged_keywords):
            return True
        if any(keyword in url.fragment for keyword in self.must_not_logged_keywords):
            return False

        return "工作台" in self.driver.page_source and "本地密码" not in self.driver.page_source

    def close(self):
        self.driver.quit()

    def __enter__(self):
        return self

    def update_storage(self):
        data = ATrustLoginStorage(
            cookies=self.driver.get_cookies(),
            local_storage=self.driver.execute_script("return window.localStorage")
        )

        # save with pickle
        with open(os.path.join(self.data_dir, "ATrustLoginStorage.pkl"), "wb") as f:
            pickle.dump(data, f)

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    @staticmethod
    def wait_for_port(port, host='localhost', loading_delay=5):
        while True:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                try:
                    s.connect((host, port))
                    logger.info(f"Detected aTrust is listening on port {port}")
                    s.close()
                    break
                except (socket.timeout, ConnectionRefusedError):
                    logger.info(f"aTrust Port {port} is not yet being listened on. Waiting for aTrust start ...")
                    time.sleep(loading_delay)

def main(username, password, portal_address="https://passport.escience.cn/oauth2/authorize?theme=arp_2018&client_id=59145&redirect_uri=https%3A%2F%2F159.226.243.221%3A443%2Fpassport%2Fv1%2Fauth%2FhttpsOauth2%3FsfDomain%3DOAuth&response_type=code", keepalive=200, data_dir="./data", driver_type=None, driver_path=None, browser_path=None, interactive=False, wait_atrust=True, input_delay=0.5, loading_delay=5):
    logger.info("Opening Web Browser")

    if wait_atrust:
        ATrustLogin.wait_for_port(54631, loading_delay=loading_delay)

    # 创建ATrustLogin对象
    at = ATrustLogin(data_dir=data_dir, portal_address=portal_address, driver_type=driver_type, driver_path=driver_path, browser_path=browser_path, interactive=interactive, input_delay=input_delay, loading_delay=loading_delay)

    at.init()

    while True:
        try:
            if not at.is_logged():
                logger.info("Session lost. Trying to login again ...")
                at.open_portal()
                at.delay_loading()
                if at.login(username=username, password=password) is True:
                    at.delay_loading()
                    at.delay_loading()

            if keepalive <= 0:
                at.close()
                exit(0)
            else:
                time.sleep(keepalive)
                at.open_portal()
                at.delay_loading()
        except Exception as e:
            logger.error("An error occurred when trying to login, retrying ...")
            logger.exception(e)
            at.delay_loading()

if __name__ == "__main__":
    from fire import Fire
    Fire(main)
