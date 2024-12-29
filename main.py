import requests
from datetime import datetime
from urllib.request import urlopen
from bs4 import BeautifulSoup
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time
# from twilio.rest import Client
# from playsound import playsound

port = 465
app_pw = "qrre fexe jkwd kskf"

account_sid = 'ACe15a540cabe3463d3f59e4b40cbb4757'
auth_token = '9ad32741979fdc445ee2b7c41d2965d7'

months_dict = {1: "january",
               2: "february",
               3: "march",
               4: "april",
               5: "may",
               6: "june",
               7: "july",
               8: "august",
               9: "september",
               10: "october",
               11: "november",
               12: "december"}

def check_status(month, year):
    if month in months_dict:
        month = months_dict[month]

    if month == 'october' or month == 'november' or month == 'december':
        new_year = str(int(year) + 1)
        link = f"https://travel.state.gov/content/travel/en/legal/visa-law0/visa-bulletin/{new_year}/visa-bulletin-for-{month}-{year}.html"
    else:
        link = f"https://travel.state.gov/content/travel/en/legal/visa-law0/visa-bulletin/{year}/visa-bulletin-for-{month}-{year}.html"

    res = requests.get(link)
    return res.status_code, link
    
def get_visa_bulletin(month, year):
    status_code, link = check_status(month, year)
    n_second = datetime.now().second
    n_minute = datetime.now().minute
    n_hour = datetime.now().hour
    n_day = datetime.now().day
    n_month = datetime.now().month
    n_year = datetime.now().year
    n_date = f"{n_day}/{n_month}/{n_year} {n_hour}:{n_minute}:{n_second}"
    
    if status_code == 200:
        data = urlopen(link).read()
        soup = BeautifulSoup(data, 'html.parser')
        # Tìm tất cả các hàng <tr> trong trang
        rows = soup.find_all('tr')

        # Kiểm tra xem hàng thứ 6 có tồn tại không
        if len(rows) >= 6:
            # Tìm tất cả các thẻ <td> trong hàng thứ 6
            tds_in_row_6 = rows[5].find_all('td')

            # Kiểm tra xem hàng thứ 6 có ít nhất 2 thẻ <td> không
            if len(tds_in_row_6) >= 2:
                # Lấy giá trị của thẻ <td> thứ hai
                td_value = tds_in_row_6[1].get_text().strip()
                print(f"{n_date} - ĐÃ CÓ LỊCH VISA F4 {str(month).upper()}/{str(year)}:", td_value)
                return td_value
    else:
        return None
       
from_email = "nhan.sg.americanstudy@gmail.com"
from_pw = "qrre fexe jkwd kskf"
# to_email = ["ngthiennhan2002@gmail.com", "ngthienphuc2006@gmail.com", "ngthien11@gmail.com"]
to_email = ["ngthiennhan2002@gmail.com"]
subject = "Test"
body = ''
 
def send_email(subject, body, from_email, from_pw, to_email):
    second = datetime.now().second
    minute = datetime.now().minute
    hour = datetime.now().hour
    day = datetime.now().day
    month = datetime.now().month
    year = datetime.now().year
    date = f"{day}/{month}/{year} {hour}:{minute}:{second}"
    
    visa_bulletin = get_visa_bulletin(month, year)
    
    if visa_bulletin is None:
        print(f"{date} - CHƯA CÓ LỊCH VISA THÁNG {str(month)}/{str(year)}")
        return False
    else:
        subject = "F4: " + visa_bulletin + f" - ĐÃ CÓ LỊCH VISA THÁNG {month}. F4: {visa_bulletin}"
        body = f"""
        Xin chào,

        Hiện tại đã có lịch visa tháng của tháng {month}.
        Nội dung: F4 ({visa_bulletin})
        Lịch Visa có vào lúc {date}.

        Trân trọng,
        Nhân.

        P/s: Đây là email tự động.
        """
        
        from_email = from_email
        password = from_pw
    
        # Tạo một đối tượng MIMEMultipart
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = ', '.join(to_email)
        msg['Subject'] = subject
    
        # Thêm phần thân email
        msg.attach(MIMEText(body, 'plain'))
    
        try:
            # Kết nối tới server SMTP của Gmail
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(from_email, password)
            text = msg.as_string()
            server.sendmail(from_email, to_email, text)
            server.quit()
            print("Email đã được gửi thành công!")
            # playsound("D:\\Videos\Criminal.mp4")
            return True
        except Exception as e:
            print(f"Không thể gửi email. Lỗi: {e}")


email_sent = False  # Trạng thái theo dõi việc gửi email
continue_checking = False

while True:
    today = datetime.now()
    day = today.day
    
    if 5 <= day <= 30 and email_sent == False:
        continue_checking = True

    if continue_checking:  # Chỉ chạy từ ngày 5 đến ngày 20
        check = send_email(subject, body, from_email, from_pw, to_email)
        if check:
            continue_checking = False
            email_sent = True
            print("App disabled. Waiting until new month...")
            
    if day == 1:
        print("Starting new month...")
        email_sent = False
        continue_checking = False
        
    if 2 <= day < 5 or 30 < day <= 31:
        print("Waiting...")
    
    time.sleep(10)