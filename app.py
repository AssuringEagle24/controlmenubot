from flask import Flask, jsonify, render_template, request
import gspread
import os
import json
from oauth2client.service_account import ServiceAccountCredentials

# Настройка Flask
app = Flask(__name__)
@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

# Настройка доступа к Google Sheets через OAuth2
"""def authenticate_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('service_account.json', scope)
    client = gspread.authorize(creds)
    return client"""


def authenticate_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials_data = os.getenv("GOOGLE_CREDENTIALS")
    if not credentials_data:
        raise ValueError("Не найдена переменная окружения GOOGLE_CREDENTIALS")

    credentials_json = json.loads(credentials_data)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_json, scope)
    client = gspread.authorize(creds)
    return client
# Получаем данные из Google Sheets
def get_schedule_data():
    client = authenticate_google_sheets()
    sheet = client.open('Замены').sheet1  # Укажите имя вашей таблицы
    records = sheet.get_all_records()  # Получаем все данные из таблицы
    return records

# Преобразование данных в нужный формат
def format_schedule_data(records, class_name):
    # Фильтруем записи по классу
    class_data = [row for row in records if row['Класс'].strip() == class_name]

    # Преобразуем записи в нужный формат
    formatted_data = [
        {
            "lesson_number": row["lesson_number"],
            "subject": row["subject"],
            "teacher": row["teacher"],
            "room": row["room"]
        }
        for row in class_data
    ]
    return formatted_data

# API для получения замен по классу
@app.route('/api/schedule/<class_name>', methods=['GET'])
def get_schedule(class_name):
    try:
        # Получаем все записи из Google Sheets
        records = get_schedule_data()

        # Форматируем данные
        formatted_data = format_schedule_data(records, class_name)

        if not formatted_data:
            return jsonify({"message": f"Нет замен для класса {class_name}."}), 200

        # Формируем JSON-ответ
        response = {class_name: formatted_data}

        # Логируем данные (для отладки)
        print(response)

        return jsonify(response)

    except Exception as e:
        # Логируем ошибку
        print(f"Ошибка при обработке данных: {e}")
        return jsonify({"error": f"Ошибка обработки данных: {str(e)}"}), 500

# Страница с расписанием для выбранного класса
@app.route('/schedule/<class_name>', methods=['GET'])
def schedule_page(class_name):
    try:
        # Получаем все записи из Google Sheets
        records = get_schedule_data()

        # Форматируем данные
        formatted_data = format_schedule_data(records, class_name)

        if not formatted_data:
            message = f"Нет замен для класса {class_name}."
            return render_template('index.html', class_name=class_name, schedule=[], message=message)

        return render_template('index.html', class_name=class_name, schedule=formatted_data, message=None)

    except Exception as e:
        print(f"Ошибка при обработке данных: {e}")
        return render_template('index.html', class_name=class_name, schedule=[], message="Ошибка при обработке данных.")

# Запуск сервера Flask
if __name__ == '__main__':
    app.run(debug=True)

