FROM python:3

WORKDIR /app
COPY app ./
COPY requirements.txt ./
RUN pip3 install -r requirements.txt

EXPOSE 8888

CMD ["fastapi", "run", "--port", "8888"]
