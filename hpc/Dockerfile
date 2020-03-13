FROM ubuntu:18.04

COPY ./download.py                /var/local
COPY ./entrypoint.sh              /var/local
COPY ./lofar.vo                   /var/local
COPY ./lta-url-copy.sh            /var/local
COPY ./srmclient-2.6.28.tar.gz    /var/local
COPY ./voms.grid.sara.nl.lsc      /var/local

RUN apt-get update && apt-get install -y wget curl python3 python3-pip gnupg2

RUN echo "deb [trusted=yes] http://repository.egi.eu/sw/production/cas/1/current egi-igtf core" >> /etc/apt/sources.list
RUN wget -q -O - http://repository.egi.eu/sw/production/cas/1/current/GPG-KEY-EUGridPMA-RPM-3 | apt-key add -

RUN apt-get update && apt-get install -y \
        openjdk-8-jdk-headless \
        globus-gass-copy-progs \
        voms-clients \
        ca-policy-egi-core \
        fetch-crl \
 && rm -rf /var/lib/apt/lists/*

RUN pip3 install requests loguru

RUN cd /var/local && tar -xzf srmclient-2.6.28.tar.gz \
 && mv srmclient-2.6.28 /opt/srmclient-2.6.28 \
 && mkdir -p /etc/grid-security/vomsdir/lofar \
 && mv voms.grid.sara.nl.lsc /etc/grid-security/vomsdir/lofar \
 && mkdir -p /etc/vomses \
 && mv lofar.vo /etc/vomses \ 
 && mkdir /local \
 && touch /local/.keep

ENTRYPOINT [ "/var/local/entrypoint.sh" ]