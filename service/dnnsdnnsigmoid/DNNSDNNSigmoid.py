#coding: utf-8
# 概要
# 
################ 変更履歴 ######################
## 2017/09/13 作成
# DNNclassを呼び出しsigmoid関数を利用した２値分類結果を取得する
###############################################
import numpy as np
import tensorflow as tf
import os
import sys
import configparser

class DNNSDNNSigmoid(object):

	# 初期化処理
	def __init__(self,dict):
		# 環境変数を取得する。
		self.homeDir = os.environ["APPMONEYTRADE"]

		# iniconfigファイルを読み出す。
		self.inifile = dict['util'].inifile

		# 当サービスの機能IDを取得する。
		self.pid = os.path.basename(__file__)[0:4]

		# 呼び出し元も機能ID
		self.called_pid = dict['pid']

		# utilClass
		self.utilClass = dict['util']

		# daoクラス
		self.daoClass = dict['dao']

		# sys.path.append(homeDir)
		sys.path.append(self.homeDir + 'batch/machinelearn/sigmoid_DNN/')
		import DNN_class
		self.DNN_class = DNN_class

		# DNNmodelpath
		self.modelpath = self.inifile.get('filepath','model')


	# ディープニューラルネットワークで計算 sigmoid関数
	def dnnsService(self,condtime,path='FLG_UPDOWN_1MINUTE'):
		# 返却interface
		returnDict = {}
		returnDict['resultCode'] = 9

		# 当メソッドの名前を取得する。
		methodname = sys._getframe().f_code.co_name

		# 処理開始ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,0)

		# 格納しないリスト
		ifList = [0,1,11,41,42,43,44,45,55,56,57,58,59,60,75,90,105]

		# マイニング結果を取得する。getDataMining
		where = ["WHERE DATA_TIME = '%s'" % condtime]
		dataList = self.daoClass.selectQuery(where,'getDataMining')

		# データ件数が1件未満の場合は処理を返す。
		if len(returnDict) != 1:
			self.utilClass.logging('data is not found so that exe is skiped data is datamining by ' + condtime ,2)
			returnDict['resultCode'] = 1
			return returnDict


		# 特徴量を整える。
		x_train = []
		x_predate = []
		paramlist = []
		for i in range(len(dataList[0])):
			# 学習データ格納
			if i not in ifList and i <= 119:
				paramlist.append(dataList[0][i])

		# input_num
		input_num = len(paramlist)

		x_predate.append(paramlist)

		# DNNの読み取れる配列に変換
		X_train = np.array(x_predate)

		# 機械学習モデルを復元す
		model = self.DNN_class.DNN(n_in = input_num,n_hiddens=[5000,8000,5000],n_out = 1)

		# 学習モデルに特徴量を与えて予想結果を取得する。
		dnnResult = model.getRestore(X_train,self.homeDir + self.modelpath + path)

		# 処理終了ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,1)

		# 返却データを整える。
		returnDict['resultCode'] = 0
		returnDict['predict'] = dnnResult[0][0]
		return returnDict
