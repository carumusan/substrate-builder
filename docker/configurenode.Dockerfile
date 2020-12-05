FROM parity/subkey AS subkey

FROM python:latest

COPY --from=subkey /usr/local/bin/subkey /usr/local/bin/

RUN pip install kubernetes

RUN pip install requests

COPY configure_node.py .

ENTRYPOINT ["python", "configure_node.py"]