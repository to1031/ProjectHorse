#coding: utf-8
# 概要
# JRA今週末データ取得
################ 変更履歴 ######################
## 2017/09/13 作成

###############################################
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import datetime
import traceback
from bs4 import BeautifulSoup
import os
import sys

class JraPostInfoGet(object):

	# 初期化処理
	def __init__(self,dict):
		# 環境変数を取得する。
		self.homeDir = os.environ["APPHORSE"]

		# iniconfigファイルを読み出す。
		self.inifile = dict['util'].inifile

		# 当サービスの機能IDを取得する。
		self.pid = 'JPAG'

		# 呼び出し元も機能ID
		self.call_pid = dict['pid']

		# util
		self.utilClass = dict['util']

		# mail
		self.mail = dict['mail']

		#
		self.daoClass = dict['dao']

		# dict
		self.dict = dict



	def jraPostInfoGet(self):
		# 当メソッドの名前を取得する。
		methodname = sys._getframe().f_code.co_name

		# 処理開始ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,0)

		# 終了コード
		returnCode = 0

		# 部品import
		sys.path.append(self.homeDir + 'service/jrapostinfoget/')
		import PostRaceInfo
		PostRaceInfoClass = PostRaceInfo.PostRaceInfo(self.dict)


		# 終了コード
		returnCode = 0
		
		try:
			# PhantomJSからwebDriverオブジェクトを取得する。
			driver = webdriver.PhantomJS('/usr/local/bin/phantomjs')
			
			# JRAトップ画面を開く。
			driver.get('http://www.jra.go.jp/')
			
			# レース結果をクリックする。
			parent = driver.find_element_by_id('q_menu3')
			parent.find_element_by_tag_name('a').click()
			
			# 1秒待つ
			time.sleep(1)
			
			# kaisaiBtn が多いためtableで絞る。
			kaisaiBtn = driver.find_element_by_class_name("kaisaiDayList")
			
			# レース会場毎に処理を進める。
			for outindex in range(len(kaisaiBtn.find_elements_by_xpath("//td [@class='kaisaiBtn']"))):
				kaisaiBtn = driver.find_element_by_class_name("kaisaiDayList")
				kaisaiBtn.find_elements_by_xpath("//td [@class='kaisaiBtn']/a[1]")[outindex].click()
				time.sleep(1)

				
				# 各レース毎に処理を進める。
				for inIndex in range(len(driver.find_elements_by_xpath("//td [@rowspan='2'][@headers='c1'][@class='shutsubaCol']/a [contains(@onclick,'accessD.html')]"))):
					
					
					# 各レースをクリックする。
					driver.find_elements_by_xpath("//td [@rowspan='2'][@headers='c1'][@class='shutsubaCol']/a [contains(@onclick,'accessD.html')]")[inIndex].click()
					time.sleep(1)

					# レース情婦を取得する。
					resultHtmlStr = driver.page_source
					PostRaceInfoClass.jraInfo_main(resultHtmlStr,0)

					
					# レースのオッズをクリックする。
					driver.find_element_by_xpath("//div [@class='heading2BtnDiv']/a [contains(@onclick,'accessO.html')]").click()
					time.sleep(1)
					
					# レース詳細情報とオッズ（単勝・複勝の情報を取得する。）
					resultHtmlStrDeitai = driver.page_source
					PostRaceInfoClass.jraInfo_main(resultHtmlStrDeitai,1)

					driver.back()
					time.sleep(1)
					
					driver.back()
					time.sleep(1)
					
					# 最後にリンクを取得して更新する。
					if inIndex == 11:
						condHtml = driver.page_source
						soup = BeautifulSoup(condHtml,'html.parser')
						link_text = soup.find('td',{'class':'kaisaiBtnStay'}).find('a')
						link_text = link_text['onclick'].strip().replace("return doAction('/JRADB/accessD.html','",'')[:-2]
						dict = {}
						dict['CONDITION_LINK'] = link_text
						koteStr = 'R0100'
						matuStr = '%'
						raceDate = soup.find('h3',{'class':'heading1Font'}).string.strip()
						raceDatePlace = soup.find('h3',{'class':'heading1Font'}).string.strip()
						# 月が10以上フラグ
						month10Flg = 1
		
						# 西暦を取得する。
						yesrStr = raceDate[0:4]
		
						# 月を取得する。
						monthStr = raceDate[5:7]
						if '月' in monthStr:
							month10Flg = 0
							monthStr = '0' + monthStr[0:1]
		
						# 日を取得する。
						dayStr = ''
						if month10Flg == 0:
							dayStr = raceDate[7:9]
							if '日' in dayStr:
								dayStr = '0' + dayStr[0:1]
						else:
							dayStr = raceDate[8:10]
							if '日' in dayStr:
								dayStr = '0' + dayStr[0:1]
						
						racePlace = ''
						if '札幌' in raceDatePlace:
							racePlace = '01'
						elif '函館' in raceDatePlace:
							racePlace = '02'
						elif '福島' in raceDatePlace:
							racePlace = '03'
						elif '新潟' in raceDatePlace:
							racePlace = '04'
						elif '東京' in raceDatePlace:
							racePlace = '05'
						elif '中山' in raceDatePlace:
							racePlace = '06'
						elif '中京' in raceDatePlace:
							racePlace = '07'
						elif '京都' in raceDatePlace:
							racePlace = '08'
						elif '阪神' in raceDatePlace:
							racePlace = '09'
						elif '小倉' in raceDatePlace:
							racePlace = '10'
						else:
							racePlace = '00'	
			
						raceDate = yesrStr + monthStr + dayStr
						raceId = koteStr + raceDate + racePlace + matuStr
						where = "WHERE RACE_ID LIKE '%s'"% raceId
						self.daoClass.update('POST_RACE_PARAM_T',dict,where)

				driver.back()
				time.sleep(1)

				
		
		except:
			# リターンコードを設定する。
			traceback.print_exc()
			returnCode = 9
		
		finally:
			print(datetime.datetime.today().strftime('%Y/%m/%d %H:%M:%S'))
			driver.close()
			
			return returnCode
