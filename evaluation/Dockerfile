FROM ubuntu:22.04

#
# install all needed programs
#
RUN apt-get update && apt-get install -y \
  make \
  tar \
  gcc \
  wget \
  less \
  curl \
  sudo \
  lbzip2 \
  unzip \
  libreadline8 \
  libreadline-dev \
  libicu70 \
  libicu-dev \
  zlib1g \
  zlib1g-dev \
  pkg-config \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

#
# create user for non-root execution
#
RUN useradd -s /bin/bash -u 1000 postgres_user -p 000000 -g sudo

#
# get postgres source
#
RUN mkdir -p /home/postgres
WORKDIR /home/postgres
RUN wget "https://ftp.postgresql.org/pub/source/v16.3/postgresql-16.3.tar.bz2" \
  && tar xf "postgresql-16.3.tar.bz2"

#
# configure and install postgres
#
WORKDIR /home/postgres
RUN mkdir build \
  && mkdir target
WORKDIR /home/postgres/build
# Run config script and specify local installation path
RUN /home/postgres/postgresql-16.3/configure --prefix=/home/postgres/target \
  && make world \
  && make install
# create hard links needed for imdb scripts
RUN ln -s /home/postgres/target/bin/psql /usr/bin/
RUN ln -s /home/postgres/target/bin/createdb /usr/bin/
RUN ln -s /home/postgres/target/bin/dropdb /usr/bin/

#
# set up for server start
# privilege management
#
RUN mkdir -p /home/postgres/target/data \
  && chown postgres_user /home/postgres/target/data
RUN touch /home/postgres/target/logfile \
  && chown postgres_user /home/postgres/target/logfile

#
# init data and start postgres
#
WORKDIR /home/postgres/target
USER postgres_user
RUN ./bin/initdb -D ./data \
  && ./bin/pg_ctl -D ./data -l logfile start \
  && ./bin/pg_ctl -D ./data stop

#
# get imdb stuff
#
ADD ./imdb-db/ /home/postgres/imdb-db
ADD ./queries/ /home/postgres/queries
#WORKDIR /home/postgres/target
USER root
RUN chown -R postgres_user /home
#WORKDIR /home/imdb-db
USER postgres_user
#RUN ../../imdb-db/workload-job-setup.sh -f --no-ext


#WORKDIR /home/postgres/imdb_scripts
#ADD ./imdb_scripts ./

#
# create start script for postgres
#
#USER root
#WORKDIR /home/nico/postgres/installation/
#RUN touch start.sh \
#  && echo "./bin/pg_ctl -D ./data -l logfile start" >> start.sh \
#  && chmod +x start.sh \
#  && chown postgres start.sh
#USER postgres

# USER root
#WORKDIR /home/nico/postgres/installation
#CMD ["nohup", "bash", "-c", "./start.sh &", "&&", "sleep", "infinity"]
#CMD ["./bin/pg_ctl", "-D", "./data", "start", "&&", "tail", "-f", "/dev/null"]
CMD ["tail", "-f", "/dev/null"]
