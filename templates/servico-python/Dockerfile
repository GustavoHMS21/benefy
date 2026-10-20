FROM python:3.12-slim

WORKDIR /app
RUN useradd --create-home --uid 10001 app

COPY pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir .

USER app
EXPOSE 8000
CMD ["uvicorn", "servico.main:app", "--host", "0.0.0.0", "--port", "8000"]
