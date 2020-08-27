#!/bin/sh
#
# Please set following environment variables.
# - ADC_YEAR        (must)
# - ADC_SECRET_KEY  (must)
# - ADC_SALT        (must)
# - ADC_PASS_ADMIN  (must)
# - ADC_PASS_USER   (optional)
#
# (example)
# env ADC_YEAR="2020" ADC_SECRET_KEY="__change_here__" ADC_SALT="__change_here__" ADC_PASS_ADMIN="__change_here__" sh docker-run.sh

docker run \
       --name adc2020 \
       -v /sys/fs/cgroup:/sys/fs/cgroup:ro \
       -v /tmp/adc2020:/run \
       -p 20022:22 \
       -p 20080:8888 \
       ipsjdasadc/adc:latest
