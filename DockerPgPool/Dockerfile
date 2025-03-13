FROM debian

RUN apt-get update && apt-get upgrade
COPY apt.postgresql.org.sh .
RUN chmod +x apt.postgresql.org.sh
RUN ./apt.postgresql.org.sh
RUN apt-get update
RUN apt-get -y install pgpool2
RUN apt-get -y install libpgpool2
RUN apt-get -y install postgresql-15-pgpool2
