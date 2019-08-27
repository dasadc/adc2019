#! /bin/sh

export GOOGLE_APPLICATION_CREDENTIALS=$HOME/adc2019/server/keyfile.json
export LANG=C
exec gcloud beta emulators datastore --data-dir $HOME/adc2019/work/datastore start
