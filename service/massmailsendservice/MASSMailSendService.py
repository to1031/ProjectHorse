#coding: utf-8
# 概要
# メール関連のサービスクラス
################ 変更履歴 ######################
## 2017/09/13 作成

###############################################
from datetime import datetime
import os
import configparser
import sys
from email.mime.text import MIMEText
import smtplib
from email.header import Header
from email.utils import formatdate
import xml.etree.ElementTree as ET
import imaplib
import email
import dateutil.parser
import requests

class MASSMailSendService(object):

	# 初期化処理
	def __init__(self,dict):
		# 環境変数を取得する。
		self.homeDir = os.environ["APPHORSE"]

		# iniconfigファイルを読み出す。
		self.inifile = dict['util'].inifile

		# 当サービスの機能IDを取得する。
		self.pid = 'MASS'

		# 呼び出し元も機能ID
		self.call_pid = dict['pid']

		# util
		self.utilClass = dict['util']

		#必要情報を取得する。
		self.fromaddress=self.inifile.get('smtp','fromaddress')
		self.server=self.inifile.get('smtp','server')
		self.toaddress=self.inifile.get('smtp','toaddress')
		self.password=self.inifile.get('smtp','password')
		self.textdir=self.inifile.get('smtp','textdir')
		self.textdir=self.homeDir + self.textdir

		self.lineto=self.inifile.get('smtp','lineto')

	# メインメソッド
	def massService(self,mailType):
		# 当メソッドの名前を取得する。
		methodname = sys._getframe().f_code.co_name

		# 処理開始ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,0)
		
		# LINE notifyで通知を送る
		url = "https://notify-api.line.me/api/notify"
		token = self.lineto
		headers = {"Authorization" : "Bearer "+ token}

		# msg調整
		body = mailType['body']
		body = ','.join(body).replace(',','\n')
		body = '[' + mailType['subject'] + ']\n' + body
		message = body

		payload = {"message" :  message}

		r = requests.post(url ,headers = headers ,params=payload)


		# 処理終了ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,1)

	# メール確認サービス
	def msscService(self,condtime):
		# 当メソッドの名前を取得する
		methodname = sys._getframe().f_code.co_name

		# 処理開始ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,0)

		# 返却用辞書
		returnDict = {}
		returnDict['resultCode'] = 0
		returnDict['sysdradeTodo'] = 0

		# メール保存用
		maildatalist = []

		# 現在時刻
		host = 'imap.gmail.com'
		mailbox = 'INBOX'

		#メールサーバ指定
		M = imaplib.IMAP4_SSL(host=host)
		M.login(self.fromaddress, self.password)

		#メールボックス選択
		M.select(mailbox)
		
		# メールの探し
		typ, data = M.search(None, 'FROM', '"%s"'% self.toaddress)

		# 5分前の日時を取得する
		cond_date = self.utilClass.addDateTimeStr(condtime,0,0,-5)


		# メールの取得
		if data[0] != "" :
			msg_ids = data[0].split()

			# 最新のメールのみ取得する
			msg_id = msg_ids[len(msg_ids) -1]
			typ, data = M.fetch(msg_id, '(RFC822)')
			#必要情報を取得する。
			raw_email=data[0][1]
			#文字コード取得用
			msg=email.message_from_string(raw_email.decode('utf-8'))
			msg_encoding=email.header.decode_header(msg.get('Subject'))[0][1] or 'iso-2022-jp'
			#パースして解析準備
			msg=email.message_from_string(raw_email.decode(msg_encoding))

			date = dateutil.parser.parse(msg.get('Date')).strftime("%Y%m%d%H%M")
			subject = email.header.decode_header(msg.get('Subject'))
			title = ""
			for sub in subject:
				if isinstance(sub[0],bytes):
					title += sub[0].decode('utf-8')
				else:
					title += sub[0]

			# ストップのメールを受け取っていた場合
			if date >= cond_date and 'ストップ' in title:
				# システムトレードを中止する。
				returnDict['sysdradeTodo'] = 1

			# リスタートのメールを受け取っていた場合
			if date >= cond_date and 'スタート' in title:
				# システムトレードを再開する
				returnDict['sysdradeTodo'] = 2

		# IMAP ログアウト
		M.close()
		M.logout()

		# 処理を中止する
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,1)

		# 返却する
		return returnDict
