#coding: utf-8
# 概要
# グラフ描写サービスクラス
################ 変更履歴 ######################
## 2017/09/13 作成

###############################################

import itertools
from datetime import datetime
import math
import os
import configparser
import sys
import matplotlib.pyplot as pyplot
import numpy as np

class GraphDepiction(object):
	
	# 初期化処理
	def __init__(self,dict):
		# 環境変数を取得する。
		self.homeDir = os.environ["APPMONEYTRADE"]

		# iniconfigファイルを読み出す。
		self.inifile = dict[['util'].inifile

		# 当サービスの機能IDを取得する。
		self.called_pid = __name__[0:4]

		# 呼び出し元も機能ID
		self.pid = dict['pid']


	# グラフ描写のためのデータを作成する。
	def gdsuService(self,x_list,y_list,x_label,y_label,title):
		# 当メソッドの名前を取得する。
		methodname = sys._getframe().f_code.co_name



		# X,Yのリストの数が一致しない場合は処理を返す。
		if len(x_list) != len(y_list):
			return

		# グラフの値を格納していく。
		pyplot.plot(x_list, y_list, label=title)
		pyplot.xlabel(x_label)
		pyplot.ylabel(y_label)
		

		# #グラフの凡例
		pyplot.legend()

		# グラフの描写
		pyplot.show()
