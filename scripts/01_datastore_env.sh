#! /bin/bash
#
# Set up environment variable for Datastore emulator
#
# (Note) source 01_datastore_env.sh

script=$(readlink -f "$0")
top_dir=$(cd $(dirname "$script")/../; pwd)
datastore_dir="${top_dir}/work/datastore"

$(gcloud beta emulators datastore --data-dir "${datastore_dir}" env-init)
