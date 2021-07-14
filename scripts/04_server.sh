#! /bin/bash
#
# (ADC2021) Launch adc2019 API server
#
# environment variable
# - CONDA_ENV
# - ADC_YEAR
# - ADC_SECRET_KEY
# - ADC_SALT
# - ADC_PASS_ADMIN
# - ADC_PASS_USER

script=$(readlink -f "$0")
top_dir=$(cd $(dirname "$script")/../; pwd)
datastore_dir="${top_dir}/work/datastore"
server_dir="${top_dir}/server/"

[ -z "${CONDA_ENV}" ] && CONDA_ENV="adc2019dev"

export PATH="/opt/miniforge3/bin:$PATH"  # for adc-apiserver.system (systemd)

cd "${server_dir}"

source $(conda info --base)/etc/profile.d/conda.sh
conda activate "${CONDA_ENV}"

if [ ! -f "${server_dir}/adcconfig.py" ]; then
    [ -n "${ADC_YEAR}" ]       || ADC_YEAR=2021
    [ -n "${ADC_SECRET_KEY}" ] || ADC_SECRET_KEY='Change_this_secret_key!!'
    [ -n "${ADC_SALT}" ]       || ADC_SALT='Change_this_salt!!!'
    sed -e "s/@CHANGE_YEAR@/${ADC_YEAR}/" \
	-e "s/@CHANGE_SECRET_KEY@/${ADC_SECRET_KEY}/" \
	-e "s/@CHANGE_SALT@/${ADC_SALT}/" \
	"${server_dir}/adcconfig.sample.py" \
	> "${server_dir}/adcconfig.py"
fi

if [ ! -f "${server_dir}/adcusers.py" ]; then
    rm -f "${server_dir}/adcusers_in.yaml"
    [ -n "${ADC_PASS_ADMIN}" ] || ADC_PASS_ADMIN='Change_admin_password!!'
    [ -n "${ADC_PASS_USER}" ]  || ADC_PASS_USER='Change_user_password!!!'
    sed -e "s/@ADC_PASS_ADMIN@/${ADC_PASS_ADMIN}/" \
	-e "s/@ADC_PASS_USER@/${ADC_PASS_USER}/" \
	"${server_dir}/adcusers_in.sample.yaml" \
	> "${server_dir}/adcusers_in.yaml"
    python adcusers_gen.py
fi

#export GOOGLE_APPLICATION_CREDENTIALS="${top_dir}/server/keyfile.json"
$(gcloud beta emulators datastore --data-dir "${datastore_dir}" env-init)
gunicorn -b :8888 --access-logfile '-' main:app  # for systemd
#gunicorn -b :8888 --access-logfile adc_access.log --error-logfile adc_error.log --log-level info main:app  # log to file
