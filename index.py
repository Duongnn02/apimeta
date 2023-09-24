from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import pickle

COOKIES_FILE_PATH = 'facebook_cookies.pkl'
url = "https://www.facebook.com/login"

driver = webdriver.Chrome()
driver.get(url)

cookies = pickle.load(open(COOKIES_FILE_PATH, "rb"))
for cookie in cookies:
    driver.add_cookie(cookie)

driver.get(url)
time.sleep(50)  # Chờ thêm một lát để trang được tải hoàn toàn sau khi thêm cookies.
