FROM python:alpine

WORKDIR /eksDemoApp

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD [ "flask", "run", "--host=0.0.0.0"]

EXPOSE 5000