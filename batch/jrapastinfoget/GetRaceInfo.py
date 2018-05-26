# coding: utf-8
from datetime import datetime
import sys
import os
import configparser
import traceback
from time import sleep

def main():
	# デバッグ
	starttime = datetime.now()
	print(starttime)
	# 基準年月日時分を取得する。
	standardTime = starttime.strftime('%Y%m%d')
	# 環境変数を取得する。
	homeDir = os.environ["APPHORSE"]

	# log用の文字列準備
	exefile = os.path.basename(__file__)
	pid = os.path.basename(__file__)[:-3] # 機能IDの取得

        # 1時的に環境パスを追加する。
	sys.path.append(homeDir)
	from initialize import Initialize

	# 初期化クラスのオブエクトか
	object_dict = {}
	object_dict['pid'] = pid
	Initializer = Initialize.Initialize(object_dict)

	# utilクラスのオブジェクト取得
	utilClass = Initializer.utilClass
	# daoクラスのオブジェクトを取得する。
	daoClass = Initializer.daoClass
	# メール送信クラスを取得する
	MASSClass = Initializer.MASSClass
	object_dict['util'] = utilClass
	object_dict['dao'] = daoClass
	object_dict['mail'] = MASSClass


	# 各クラスのオブジェクト化
	# JRA過去情報取得サービス
	JraPastInfoGetClass = Initializer.class_ins('JraPastInfoGet',object_dict)
	# JRA今週末情報取得サービス
	JraPostInfoGetClass = Initializer.class_ins('JraPostInfoGet',object_dict)
	# スピード指数計算
	AnalyzeClass = Initializer.class_ins('RaceAnalyze',object_dict)
	# 騎手指数計算
	JocAnalyzeClass = Initializer.class_ins('JocAnalyze',object_dict)
	# 予想指数算出
	PostForecastClass = Initializer.class_ins('PostRaceForecast',object_dict)

	# configファイルから情報を抜き出す.
	inifile = utilClass.inifile

	# JRA過去情報を取得する
	result = jrapast(JraPastInfoGetClass,standardTime)

	# JRA現在情報を取得する
	result = jrapost(JraPostInfoGetClass,standardTime)

	# レースのスピード指数を計算する。
	result = analyze(AnalyzeClass,standardTime)

	# 騎手の指数を取得する
	result = jocAnalyze(JocAnalyzeClass)

	# 予想指数を算出
	result = postForecast(PostForecastClass)


def jrapast(class_,time):
	# メソッド名取得
	methodname = sys._getframe().f_code.co_name
	class_.utilClass.logging('[' + methodname + ']' ,0)

	resultDict = {}
	resultDict['returnCode'] = 0


	# 
	class_.jraPastInfoGet(time)

	return resultDict




def jrapost(class_,time):
	# メソッド名取得
	methodname = sys._getframe().f_code.co_name
	class_.utilClass.logging('[' + methodname + ']' ,0)

	resultDict = {}
	resultDict['returnCode'] = 0

	# 
	class_.jraPostInfoGet()


	return resultDict


def analyze(class_,stantime):
	# メソッド名取得
	methodname = sys._getframe().f_code.co_name
	class_.utilClass.logging('[' + methodname + ']' ,0)

	resultDict = {}
	resultDict['returnCode'] = 0

	# 一ヶ月前の日付取得
	from_date = class_.utilClass.addDateTimeStr(stantime + '0000',-30,0,0)
	from_date = from_date[0:8]

	class_.raceAnalyze(from_date,stantime)

	return resultDict

def jocAnalyze(class_):
	# メソッド名取得
	methodname = sys._getframe().f_code.co_name
	class_.utilClass.logging('[' + methodname + ']' ,0)

	resultDict = {}
	resultDict['returnCode'] = 0

	class_.jocAnalyze()

	return resultDict

def postForecast(class_):
	# メソッド名取得
	methodname = sys._getframe().f_code.co_name
	class_.utilClass.logging('[' + methodname + ']' ,0)

	resultDict = {}
	resultDict['returnCode'] = 0

	class_.postRaceForecast()

	return resultDict

if __name__ == '__main__':
	main()
