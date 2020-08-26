#! /bin/bash

script=$(readlink -f "$0")
top_dir=$(cd $(dirname "$script")/../; pwd)
datastore_dir="${top_dir}/work/datastore"

export PATH="/opt/miniconda3/bin:$PATH"  # for adc-apiserver.system (systemd)

source $(conda info --base)/etc/profile.d/conda.sh
conda activate py38

#export GOOGLE_APPLICATION_CREDENTIALS="${top_dir}/server/keyfile.json"
$(gcloud beta emulators datastore --data-dir "${datastore_dir}" env-init)
cd "${top_dir}/server/"
gunicorn -b :8888 --access-logfile '-' main:app  # for systemd
#gunicorn -b :8888 --access-logfile adc_access.log --error-logfile adc_error.log --log-level info main:app  # log to file
