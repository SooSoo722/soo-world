from selenium.webdriver import Edge
from selenium.webdriver import EdgeOptions
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webelement import WebElement as WW
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from subprocess import CREATE_NO_WINDOW

from typing import Final
import io
import sys


# ! web driver 클래스
class Web_driver():
    # * 드라이버 종류
    driver: Edge

    # ? 초기화
    def __init__(self) -> None:
        # * 엣지 옵션
        options: EdgeOptions = EdgeOptions()

        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)
        options.headless = True

        # * cmd창 미생성
        buffer = io.StringIO()
        sys.stdout = buffer
        sys.stderr = buffer

        # * 서비스 생성
        service = Service(EdgeChromiumDriverManager().install())
        service.creation_flags = CREATE_NO_WINDOW

        # * 드라이버 생성
        self.driver = Edge(service=service, options=options)

    # ? 대기 없이 요소 찾기 --- selector: css selector, is_multiple: 여러 요소인지, is_except: 에러 핸들링을 직접 할 것인지
    def find_element_without_wait(self, selector: str, is_multiple: bool | None = False, is_except: bool | None = False) -> WW | list[WW]:
        # * 찾을 때까지 무한대기
        if is_except:
            while True:
                try:
                    if is_multiple:
                        return self.driver.find_elements(By.CSS_SELECTOR, selector)
                    else:
                        return self.driver.find_element(By.CSS_SELECTOR, selector)
                except NoSuchElementException:
                    pass

        # * 직접 에러 핸들링
        else:
            if is_multiple:
                return self.driver.find_elements(By.CSS_SELECTOR, selector)
            else:
                return self.driver.find_element(By.CSS_SELECTOR, selector)

    # ? 브라우저 종료
    def quit(self) -> None:
        self.driver.quit()
