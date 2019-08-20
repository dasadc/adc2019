# coding: utf-8
"""
adcusers_in.sample py is a sample file of adcusers_in.py 
  cp adcusers_in.sample.py adcusers_in.py 

adcusers_in.py 
input file of user definition
Run "python adcusers_gen.py" to generate adcusers.py
"""

ADMIN_USERNAME = 'administrator'
ADMIN_PASSWORD = '***CHANGE HERE PLEASE!!***'

# password generator
# apg -m 14 -x 10 -n 15 -M NCL

USERS = [
    # 0:username      1:password       2:displayname         3:uid 4:gid
    [ADMIN_USERNAME, ADMIN_PASSWORD,  'ADCマネージャー',      0,    0],
    ['test-01', '****CHANGE****',    'あんこうチーム',     1001, 1000],
    ['test-02', '****CHANGE****',    'カメさんチーム',     1002, 1000],
    ['test-03', '****CHANGE****',    'アヒルさんチーム',   1003, 1000],
    ['test-04', '****CHANGE****',    'カバさんチーム',     1004, 1000],
    ['test-05', '****CHANGE****',    'ウサギさんチーム',   1005, 1000],
    ['test-06', '****CHANGE****',    'カモさんチーム',     1006, 1000],
    ['test-07', '****CHANGE****',    'レオポンさんチーム', 1007, 1000],
    ['test-08', '****CHANGE****',    'アリクイさんチーム', 1008, 1000],
    ['test-09', '****CHANGE****',    'サメさんチーム',     1009, 1000],
    #
    ['ADC-0',   '****CHANGE****',    '司会者',             2000, 2000],
    #
    ['ADC-1',   '****CHANGE****',    '聖グロ',             2001, 2000],
    ['ADC-2',   '****CHANGE****',    'サンダース',         2002, 2000],
    ['ADC-3',   '****CHANGE****',    'アンツィオ',         2003, 2000],
    ['ADC-4',   '****CHANGE****',    'プラウダ',           2004, 2000],
    ['ADC-5',   '****CHANGE****',    '黒森峰',             2005, 2000],
    ['ADC-6',   '****CHANGE****',    '継続',               2006, 2000],
    ['ADC-7',   '****CHANGE****',    '知波単',             2007, 2000],
    ['ADC-8',   '****CHANGE****',    '大学選抜',           2008, 2000],
    ['ADC-9',   '****CHANGE****',    'BC自由学園',         2009, 2000],
]


"""
ADC本番のときは、ADC-1〜9を使用
"""
