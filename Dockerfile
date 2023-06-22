# syntax=docker/dockerfile:1

FROM python:3.10
ENV PYTHONUNBUFFERED 1

# Install dependencies
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Copy application code
COPY . /app

WORKDIR /app

ENV RUNINDOCKER=1

# Load environment variables from .env file
ENV PATH="/${PATH}"
COPY .env /.env

ENV FLASK_APP=main.py

EXPOSE 5000

# Run the application
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]