FROM python:latest

RUN pip install kubernetes

RUN pip install requests

COPY reserved_nodes.py .

CMD ["python", "reserved_nodes.py"]
