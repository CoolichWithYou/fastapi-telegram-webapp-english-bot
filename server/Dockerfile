# Используем официальный образ Python
FROM python:3.13

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы
COPY . /app

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Команда по умолчанию
CMD ["python", "main.py"]
