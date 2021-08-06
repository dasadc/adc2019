#! /bin/bash
# deploy前のテスト実行方法

script=$(readlink -f "$0")
top_dir=$(cd $(dirname "$script")/../; pwd)
datastore_dir="${top_dir}/work/datastore"
server_dir="${top_dir}/server/"

[ -z "${CONDA_ENV}" ] && CONDA_ENV="adc2019dev"

cd "${server_dir}"

source $(conda info --base)/etc/profile.d/conda.sh
conda activate "${CONDA_ENV}"

#export GOOGLE_APPLICATION_CREDENTIALS="${top_dir}/server/keyfile.json"
$(gcloud beta emulators datastore --data-dir "${datastore_dir}" env-init)
#gunicorn -b :8888 --access-logfile '-' main:app
gunicorn -b :8000 --access-logfile adc_access.log --error-logfile adc_error.log --log-level info main:app
