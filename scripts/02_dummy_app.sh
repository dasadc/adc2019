#! /bin/bash

cd $HOME/adc2019/hello_world/
ln -s $HOME/adc2019/pip-dir /tmp/
source $HOME/adc2019/venv27/bin/activate
export GOOGLE_APPLICATION_CREDENTIALS=$HOME/adc2019/server/keyfile.json
export CLOUDSDK_PYTHON=$HOME/adc2019/venv27/bin/python
export PIP_CONFIG_FILE=$HOME/adc2019/hello_world/pip.conf
$(gcloud beta emulators datastore --data-dir $HOME/adc2019/work/datastore env-init)
exec dev_appserver.py --application=test813 --support_datastore_emulator=true app.yaml 
#exec dev_appserver.py --application=test813 --support_datastore_emulator=true app.yaml --admin_host 0.0.0.0 --admin_port 8000 --enable_host_checking=False
