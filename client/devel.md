adc2019 command line tool addcli
================================

[../devel.md](../devel.md)



test
----

``` python
from importlib import reload
import adcclient
reload(adcclient)

cli = adcclient.ADCClient()
cli.read_config()
```
