FROM saltstack/salt:2019.2

RUN apk add --update --no-cache libgit2 py3-pygit2

ADD etc/salt/minion.d/flags.conf /etc/salt/minion.d/flags.conf
ADD srv/pillar.yaml /srv/pillar.yaml
ADD srv/salt /srv/salt

