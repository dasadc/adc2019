# coding: utf-8
#
"""
a sample config file for DAシンポジウム アルゴリズムデザインコンテスト

adc2019/scripts/04_server.sh will replace "@...@" and create adcconfig.py.
"""

YEAR = @CHANGE_YEAR@  # 2022

SECRET_KEY = '@CHANGE_SECRET_KEY@'  # 'secret_key_0123456789'
SALT = '@CHANGE_SALT@'  # 'secret_salt_XXX'

TEST_MODE = True     # テストモード
# TEST_MODE = False  # コンテスト本番モード

VIEW_SCORE_MODE = True     # Trueのとき、ユーザーは全チームのスコアを表示できる
# VIEW_SCORE_MODE = False  # 競技中にFalseに変更することで、他のチームのスコアを表示できなくなる

URL_CLIENT_APP_README = 'https://github.com/dasadc/adc2019/blob/adc2022-yt/client-app/README.md'

LOG_TO_DATASTORE = False   # Datastoreにlogを記録する

QUALITY_POINT = 5.0  # 品質ポイント。2020年まで10.0、2021年は5.0に変更

FASTEST_POINT = 0.5  # 最速回答ポイント
