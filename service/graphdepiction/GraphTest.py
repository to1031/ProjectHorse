# coding: utf-8
import time
import sys
import os
import configparser
from datetime import datetime

def main():
	starttime = datetime.now()


	# 環境変数を取得する。
	homeDir = os.environ["APPMONEYTRADE"]

	# log用の文字列準備
	pid = os.path.basename(__file__)[0:3] # 機能IDの取得

        # 1時的に環境変数を追加する。
	sys.path.append(homeDir)
	import GraphDepiction
	from dataBaseAccess import SELECTGET
	from util import Util
	from util import JsonParse
	from forge import ForgeApi
	from dataBaseAccess import Dao

	# utilクラスのオブジェクト取得
	utilClass = Util.Util(pid)

	# Test対象クラスのインスタンスを生成する。
	GraphDepictionClass = GraphDepiction.GraphDepiction(pid)

	# daoクラスを生成する。
	dao = Dao.Dao(pid)

	# リストを初期化する。
	x_list = []
	y_list = []
	graphTitle = 'title'
	x_label = 'yyyymmddHHMM'
	y_label = 'JPY/yen'

	# 最小値
	z_list = []


	where = ["WHERE EXEC_DATE >= '201707010000' AND EXEC_DATE < '201707100000' ORDER BY EXEC_DATE,FINAL_TRADE_PRICE"]
	dataList = dao.selectQuery(where,'graphDe')

	# リスト
	condymd = ''
	condMaxVal = 0.0
	condMinVal = 0.0
	condVal = 0.0
	for i in range(len(dataList)):
		# condymdを変化したら各値を初期化
		if condymd != dataList[i][1]:

			# リストに追加
			if condymd != '':
				x_list.append(convertDatetime(condymd))
				y_list.append(condMaxVal)
				z_list.append(condMinVal)

			# 最大値と最小値の更新
			condymd = dataList[i][1]
			condMaxVal = dataList[i][0]
			condMinVal = dataList[i][0]



		# 最大値の更新処理
		if dataList[i][0] >= condMaxVal:
			condMaxVal = dataList[i][0]

		# 最小値の更新処理
		if dataList[i][0] <= condMinVal:
			condMinVal = dataList[i][0]

		# ymdmの更新
		condymd = dataList[i][1]


		# 最後の時のみ処理する
		if len(dataList) - 1 == i:
			x_list.append(convertDatetime(condymd))
			y_list.append(condMaxVal)
			z_list.append(condMinVal)


	# mainクラスを呼び出す。
	GraphDepictionClass.gdsuService(x_list,y_list,x_label,y_label,graphTitle)
	GraphDepictionClass.gdsuService(x_list,z_list,x_label,y_label,graphTitle)

	# 実行時間
	endtime = datetime.now()
	delta = endtime - starttime
	print('実行秒数:' + str(delta.total_seconds()))


def convertDatetime(condStr):
	tdatetime = datetime.strptime(condStr, '%Y%m%d%H%M')
	return tdatetime

if __name__ == '__main__':
	main()
