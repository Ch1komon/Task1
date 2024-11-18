import time
import requests
import csv
import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

city = "london"
api_key = "80afe1c9cf2eff8b23d140ad99801b7c"
url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
# записываем данные в файл
file_name = "data.csv"

# Email настройки
sender_email = os.getenv("sender_email")  # Ваш email
sender_password = os.getenv("sender_password")  # Ваш пароль
receiver_email = os.getenv("receiver_email")  # Email получателя

def send_email(weather_data):
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = "Погода в Лондоне"

    body = f"Погода в Лондоне:\n\n"
    for key, value in weather_data.items():
        body += f"{key}: {value}\n"

    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print("Email отправлен успешно!")
    except Exception as e:
        print(f"Ошибка при отправке email: {e}")

def get_weather_data():
    responce = requests.get(url) # отправка запроса

    if responce.status_code == 200:
        # выводим данные из json
        data = responce.json()
        weather_data = {
            "Время записи": time.strftime("%Y-%m-%d %H:%M:%S"),
            "Температура (K)": data["main"]["temp"],
            "Влажность (%)": data["main"]["humidity"],
            "Скорость ветра (m/s)": data["wind"]["speed"],
            "Описание погоды": data["weather"][0]["description"]
        }
        return(weather_data)
    else:
        print(f"Ошибка при получении данных: {responce.status_code}")
        return None

# проверка, пуст ли файл
if not os.path.exists(file_name):
     # если файл пустой, добавляем заголовки
    with open(file_name, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(get_weather_data())

while True:
    weather_data = get_weather_data()
    # добавляем данные в файл, независимо от его пустоты, каждые 60 секунд
    if weather_data:
        with open(file_name, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(weather_data.values())
        send_email(weather_data)  # отправка email
    time.sleep(60)