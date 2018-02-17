FROM python:3
WORKDIR /srv/
COPY constructions.txt /srv/
RUN pip install -r /srv/constructions.txt
COPY views /srv/views/
COPY static /srv/static/
COPY server.py config.yml /srv/
ENV THIRD_EYE_CONFIG=/srv/config.yml
CMD ["/srv/server.py"]
