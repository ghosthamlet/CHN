FROM python:3.6.7-stretch
# FROM python:3.6.7-alpine
# RUN apk add --update git gcc

ENV PYTHONUNBUFFERED 1
RUN mkdir /app && \
#   useradd -d /app chn && \
#   echo 'chn ALL=(ALL:ALL) NOPASSWD:ALL' >> /etc/sudoers && \
#   chown -R chn:chn /app && \
    cd /app

WORKDIR /app

RUN python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --upgrade pip

COPY requirements.txt /app/requirements.txt
RUN python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
RUN python -m spacy download en_core_web_md

COPY . /app/

# must after pip install, install have to use root perm
# USER chn

# CMD ["python", "ui.py", "-p", "127.0.0.1:19180"]

# can't open web browser to show comment/post page from docker
# docker run -it --rm --name CHN --volume /srv/CHN/data:/app/data ghosthamlet/CHN:latest python ui.py
# use proxy
# docker run -it --rm --net host --name CHN --volume /srv/CHN/data:/app/data ghosthamlet/CHN:latest python ui.py -p 127.0.0.1:19180
