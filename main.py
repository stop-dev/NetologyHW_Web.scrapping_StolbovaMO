# python3 -m pip install requests

import requests
import bs4
from pprint import pprint

import re
from time import sleep
from selenium.common import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions

#    header, topics and body text KEYWORDS
KEYWORDS = ['дизайн', 'фото', 'web', 'python', 'ИИ']

def wait_element(browser, delay=3, by=By.CSS_SELECTOR, value=None):
    try:
        return WebDriverWait(browser, delay).until(
            expected_conditions.presence_of_element_located((by, value))
        )
    except TimeoutException:
        return None

# OUTPUT: <дата> – <заголовок> – <ссылка>.
def print_result(parsed_data, index_list:list):
    for i in index_list:
        data = parsed_data[i]
        print(f'<{data["date"]}> – <{data["title"]}> – <{data["link"]}>')

def join_all_content(p_list, title:str, topics_list) -> str:
    text_list = [title]
    text_list.extend(p.text for p in p_list)
    text_list.extend(topic.text for topic in topics_list)
    return ' '.join(text_list)

# map(re.escape, KEYWORDS) — экранирует все специальные символы (C++, + экранируется).
# '|'.join(...) — соединяет все ключевые слова через |: дизайн|фото|web|python.
# \b(...)\b — проверка границ слова, чтобы не находить web в webinar.
# re.IGNORECASE — поиск без учёта регистра.
def content_analysis(parsed_data) -> list:
    index_list = []
    pattern = re.compile(
        r'\b(' + '|'.join(map(re.escape, KEYWORDS)) + r')\b',
        flags=re.IGNORECASE
    )
    for i, data in enumerate(parsed_data):
        if bool(pattern.search(data['all_content'])):
            index_list.append(i)
    return index_list

def get_page_info(url:str):
    parsed_data = []

    chrome_path = ChromeDriverManager().install()
    service = Service(executable_path=chrome_path)
    browser = Chrome(service=service)
    browser.get(url)
    sleep(3)

    if len(browser.find_elements(by=By.CSS_SELECTOR, value='h1.fc-dialog-headline')):
        print("Consent to use personal data: yes")
        consent_button = wait_element(browser, value='button[aria-label="Consent"]')
        consent_button.click()

    articles = browser.find_elements(by=By.CSS_SELECTOR, value='article[id]')
    # delete announcements like : 🎄🎁 Анонимный Дед Мороз на Хабре
    articles_with_h2 = [a for a in articles if a.find_elements(By.CSS_SELECTOR, value="h2 span")]
    for article in articles_with_h2:
        title = wait_element(article, value='h2 span').text.strip()
        article_date = wait_element(article, value='time').get_attribute('title')
        article_link = wait_element(article, value="h2 > a").get_attribute('href')
        p_list = article.find_elements(By.CSS_SELECTOR, value='.lead p')
        topics_list = article.find_elements(
            By.CSS_SELECTOR,
            value='.tm-publication-hub__link-container a span:not([class])'
        )
        all_content = join_all_content(p_list, title, topics_list)
        parsed_data.append({
            'title': title,
            'date': article_date,
            'link': article_link,
            'all_content': all_content
        })
    print_result(parsed_data, content_analysis(parsed_data))


#BeautifulSoup practice
# def one_page_search(link:str):
#     parsed_data = []
#
#     response = requests.get(link)
#     soup = bs4.BeautifulSoup(response.text, features='lxml')
#     articles_tag_list = soup.select('article')
#     # delete announcements like : 🎄🎁 Анонимный Дед Мороз на Хабре
#     articles_with_h2 = [a for a in articles_tag_list if a.find("h2")]
#     for article in articles_with_h2:
#         header_name = article.select_one("h2 span").text.strip()
#         print(header_name)
#         article_date =  article.select_one("time")["title"]
#         article_link = "https://habr.com" + article.select_one("h2 > a")["href"]
#         parsed_data.append({
#             'title': header_name,
#             'date': article_date,
#             'link': article_link
#         })

if __name__ == '__main__':
    print('Hello!')
    link = "https://habr.com/ru/articles/"
    # one_page_search(link)
    get_page_info(link)
