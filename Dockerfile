FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    librdkafka-dev \
    python3-dev \
    # If you need other system deps, list them here
    && rm -rf /var/lib/apt/lists/*

# Option 1: Use a requirements.txt file
# COPY requirements.txt .
# RUN pip install -r requirements.txt

# Option 2: Install inline
RUN pip install \
    streamlit==1.17.0 \
    altair==4.2.0 \
    confluent-kafka==1.9.2 \
    hdfs==2.6.0 \
    faker==15.3.4 \
    pyecharts==1.9.1 \
    streamlit-echarts==0.4.0 \
    plotly==5.6.0 \
    xgboost==1.6.2 \
    scikit-learn==1.1.1 \
    pandas==1.4.3 \
    numpy==1.23.1 \
    matplotlib==3.5.2 \
    seaborn==0.11.2

WORKDIR /app
COPY . /app
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000
CMD ["/app/entrypoint.sh"]