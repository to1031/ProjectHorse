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
	import DNNSDNNSogmoid
	from dataBaseAccess import SELECTGET
	from util import Util
	from util import JsonParse
	from forge import ForgeApi
	from dataBaseAccess import Dao

	# utilクラスのオブジェクト取得
	utilClass = Util.Util(pid)
	# daoクラスを生成する。
	dao = Dao.Dao(pid)

	# Test対象クラスのインスタンスを生成する。
	DNNSDNNSogmoidClass = DNNSDNNSogmoid.DNNSDNNSogmoid(pid,utilClass,dao)

	# デバッグ
	condtime = '201707210629'

	result = DNNSDNNSogmoidClass.dnnsService(condtime,'FLG_UPDOWN_1MINUTE')


	# 実行時間
	endtime = datetime.now()
	delta = endtime - starttime
	print('実行秒数:' + str(delta.total_seconds()))


def convertDatetime(condStr):
	tdatetime = datetime.strptime(condStr, '%Y%m%d%H%M')
	return tdatetime

if __name__ == '__main__':
	main()
