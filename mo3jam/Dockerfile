FROM python:3.7
COPY ./requirements.txt /var/www/requirement.txt
RUN pip install -r var/www/requirement.txt
COPY . /app
WORKDIR /app
ENTRYPOINT ["python"]
CMD ["run.py"]