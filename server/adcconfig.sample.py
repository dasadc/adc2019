# coding: utf-8
#
"""
a sample config file for DAS2020 ADC

adc2019/scripts/04_server.sh will replace "@...@" and create adcconfig.py.
"""

YEAR = @CHANGE_YEAR@  # 2021

SECRET_KEY = '@CHANGE_SECRET_KEY@'  # 'secret_key_0123456789'
SALT = '@CHANGE_SALT@'  # 'secret_salt_XXX'

TEST_MODE = True     # テストモード
# TEST_MODE = False  # コンテスト本番モード

VIEW_SCORE_MODE = True     # Trueのとき、ユーザーは全チームのスコアを表示できる
# VIEW_SCORE_MODE = False  # 競技中にFalseに変更することで、他のチームのスコアを表示できなくなる
