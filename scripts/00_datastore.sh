#! /bin/bash
#
# Launch Datastore emulator (Google Cloud)

script=$(readlink -f "$0")
top_dir=$(cd $(dirname "$script")/../; pwd)
datastore_dir="${top_dir}/work/datastore"

#export GOOGLE_APPLICATION_CREDENTIALS="${top_dir}/server/keyfile.json"
export LANG=C

if [ ! -d "${datastore_dir}" ]; then
    mkdir -p "${datastore_dir}"
fi

exec gcloud beta emulators datastore --data-dir "${datastore_dir}" start
