FROM python:latest

RUN pip install requests

COPY rotate_keys.py .

ENTRYPOINT [ "python", "rotate_keys.py" ]