from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

class InstagramScraper:
    def __init__(self):
        self.driver = None
        self.client = None
        self.db = None
        self.collection = None
#initialser le driver google 
    def initialize_driver(self):
        chrome_options = Options()
        service = Service('C:/Users/this PC/Downloads/chromedriver_win32')  # Specify the path to the ChromeDriver executable
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.get('https://www.instagram.com/')
        time.sleep(5)
#fonction de login vers insta
    def login(self, username, password):
        username_field = self.driver.find_element(By.NAME, 'username')
        password_field = self.driver.find_element(By.NAME, 'password')
        username_field.send_keys(username)
        password_field.send_keys(password)
        login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()
#chercher les posts
    def fetch_post_html(self, url):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        response = requests.get(url, headers=headers)
        return response.text
#découper le contenue pour avoir un dictionnaire 
    def parse_post(self, html,url):
        soup = BeautifulSoup(html, "html.parser")
        image_url = soup.find("meta", property="og:image")["content"]
        caption = soup.find("meta", property="og:description")["content"]
        comments = []

        for comment in soup.find_all("li", class_="_a9zr"):
            user = comment.find("a").text.strip()
            text = comment.find("span", class_="").text.strip()
            comments.append({"user": user, "text": text})

        return {"post_url":url ,"image_url": image_url, "caption": caption, "comments": comments}
#se connecter a mongo
    def connect_to_mongodb(self, connection_string, database_name, collection_name):
        self.client = MongoClient(connection_string)
        self.db = self.client[database_name]
        self.collection = self.db[collection_name]
#scrape le tag demandé
    def scrape_instagram_posts(self, search_tag):
        self.driver.get(f'https://www.instagram.com/explore/tags/{search_tag}/')
        time.sleep(2)

        for _ in range(3):
            self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            time.sleep(2)

        post_links = self.driver.find_elements(By.CSS_SELECTOR, 'article div a')
        post_urls = [link.get_attribute('href') for link in post_links]

        for url in post_urls:
            html = self.fetch_post_html(url)
            post_data = self.parse_post(html,url)
            self.collection.insert_one(post_data)

    def close_driver(self):
        self.driver.quit()


def main():
    username = input("Enter your Instagram username: ")
    password = input("Enter your Instagram password: ")
    tag = input("Enter the tag to search on Instagram: ")
    connection_string = 'localhost:27017'
    database_name = 'instagram_posts'
    collection_name = 'posts'
    scraper = InstagramScraper()
    scraper.initialize_driver()
    scraper.login(username, password)
    scraper.connect_to_mongodb(connection_string, database_name, collection_name)
    time.sleep(6)
    scraper.scrape_instagram_posts(tag)
    scraper.close_driver()


if __name__ == '__main__':
    main()
