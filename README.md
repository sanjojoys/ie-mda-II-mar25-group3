
# Dating-data dashboard analytics

This project demonstrates an end-to-end real-time analytics infrastructure that leverages modern data engineering and machine learning techniques. 
It integrates real-time data ingestion with Kafka, streaming and processing with Spark, data storage and advanced querying using HDFS sparkML, 
machine learning model training and evaluation using XGBoost and BigQuery ML, and interactive dashboards built with Streamlit.

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Components](#components)
- [Prerequisites](#prerequisites)
- [Setup & Running the Project](#setup--running-the-project)
- [Contributing](#contributing)
- [License](#license)

## Overview

This project is designed to simulate an AI marketing analytics pipeline. It generates synthetic user events via a Kafka producer, consumes and processes these events using a Kafka consumer that writes data to HDFS (and optionally to a local CSV), and streams data via Spark. The pipeline includes machine learning model training and testing using XGBoost to predict user engagement, and a dashboard (built with Streamlit) to visualize key metrics.

## Project Structure

.
├── docker-compose.yml         # Docker Compose configuration for multi-container setup
├── Dockerfile                 # Dockerfile for the main application (e.g., Streamlit app)
├── Dockerfile.spark           # Dockerfile for the Spark job container
├── entrypoint.sh              # Entrypoint script for the application container
├── create_hdfs_dir.py         # Script to initialize HDFS directories
├── kafka_producer.py          # Generates synthetic Kafka events (random user events)
├── kafka_consumer.py          # Consumes Kafka events and writes data to HDFS/local CSV
├── spark_streaming_script.py  # Reads streaming data from Kafka and writes to HDFS as CSV
├── spark_sql.ipynb            # Jupyter Notebook for Spark SQL analysis (if applicable)
├── sparkml.ipynb              # Jupyter Notebook for Spark ML experiments
├── train_xgboost_model.py     # Processes kafka_data.csv and trains XGBoost ML models
├── test_xgboost_model.py      # Loads and evaluates the trained XGBoost models
└── dashboard.py               # Streamlit dashboard for visualizing metrics and predictions

## Components

- **Kafka Producer & Consumer**:  
  - `kafka_producer.py` generates random user events and sends them to Kafka.
  - `kafka_consumer.py` consumes events, appends data to a CSV file, and writes to HDFS.

- **Spark Streaming**:  
  - `spark_streaming_script.py` reads Kafka streams, parses JSON events, and writes CSV files to HDFS.

- **Machine Learning**:  
  - `train_xgboost_model.py` handles data cleaning, feature engineering, and trains regression and classification models using XGBoost.
  - `test_xgboost_model.py` evaluates the performance of the trained models and saves predictions.

- **Dashboard**:  
  - `dashboard.py` uses Streamlit, Plotly, and pyecharts to create interactive visualizations and reports based on the analytics data.

- **Docker & Infrastructure**:  
  - `docker-compose.yml`, `Dockerfile`, `Dockerfile.spark`, and `entrypoint.sh` define the containerized environment for deploying the project components (Kafka, HDFS, Spark, etc.).

## Prerequisites

- **Docker** and **docker-compose** installed on your system.
- Python 3.x with necessary libraries (Faker, confluent_kafka, pandas, numpy, xgboost, scikit-learn, matplotlib, seaborn, streamlit, plotly, pyecharts, etc.).
- A Kafka broker running (or via Docker as specified).
- Access to an HDFS instance (or use the provided Docker image for HDFS).
- Google Cloud account (for BigQuery and additional cloud services, if needed).

## Setup & Running the Project

1. **Clone the Repository**

   ```bash
   git clone https://github.com/sanjojoys/MDA.git
   cd MDA

	2.	Build and Run Docker Containers
Use the provided docker-compose.yml to start all required services:

docker-compose up --build

This command will build the Docker images and start containers for the app, Kafka, Zookeeper, HDFS, and Spark.

	3.	Run Individual Components
	•	Kafka Producer:
Run kafka_producer.py to start generating events.

python kafka_producer.py


	•	Kafka Consumer:
Run kafka_consumer.py to consume events and write data.

python kafka_consumer.py


	•	Spark Streaming:
Submit Spark streaming job using the spark_streaming_script.py.
	•	Machine Learning:
Execute train_xgboost_model.py to train models, and then run test_xgboost_model.py to evaluate them.
	•	Dashboard:
Launch the dashboard with Streamlit:

streamlit run dashboard.py


Contributing
	•	Branches - Collaborators should work on separate branches (e.g., isaac-branch, maine-branch, etc.) and merge via pull requests.
	•	Commit Guidelines:
Use clear commit messages. Ensure that only relevant files for your task are included.
	•	Issue Tracking:
Use GitHub issues to discuss bugs or enhancements.



Terraform Deployment (Optional)

If you’d like to provision the Docker containers using Terraform instead of docker-compose, you can use the following example Terraform script.
Place this in a file (e.g., main.tf), update paths in the volumes section to match your local directory structure, then run:

terraform init
terraform apply
