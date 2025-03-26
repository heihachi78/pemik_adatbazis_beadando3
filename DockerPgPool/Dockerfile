FROM debian

RUN apt-get update
COPY apt.postgresql.org.sh .
RUN chmod +x apt.postgresql.org.sh
RUN ./apt.postgresql.org.sh
RUN apt-get install -y pgpool2
RUN apt-get install -y postgresql-client
RUN apt-get install -y netcat-openbsd
RUN apt-get clean
RUN rm -rf /var/cache/apt/archives/* /var/lib/apt/lists/*
RUN mkdir /var/run/pgpool
RUN chmod 777 /var/run/pgpool

CMD ["/bin/bash", "-c", "exec pgpool -n -f /mnt/config/pgpool.conf -a /mnt/config/pool_hba.conf"]
