FROM python:3.8
ENV HOME /root

WORKDIR /root

ADD  requirements.txt ${HOME}

USER root

ENV TZ Asia/Seoul
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
 

RUN mkdir -p "/etc/config"
RUN echo "devprdflag=dev"> "/etc/config/env.properties"
RUN pip install -r requirements.txt

ADD  . ${HOME}
RUN  chmod -R a+rw ${HOME}

CMD ["python","app.py"]
