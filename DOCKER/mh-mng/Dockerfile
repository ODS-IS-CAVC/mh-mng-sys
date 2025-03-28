FROM python:3.12.7-bullseye

ARG project_dir=/projects/

ENV NO_PROXY="localhost,plantuml"
ENV no_proxy="localhost,plantuml"

WORKDIR $project_dir

COPY nginx.key ./

# 最新のnginxを使うため
# apt-keyが非推奨になったためgpgを使用する
RUN gpg --no-default-keyring --keyring /usr/share/keyrings/nginx.gpg --import ./nginx.key
RUN echo "deb [signed-by=/usr/share/keyrings/nginx.gpg] https://nginx.org/packages/ubuntu/ focal nginx" | tee -a /etc/apt/sources.list
RUN echo "deb-src [signed-by=/usr/share/keyrings/nginx.gpg] https://nginx.org/packages/ubuntu/ focal nginx" | tee -a /etc/apt/sources.list
RUN rm -rf nginx.key
EXPOSE 80

RUN apt-get update \
    && apt-get install -y openssl \
    && apt-get install -y --allow-remove-essential gcc g++ unixodbc libtinfo5 \
    && apt-get install -y logrotate \
    && apt-get install -y nginx \
    && apt-get install -y cron \
    && apt-get install -y iputils-ping \
    && apt-get install -y vim \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists

COPY ./config/requirements.txt ./
RUN pip install --upgrade pip \
    && pip install uwsgi flask supervisor \
    && pip install -r requirements.txt

RUN rm -rf  /etc/logrotate.d/*
COPY ./config/logrotate.d ./logrotate.d

RUN  mv ./logrotate.d/app /etc/logrotate.d/app

COPY ./config/entrypoint.sh /etc/
RUN cp -f /etc/cron.daily/logrotate /etc/cron.hourly/logrotate
RUN chmod 755 /etc/logrotate.d
RUN chmod 444 /etc/logrotate.d/app
RUN chmod 755 /etc/entrypoint.sh

ENTRYPOINT ["/etc/entrypoint.sh"]

