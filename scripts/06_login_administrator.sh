#! /bin/bash

script=$(readlink -f "$0")
top_dir=$(cd $(dirname "$script")/../; pwd)


#"${top_dir}"/client/adccli --URL='http://127.0.0.1:8888/' --username='administrator' --password='ADMIN-PASSWORD' login
"${top_dir}"/client/adccli --URL='http://127.0.0.1:8888/' --username='administrator' login
