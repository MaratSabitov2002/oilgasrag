FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY setup.py .
COPY config.py .
COPY data/chroma_db ./data/chroma_db
COPY data/app.py ./data/
COPY data/model.py ./data/
COPY data/promts.py ./data/
COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN pip install -e .

EXPOSE 8501

CMD ["streamlit", "run", "data/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
