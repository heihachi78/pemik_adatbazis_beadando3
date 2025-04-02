FROM postgres:17

RUN apt-get update
RUN apt-get install -y postgresql-17-repmgr
RUN apt install -y postgresql-common
COPY apt.postgresql.org.sh .
RUN chmod +x apt.postgresql.org.sh
RUN ./apt.postgresql.org.sh
RUN apt-get install -y pgagent
RUN apt-get install -y rsync
RUN apt-get install -y ssh
RUN apt-get install -y postgresql-17-wal2json
RUN apt-get clean
RUN rm -rf /var/cache/apt/archives/* /var/lib/apt/lists/*
ENV PATH="/usr/lib/postgresql/17/bin:$PATH"
