terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 2.13.0"
    }
  }
}

provider "docker" {}

resource "docker_image" "zookeeper" {
  name = "confluentinc/cp-zookeeper:latest"
}

resource "docker_container" "zookeeper" {
  name  = "zookeeper"
  image = docker_image.zookeeper.name
  ports {
    internal = 2181
    external = 2181
  }
  env = ["ZOOKEEPER_CLIENT_PORT=2181"]
}

resource "docker_image" "kafka" {
  name = "confluentinc/cp-kafka:latest"
}

resource "docker_container" "kafka" {
  name  = "kafka"
  image = docker_image.kafka.name
  ports {
    internal = 9092
    external = 9092
  }
  env = [
    "KAFKA_BROKER_ID=1",
    "KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181",
    "KAFKA_LISTENERS=PLAINTEXT://0.0.0.0:9092",
    "KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092",
    "KAFKA_LISTENER_SECURITY_PROTOCOL_MAP=PLAINTEXT:PLAINTEXT",
    "KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1"
  ]
  depends_on = [docker_container.zookeeper]
}

resource "docker_image" "python" {
  name = "python:3.8"
}

resource "docker_container" "kafka_producer" {
  name  = "kafka_producer"
  image = docker_image.python.name
  volumes {
    host_path      = "/Users/sanjojoy/docker-data"
    container_path = "/app"
  }
  command = ["python", "/app/kafka_producer.py"]
  depends_on = [docker_container.kafka]
}

resource "docker_container" "kafka_consumer3" {
  name  = "kafka_consumer3"
  image = docker_image.python.name
  volumes {
    host_path      = "/Users/sanjojoy/docker-data"
    container_path = "/app"
  }
  command = ["python", "/app/kafka_consumer3.py"]
  depends_on = [docker_container.kafka]
}

resource "docker_container" "dashboard47" {
  name  = "dashboard47"
  image = docker_image.python.name
  volumes {
    host_path      = "/Users/sanjojoy/docker-data"
    container_path = "/app"
  }
  command = ["python", "/app/dashboard47.py"]
  depends_on = [docker_container.kafka]
}