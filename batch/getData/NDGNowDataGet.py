# coding: utf-8
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import sys
import os
import configparser
import urllib.request
import json

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
	from initialize import Initialize

	# 初期化クラスのオブエクトか
	object_dict = {}
	object_dict['pid'] = pid
	Initializer = Initialize.Initialize(object_dict)

	# utilクラスのオブジェクト取得
	utilClass = Initializer.utilClass
	# daoクラスのオブジェクトを取得する。
	dao = Initializer.daoClass
	# メール送信クラスを取得する
	MASSClass = Initializer.MASSClass
	object_dict['util'] = utilClass
	object_dict['dao'] = dao
	object_dict['mass'] = MASSClass

	# jsonparseクラスのオブジェクト取得
	jsonClass = Initializer.class_ins('JsonParse',object_dict)


	# bitflyyerApiクラスを取得
	bitflyerClass = Initializer.class_ins('BitflyerApi',object_dict)


	# configファイルから情報を抜き出す.
	inifile = utilClass.inifile

	# 呼び出す仮想通貨の種類を洗い出す
	coinlist = utilClass.coinlistGet()
	cointype = utilClass.cointypeGet()

	# 前回実行時間を取得する。
	f = open(homeDir + inifile.get(pid,'exetime'), "r")
	exetime = f.read()[0:12]
	if exetime == condTime:
		# 前回と同じ時間なので処理しない。
		utilClass.logging(pid + ' ' + condTime + ' is skip for before this time has done arleady',2)
		return

	f.close()


	# pueryの固定文字列をs￥抜き出す
	pueryStayStr = inifile.get('url','productcode')
	
	# 呼び出すAPIの種類を探す
	board = inifile.get('apitype','board')
	executions = inifile.get('apitype','executions')

	# apiurlを取得する。
	apiurl = inifile.get('url','futuredatabefore')

	# qyeryで空文字のやつを取得する。
	brankcoin = inifile.get('coin','nonpuery')

	# ファイルパスを取得する。
	outPath = inifile.get('filepath','inoutpath')

	# このバッチ処理の開始log
	utilClass.logging(pid + ' ' + condTime,0)

	# コインの数だけ呼び出す。
	for coin in coinlist:
		# log
		logstr = ''
		logstr = 'call webAPI by ' + coin
		utilClass.logging(logstr,0)

		# ファイルパスを取得する。
		filepath = homeDir + outPath + 'board' + '/' + condTime + coin

		puery = ''
		if coin != brankcoin:
			puery = pueryStayStr
		
		# webapiを呼び出す。
		josnStr = bitflyerClass.boardApi(apiurl,coin,puery,board)

		#ファイルを保存する。
		savaFile(josnStr,filepath)

		# ファイルパスを再作成する。
		filepath = homeDir + outPath + 'executions' + '/' + condTime + coin

		# webapiを呼び出す。
		josnStr = bitflyerClass.boardApi(apiurl,coin,puery,executions)

		#ファイルを保存する
		savaFile(josnStr,filepath)

		#log
		utilClass.logging(logstr,1)


	# jsonFileの読み出し。
	for coin in coinlist:
		# cointypeの取得
		cointypeStr = cointype[coin]

		#filepath
		filepath = homeDir + outPath + 'board' + '/' + condTime + coin + '.json'

		# log
		logstr = ''
		logstr = 'read json by ' + filepath
		utilClass.logging(logstr,0)

		# ファイルの存在チェック
		if not os.path.exists(filepath):
			logstr = 'file not found:' + filepath
			utilClass.loggingError(logstr)
			return


		# json読み込みとパース
		resultDict = jsonClass.boardParse(filepath)

		# boradの挿入を行う。
		boardInsert(resultDict,pid,cointype[coin],condTime,dao)

		# ファイルを消する。
		os.remove(filepath)
		
		# filepathの再作成
		filepath = homeDir + outPath + 'executions' + '/' + condTime + coin + '.json'

		# log
		utilClass.logging(logstr,1)
		logstr = ''
		logstr = 'read json by ' + filepath
		utilClass.logging(logstr,0)

		# ファイルの存在チェック
		if not os.path.exists(filepath):
			logstr = 'file not found:' + filepath
			utilClass.loggingError(logstr)
			return

		# json読み込みとパース
		resultDict = jsonClass.executionsParse(filepath)

		# executionsの挿入を行う
		executionsInsert(resultDict,pid,cointype[coin],condTime,dao)
		# ファイルを消す。	
		os.remove(filepath)
		
		# log
		utilClass.logging(logstr,1)

	# 最後に実行時間を更新する。
	f = open(homeDir + inifile.get(pid,'exetime'), "w")
	f.write(condTime)
	

	# このバッチ処理の終了log
	utilClass.logging(pid + ' ' + condTime,1)


# webapi呼び出し
def call_api(apiurl,coin,puery,apitype):
	
	# ビットコイン/円の場合はパラメータが必要ない
	data = {}
	data['product_code'] = coin
	if 'executions' in apitype:
		data['count'] = 500
	url_values = urllib.parse.urlencode(data)
	
	if puery != '':
		req = urllib.request.Request(apiurl + apitype + "?" + url_values,headers={'User-Agent': 'Mozilla/5.0'})
	else:
		req = urllib.request.Request(apiurl + apitype,headers={'User-Agent': 'Mozilla/5.0'})
		
	with urllib.request.urlopen(req) as res:
		response = res.read().decode("utf-8")
		return response

# webapi取得結果の保存
def savaFile(jsonStr,path):
	# ファイルを保存する。
	f = open(path + ".json", "w")
	f.write(jsonStr)
	f.close()


# board結果の保存
def boardInsert(dict,pid,cointype,condTime,dao):
	
	# 辞書の中身を取得する。
	mid_price = dict['mid_price']
	bidsnumList = dict['bidsnumList']
	bidsammountList = dict['bidsammountList']
	bidspriceList = dict['bidspriceList']
	asksnumList = dict['asksnumList']
	asksammountList = dict['asksammountList']
	askspriceList = dict['askspriceList']

	# 基礎的なdictを宣言する。
	mid_place_dict = {}
	mid_place_dict['LOGIC_DEL_FLG'] = 0
	mid_place_dict['INS_PID'] = pid
	mid_place_dict['UPD_PID'] = pid
	mid_place_dict['DATA_TIME'] = condTime 
	mid_place_dict['COIN_TYPE'] = cointype
	mid_place_dict['COIN_MID_PRICE'] = mid_price
	# VIRTUAL_BIDS_MID_T
	result = dao.insert('VIRTUAL_BIDS_MID_T',mid_place_dict)

	# VIRTUAL_COIN_ASKS_Tの基礎的dict
	bids_dict = {}
	bids_dict['LOGIC_DEL_FLG'] = 0
	bids_dict['INS_PID'] = pid
	bids_dict['UPD_PID'] = pid
	bids_dict['DATA_TIME'] = condTime
	bids_dict['VIRTUAL_COIN'] = cointype
	
	# VIRTUAL_COIN_ASKS_Tの基礎的dict
	asks_dict = {}
	asks_dict['LOGIC_DEL_FLG'] = 0
	asks_dict['INS_PID'] = pid
	asks_dict['UPD_PID'] = pid
	asks_dict['DATA_TIME'] = condTime
	asks_dict['VIRTUAL_COIN'] = cointype

	for i in range(len(bidsnumList)):
		bids_dict['BIDS_NUM'] = bidsnumList[i]
		bids_dict['BIDS_AMOUNT'] = bidsammountList[i]
		bids_dict['BIDS_PRICE'] = bidspriceList[i]
		asks_dict['ASKS_NUM'] = asksnumList[i]
		asks_dict['ASKS_AMOUNT'] = asksammountList[i]
		asks_dict['ASKS_PRICE'] = askspriceList[i]

		# DBinsert 
		#result = dao.VIRTUAL_COIN_ASKS_T_Insert(asks_dict)
		#result = dao.VIRTUAL_COIN_BIDS_T_Insert(bids_dict)

	
	


def executionsInsert(dict,pid,cointype,condTime,dao):
	
	# 辞書を見せる。
	insert_dict = {}
	insert_dict['LOGIC_DEL_FLG'] = 0
	insert_dict['INS_PID'] = pid
	insert_dict['UPD_PID'] = pid
	insert_dict['DATA_TIME'] = condTime
	insert_dict['COIN_TYPE'] = cointype
	insert_dict['SELL_COUNT'] = dict['sell_count']
	insert_dict['SELL_AMMOUNT'] = dict['sell_ammount']
	insert_dict['BUY_COUNT'] = dict['buy_count']
	insert_dict['BUY_AMMOUNT'] = dict['buy_ammount']
	insert_dict['END_TRADE_PRICE'] = dict['endTradePrice']
	# insert
	result = dao.insert('VIRTUAL_CURRENCY_T',insert_dict)

if __name__ == '__main__':
	main()
