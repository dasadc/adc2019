#! /bin/bash
# deploy前のテスト実行方法

script=$(readlink -f "$0")
top_dir=$(cd $(dirname "$script")/../; pwd)

source $(conda info --base)/etc/profile.d/conda.sh
conda activate py38

#export GOOGLE_APPLICATION_CREDENTIALS="${top_dir}/server/keyfile.json"
$(gcloud beta emulators datastore env-init)
cd "${top_dir}/server/"
#gunicorn -b :8888 --access-logfile '-' main:app
gunicorn -b :8000 --access-logfile adc_access.log --error-logfile adc_error.log --log-level info main:app
