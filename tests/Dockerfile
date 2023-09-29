FROM python:3.11-slim
RUN apt-get update && apt-get install -y curl jq 
WORKDIR /tests/python
RUN pip install pipenv
COPY python/Pipfile python/Pipfile.lock /tests/python/
RUN pipenv install
CMD ["./wait-for-grid.sh", "pipenv", "run", "tests"]
COPY python/conftest.py python/tests.py wait-for-grid.sh wait-for-sc.sh /tests/python/
RUN chmod +x wait-for-grid.sh wait-for-sc.sh
