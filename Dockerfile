FROM python:3.12-slim

#Чтобы Python не создавал .pyc и сразу выводил логи в консоль
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

#Рабочая папка внутри контейнера
WORKDIR /app

#Копируем зависимости отдельно, чтобы Docker кэшировал их установку
COPY requirements.txt .

#Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

#Копируем весь проект
COPY . .

#Открываем порт приложения
EXPOSE 8000

#Запускаем FastAPI через uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]