# coding: utf-8
# 概要
# ゆーティルクラス
################ 変更履歴 ######################
## 2017/09/13 作成

###############################################

import itertools
from datetime import datetime,timedelta
import math
import os
import configparser
import sys

class Util(object):
	START = 'start.'
	END = 'end.'
	INFO = '[INFO] '
	ERROR = '[ERROR] '
	WARN = '[WARN] '

	
	# 初期化処理
	def __init__(self,dict):
		# 環境変数を取得する。
		self.homeDir = os.environ["APPHORSE"]

		# iniconfigファイルを読み出す。
		condigPath = self.homeDir + '../temp_ProjectHorse/conf'
		inifile = configparser.ConfigParser()
		inifile.read(condigPath + '/config.ini', 'UTF-8')
		self.inifile = inifile

		# 機能ID
		self.pid = dict['pid']


	# ログ出力util
	def logging(self,logStr,flg):
		# 現在時刻を取得する。
		tdatetime = datetime.now()
		ymdt = tdatetime.strftime('%Y-%m-%d %H:%M:%S')
		ymd = tdatetime.strftime('%Y%m%d')

		#ファイルパスを取得する。
		filePath = self.inifile.get('filepath','log')
		filePath = self.homeDir + filePath + self.pid + ymd + '.log'
		
		# start or end
		if flg == 0:
			logStr = logStr + ' ' +self.START
		elif flg == 1:
			logStr = logStr + ' ' +self.END
		else:
			logStr = logStr	

		# info log の付加
		logStr = self.INFO + '[' + self.pid  + ']' + logStr
		# ファイル名取得する。
		f = open(filePath,'a')
		f.write(ymdt + ' ' + logStr + '\n')
		f.close()

	# ログ出力util
	def loggingError(self,logStr):
		# 現在時刻を取得する。
		tdatetime = datetime.now()
		ymdt = tdatetime.strftime('%Y-%m-%d %H:%M:%S')
		ymd = tdatetime.strftime('%Y%m%d')

		#ファイルパスを取得する。
		filePath = self.inifile.get('filepath','log')
		filePath = self.homeDir + filePath + self.pid + ymd + '.log'

		# info log の付加
		logStr = '[ERROR]' + '[' + self.pid  + ']' + logStr
		# ファイル名取得する。
		f = open(filePath,'a')
		f.write(ymdt + ' ' + logStr + '\n')
		f.close()


	# ログ出力util
	def loggingWarn(self,logStr):
		# 現在時刻を取得する。
		tdatetime = datetime.now()
		ymdt = tdatetime.strftime('%Y-%m-%d %H:%M:%S')
		ymd = tdatetime.strftime('%Y%m%d')

		#ファイルパスを取得する。
		filePath = self.inifile.get('filepath','log')
		filePath = self.homeDir + filePath + self.pid + ymd + '.log'

		# info log の付加
		logStr = self.WARN +'[' + self.pid  + ']' + logStr
		# ファイル名取得する。
		f = open(filePath,'a')
		f.write(ymdt + ' ' + logStr + '\n')
		f.close()

	# coinlistの取得
	def coinlistGet(self):
		#コインリストを取得する。
		coinlist = self.inifile.get('coin','coinlist').split(',')
		return coinlist
	# コイン種別の取得
	def cointypeGet(self):
		#コインリストを取得する。
		coinlist = self.inifile.get('coin','coinlist').split(',')
		cointype = self.inifile.get('coin','cointype').split(',')
		
		# 辞書として返す。
		cointypeDict = {}
		for i in range(len(coinlist)):
			cointypeDict[coinlist[i]] = cointype[i]
		return cointypeDict

	# コードマスタの取得
	def getCodM(self,dao):
		# 1時的にDBアクセスクラスをappendする。
		daoClass = dao

		# cod_mを全件取得する。
		codm = daoClass.selectQuery('','codm')

		# cod_mのdictを取得する。
		cod_dict = {}
		inner_dict = {}
		cowcod_id = ''
		for cod in codm:
			if cowcod_id != cod[0] and len(inner_dict) != 0:
				cod_dict[cowcod_id] = inner_dict
				cowcod_id = cod[0]
				inner_dict = {}
			
			cowcod_id = cod[0]
			inner_dict[cod[1]] = cod[2]

		cod_dict[cowcod_id] = inner_dict
		return cod_dict

	# 文字列日時からその曜日を取得する。
	def getwhatday(self,conddate):
		# 文字列をdatetime型に変換する。
		nowdate = datetime.strptime(conddate,'%Y%m%d')

		# datetime型から曜日を取得する。
		whatday = nowdate.weekday()

		# 曜日の読みかえを行う。0:月曜-01,6:日曜-07
		dict = {}
		dict[0] = '01'
		dict[1] = '02'
		dict[2] = '03'
		dict[3] = '04'
		dict[4] = '05'
		dict[5] = '06'
		dict[6] = '07'

		whatday = dict[whatday]
		return whatday

	# 祝日か平日か判断する。
	def publicHolideyCheck(self,conddate,dao):
		daoClass = dao

		# public holiday マスタを取得する。
		where = ["WHERE COND_DATE = '%s'"% conddate[0:8]]
		num = daoClass.selectQuery(where,'publicholidaym')

		# numの数次第で判定する。
		if num[0][0] == 1:
			return True
		return False


	# 何分すぎたか取得する。
	def timeOfDay(self,conddate):
		# 時、分を取得する。
		hours = int(conddate[8:10])
		minutes = int(conddate[10:12])

		# 分を取得する。
		min = hours * 60 + minutes

		return min


	# 引数の文字列(日時分)が引数の数値(分)だけ引いた数を文字列型で返す。
	def addDateTimeStr(self,condDate,addDay,addHour,addMinute):
		# 引数の文字列をdatetime型に変換
		nowdate = datetime.strptime(condDate,'%Y%m%d%H%M')

		# 日数を加算する
		nowdate = nowdate + timedelta(days=addDay)

		# 時間を加算する
		nowdate = nowdate + timedelta(hours=addHour)

		# 分を加算する
		nowdate = nowdate + timedelta(minutes=addMinute)

		# 文字列に直す。
		tstr = nowdate.strftime('%Y%m%d%H%M')		
		return tstr


	# %Y-%m-%dT%H:%M:%S形式のアメリカ標準時を日本標準時刻に変換 -> datetime
	def convertJapaneseTime(self,condDatetime):
		# 引数の文字列をいい感じに修正
		condDatetime = condDatetime.replace('T',' ')[0:19]

		# datetime型に変換
		condDatetime = datetime.strptime(condDatetime, '%Y-%m-%d %H:%M:%S')

		# 9時間後の時間に設定する。
		condDatetime = condDatetime + timedelta(hours=9)

		# 返却する
		return condDatetime

	# %Y%m%d%H%Mの文字列から日時を返却する。if 空文字の場合は現在時刻を返す。
	def convertStrToDateTime(self,condStr):
		# 空文字の場合
		if condStr is None or condStr == '':
			retunrStr = datetime.now()
			retunrStr = str(retunrStr)[0:19]
			return retunrStr

		# 空文字でない場合の処理
		retunrStr = datetime.strptime(condStr, '%Y%m%d%H%M')
		retunrStr = str(retunrStr)[0:19]
		return retunrStr

	# 文字列日付の差分の秒数を取得する
	def strDateMinus(self,condA,condB):
		# 日付型に変換
		condA = datetime.strptime(condA, '%Y%m%d%H%M')
		condB = datetime.strptime(condB, '%Y%m%d%H%M')

		# 差分
		second = condA - condB
		return second.total_seconds()


