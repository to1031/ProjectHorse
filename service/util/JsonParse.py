# coding: utf-8
# 概要
# JSOMパースクラス
################ 変更履歴 ######################
## 2017/09/13 作成

###############################################

import itertools
from datetime import datetime
import math
import os
import configparser
import json
import sys
class JsonParse(object):
	
	# 初期化処理
	def __init__(self,dict):
		# 環境変数を取得する。
		self.homeDir = os.environ["APPMONEYTRADE"]

		# iniconfigファイルを読み出す。
		self.inifile = dict['util'].inifile

		# 機能ID
		self.pid = dict['pid']

		sys.path.append(self.homeDir)
		self.utilClass =  dict['util']


	# boardのぱーす
	def boardParse(self,filepath):
		# ファイルの読み恋
		f = open(filepath, 'r')
		# 辞書型に変換
		json_dict = json.load(f)
		
		# mid_price
		mid_price = json_dict['mid_price']
		
		# bidlist
		bidDictList = json_dict['bids']
		bidsnumList =[]
		bidsammountList =[]
		bidspriceList =[]
		roop_num = 1
		for dict in bidDictList:
			bidsnumList.append(roop_num)
			bidsammountList.append(dict['size'])
			bidspriceList.append(dict['price'])
			roop_num =roop_num + 1
		
		# asksist
		asksDictList = json_dict['asks']
		asksnumList =[]
		asksammountList =[]
		askspriceList =[]
		roop_num = 1
		for dict in bidDictList:
			asksnumList.append(roop_num)
			asksammountList.append(dict['size'])
			askspriceList.append(dict['price'])
			roop_num =roop_num + 1
			
		# 最終的に引き渡す辞書データを作成する。
		returnDict = {}
		returnDict['mid_price'] = mid_price
		returnDict['bidsnumList'] = bidsnumList
		returnDict['bidsammountList'] = bidsammountList
		returnDict['bidspriceList'] = bidspriceList
		returnDict['asksnumList'] = asksnumList
		returnDict['asksammountList'] = asksammountList
		returnDict['askspriceList'] = askspriceList
		
		# 返す
		return returnDict

	# executionsのぱーす
	def executionsParse(self,filepath):
		# ファイルの読み恋
		f = open(filepath, 'r')
		# 辞書型に変換
		json_dict = json.load(f)
		
		# 最終取引額のみ取得する。
		dict = json_dict[0]
		endTradePrice = dict['price']
		
		# SELL,BUYの回数および合計額を算出する。
		sell_count = 0
		buy_count = 0
		sell_ammount = 0
		buy_ammount = 0
		
		for i in range(len(json_dict)):
			# sellの場合
			if json_dict[i]['side'] =='SELL':
				sell_count = sell_count + 1
				sell_ammount = sell_ammount + json_dict[i]['price'] * json_dict[i]['size']
			else:
				buy_count = buy_count + 1
				buy_ammount = buy_ammount + json_dict[i]['price'] * json_dict[i]['size']
		
		returnDict ={}
		returnDict['endTradePrice'] = endTradePrice
		returnDict['sell_count'] = sell_count
		returnDict['sell_ammount'] = sell_ammount
		returnDict['buy_count'] = buy_count
		returnDict['buy_ammount'] = buy_ammount
		return returnDict

	# jsonClass.forgePairParse
	def forgePairParse(self,josnfile):
		# 返却dict
		result_dict = {}
		json_dict = json.loads(josnfile)

		for val in json_dict:
			result_dict[val['symbol'][0:3] + "_" + val['symbol'][3:6]] = val['price']

		return result_dict




	# jsonClass.forgePairParse
	def executionsPostParse(self,josnfile,cointype):
		# ファイルの読み恋
		f = open(josnfile, 'r')
		# 辞書型に変換
		json_dict = json.load(f)
		
		# 返却リストを取得する。
		resultList = []
		
		for i in range(len(json_dict)):
			returnDict ={}
			returnDict['LOGIC_DEL_FLG'] = '0'
			returnDict['INS_PID'] = self.pid 
			returnDict['UPD_PID'] = self.pid
			returnDict['TRADE_ID'] = json_dict[i]['id']
			returnDict['COIN_TYPE'] = cointype
			returnDict['TRADE_TYPE'] = '0' if json_dict[i]['side'] == 'SELL' else '1'
			returnDict['TRADE_AMMOUNT'] = json_dict[i]['size']
			returnDict['FINAL_TRADE_PRICE'] = json_dict[i]['price']
			returnDict['EXEC_DATE'] = self.utilClass.addDateTimeStr(json_dict[i]['exec_date'].replace('-','').replace('T','').replace(':','')[0:12],0,9,0)
			resultList.append(returnDict)


		return resultList
