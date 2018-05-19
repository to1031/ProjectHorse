#coding: utf-8
# 概要
# JRA過去データ取得
################ 変更履歴 ######################
## 2017/09/13 作成

###############################################
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import sys
import os
import datetime
import traceback

class JraPastInfoGet(object):
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

		# dict
		self.dict = dict


	##################################################################
	###### 引数1:yyyymmdd
	###### 概要:引数で取得した年月に開催されたレースの情報を取得する。
	##################################################################
	def jraPastInfoGet(self,today):
		# 当メソッドの名前を取得する。
		methodname = sys._getframe().f_code.co_name

		# 処理開始ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,0)

		# 引数取得
		COND_YEAR = today[0:4]
		COND_MONTH = today[4:6]

		# 対象年月ログ出力
		self.utilClass.logging('target_ym:' + COND_YEAR + '/' + COND_MONTH,2)

		# 終了コード
		returnCode = 0

		
		# 部品import
		sys.path.append(self.homeDir + 'service/jrapastinfoget/')
		import RaceResult
		import RaceResultOdds


		RaceResultClass = RaceResult.RaceResult(self.dict)
		RaceResultOddsClass = RaceResultOdds.RaceResultOdds(self.dict)
		try:

			
			# PhantomJSからwebDriverオブジェクトを取得する。
			driver = webdriver.PhantomJS('/usr/local/bin/phantomjs')
			
			# JRAトップ画面を開く。
			driver.get('http://www.jra.go.jp/')
			
			# レース結果をクリックする。
			parent = driver.find_element_by_id('q_menu6')
			parent.find_element_by_tag_name('a').click()
			
			# 1秒待つ
			time.sleep(1)
			
			# 過去レース検索画面はこちらをご覧ください。をクリックする。
			driver.find_element_by_link_text('過去レース検索画面はこちらをご覧ください。').click()
		
			# 1秒待つ
			time.sleep(1)
			
			# 過去レース検索画面から西暦と月を指定してクリックする。
			# 年を選択してクリックする。
			selYear = driver.find_element_by_id('kaisaiY_list')
			for option in selYear.find_elements_by_tag_name('option'):
				if option.text == COND_YEAR:
					option.click()
					break
			
			time.sleep(1)
			
			# 月を選択してクリックする。
			selMonth = driver.find_element_by_id('kaisaiM_list')
			for option in selMonth.find_elements_by_tag_name('option'):
				if option.text == COND_MONTH:
					option.click()
					break
			
			time.sleep(1)
			
			# 検索ボタンlinkをクリックする。
			driver.find_elements_by_tag_name('a')[104].click()
			
			# 練習として見つかった一個目の画面に入る。
			roop = 104
			for i in range(len(driver.find_elements_by_tag_name('a'))):
				# リンクの値を変数に格納する。
				linkCond = driver.find_elements_by_tag_name('a')[roop].text
				
				# 空文字の場合はskipする。
				if linkCond == '':
					roop = roop + 1
					continue
				
				# 重賞レース及び日付のリンクを処理しない。
				if '回' in linkCond[0:4]:
					# 遷移先に移動
					driver.find_elements_by_tag_name('a')[roop].click()
					
					# 2秒まつ
					time.sleep(1)
					
					# 遷移先のレース一覧画面で1Rから順に画面を開く。
					roop_rist = 0
					# レース結果詳細画面にリンクするリンクを取得する。
					for i in range(len(driver.find_elements_by_css_selector("a[onclick*='accessS']"))):
						# 要素がから文字の場合スキップする。
						if driver.find_elements_by_css_selector("a[onclick*='accessS']")[roop_rist].text == '':
							roop_rist = roop_rist + 1
							continue
						# 競馬場及び回数のリンクをスキップし、ロープする条件を取得する。
						elif driver.find_elements_by_css_selector("a[onclick*='accessS']")[roop_rist + 1].text != '':
							roop_rist = roop_rist + 1
							continue
						else:
							roop_rist = roop_rist + 2
							break
					
					# レース結果画面に遷移する。
					for index in range(roop_rist,len(driver.find_elements_by_css_selector("a[onclick*='accessS']"))):
						# レースリザルトを取得する。
						driver.find_elements_by_css_selector("a[onclick*='accessS']")[roop_rist].click()
						time.sleep(1)
						resultHtmlStr = driver.page_source
						RaceResultClass.jraResult_main(resultHtmlStr)
						
						driver.back()
		
						time.sleep(1)
						
						roop_rist = roop_rist + 1
						
					# レースのオッズ情報を取得する。
					# オッズ情報を取得する。
					driver.save_screenshot('gggg.png')
					for index in range(2,len(driver.find_elements_by_css_selector("a[onclick*='accessO']"))):
						driver.find_elements_by_css_selector("a[onclick*='accessO']")[index].click()
						time.sleep(1)
						oddsHtmlStr = driver.page_source
						RaceResultOddsClass.jraResultOdds_main(oddsHtmlStr,1)
						time.sleep(1)
						
						# 馬連のオッズ情報を取得する。
						driver.find_element_by_partial_link_text("馬連").click()
						time.sleep(1)
						oddsUmarenHtmlStr = driver.page_source
						RaceResultOddsClass.jraResultOdds_main(oddsUmarenHtmlStr,2)
						driver.back()
						time.sleep(1)
					
						# 馬単のオッズ情報を取得する。
						driver.find_element_by_partial_link_text("馬単").click()
						time.sleep(1)
						oddsUmatanHtmlStr = driver.page_source
						RaceResultOddsClass.jraResultOdds_main(oddsUmatanHtmlStr,3)
						driver.back()
						time.sleep(1)
	
						# ワイドのオッズ情報を取得する。
						driver.find_element_by_partial_link_text("ワイド").click()
						time.sleep(1)
						oddsWideHtmlStr = driver.page_source
						RaceResultOddsClass.jraResultOdds_main(oddsWideHtmlStr,4)
						driver.back()
						time.sleep(1)
						
						# 3連複のオッズ情報を取得する。
						driver.find_element_by_partial_link_text("3連複").click()
						time.sleep(1)
						odds3renpukuHtmlStr = driver.page_source
						RaceResultOddsClass.jraResultOdds_main(odds3renpukuHtmlStr,5)
						driver.back()
						time.sleep(1)

					
						# 3連単のオッズ情報を取得する。	
						driver.find_element_by_partial_link_text("3連単").click()
						time.sleep(2)
						odds3RentanHtmlStr = driver.page_source
						RaceResultOddsClass.jraResultOdds_main(odds3RentanHtmlStr,6)
						driver.back()
						time.sleep(1)
					
					driver.back()
					time.sleep(1)			
					roop = roop + 1
				else:
					roop = roop + 1
					continue
					
				
				# リターンコードを設定する。
				returnCode = 0
		
		except:
			# リターンコードを設定する。
			traceback.print_exc()
			returnCode = 9
		
		finally:
			print(datetime.datetime.today().strftime('%Y/%m/%d %H:%M:%S'))
			driver.close()
			
			# 処理を返す。
			return returnCode
