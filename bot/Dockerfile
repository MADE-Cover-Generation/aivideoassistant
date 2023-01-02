FROM python:3.10-slim-buster
RUN mkdir /bot && chmod 777 /bot
WORKDIR /bot
COPY . .
RUN pip3 install --no-cache-dir --upgrade -r requirements.txt
CMD ["python3","bot.py"]