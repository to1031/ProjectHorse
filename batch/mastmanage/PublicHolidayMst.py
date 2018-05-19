# coding: utf-8
# 祝日・振替休日マスタ作成


################ 変更履歴 ######################
## 2017/05/05 作成

###############################################

import itertools
import datetime
import math
import os
import sys

def main():
	# 環境変数を取得する。
	homeDir = os.environ["APPMONEYTRADE"]

	# log用の文字列準備
	pid = os.path.basename(__file__)[0:3] # 機能IDの取

        # 1時的に環境変数を追加する。
	sys.path.append(homeDir)
	from dataBaseAccess import SELECTGET
	from dataBaseAccess import INSERTDICT
	from util import Util
	from dataBaseAccess import Dao
	
	# ファイルを読み込む。
	f = open('holiday_v01.csv')
	
	# オブジェクト取得
	lines2 = f.readlines()
	
	# ファイルをクローズ
	f.close()
	
	# 取得行数分処理する。
	for info in lines2:
		infoList = info.split(",")
		
		# 各隊を取得する。
		startDate = ''
		hlidayname = ''
		
		# 各値を取得する。
		startDate = infoList[0]
		hlidayname = infoList[1]
		
		# insert_dict
		insert_dict = {}
		insert_dict['LOGIC_DEL_FLG'] = 0
		insert_dict['INS_PID'] = pid
		insert_dict['UPD_PID'] = pid
		insert_dict['COND_DATE'] = startDate.replace('-','')
		insert_dict['PUBLIC_HOLIDAY'] = hlidayname.replace('\n','') 
		INSERTDICT.MySQL('PUBLIC_HOLIDAY_M',insert_dict)

if __name__ == '__main__':
	main()
