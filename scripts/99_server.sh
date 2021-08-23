#! /bin/bash
# deploy前のテスト実行方法
#
# Usage: ./99_server.sh [-h|--help] [-d|--debug] [-e|--conda-env NAME] [-p|--port NUMBER]

script=$(readlink -f "$0")
top_dir=$(cd $(dirname "$script")/../; pwd)
datastore_dir="${top_dir}/work/datastore"
server_dir="${top_dir}/server/"

[ -z "${CONDA_ENV}" ] && CONDA_ENV="adc2019dev"
DEBUG=""
PORT=8000
while [ $# -gt 0 ]; do
    case "$1" in
	-d|--debug)
	    DEBUG=1
	    ;;
	-e|--conda-env)
	    shift
	    CONDA_ENV="$1"
	    ;;
	-p|--port)
	    shift
	    PORT="$1"
	    ;;
	-h|--help|*)
	    cat <<EOF
Usage:
  ./99_server.sh [-h|--help]
                 [-d|--debug] [-e|--conda-env NAME] [-p|--port NUMBER]
default:
    port: ${PORT}
    conda-env: ${CONDA_ENV}
EOF
	    exit 0
    esac
    shift
done


cd "${server_dir}"

source $(conda info --base)/etc/profile.d/conda.sh
conda activate "${CONDA_ENV}"

#export GOOGLE_APPLICATION_CREDENTIALS="${top_dir}/server/keyfile.json"
$(gcloud beta emulators datastore --data-dir "${datastore_dir}" env-init)

if [ -z "${DEBUG}" ]; then
    ACCESS_LOG="adc_access.log"
    ERROR_LOG="adc_error.log"
    LOG_LEVEL="info"
else
    ACCESS_LOG="-"
    ERROR_LOG="-"
    LOG_LEVEL="debug"
fi

gunicorn -b :${PORT} --access-logfile "${ACCESS_LOG}" --error-logfile "${ERROR_LOG}" --log-level "${LOG_LEVE}" main:app
