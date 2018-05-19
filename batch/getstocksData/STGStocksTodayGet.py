# coding: utf-8
import time
import sys
import os
import configparser
import traceback

def main():
	# 環境変数を取得する。
	homeDir = os.environ["APPMONEYTRADE"]

	# log用の文字列準備
	pid = os.path.basename(__file__)[0:3] # 機能IDの取得

	#引数の取得
	args = sys.argv
	condTime = args[1]

        # 1時的に環境変数を追加する。
	sys.path.append(homeDir)
	from dataBaseAccess import SELECTGET
	from util import Util
	from util import JsonParse
	from Quandl import QuandlApi
	from dataBaseAccess import Dao

	# utilクラスのオブジェクト取得
	utilClass = Util.Util(pid)

	# daoクラスのオブジェクトを取得する。
	dao = Dao.Dao(pid)

	# QuandlApiクラスを取得
	QuandlApiClass = QuandlApi.QuandlApi(pid)

	# utilクラス、propatiesファイル、DBアクセスクラスまでのpathを取得する。
	condigPath = homeDir + 'conf'
	utilPath = homeDir + 'util'
	dbPath = homeDir + 'dataBaseAccess'
	
	# configファイルから情報を抜き出す.
	inifile = configparser.ConfigParser()
	inifile.read(condigPath + '/config.ini', 'UTF-8')

	# キーを取得する。　
	key=inifile.get('apikey','Quandl')
	# 前回実行時間を取得する。
	f = open(homeDir + inifile.get(pid,'exetime'), "r")
	exetime = f.read()[0:8]
	if exetime == condTime[0:8]:
		utilClass.logging(pid + ' ' + condTime + ' is skip for before this time has done arleady',2)
		return

	f.close()
	# バッチのログを出力する.
	utilClass.logging(pid + ' ' + condTime,0)

	# DB格納辞書の初期化
	insert_dict = {}

	# 日付の整形
	todayStr = condTime[0:4] + '-' +  condTime[4:6] + '-' +  condTime[6:8]

	# 呼び出しAPIのvalueを取得する。
	valuelist=inifile.get('stocks','stocks').split(',')
	for val in valuelist:
		# api呼び出し前に調整
		val = val.replace('¥','/')

		# api呼び出し
		apiresult = QuandlApiClass.stocksApi(key,val)

		# columns
		column = val.replace('/','_')
		column = column.replace('¥','_')

		# 株価指数の初期化
		stockindex = 0


		# 結果から当日分のclose値を取り出す。
		#closeのカラム番号を取得する。
		try:
			if column == 'NIKKEI_INDEX':
				stockindex = apiresult[todayStr:todayStr]['Close Price'].values[0]
			else:
				stockindex = apiresult[todayStr:todayStr]['Close'].values[0]
		except:
			stockindex = 0
			utilClass.logging(pid + ' ' + column + ':' + condTime + ' is not found stocks makes value 0',2)
			utilClass.logging("".join(traceback.format_stack()),2)

		# 辞書に格納
		insert_dict[column] = stockindex	

	# insert処理
	stocksInsert(insert_dict,pid,condTime[0:8],dao)

	# 最後に実行時間を更新する。
	f = open(homeDir + inifile.get(pid,'exetime'), "w")
	f.write(condTime)
	
	# このバッチ処理の終了log
	utilClass.logging(pid + ' ' + condTime,1)

def stocksInsert(insert_dict,pid,condTime,dao):
	
	# 辞書を見せる。
	insert_dict['LOGIC_DEL_FLG'] = 0
	insert_dict['INS_PID'] = pid
	insert_dict['UPD_PID'] = pid
	insert_dict['DATE'] = condTime

	# insert
	result = dao.STOCKS_T_Insert(insert_dict)

if __name__ == '__main__':
	main()
