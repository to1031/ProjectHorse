#coding: utf-8
# 概要
# 定数クラス
################ 変更履歴 ######################
## 2017/09/13 作成
###############################################

class Const(object):
	
	# 初期化処理
	def __init__(self,pid,util,dao,mail):
		# 環境変数を取得する。
		self.homeDir = os.environ["APPMONEYTRADE"]


	# クラス定数 homeDirからの相対パス
	CONFPATH = '../../temp_ProjectMoneyTrade/conf'
