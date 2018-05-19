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
	standardTime = starttime.strftime('%Y%m%d%H%M')
	# 環境変数を取得する。
	homeDir = os.environ["APPMONEYTRADE"]

	# log用の文字列準備
	exefile = os.path.basename(__file__)
	pid = os.path.basename(__file__)[0:4] # 機能IDの取得

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
	object_dict['mass'] = MASSClass



	# データマイニングクラスを取得する。
	#DTMClass = DTMDataMining.DTMDataMining(pid,utilClass,daoCass)
	# トレード決定サービスクラスを取得する。
	#TradeClass = TradeDecision.TradeDecision(pid,utilClass,daoClass,MASSClass)
	# 機械学習(sigmoid)を呼び出す
	#DNNSigmoidClass = DNNSDNNSigmoid.DNNSDNNSigmoid(pid,utilClass,daoClass)
	# データ収集クラスを呼び出す。
	#DataGatherSaveClass = DGGSDataGatherSave.DGGSDataGatherSave(pid,utilClass,daoClass,MASSClass)

	


if __name__ == '__main__':
	main()
