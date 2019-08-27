#! /bin/bash

source $HOME/adc2019/venv36/bin/activate
export GOOGLE_APPLICATION_CREDENTIALS=$HOME/adc2019/server/keyfile.json
$(gcloud beta emulators datastore --data-dir $HOME/adc2019/work/datastore env-init)
cd $HOME/adc2019/server/
gunicorn -b :4280 --access-logfile '-' main:app
