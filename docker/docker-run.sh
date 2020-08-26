#!/bin/sh

docker run -it \
       --name adc2020 \
       -v /sys/fs/cgroup:/sys/fs/cgroup:ro \
       -v /tmp/adc2020:/run \
       -p 20022:22 \
       -p 20080:8888 \
       ipsjdasadc/adc:20200827
