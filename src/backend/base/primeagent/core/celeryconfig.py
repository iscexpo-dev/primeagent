# celeryconfig.py
import os

primeagent_valkey_host = os.environ.get("PRIMEAGENT_VALKEY_HOST")
primeagent_valkey_port = os.environ.get("PRIMEAGENT_VALKEY_PORT")
primeagent_redis_host = os.environ.get("PRIMEAGENT_REDIS_HOST")
primeagent_redis_port = os.environ.get("PRIMEAGENT_REDIS_PORT")
# broker default user

if primeagent_valkey_host and primeagent_valkey_port:
    # Valkey is wire-compatible with Redis. Celery/kombu registers redis://,
    # not valkey://, as the transport scheme.
    broker_url = f"redis://{primeagent_valkey_host}:{primeagent_valkey_port}/0"
    result_backend = f"redis://{primeagent_valkey_host}:{primeagent_valkey_port}/0"
elif primeagent_redis_host and primeagent_redis_port:
    broker_url = f"redis://{primeagent_redis_host}:{primeagent_redis_port}/0"
    result_backend = f"redis://{primeagent_redis_host}:{primeagent_redis_port}/0"
else:
    # RabbitMQ
    mq_user = os.environ.get("RABBITMQ_DEFAULT_USER", "primeagent")
    mq_password = os.environ.get("RABBITMQ_DEFAULT_PASS", "primeagent")
    broker_url = os.environ.get("BROKER_URL", f"amqp://{mq_user}:{mq_password}@localhost:5672//")
    result_backend = os.environ.get("RESULT_BACKEND", "redis://localhost:6379/0")
# Broker and result data must never be deserialized as Python objects. A broker
# writer can otherwise execute code in the worker before task routing runs.
task_serializer = "json"
result_serializer = "json"
accept_content = ["json"]
result_accept_content = ["json"]
