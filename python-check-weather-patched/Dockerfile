FROM python:3.12-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN useradd --system --no-create-home app && chown -R app /app
USER app
EXPOSE 8000
CMD ["waitress-serve", "--port=8000", "wsgi:app"]
