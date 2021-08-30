# coding: utf-8
#
# Get score data from API server

import base64
import pickle
import pandas as pd
import adcclient

cli = adcclient.ADCClient()
cli.read_config()

res = cli.score_dump(round_count=999)
tmp = base64.b64decode(res[6]['score'])
score_board, ok_point, q_point, bonus_point, q_factors, misc, put_a_date, fastest_point = pickle.loads(tmp)

print('score_board')
print(pd.DataFrame(score_board))
print('ok_point')
print(pd.DataFrame(ok_point))
print('q_point')
print(pd.DataFrame(q_point))
print('fastest_point')
print(pd.DataFrame(fastest_point))
print('*'*72)
print('q_factors')
print(pd.DataFrame(q_factors))
print('put_a_data')
print(pd.DataFrame(put_a_date))
