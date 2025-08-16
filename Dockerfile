# shopify_insights_app/Dockerfile

FROM python:3.12-slim-bookworm

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Command to run the application when the container starts.
# This will execute main.py, which in turn calls uvicorn.run().
CMD ["python3", "main.py"]