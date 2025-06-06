FROM python:3.10-slim

WORKDIR /app

COPY . .

# Instala dependencias del sistema para sox/audio, necesarias para TTS
RUN apt-get update && \
    apt-get install -y ffmpeg libsndfile1 sox git && \
    pip install --upgrade pip && \
    pip install Flask && \
    pip install torch && \
    pip install TTS

CMD ["python", "main.py"]