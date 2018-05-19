# coding: utf-8
# 


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
	from util import Util
	from dataBaseAccess import Dao
	daoClass = Dao.Dao(pid)

	# DBから処理年月日のリストを取得する。
	targetYmList = daoClass.selectQuery('','BTV_getTargetYm')
	
	# 取得行数分処理する。
	for targetYMD in targetYmList:
		# 処理年月日時分/処理対象フラグ
		ymdhm = targetYMD[0]
		exeflg = targetYMD[1]
		if exeflg != 1:
			continue

		# 処理対象の年月時分の情報を取得する。
		insert_dict = exeymdhm(ymdhm,daoClass)
		insert_dict['INS_PID'] = pid
		insert_dict['UPD_PID'] = pid
		daoClass.insert('VIRTUAL_CURRENCY_T',insert_dict)

	# コネクションの削除
	daoClass.closeConn()


def exeymdhm(ymdhm,daoClass):
	# sqlを実行する。
	where = ["WHERE EXEC_DATE = '%s'"% ymdhm," ORDER BY INS_DDT DESC LIMIT 500"]
	result = daoClass.selectQuery(where,'BTV_getData')
	# 変数初期化
	sellcount = 0
	sellammount = 0
	buycount = 0
	buyammount = 0
	ftp = 0
	for info in result:
		if ftp == 0:
			ftp = info[2]
		# 取得結果を格納する。
		if info[0] == '0': #売りの処理
			sellcount = sellcount + 1
			sellammount = sellammount + (info[1] * info[2])
		else:
			buycount = buycount + 1
			buyammount = buyammount + (info[1] * info[2])

	dict = {}
	dict['LOGIC_DEL_FLG'] = '0' 
	dict['DATA_TIME'] = ymdhm
	dict['COIN_TYPE'] = '02'
	dict['END_TRADE_PRICE'] = ftp
	dict['SELL_COUNT'] = sellcount
	dict['SELL_AMMOUNT'] = sellammount
	dict['BUY_COUNT'] = buycount
	dict['BUY_AMMOUNT'] = buyammount
	return dict
if __name__ == '__main__':
	main()
