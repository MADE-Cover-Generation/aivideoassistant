FROM pytorch/pytorch:1.13.1-cuda11.6-cudnn8-runtime
RUN mkdir /backend && chmod 777 /backend
WORKDIR /backend
COPY . .
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
RUN pip3 install --no-cache-dir --upgrade -r requirements.txt
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "8000"]
