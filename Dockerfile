# syntax=docker/dockerfile:1

FROM python:3.10-slim
ENV PYTHONUNBUFFERED 1

# Install dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt


# Copy application code
COPY . /app
#
WORKDIR /app

ENV PORT 8080
#ENV FLASK_APP=main.py
# Run the application
#CMD [ "python3", "-m" , "flask", "run"]

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
# Timeout is set to 0 to disable the timeouts of the workers to allow Cloud Run to handle instance scaling.
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app