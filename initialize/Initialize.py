#coding: utf-8
# 概要
# 初期化クラス
################ 変更履歴 ######################
## 2017/09/13 作成

###############################################
import os
import configparser
import sys

class Initialize(object):

	# 初期化処理
	def __init__(self,dict):
		# 環境変数を取得する。
		self.homeDir = os.environ["APPHORSE"]

		# 当サービスの機能IDを取得する。
		self.pid = 'INI'

		# 呼び出し元も機能ID
		self.call_pid = dict['pid']

		# iniconfig_classファイルを読み出す。
		condigPath = self.homeDir + '../temp_ProjectHorse/conf'
		inifile_class = configparser.ConfigParser()
		inifile_class.read(condigPath + '/config_class.ini', 'UTF-8')
		self.inifile_class = inifile_class

		# iniconfigファイルを読み出す
		inifile = configparser.ConfigParser()
		inifile.read(condigPath + '/config.ini', 'UTF-8')
		self.inifiles = inifile

		# 一時的に環境パスに追加する
		sys.path.append(self.homeDir)
		sys.path.append(self.homeDir + 'service/')
		sys.path.append(self.homeDir + 'batch/')
	
		# import
		from dataBaseAccess import Dao
		from util import Util
		from massmailsendservice import MASSMailSendService

		# utilクラス、daoクラス、メールクラスをインスタンス化
		object_dict = {}
		object_dict['pid'] = self.call_pid
		self.utilClass = Util.Util(object_dict)
		object_dict['util'] = self.utilClass
		self.daoClass = Dao.Dao(object_dict)
		self.MASSClass = MASSMailSendService.MASSMailSendService(object_dict)

	# クラスの生成
	def class_ins(self,class_name,dict=None):
		# 一時的に環境パスを追加する
		sys.path.append(self.homeDir)
		sys.path.append(self.homeDir + 'service/')
		sys.path.append(self.homeDir + 'batch/')

		# configファイルからクラス情報を取得する。
		pack_class = self.inifile_class.get('class',class_name)
		
		# パッケージ名とクラス名を取得する。
		project_name = pack_class.split(',')[0]
		pack_name = pack_class.split(',')[1]
		class_name = pack_class.split(',')[2]

		# 環境変数追加
		sys.path.append(self.homeDir + project_name + '/' + pack_name)

		# 動的import
		mod = __import__(class_name,fromlist=[class_name])
		class_def = getattr(mod,class_name)
		obj = class_def(dict)

		# 返却
		return obj


		
