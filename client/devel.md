adc2019 command line tool addcli
================================

[../devel.md](../devel.md)



test client
-----------

``` bash
export ADCCLIENT_JSON=$HOME/adcclient_devel.json
```

``` python
from importlib import reload
import adcclient
reload(adcclient)

cli = adcclient.ADCClient()
cli.read_config()
```

``` python
import pandas as pd
import pickle
import base64

txt = res[6]['score']

pd.set_option('display.max_rows', 400)
pd.set_option('display.max_columns', 4000)
pd.set_option("display.width", 4000)
tmp = base64.b64decode(txt)
score_board, ok_point, q_point, bonus_point, q_factors, misc, put_a_date, fastest_point = pickle.loads(tmp)

df_score_board = pd.DataFrame(score_board).sort_index().sort_index(axis=1)



from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows

wb = Workbook()
ws = wb.active

ws = wb.create_sheet('score_board', 0)
for r in dataframe_to_rows(df_score_board, index=True, header=True):
    ws.append(r)


wb.save("score-tmp.xlsx")
```
