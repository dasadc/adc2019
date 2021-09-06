#!/bin/sh
#
# Prepare `./env.conf`, like this.
#
# curl -O https://raw.githubusercontent.com/dasadc/adc2019/master/docker/env.sample.conf
# cp env.sample.conf env.conf
# vi env.conf

docker run \
       --name adc2021 \
       -v /sys/fs/cgroup:/sys/fs/cgroup:ro \
       -v /tmp/adc2021:/run \
       -v "./env.conf":/etc/systemd/system/adc-server.service.d/env.conf \
       -p 30022:22 \
       -p 30080:8888 \
       ipsjdasadc/adc:latest
