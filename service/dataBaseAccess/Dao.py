# coding: utf-8
# 概要
# Dao
################ 変更履歴 ######################
## 2017/09/13 作成

###############################################
from datetime import datetime
import os
import configparser
import sys
import MySQLdb
import xml.etree.ElementTree as ET


class Dao(object):
	# グローバル変数
	homeDir = ''
	inifile = ''
	pid = ''
	START = 'start.'
	END = 'end.'
	INFO = '[INFO] '
	ERROR = '[ERROR] '
	WARN = '[WARN] '
	INSERT = None
	SELECT =None
	UPDATE = None
	db = None
	user = None
	host = None
	passwd = None
	charset = None

	# DBアクセス
	connection = None
	cursor = None
	root = None
	sql = None

	# Util
	utilClass = None

	# 初期化処理
	def __init__(self,dict):
		# 環境変数を取得する。
		self.homeDir = os.environ["APPMONEYTRADE"]

		# iniconfigファイルを読み出す。
		self.inifile = dict['util'].inifile

		# DB情報を取得
		self.db = self.inifile.get('mysql','db')
		self.host = self.inifile.get('mysql','host')
		self.user = self.inifile.get('mysql','user')
		self.passwd = self.inifile.get('mysql','passwd')
		self.charset = self.inifile.get('mysql','charset')

		# 機能ID
		self.pid = dict['pid']

		# utilクラス
		self.utilClass = dict['util']
		
		# DBクラスを取得する。
		sys.path.append(self.homeDir)

		# コネクションの生成
		self.connection = MySQLdb.connect(db=self.db, host=self.host,user=self.user, passwd=self.passwd, charset=self.charset)

		# 実行中のディレクトリを取得する。
		exeNowPath = os.path.abspath(os.path.abspath(os.path.dirname(__file__)))
		
		#　呼び出し元もでイレクトリを取得する。
		calledPath = os.getcwd()
		
		# 実行中のディレクトリをカレントディクトリとする.
		os.chdir(exeNowPath)
		
		# xmlファイルの読み込み
		tree = ET.parse('select_map.xml')
		self.root = tree.getroot()
		
		# 作業ディレクトリを元に戻す
		os.chdir(calledPath)


	# 抽出
	def selectQuery(self,where,id):
		self.makeConn()
		list = self.selectexe(where,id)
		return list

	# コネクションの削除
	def closeConn(self):
		self.connection.close()
		return

	# コネクション生成
	def makeConn(self):
		if self.connection is None or self.connection == '':
			self.connection = MySQLdb.connect(db=self.db, host=self.host,user=self.user, passwd=self.passwd, charset=self.charset)

		return

	# 挿入
	def insert(self,tablename,dict):
		self.makeConn()
		self.insertexe(tablename,dict)
		return True

	# 更新
	def update(self,tablename,dict,where):
		self.makeConn()
		self.updateexe(tablename,dict,where)
		return True


	# SELECT
	def selectexe(self,where,sqlId):
		# xmlファイルからSQLを取得する。
		es = self.root.find(".//sql[@name='%s']"% sqlId)
		sql = ''
		for query in es.findall(".//query"):
			sql = sql + query.text.strip() + ' '
		
		
		# 任意の句を整える。
		phrase = ''
		for index in range(len(where)):
			phrase = phrase + where[index]
		
		sql = sql + phrase
		
		sql = sql.strip() + ';'

		# デバッグsQL
		cursor = self.connection.cursor()		
		cursor.execute(sql)
				
		resultList = []
		for row in cursor.fetchall():
			resultList.append(row)

		self.connection.commit()
		cursor.close()
		return resultList

	# INSERT
	def insertexe(self, table, dict):
		sql = self.buildQueryInsertFromDict(table, dict)
		cursor = self.connection.cursor()
		cursor.execute(sql, dict)
		cursor.close()
		self.connection.commit()

	# INSERT部品
	def dictValuePad(self, key):
		return "%(" + str(key) + ")s"

	# INSERT部品
	def buildQueryInsertFromDict(self, table, dict):
		sql = "INSERT INTO " + table + " (" + ",".join(dict) + ") VALUES (" + ",".join(map(self.dictValuePad, dict)) + ")"
		sql += ";"
		return sql


	# UPDATE
	def updateexe(self,table, dict,where):
		sql = self.buildQueryUpdateFromDict(table, dict, where)
		cursor = self.connection.cursor()
		cursor.execute(sql)
		cursor.close()
		self.connection.commit()

	# update部品
	def buildQueryUpdateFromDict(self, table, dict , where):
		query = "UPDATE " + table + " SET "
		updateColumns = ''
		for k, v in dict.items():
			update = "%s = '%s' ,"% (k,v)
			updateColumns = updateColumns + update
		
		if updateColumns != '':
			updateColumns = updateColumns[:-1]
		
		sql = query + updateColumns + ' ' + where
		sql += ";"
		return sql


