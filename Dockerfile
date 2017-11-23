FROM python:3
COPY constructions.txt /srv/
RUN pip install -r /srv/constructions.txt
COPY server.py /srv
COPY views /srv/views/
COPY static /srv/static/
CMD ["/srv/server.py"]
