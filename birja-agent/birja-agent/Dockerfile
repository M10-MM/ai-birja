FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Baza image yig'ilayotganda yaratiladi: DEMO reyestr + data/real dagi haqiqiy kotirovkalar
RUN python cli.py demo
ENV PORT=8000
EXPOSE 8000
# Hosting (Render, Railway ...) PORT ni o'zi beradi
CMD ["sh", "-c", "python cli.py serve --host 0.0.0.0 --port ${PORT}"]
