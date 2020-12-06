# pull official base image
FROM python:3.7.9-alpine

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

# copy project
# COPY . .

CMD ["gunicorn", "--bind", ":8000", "--workers", "3", "muxy.wsgi:application"]