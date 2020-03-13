FROM saltstack/salt:2018.3

RUN apk add --no-cache --update --virtual .build-deps \
    libgit2 \
    py3-pygit2 \
    libgit2-dev \
    gcc \
    python3-dev \
    py3-pygit2 \
 && apk del --no-cache .build-deps \
 && salt-call --versions-report

#RUN pip install timelib \
# && pip install libnacl

ADD etc/salt/minion.d/flags.conf /etc/salt/minion.d/flags.conf
ADD srv/pillar.yaml /srv/pillar.yaml
ADD srv/salt /srv/salt

