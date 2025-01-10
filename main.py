import requests
from datetime import datetime
from urllib.request import urlopen
from bs4 import BeautifulSoup
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time
import csv
import pytz

port = 465
app_pw = "qrre fexe jkwd kskf"

account_sid = 'ACe15a540cabe3463d3f59e4b40cbb4757'
auth_token = '9ad32741979fdc445ee2b7c41d2965d7'

from_email = "nhan.sg.americanstudy@gmail.com"
from_pw = "qrre fexe jkwd kskf"
    
with open("emails.csv", mode="r") as file:
    reader = csv.reader(file)
    to_email = [row[0] for row in reader]

subject = "Test"
body = ''

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

def convert_timezone(gmt_time):
    gmt_format = "%a, %d %b %Y %H:%M:%S %Z"  # Định dạng chuỗi thời gian
    gmt_datetime = datetime.strptime(gmt_time, gmt_format)

    gmt_timezone = pytz.timezone("GMT")
    gmt_datetime = gmt_timezone.localize(gmt_datetime)

    vietnam_timezone = pytz.timezone("Asia/Ho_Chi_Minh")
    vietnam_datetime = gmt_datetime.astimezone(vietnam_timezone)
    
    return str(vietnam_datetime.strftime('%d-%m-%Y %H:%M:%S'))


def check_status(month, year):
    if month in months_dict:
        month = months_dict[month]

    if month == 'october' or month == 'november' or month == 'december':
        new_year = str(int(year) + 1)
        link = f"https://travel.state.gov/content/travel/en/legal/visa-law0/visa-bulletin/{new_year}/visa-bulletin-for-{month}-{year}.html"
    else:
        link = f"https://travel.state.gov/content/travel/en/legal/visa-law0/visa-bulletin/{year}/visa-bulletin-for-{month}-{year}.html"

    res = requests.get(link)
    
    try:
        last_modified = requests.head(link).headers['Last-Modified']
    except:
        last_modified
    return res.status_code, link, last_modified
    
def get_visa_bulletin(month, year):
    status_code, link, last_modified = check_status(month, year)
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
                return td_value, link, last_modified
    else:
        return None, None, None

def send_email(subject, body, from_email, from_pw, to_email):
    second = datetime.now().second
    minute = datetime.now().minute
    hour = datetime.now().hour
    day = datetime.now().day
    month = datetime.now().month + 1
    year = datetime.now().year
    if month == 13:
        month = 1
        year += 1
    date = f"{day}/{month}/{year} {hour}:{minute}:{second}"
    
    visa_bulletin, link, last_modified = get_visa_bulletin(month, year)
    
    gmt_time = last_modified
    vietnam_time = convert_timezone(gmt_time)
    
    if visa_bulletin is None:
        print(f"{date} - CHƯA CÓ LỊCH VISA THÁNG {str(month)}/{str(year)}")
        return False
    else:
        subject = f"[F4 - {visa_bulletin}] IMPORTANT: ĐÃ CÓ LỊCH VISA THÁNG {month}"
        # subject = f"ĐANG TEST LẠI [F4 - {visa_bulletin}] IMPORTANT: ĐÃ CÓ LỊCH VISA THÁNG {month}"
        body = f"""
        Xin chào,

        Hiện tại đã có lịch visa tháng của Tháng {month} (Final Action Dates).
        Nội dung: F4 - {visa_bulletin}.
        Lịch Visa có vào lúc:
           + Giờ Việt Nam: {vietnam_time}
           + Giờ GMT: {gmt_time}
        Link: {link}.

        Trân trọng.

        P/s: Đây là email tự động.
        """
        password = from_pw
    
        # Tạo một đối tượng MIMEMultipart
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = ', '.join(to_email)
        msg['Subject'] = subject
        msg["X-Priority"] = "1"  # Đánh dấu email ưu tiên cao
        msg["X-MSMail-Priority"] = "High"
        msg["Importance"] = "High"
            
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


def running_announcement(from_email, to_email):
    subject = f"Running Visa Bulletin"
    body = f"""
    Đây là email tự động để kiểm tra xem ứng dụng Visa Bulletin vẫn đang chạy...
    """
    password = from_pw

    # Tạo một đối tượng MIMEMultipart
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = ', '.join(to_email)
    msg['Subject'] = subject
    msg["X-Priority"] = "1"  # Đánh dấu email ưu tiên cao
    msg["X-MSMail-Priority"] = "High"
    msg["Importance"] = "High"
        
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
        return True
    except Exception as e:
        print(f"Không thể gửi email. Lỗi: {e}")

email_sent = False  # Trạng thái theo dõi việc gửi email
continue_checking = False
sent_checking = False

while True:
    today = datetime.now()
    day = today.day
    
    if 5 <= day <= 20 and email_sent == False:
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
        
    if 2 <= day < 5 or 20 < day <= 31:
        print("Waiting...")
       
    if today.hour == 8 and sent_checking == False:
        running_announcement("nhan.sg.americanstudy@gmail.com", "ngthiennhan2002@gmail.com")
        sent_checking = True
    elif today.hour != 8:
        sent_checking = False
    
    time.sleep(5)