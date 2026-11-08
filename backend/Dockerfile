FROM python:3.12-slim
WORKDIR /app
RUN useradd --create-home appuser
COPY pyproject.toml ./
COPY app ./app
RUN pip install --no-cache-dir .
USER appuser
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
