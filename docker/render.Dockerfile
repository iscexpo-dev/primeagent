FROM khulnasoft/primeagent:latest

ENV PRIMEAGENT_AUTO_LOGIN=false

ENTRYPOINT ["python", "-m", "primeagent", "run"]
