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
	object_dict['mass'] = MASSClass


	# Test対象クラスのインスタンスを生成する。
	DTMDataMiningClass = Initializer.class_ins('DTMDataMining',object_dict)


	# VIRTUAL_CURRENCY_T に格納されている日時分を全て取得する。
	where = ["WHERE INS_PID !='BTV' AND DATA_TIME > '201706081726'"," ORDER BY DATA_TIME"]
	result = daoClass.selectQuery(where,'BTV_currency_t')

	for info in result:
		condTime = info[0]

		# mainクラスを呼び出す。
		DTMDataMiningClass.dtmservice(condTime)


	DTMDataMiningClass.finish()

if __name__ == '__main__':
	main()
