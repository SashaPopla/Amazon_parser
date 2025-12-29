# Використовуємо Python 3.9
FROM python:3.9

# 1. Оновлюємо систему і встановлюємо wget (саме цього не вистачало для помилки 127)
RUN apt-get update && apt-get install -y wget unzip

# 2. Скачуємо стабільний Chrome прямим файлом
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb

# 3. Встановлюємо Chrome (apt-get install -y ./... сам підтягне залежності)
RUN apt-get install -y ./google-chrome-stable_current_amd64.deb

# 4. Видаляємо інсталяційний файл, щоб зменшити розмір
RUN rm google-chrome-stable_current_amd64.deb

# 5. Налаштовуємо Python
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 6. Копіюємо проект
COPY ./app /code/app
COPY ./frontend /code/frontend

# 7. Вказуємо змінну середовища для вашого коду (щоб parser.py знав де Chrome)
ENV CHROME_BIN=/usr/bin/google-chrome

# 8. Запускаємо
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]