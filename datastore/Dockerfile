FROM google/cloud-sdk:alpine

RUN apk add --update --no-cache openjdk8-jre \
  && gcloud components install cloud-datastore-emulator beta --quiet

COPY . /datastore/

WORKDIR /datastore

RUN chmod +x ./entrypoint
#RUN chmod +x ./import/run.sh

ENTRYPOINT ["./entrypoint"]

