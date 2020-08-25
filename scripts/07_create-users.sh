#! /bin/bash

script=$(readlink -f "$0")
top_dir=$(cd $(dirname "$script")/../; pwd)

${top_dir}/client/adccli create-users ${top_dir}/server/adcusers_in.yaml
