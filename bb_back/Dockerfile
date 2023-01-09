FROM python:3.8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt --no-cache-dir
RUN pip install django-environ
COPY . /code/
RUN echo pip freeze
CMD ["bash", "start.sh"]