#coding: utf-8
# 概要
# 機械学習のためにデータを整える
################ 変更履歴 ######################
## 2017/09/13 作成

###############################################

import itertools
from datetime import datetime
import math
import os
import configparser
import sys

class DTMDataMining(object):
	
	# 初期化処理
	def __init__(self,dict):
		# 環境変数を取得する。
		self.homeDir = os.environ["APPMONEYTRADE"]

		# iniconfigファイルを読み出す。
		self.inifile = dict['util'].inifile

		# 当サービスの機能IDを取得する。
		self.pid = os.path.basename(__file__)[0:3]

		# 呼び出し元も機能ID
		self.call_pid = dict['pid']

		# Utilクラスの初期化
		# 1時的に環境変数を追加する。
		self.utilClass = dict['util']
		self.daoClass = dict['dao']

	# メインメソッド
	def dtmservice(self,date_time,dict=None):
		# 返却辞書を生成する。
		returnDict = {}
		returnDict['resultCode'] = 9


		# 当メソッドの名前を取得する。
		methodname = sys._getframe().f_code.co_name

		# 処理開始ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + '] condtime is [' + date_time + ']',0)

		# UPDATEフラグ
		update_flg = 0


		# 既にデータマイニングが格納されている場合またはまだカレントの値段がない場合は処理しない。
		check_result = self.dataExistCheck(date_time)
		if check_result['resultCode'] == 1 and dict is not None:
			# 既にデータマイニングされている場合はデータを更新して改めてデータマイニング
			where = "WHERE COIN_TYPE = '02' AND DATA_TIME = '%s'"% date_time
			update_dict = {}
			update_dict['UPD_PID'] = self.call_pid + '_' + self.pid
			update_dict['END_TRADE_PRICE'] = dict['endTradePrice']
			update_dict['SELL_COUNT'] = dict['sell_count']
			update_dict['SELL_AMMOUNT'] = dict['sell_ammount']
			update_dict['BUY_COUNT'] = dict['buy_count']
			update_dict['BUY_AMMOUNT'] = dict['buy_ammount']
			self.daoClass.update('VIRTUAL_CURRENCY_T',update_dict,where)
			self.utilClass.logging('[' + self.pid + '][' + methodname + '] condtime has already now data so VIRTUAL_CURRENCY_T is updated',2)
			update_flg = 1
		elif check_result['resultCode'] == 2 and dict is not None:
			# まだカレントの値段がない場合
			returnDict['resultCode'] = 1
			self.utilClass.loggingWarn('[' + self.pid + '][' + methodname + '] condtime has not get now data so return false')
			return returnDict

		# DB格納値のdictを予めに初期化
		insert_dict = {}
		insert_dict['LOGIC_DEL_FLG'] = 0
		insert_dict['INS_PID'] = self.pid + '_' + self.call_pid
		insert_dict['UPD_PID'] = self.pid + '_' + self.call_pid
		insert_dict['DATA_TIME'] = date_time
		
		# コードマスタを取得する。
		codm_dict = self.utilClass.getCodM(self.daoClass)

		# 日時の曜日を取得する。
		whatday = int(self.utilClass.getwhatday(date_time[0:8]))
		insert_dict['WHAT_DAY'] = whatday

		# 曜日のフラグを準備する。
		insert_dict = self.whatdayhantei(insert_dict)

		# 平日か否かを判断する。
		insert_dict = self.weekdayhantei(insert_dict) 

		# 何分すぎたか取得する。
		min = self.utilClass.timeOfDay(date_time)
		insert_dict['DAY_OF_TIME'] = (min + 1) / 1440

		# 過去のデータから各値を取得する。
		insert_dict = self.getDataByPastData(insert_dict)	
		if insert_dict is False:
			self.utilClass.loggingWarn('[' + self.pid + '][' + methodname + '] condtime has not get now data so return false')
			returnDict['resultCode'] = 1
			return returnDict
		

		# insertする前にnullチェックする。
		insert_dict = self.nullCheck(insert_dict)
		if insert_dict == 0:
			self.utilClass.loggingWarn('[' + self.pid + '][' + methodname + '] condtime is too much null so skipped')
			return returnDict

		# 取得した情報をinsertする。
		if update_flg == 0:
			self.daoClass.insert('DATA_MINING_T',insert_dict)
		else:
			where = "WHERE DATA_TIME = '%s'"% date_time
			del insert_dict['DATA_TIME']
			del insert_dict['INS_PID']
			del insert_dict['LOGIC_DEL_FLG']
			insert_dict['UPD_PID'] = self.call_pid + '_' + self.pid
			self.daoClass.update('DATA_MINING_T',insert_dict,where)


		# 処理終了ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + '] condtime is [' + date_time + ']',1)

		# 返却
		returnDict['resultCode'] = 0
		return returnDict

	# 過去データを取得して各値を取得する。
	def getDataByPastData(self,insert_dict):
		# 基準日を取得する。
		condList = {}
		condDateTime = insert_dict['DATA_TIME'] # 条件日時分
		condList['minus1M'] = minus1M = self.utilClass.addDateTimeStr(condDateTime,0,0,-1) # 1分前
		condList['minus2M'] = minus2M = self.utilClass.addDateTimeStr(condDateTime,0,0,-2) # 2分前
		condList['minus3M'] = minus3M = self.utilClass.addDateTimeStr(condDateTime,0,0,-3) # 3分前
		condList['minus4M'] = minus4M = self.utilClass.addDateTimeStr(condDateTime,0,0,-4) # 4分前
		condList['minus5M'] = minus5M = self.utilClass.addDateTimeStr(condDateTime,0,0,-5) # 5分前
		condList['minus6M'] = minus6M = self.utilClass.addDateTimeStr(condDateTime,0,0,-6) # 6分前
		condList['minus7M'] = minus7M = self.utilClass.addDateTimeStr(condDateTime,0,0,-7) # 7分前
		condList['minus8M'] = minus8M = self.utilClass.addDateTimeStr(condDateTime,0,0,-8) # 8分前
		condList['minus9M'] = minus9M = self.utilClass.addDateTimeStr(condDateTime,0,0,-9) # 9分前
		condList['minus10M'] = minus10M = self.utilClass.addDateTimeStr(condDateTime,0,0,-10) # 10分前
		condList['minus30M'] = minus30M = self.utilClass.addDateTimeStr(condDateTime,0,0,-30) # 30分前
		condList['minus60M'] = minus60M = self.utilClass.addDateTimeStr(condDateTime,0,0,-60) # 60分前
		condList['minus2H'] = minus2H = self.utilClass.addDateTimeStr(condDateTime,0,-2,0) # 2時間前
		condList['minus3H'] = minus3H = self.utilClass.addDateTimeStr(condDateTime,0,-3,0) # 3時間前
		condList['minus4H'] = minus4H = self.utilClass.addDateTimeStr(condDateTime,0,-4,0) # 4時間前
		condList['minus5H'] = minus5H = self.utilClass.addDateTimeStr(condDateTime,0,-5,0) # 5時間前
		condList['minus6H'] = minus6H = self.utilClass.addDateTimeStr(condDateTime,0,-6,0) # 6時間前
		condList['minus12H'] = minus12H = self.utilClass.addDateTimeStr(condDateTime,0,-12,0) # 12時間前
		condList['minus18H'] = minus18H = self.utilClass.addDateTimeStr(condDateTime,0,-18,0) # 18時間前
		condList['minus24H'] = minus24H = self.utilClass.addDateTimeStr(condDateTime,0,-24,0) # 24時間前
		condList['minus2D'] = minus2D = self.utilClass.addDateTimeStr(condDateTime,-2,0,0) # 2日前	
		condList['minus4D'] = minus4D = self.utilClass.addDateTimeStr(condDateTime,-4,0,0) # 4日前
		condList['minus7D'] = minus7D = self.utilClass.addDateTimeStr(condDateTime,-7,0,0) # 7日前  
		condList['minus14D'] = minus14D = self.utilClass.addDateTimeStr(condDateTime,-8,0,0) # 14日前
		condList['minus28'] = minus28D = self.utilClass.addDateTimeStr(condDateTime,-28,0,0) # 28日前


		# 1 . 1日分を取得する。
		where = ["WHERE VIRTUAL_CURRENCY_T.COIN_TYPE = '02' AND VIRTUAL_CURRENCY_T.DATA_TIME <= '%s'" % condDateTime,"AND VIRTUAL_CURRENCY_T.DATA_TIME >= '%s'"% minus24H,
			" ORDER BY VIRTUAL_CURRENCY_T.DATA_TIME DESC"]
		pastData = self.daoClass.selectQuery(where,'currency_t')
		
		# 1日分をループして各値取得する。
		# 事前処理
		ftp = 0 # 最終取引価格
		fsc = 0 # 最終取引時の過去500件取引高売りの件数
		fsa = 0 # 最終取引時の過去500件取引高売りの価格
		fbc = 0 # 最終取引時の過去500件取引高買いの件数
		fba = 0 # 最終取引時の過去500件取引高売りの価格
		high10m = 0
		high1h = 0
		high2h = 0
		high3h = 0
		high4h = 0
		high5h = 0
		high6h = 0
		high12h = 0
		high24h = 0
		low10m = 10000000
		low1h = 10000000
		low2h = 10000000
		low3h = 10000000
		low4h = 10000000
		low5h = 10000000
		low6h = 10000000
		low12h = 10000000
		low24h = 10000000
		fsc1m = 0
		fsc2m = 0
		fsc3m = 0
		fsc4m = 0
		fsc5m = 0
		fsc10m = 0
		fsc60m = 0
		fsc2h = 0
		fsc3h = 0
		fsc4h = 0
		fsc5h = 0
		fsc6h = 0
		fsc12h = 0
		fsc24h = 0
		fsa1m = 0
		fsa2m = 0
		fsa3m = 0
		fsa4m = 0
		fsa5m = 0
		fsa10m = 0
		fsa60m = 0
		fsa2h = 0
		fsa3h = 0
		fsa4h = 0
		fsa5h = 0
		fsa6h = 0
		fsa12h = 0
		fsa24h = 0
		fbc1m = 0
		fbc2m = 0
		fbc3m = 0
		fbc4m = 0
		fbc5m = 0
		fbc10m = 0
		fbc60m = 0
		fbc2h = 0
		fbc3h = 0
		fbc4h = 0
		fbc5h = 0
		fbc6h = 0
		fbc12h = 0
		fbc24h = 0
		fba1m = 0
		fba2m = 0
		fba3m = 0
		fba4m = 0
		fba5m = 0
		fba10m = 0
		fba60m = 0
		fba2h = 0
		fba3h = 0
		fba4h = 0
		fba5h = 0
		fba6h = 0
		fba12h = 0
		fba24h = 0
		for data in pastData:
			# 最終取引価格取得
			if data[0] == condDateTime:
				ftp = data[1]
				insert_dict['FINAL_TRANS_PRICE'] = ftp
				fsc = data[2]
				fsa = data[3]
				fbc = data[4]
				fba = data[5]
				insert_dict['FINAL_SELL_COUNT'] = fsc /(fsc + fbc)
				insert_dict['FINAL_SELL_AMMOUNT'] = fsa/(fsa + fba)
				insert_dict['FINAL_BUY_COUNT'] = fbc/(fsc + fbc)
				insert_dict['FINAL_BUY_AMMOUNT'] = fba/(fsa + fba)
				insert_dict['COIN_MID_PRICE'] = data[6] / ftp
			if ftp == 0:# 基準時間と同時刻の最終鳥日価格が取得できない場合は処理しない。
				self.utilClass.loggingWarn(condDateTime + 'is skiped not to get lastprice')
				return False

			# 1分前までの処理
			if data[0] >= minus1M:
				if data[0] == minus1M:
					insert_dict['FTP_DIS_1MINUTE'] = data[1] / ftp
				
				# fscの加算を行う
				fsc1m = fsc1m + data[2]

				# fsaの加算を行う
				fsa1m = fsa1m + data[3]

				# fbcの加算を行う
				fbc1m = fbc1m + data[4]

				# fbaの加算を行う
				fba1m = fba1m + data[5]			

			# 2分前までの処理
			if data[0] >= minus2M:
				if data[0] == minus2M:
					insert_dict['FTP_DIS_2MINUTES'] = data[1] / ftp

				# fscの加算を行う
				fsc2m = fsc2m + data[2]

				# fsaの加算を行う
				fsa2m = fsa2m + data[3]

				# fbcの加算を行う
				fbc2m = fbc2m + data[4]

				# fbaの加算を行う
				fba2m = fba2m + data[5]	

			# 3分前までの処理
			if data[0] >= minus3M:
				if data[0] == minus3M:
					insert_dict['FTP_DIS_3MINUTES'] = data[1] / ftp

				# fscの加算を行う
				fsc3m = fsc3m + data[2]

				# fsaの加算を行う
				fsa3m = fsa3m + data[3]

				# fbcの加算を行う
				fbc3m = fbc3m + data[4]

				# fbaの加算を行う
				fba3m = fba3m + data[5]	

			# 4分前までの処理
			if data[0] >= minus4M: 
				if data[0] == minus4M:
					insert_dict['FTP_DIS_4MINUTES'] = data[1] / ftp

				# fscの加算を行う
				fsc4m = fsc4m + data[2]

				# fsaの加算を行う
				fsa4m = fsa4m + data[3]

				# fbcの加算を行う
				fbc4m = fbc4m + data[4]

				# fbaの加算を行う
				fba4m = fba4m + data[5]	

			# 5分前までの処理
			if data[0] >= minus5M:
				if data[0] == minus5M:
					insert_dict['FTP_DIS_5MINUTES'] = data[1] / ftp

				# fscの加算を行う
				fsc5m = fsc5m + data[2]

				# fsaの加算を行う
				fsa5m = fsa5m + data[3]

				# fbcの加算を行う
				fbc5m = fbc5m + data[4]

				# fbaの加算を行う
				fba5m = fba5m + data[5]	

			# 6分前までの処理
			if data[0] >= minus6M:
				if data[0] == minus6M:
					insert_dict['FTP_DIS_6MINUTES'] = data[1] / ftp


			# 7分前までの処理
			if data[0] >= minus7M:
				if data[0] == minus7M:
					insert_dict['FTP_DIS_7MINUTES'] = data[1] / ftp


			# 8分前までの処理
			if data[0] >= minus8M:
				if data[0] == minus8M:
					insert_dict['FTP_DIS_8MINUTES'] = data[1] / ftp

			# 9分前までの処理
			if data[0] >= minus9M:
				if data[0] == minus9M:
					insert_dict['FTP_DIS_9MINUTES'] = data[1] / ftp

			# 10分前までの処理
			if data[0] >= minus10M:
				if data[0] == minus10M:
					insert_dict['FTP_DIS_10MINUTES'] = data[1] / ftp

				# 最大値を取得する。
				if high10m < data[1]:
					high10m = data[1]

				# 最小値を取得する。
				if low10m > data[1]:
					low10m = data[1]

				# fscの加算を行う
				fsc10m = fsc10m + data[2]

				# fsaの加算を行う
				fsa10m = fsa10m + data[3]

				# fbcの加算を行う
				fbc10m = fbc10m + data[4]

				# fbaの加算を行う
				fba10m = fba10m + data[5]


			# 30分前までの処理
			if data[0] >= minus30M:
				if data[0] == minus30M:
					insert_dict['FTP_DIS_30MINUTES'] = data[1] / ftp


			# 60分前までの処理
			if data[0] >= minus60M:
				if data[0] <= self.utilClass.addDateTimeStr(minus60M,0,0,10):
					insert_dict['FTP_DIS_60MINUTES'] = data[1] / ftp


				# 最大値を取得する。
				if high1h < data[1]:
					high1h = data[1]

				# 最小値を取得する。
				if low1h > data[1]:
					low1h = data[1]

				# fscの加算を行う
				fsc60m = fsc60m + data[2]

				# fsaの加算を行う
				fsa60m = fsa60m + data[3]

				# fbcの加算を行う
				fbc60m = fbc60m + data[4]

				# fbaの加算を行う
				fba60m = fba60m + data[5]	


			# 2時間前までの処理
			if data[0] >= minus2H:
				if data[0] <= self.utilClass.addDateTimeStr(minus2H,0,0,30):
					insert_dict['FTP_DIS_2HOURS'] = data[1] / ftp

				# 最大値を取得する。
				if high2h < data[1]:
					high2h = data[1]

				# 最小値を取得する。
				if low2h > data[1]:
					low2h = data[1]

				# fscの加算を行う
				fsc2h = fsc2h + data[2]

				# fsaの加算を行う
				fsa2h = fsa2h + data[3]

				# fbcの加算を行う
				fbc2h = fbc2h + data[4]

				# fbaの加算を行う
				fba2h = fba2h + data[5]	

			# 3時間前までの処理
			if data[0] >= minus3H:
				if data[0] <= self.utilClass.addDateTimeStr(minus3H,0,0,30):
					insert_dict['FTP_DIS_3HOURS'] = data[1] / ftp

				# 最大値を取得する。
				if high3h < data[1]:
					high3h = data[1]

				# 最小値を取得する。
				if low3h > data[1]:
					low3h = data[1]

				# fscの加算を行う
				fsc3h = fsc3h + data[2]

				# fsaの加算を行う
				fsa3h = fsa3h + data[3]

				# fbcの加算を行う
				fbc3h = fbc3h + data[4]

				# fbaの加算を行う
				fba3h = fba3h + data[5]	

			# 4時間前までの処理
			if data[0] >= minus4H:
				if data[0] <= self.utilClass.addDateTimeStr(minus4H,0,0,30):
					insert_dict['FTP_DIS_4HOURS'] = data[1] / ftp


				# 最大値を取得する。
				if high4h < data[1]:
					high4h = data[1]

				# 最小値を取得する。
				if low4h > data[1]:
					low4h = data[1]

				# fscの加算を行う
				fsc4h = fsc4h + data[2]

				# fsaの加算を行う
				fsa4h = fsa4h + data[3]

				# fbcの加算を行う
				fbc4h = fbc4h + data[4]

				# fbaの加算を行う
				fba4h = fba4h + data[5]	


			# 5時間前までの処理
			if data[0] >= minus5H:
				if data[0] <= self.utilClass.addDateTimeStr(minus5H,0,0,30):
					insert_dict['FTP_DIS_5HOURS'] = data[1] / ftp

				# 最大値を取得する。
				if high5h < data[1]:
					high5h = data[1]

				# 最小値を取得する。
				if low5h > data[1]:
					low5h = data[1]

				# fscの加算を行う
				fsc5h = fsc5h + data[2]

				# fsaの加算を行う
				fsa5h = fsa5h + data[3]

				# fbcの加算を行う
				fbc5h = fbc5h + data[4]

				# fbaの加算を行う
				fba5h = fba5h + data[5]	

			# 6時間前までの処理
			if data[0] >= minus6H:
				if data[0] <= self.utilClass.addDateTimeStr(minus6H,0,0,30):
					insert_dict['FTP_DIS_6HOURS'] = data[1] / ftp
				# 最大値を取得する。
				if high6h < data[1]:
					high6h = data[1]

				# 最小値を取得する。
				if low6h > data[1]:
					low6h = data[1]


				# fscの加算を行う
				fsc6h = fsc6h + data[2]

				# fsaの加算を行う
				fsa6h = fsa6h + data[3]

				# fbcの加算を行う
				fbc6h = fbc6h + data[4]

				# fbaの加算を行う
				fba6h = fba6h + data[5]	

			# 12時間前までの処理
			if data[0] >= minus12H:
				if data[0] <= self.utilClass.addDateTimeStr(minus12H,0,1,0):
					insert_dict['FTP_DIS_12HOURS'] = data[1] / ftp

				# 最大値を取得する。
				if high12h < data[1]:
					high12h = data[1]

				# 最小値を取得する。
				if low12h > data[1]:
					low12h = data[1]

				# fscの加算を行う
				fsc12h = fsc12h + data[2]

				# fsaの加算を行う
				fsa12h = fsa12h + data[3]

				# fbcの加算を行う
				fbc12h = fbc12h + data[4]

				# fbaの加算を行う
				fba12h = fba12h + data[5]	


			# 18時間前までの処理
			if data[0] >= minus18H:
				if data[0] <= self.utilClass.addDateTimeStr(minus18H,0,1,0):
					insert_dict['FTP_DIS_18HOURS'] = data[1] / ftp

			# 24時間前までの処理
			if data[0] >= minus24H:
				if data[0] <= self.utilClass.addDateTimeStr(minus24H,0,1,0):
					insert_dict['FTP_DIS_24HOURS'] = data[1] / ftp

				# 最大値を取得する。
				if high24h < data[1]:
					high24h = data[1]

				# 最小値を取得する。
				if low24h > data[1]:
					low24h = data[1]

				# fscの加算を行う
				fsc24h = fsc24h + data[2]

				# fsaの加算を行う
				fsa24h = fsa24h + data[3]

				# fbcの加算を行う
				fbc24h = fbc24h + data[4]

				# fbaの加算を行う
				fba24h = fba24h + data[5]	


		# ループから抜けたの 最大値/最小値系の値を格納する。
		insert_dict['FTP_DIS_10M_LOW'] = low10m / ftp
		insert_dict['FTP_DIS_1H_LOW'] = low1h / ftp
		insert_dict['FTP_DIS_2H_LOW'] = low2h / ftp
		insert_dict['FTP_DIS_3H_LOW'] = low3h / ftp
		insert_dict['FTP_DIS_4H_LOW'] = low4h / ftp
		insert_dict['FTP_DIS_5H_LOW'] = low5h / ftp
		insert_dict['FTP_DIS_6H_LOW'] = low6h / ftp
		insert_dict['FTP_DIS_12H_LOW'] = low12h / ftp
		insert_dict['FTP_DIS_24H_LOW'] = low24h / ftp
		insert_dict['FTP_DIS_10M_HIGH'] = high10m / ftp
		insert_dict['FTP_DIS_1H_HIGH'] = high1h / ftp
		insert_dict['FTP_DIS_2H_HIGH'] = high2h / ftp
		insert_dict['FTP_DIS_3H_HIGH'] = high3h / ftp
		insert_dict['FTP_DIS_4H_HIGH'] = high4h / ftp
		insert_dict['FTP_DIS_5H_HIGH'] = high5h / ftp
		insert_dict['FTP_DIS_6H_HIGH'] = high6h / ftp
		insert_dict['FTP_DIS_12H_HIGH'] = high12h / ftp
		insert_dict['FTP_DIS_24H_HIGH'] = high24h / ftp

		# fsc/fbcの処理を行う
		insert_dict['FSC_SUMIN_1MINUTE'] = self.getWariai(fsc1m,fbc1m)
		insert_dict['FSC_SUMIN_2MINUTES'] = self.getWariai(fsc2m,fbc2m)
		insert_dict['FSC_SUMIN_3MINUTES'] = self.getWariai(fsc3m,fbc3m)
		insert_dict['FSC_SUMIN_4MINUTES'] = self.getWariai(fsc4m,fbc4m)
		insert_dict['FSC_SUMIN_5MINUTES'] = self.getWariai(fsc5m,fbc5m)
		insert_dict['FSC_SUMIN_10MINUTES'] = self.getWariai(fsc10m,fbc10m)
		insert_dict['FSC_SUMIN_60MINUTES'] = self.getWariai(fsc60m,fbc60m)
		insert_dict['FSC_SUMIN_2HOURS'] = self.getWariai(fsc2h,fbc2h)
		insert_dict['FSC_SUMIN_3HOURS'] = self.getWariai(fsc3h,fbc3h)
		insert_dict['FSC_SUMIN_4HOURS'] = self.getWariai(fsc4h,fbc4h)
		insert_dict['FSC_SUMIN_5HOURS'] = self.getWariai(fsc5h,fbc5h)
		insert_dict['FSC_SUMIN_6HOURS'] = self.getWariai(fsc6h,fbc6h)
		insert_dict['FSC_SUMIN_12HOURS'] = self.getWariai(fsc12h,fbc12h)
		insert_dict['FSC_SUMIN_24HOURS'] = self.getWariai(fsc24h,fbc24h)

		insert_dict['FBC_SUMIN_1MINUTE'] = self.getWariai(fbc1m,fsc1m)
		insert_dict['FBC_SUMIN_2MINUTES'] = self.getWariai(fbc2m,fsc2m)
		insert_dict['FBC_SUMIN_3MINUTES'] = self.getWariai(fbc3m,fsc3m)
		insert_dict['FBC_SUMIN_4MINUTES'] = self.getWariai(fbc4m,fsc4m)
		insert_dict['FBC_SUMIN_5MINUTES'] = self.getWariai(fbc5m,fsc5m)
		insert_dict['FBC_SUMIN_10MINUTES'] = self.getWariai(fbc10m,fsc10m)
		insert_dict['FBC_SUMIN_60MINUTES'] = self.getWariai(fbc60m,fsc60m)
		insert_dict['FBC_SUMIN_2HOURS'] = self.getWariai(fbc2h,fsc2h)
		insert_dict['FBC_SUMIN_3HOURS'] = self.getWariai(fbc3h,fsc3h)
		insert_dict['FBC_SUMIN_4HOURS'] = self.getWariai(fbc4h,fsc4h)
		insert_dict['FBC_SUMIN_5HOURS'] = self.getWariai(fbc5h,fsc5h)
		insert_dict['FBC_SUMIN_6HOURS'] = self.getWariai(fbc6h,fsc6h)
		insert_dict['FBC_SUMIN_12HOURS'] = self.getWariai(fbc12h,fsc12h)
		insert_dict['FBC_SUMIN_24HOURS'] = self.getWariai(fbc24h,fsc24h)

		# fsa/fbaの処理を行う
		insert_dict['FSA_SUMIN_1MINUTE'] = self.getWariai(fsa1m,fba1m)
		insert_dict['FSA_SUMIN_2MINUTES'] = self.getWariai(fsa2m,fba2m)
		insert_dict['FSA_SUMIN_3MINUTES'] = self.getWariai(fsa3m,fba3m)
		insert_dict['FSA_SUMIN_4MINUTES'] = self.getWariai(fsa4m,fba4m)
		insert_dict['FSA_SUMIN_5MINUTES'] = self.getWariai(fsa5m,fba5m)
		insert_dict['FSA_SUMIN_10MINUTES'] = self.getWariai(fsa10m,fba10m)
		insert_dict['FSA_SUMIN_60MINUTES'] = self.getWariai(fsa60m,fba60m)
		insert_dict['FSA_SUMIN_2HOURS'] = self.getWariai(fsa2h,fba2h)
		insert_dict['FSA_SUMIN_3HOURS'] = self.getWariai(fsa3h,fba3h)
		insert_dict['FSA_SUMIN_4HOURS'] = self.getWariai(fsa4h,fba4h)
		insert_dict['FSA_SUMIN_5HOURS'] = self.getWariai(fsa5h,fba5h)
		insert_dict['FSA_SUMIN_6HOURS'] = self.getWariai(fsa6h,fba6h)
		insert_dict['FSA_SUMIN_12HOURS'] = self.getWariai(fsa12h,fba12h)
		insert_dict['FSA_SUMIN_24HOURS'] = self.getWariai(fsa24h,fba24h)

		insert_dict['FBA_SUMIN_1MINUTE'] = self.getWariai(fba1m,fsa1m)
		insert_dict['FBA_SUMIN_2MINUTES'] = self.getWariai(fba2m,fsa2m)
		insert_dict['FBA_SUMIN_3MINUTES'] = self.getWariai(fba3m,fsa3m)
		insert_dict['FBA_SUMIN_4MINUTES'] = self.getWariai(fba4m,fsa4m)
		insert_dict['FBA_SUMIN_5MINUTES'] = self.getWariai(fba5m,fsa5m)
		insert_dict['FBA_SUMIN_10MINUTES'] = self.getWariai(fba10m,fsa10m)
		insert_dict['FBA_SUMIN_60MINUTES'] = self.getWariai(fba60m,fsa60m)
		insert_dict['FBA_SUMIN_2HOURS'] = self.getWariai(fba2h,fsa2h)
		insert_dict['FBA_SUMIN_3HOURS'] = self.getWariai(fba3h,fsa3h)
		insert_dict['FBA_SUMIN_4HOURS'] = self.getWariai(fba4h,fsa4h)
		insert_dict['FBA_SUMIN_5HOURS'] = self.getWariai(fba5h,fsa5h)
		insert_dict['FBA_SUMIN_6HOURS'] = self.getWariai(fba6h,fsa6h)
		insert_dict['FBA_SUMIN_12HOURS'] = self.getWariai(fba12h,fsa12h)
		insert_dict['FBA_SUMIN_24HOURS'] = self.getWariai(fba24h,fsa24h)


		# 1日以上過去データについて取得する。
		# データベースから対象データを取得する。
		where = ["WHERE VIRTUAL_CURRENCY_T.COIN_TYPE = '02' AND VIRTUAL_CURRENCY_T.DATA_TIME < '%s'" % minus24H,"AND VIRTUAL_CURRENCY_T.DATA_TIME >= '%s'"% minus28D,
			" ORDER BY VIRTUAL_CURRENCY_T.DATA_TIME DESC"]
		pastData = self.daoClass.selectQuery(where,'currency_t')
	
		# 1日分で取得した値を当てはめる。
		high2d = high24h
		high4d = high24h
		high7d = high24h
		high14d = high24h
		high28d = high24h
		low2d = low24h
		low4d = low24h
		low7d = low24h
		low14d = low24h
		low28d = low24h
		for data in pastData:
			# 2日前までの処理
			if data[0] >= minus2D:

				# 最大値を取得する。
				if high2d < data[1]:
					high2d = data[1]

				# 最小値を取得する。
				if low2d > data[1]:
					low2d = data[1]

			# 4日前までの処理
			if data[0] >= minus4D:

				# 最大値を取得する。
				if high4d < data[1]:
					high4d = data[1]

				# 最小値を取得する。
				if low4d > data[1]:
					low4d = data[1]

			# 7日前までの処理
			if data[0] >= minus7D:

				# 最大値を取得する。
				if high7d < data[1]:
					high7d = data[1]

				# 最小値を取得する。
				if low7d > data[1]:
					low7d = data[1]

			# 14日前までの処理
			if data[0] >= minus14D:

				# 最大値を取得する。
				if high14d < data[1]:
					high14d = data[1]

				# 最小値を取得する。
				if low14d > data[1]:
					low14d = data[1]

			# 28日前までの処理
			if data[0] >= minus28D:

				# 最大値を取得する。
				if high28d < data[1]:
					high28d = data[1]

				# 最小値を取得する。
				if low28d > data[1]:
					low28d = data[1]

		# ループから抜けたので値を確定していく
		insert_dict['FTP_DIS_2D_HIGH'] = high2d / ftp
		insert_dict['FTP_DIS_4D_HIGH'] = high4d / ftp
		insert_dict['FTP_DIS_7D_HIGH'] = high7d / ftp
		insert_dict['FTP_DIS_14D_HIGH'] = high14d / ftp
		insert_dict['FTP_DIS_28D_HIGH'] = high28d / ftp
		insert_dict['FTP_DIS_2D_LOW'] = low2d / ftp
		insert_dict['FTP_DIS_4D_LOW'] = low4d / ftp
		insert_dict['FTP_DIS_7D_LOW'] = low7d / ftp
		insert_dict['FTP_DIS_14D_LOW'] = low14d / ftp
		insert_dict['FTP_DIS_28D_LOW'] = low28d / ftp

		# オブジェクトを返却する。
		return insert_dict







	# 終了処理
	def finish(self):
		self.daoClass.closeConn()


	# 2つの引数a,b -> a / (a + b)
	def getWariai(self,valueA,valueB):
		return valueA / (valueA + valueB)



	# 曜日のフラグを整える。
	def whatdayhantei(self,insert_dict):
		
		# 曜日を取得する。
		whatday = insert_dict['WHAT_DAY']
		# 曜日のフラグを準備する。
		insert_dict['DAY_MONDAY'] = 0
		insert_dict['DAY_TUESDAY'] = 0
		insert_dict['DAY_WEDNESDAY'] = 0
		insert_dict['DAY_THURSDAY'] = 0
		insert_dict['DAY_FRIDAY'] = 0
		insert_dict['DAY_SATURDAY'] = 0
		insert_dict['DAY_SUNDAY'] = 0

		if whatday == 1:
			insert_dict['DAY_MONDAY'] = 1
		if whatday == 2:
			insert_dict['DAY_TUESDAY'] = 1
		if whatday == 3:
			insert_dict['DAY_WEDNESDAY'] = 1
		if whatday == 4:
			insert_dict['DAY_THURSDAY'] = 1
		if whatday == 5:
			insert_dict['DAY_FRIDAY'] = 1
		if whatday == 6:
			insert_dict['DAY_SATURDAY'] = 1
		if whatday == 7:
			insert_dict['DAY_SUNDAY'] = 1

		return insert_dict

	# 平日のフラグを整える。
	def weekdayhantei(self,insert_dict):
		# 土曜か日曜日の場合は休日
		whatday = insert_dict['WHAT_DAY']
		if whatday > 5:
			insert_dict['WEEK_DAY'] = 1
			return insert_dict

		# 平日の場合は祝日判定を実施する。
		if self.utilClass.publicHolideyCheck(insert_dict['DATA_TIME'][0:8],self.daoClass):
			insert_dict['WEEK_DAY'] = 1
			return insert_dict

		insert_dict['WEEK_DAY'] = 0
		return insert_dict

	# 辞書の中にないカラムを抽出する。
	def nullCheck(self,dict):
		# 辞書に格納されているであろう値を取得する。
		list = [
		'LOGIC_DEL_FLG',
		'INS_PID',
		'UPD_PID',
		'DATA_TIME',
		'WHAT_DAY',
		'DAY_MONDAY',
		'DAY_TUESDAY',
		'DAY_WEDNESDAY',
		'DAY_THURSDAY',
		'DAY_FRIDAY',
		'DAY_SATURDAY',
		'DAY_SUNDAY',
		'WEEK_DAY',
		'DAY_OF_TIME',
		'FINAL_TRANS_PRICE',
		'FTP_DIS_1MINUTE',
		'FTP_DIS_2MINUTES',
		'FTP_DIS_3MINUTES',
		'FTP_DIS_4MINUTES',
		'FTP_DIS_5MINUTES',
		'FTP_DIS_6MINUTES',
		'FTP_DIS_7MINUTES',
		'FTP_DIS_8MINUTES',
		'FTP_DIS_9MINUTES',
		'FTP_DIS_10MINUTES',
		'FTP_DIS_30MINUTES',
		'FTP_DIS_60MINUTES',
		'FTP_DIS_2HOURS',
		'FTP_DIS_3HOURS',
		'FTP_DIS_4HOURS',
		'FTP_DIS_5HOURS',
		'FTP_DIS_6HOURS',
		'FTP_DIS_12HOURS',
		'FTP_DIS_18HOURS',
		'FTP_DIS_24HOURS',
		'FTP_DIS_10M_HIGH',
		'FTP_DIS_1H_HIGH',
		'FTP_DIS_2H_HIGH',
		'FTP_DIS_3H_HIGH',
		'FTP_DIS_4H_HIGH',
		'FTP_DIS_5H_HIGH',
		'FTP_DIS_6H_HIGH',
		'FTP_DIS_12H_HIGH',
		'FTP_DIS_24H_HIGH',
		'FTP_DIS_2D_HIGH',
		'FTP_DIS_4D_HIGH',
		'FTP_DIS_7D_HIGH',
		'FTP_DIS_14D_HIGH',
		'FTP_DIS_28D_HIGH',
		'FTP_DIS_10M_LOW',
		'FTP_DIS_1H_LOW',
		'FTP_DIS_2H_LOW',
		'FTP_DIS_3H_LOW',
		'FTP_DIS_4H_LOW',
		'FTP_DIS_5H_LOW',
		'FTP_DIS_6H_LOW',
		'FTP_DIS_12H_LOW',
		'FTP_DIS_24H_LOW',
		'FTP_DIS_2D_LOW',
		'FTP_DIS_4D_LOW',
		'FTP_DIS_7D_LOW',
		'FTP_DIS_14D_LOW',
		'FTP_DIS_28D_LOW',
		'FINAL_SELL_COUNT',
		'FSC_SUMIN_1MINUTE',
		'FSC_SUMIN_2MINUTES',
		'FSC_SUMIN_3MINUTES',
		'FSC_SUMIN_4MINUTES',
		'FSC_SUMIN_5MINUTES',
		'FSC_SUMIN_10MINUTES',
		'FSC_SUMIN_60MINUTES',
		'FSC_SUMIN_2HOURS',
		'FSC_SUMIN_3HOURS',
		'FSC_SUMIN_4HOURS',
		'FSC_SUMIN_5HOURS',
		'FSC_SUMIN_6HOURS',
		'FSC_SUMIN_12HOURS',
		'FSC_SUMIN_24HOURS',
		'FINAL_SELL_AMMOUNT',
		'FSA_SUMIN_1MINUTE',
		'FSA_SUMIN_2MINUTES',
		'FSA_SUMIN_3MINUTES',
		'FSA_SUMIN_4MINUTES',
		'FSA_SUMIN_5MINUTES',
		'FSA_SUMIN_10MINUTES',
		'FSA_SUMIN_60MINUTES',
		'FSA_SUMIN_2HOURS',
		'FSA_SUMIN_3HOURS',
		'FSA_SUMIN_4HOURS',
		'FSA_SUMIN_5HOURS',
		'FSA_SUMIN_6HOURS',
		'FSA_SUMIN_12HOURS',
		'FSA_SUMIN_24HOURS',
		'FINAL_BUY_COUNT',
		'FBC_SUMIN_1MINUTE',
		'FBC_SUMIN_2MINUTES',
		'FBC_SUMIN_3MINUTES',
		'FBC_SUMIN_4MINUTES',
		'FBC_SUMIN_5MINUTES',
		'FBC_SUMIN_10MINUTES',
		'FBC_SUMIN_60MINUTES',
		'FBC_SUMIN_2HOURS',
		'FBC_SUMIN_3HOURS',
		'FBC_SUMIN_4HOURS',
		'FBC_SUMIN_5HOURS',
		'FBC_SUMIN_6HOURS',
		'FBC_SUMIN_12HOURS',
		'FBC_SUMIN_24HOURS',
		'FINAL_BUY_AMMOUNT',
		'FBA_SUMIN_1MINUTE',
		'FBA_SUMIN_2MINUTES',
		'FBA_SUMIN_3MINUTES',
		'FBA_SUMIN_4MINUTES',
		'FBA_SUMIN_5MINUTES',
		'FBA_SUMIN_10MINUTES',
		'FBA_SUMIN_60MINUTES',
		'FBA_SUMIN_2HOURS',
		'FBA_SUMIN_3HOURS',
		'FBA_SUMIN_4HOURS',
		'FBA_SUMIN_5HOURS',
		'FBA_SUMIN_6HOURS',
		'FBA_SUMIN_12HOURS',
		'FBA_SUMIN_24HOURS']
		
		permitlist = [
		'FTP_DIS_2D_LOW',
		'FTP_DIS_4D_LOW',
		'FTP_DIS_7D_LOW',
		'FTP_DIS_14D_LOW',
		'FTP_DIS_28D_LOW',
		'TP_DIS_2D_HIGH',
		'FTP_DIS_4D_HIGH',
		'FTP_DIS_7D_HIGH',
		'FTP_DIS_14D_HIGH',
		'FTP_DIS_28D_HIGH']


		for val in list:
			if val not in dict.keys():
				if val in permitlist:
					self.utilClass.loggingWarn('data is not found by ' + val + ' so packed 0')
					dict[val] = 0
				else:
					self.utilClass.loggingError(' data is not found by ' + val + ' so skiped')
					return 0

		return dict

	# 既にデータ存在しているか確認する。
	def dataExistCheck(self,condtime):
		dict = {}
		dict['resultCode'] = 0

		# カレントの値段が既に存在しているか確認する。
		where = ["WHERE VIRTUAL_CURRENCY_T.COIN_TYPE = '02' AND VIRTUAL_CURRENCY_T.DATA_TIME = '%s'" % condtime]
		pastData = self.daoClass.selectQuery(where,'currency_t')

		if pastData is None or len(pastData) == 0:
			dict['resultCode'] = 2
			return dict

		# データマイニングTが既にあるか確認する
		where = ["WHERE DATA_TIME = '%s'" % condtime]
		dataList = self.daoClass.selectQuery(where,'getDataMining')
		if len(dataList) == 1:
			dict['resultCode'] = 1
			return dict
		
		return dict


