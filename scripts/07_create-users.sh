#! /bin/bash

script=$(readlink -f "$0")
top_dir=$(cd $(dirname "$script")/../; pwd)

${top_dir}/client/adccli create-users ${top_dir}/server/adcusers.yaml

echo "get-user"
${top_dir}/client/adccli get-user

echo "get-user-list"
${top_dir}/client/adccli get-user-list
