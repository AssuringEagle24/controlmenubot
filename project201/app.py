"""from flask import Flask, render_template, jsonify

app = Flask(__name__)

# Пример данных расписания
schedule_data = {
    "5а": [
        {"lesson_number": 1, "subject": "Математика", "teacher": "Иванова И.И.", "room": "101"},
        {"lesson_number": 3, "subject": "История", "teacher": "Петров П.П.", "room": "203"},
    ],
    "6а": [
        {"lesson_number": 2, "subject": "Русский язык", "teacher": "Сидорова С.С.", "room": "202"},
        {"lesson_number": 4, "subject": "Биология", "teacher": "Кузнецова К.К.", "room": "105"},
    ],
}

# Отображение главной страницы
@app.route("/")
def home():
    return render_template("index.html")

# API для получения расписания
@app.route("/api/schedule/<class_name>", methods=["GET"])
def get_schedule(class_name):
    schedule = schedule_data.get(class_name.lower(), [])
    return jsonify(schedule)

if __name__ == "__main__":
    app.run(debug=True)
"""
"""from flask import Flask, jsonify, render_template, request
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Настройка Flask
app = Flask(__name__)

# Настройка доступа к Google Sheets через OAuth2
def authenticate_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('service_account.json', scope)
    client = gspread.authorize(creds)
    return client

# Получаем данные из Google Sheets
def get_schedule_data():
    client = authenticate_google_sheets()
    sheet = client.open('Замены').sheet1  # Укажите имя вашей таблицы
    records = sheet.get_all_records()  # Получаем все данные из таблицы
    return records

# Главная страница с выбором класса
@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

# API для получения замен по классу
@app.route('/api/schedule/<class_name>', methods=['GET'])
def get_schedule(class_name):
    try:
        # Получаем все записи из Google Sheets
        records = get_schedule_data()

        # Фильтруем записи по классу
        class_data = [row for row in records if row['Класс'].strip() == class_name]

        if not class_data:
            return jsonify({"message": f"Нет замен для класса {class_name}."}), 200

        # Подготавливаем данные для ответа
        response = {"Класс": class_name, "Замены": class_data}

        # Логируем данные (для отладки)
        print(f"Ответ для {class_name}: {response}")

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

        # Фильтруем записи по классу
        class_data = [row for row in records if row['Класс'].strip() == class_name]

        if not class_data:
            message = f"Нет замен для класса {class_name}."
            return render_template('index.html', class_name=class_name, schedule=[], message=message)

        return render_template('index.html', class_name=class_name, schedule=class_data, message=None)

    except Exception as e:
        print(f"Ошибка при обработке данных: {e}")
        return render_template('schedule.html', class_name=class_name, schedule=[], message="Ошибка при обработке данных.")

# Запуск сервера Flask
if __name__ == '__main__':
    app.run(debug=True)
"""
from flask import Flask, jsonify, render_template, request
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Настройка Flask
app = Flask(__name__)
@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

# Настройка доступа к Google Sheets через OAuth2
def authenticate_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('service_account.json', scope)
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
