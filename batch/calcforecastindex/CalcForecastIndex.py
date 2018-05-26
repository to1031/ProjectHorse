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

	# レース情報更新クラスを取得する
	raceUpdateClass = Initializer.class_ins('RaceInfoUpdate',object_dict)

	# データマイニングクラスを取得する
	dataMiningClass = Initializer.class_ins('DataMining',object_dict)


	# configファイルから情報を抜き出す.
	inifile = utilClass.inifile

	# メソッド名取得
	methodname = sys._getframe().f_code.co_name
	# 開始ログ出力
	utilClass.logging('[' + methodname + ']',0)


	# 基準日以降に開催されるレースIDを全て取得する
	where =["AND RACE_DATE >= '%s'"% standardTime," ORDER BY RACE_DATE ASC"]
	raceIdList =  daoClass.selectQuery(where,'selectPostRace')

	# レースIDを一件づつ処理する
	for race_id in raceIdList:
		raceId = race_id[0] # レースID 取得
		utilClass.logging(raceId + 'is started',2) # レースID 取得

		# レース情報更新サービス呼び出し
		result = raceUpdateClass.execute(raceId,1)
		if result['returnCode'] != 0:
			if result['returnCode'] == 9:
				utilClass.loggingError(raceId + 'is faled in raceInfoUpdate\n' + result['msg']) 
				break
			else:
				utilClass.loggingWarn(raceId + 'is warned in raceInfoUpdate\n' + result['msg'])
				continue

		result = raceUpdateClass.execute(raceId,2)
		if result['returnCode'] != 0:
			if result['returnCode'] == 9:
				utilClass.loggingError(raceId + 'is faled in raceInfoUpdate\n' + result['msg']) 
				break
			else:
				utilClass.loggingWarn(raceId + 'is warned in raceInfoUpdate\n' + result['msg'])
				continue

		# データマイニングサービス呼び出し
		result = dataMiningClass.execute(raceId,2)
		if result['returnCode'] != 0:
			if result['returnCode'] == 9:
				utilClass.loggingError(raceId + 'is faled in dataMining\n' + result['msg']) 
				break
			else:
				utilClass.loggingWarn(raceId + 'is warned in dataMining\n' + result['msg'])
				continue

		utilClass.logging(raceId + 'is ended',2)


	# 終了ログ
	utilClass.logging('[' + methodname + ']',0)



if __name__ == '__main__':
	main()
