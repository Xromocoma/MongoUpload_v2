FROM python:latest
ENV DEBIAN_FRONTEND="noninteractive"

ENV PYTHONPATH=.

WORKDIR /code
COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY mongo_upload_media /code
RUN ls
RUN pwd
CMD ["python", "main.py"]