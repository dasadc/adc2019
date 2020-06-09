FROM python:3.7-slim-buster

ENV HOME /api/

WORKDIR ${HOME}

COPY ./requirements.txt ${HOME}/
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r ${HOME}/requirements.txt

ADD ./ ${HOME}
RUN python ./adcusers_gen.py

ENTRYPOINT ["python", "./main.py", "--ip", "0.0.0.0", "--p", "4280", "--anonymous"]

