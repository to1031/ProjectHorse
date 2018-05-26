#coding: utf-8
# 概要
# accessS.htmlのスクレイピング
################ 変更履歴 ######################
## 2017/09/13 作成

###############################################
from bs4 import BeautifulSoup
import codecs
import datetime
import re
import sys
import os
import math
import requests

class RaceInfoUpdate(object):
	# 初期化処理
	def __init__(self,dict):
		# 環境変数を取得する。
		self.homeDir = os.environ["APPHORSE"]

		# iniconfigファイルを読み出す。
		self.inifile = dict['util'].inifile

		# 当サービスの機能IDを取得する。
		self.pid = 'RaceInfoUpdate'

		# 呼び出し元も機能ID
		self.call_pid = dict['pid']

		# util
		self.utilClass = dict['util']

		# dao
		self.daoClass = dict['dao']

		self.dict = dict


	##################################################################
	###### 引数1:レースID
	###### 概要:引数で取得したレースIDの馬体重およびオッズ情報(単勝とか）
	###### の情報を更新する。
	##################################################################
	def execute(self,race_id,type):
		# 当メソッドの名前を取得する。
		methodname = sys._getframe().f_code.co_name

		# 処理開始ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,0)

		# import
		sys.path.append(self.homeDir + 'service/')
		from jrapostinfoget import PostRaceInfo

		PostRaceInfoClass = PostRaceInfo.PostRaceInfo(self.dict)

		# 終了コード
		returnDict = {}
		returnDict['returnCode'] = 0

		try:

			# html取得
			result = self.getHtml(race_id,type)
			if result['resultCode'] == 1:
				return result
			soup = result['soup']

			if type == 1: # detail
				PostRaceInfoClass.post_race_detail_t(soup)
			elif type == 2: # 単勝・複勝
				PostRaceInfoClass.odds_and_param(soup)
			elif type == 3: # 馬連
				self.race_umaren_t(soup)
			elif type == 4: # 馬単
				self.race_umatan_t(soup)
			elif type == 5: # ワイド
				self.race_wide_t(soup)
			elif type == 6: # 3連複
				self.race_3renpuku_t(soup)
			elif type == 7: # 3連単
				self.race_3rentan_t(soup)

		except:
			# リターンコードを設定する。
			import traceback
			returnCode = 9
			error_text = traceback.format_exc()
			self.utilClass.loggingError(error_text)
			returnDict['returnCode'] = 9
			returnDict['msg'] = error_text

		finally:
			self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,1)
			# 処理を返す。
			return returnDict






	##################################################################
	###### 引数1:race_id
	###### 戻り値:なし
	###### 概要:引数で取得したrace_idのレース詳細情報を更新する
	###### 
	##################################################################
	def race_umaren_t(self,soup):
		# メソッドの名
		methodname = sys._getframe().f_code.co_name
		# メソッド開始ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,0)
		self.utilClass.logging('target race is ' + race_id,2)

		# レースIDを取得するための処理を記述する。
		racePlaceDate = soup.find('td',{'class':'cTtl headerOdds'}).text.strip() 
		racePlace = self.racePlaceGet(racePlaceDate)
		raceDate = self.raceDateGet(racePlaceDate)
		if soup.find('td',{'class':'TtlNMnonDK headerOdds4'}) is None:
			raceName = soup.find('td',{'class':'TtlNMWIN5DK headerOdds4'}).text.strip() 
		else:
			raceName = soup.find('td',{'class':'TtlNMnonDK headerOdds4'}).text.strip() 
		raceNo = self.raceNoGet(raceName)
	
		# レースIDを取得する。
		raceId = 'R0100' + raceDate + racePlace + raceNo

	
		# スクレイピングを開始する。
		raceOddsList = soup.find_all('table',{'class':'ozUmarenUmaINTable'})
		
		# DBにすでに情報がある場合は更新する。
		selectPostRaceUmaren = ["WHERE RACE_ID = '%s'"% raceId]
		result = self.daoClass.selectQuery(selectPostRaceUmaren,'selectPostRaceUmaren')		

		updateFlg = 1
		if result[0][0] == 0:
			updateFlg = 0
		
		# 取得したリスト毎に処理を進める。
		for numAndOdds in raceOddsList:
			# 変数初期化
			targetStartNum = 0
			target2StartNum = 0
			oddsList = []
			startNumList = []
			dict_Db_RACE_ODDS_UMAREN_T = {}
			
			# DB格納値の固定値
			dict_Db_RACE_ODDS_UMAREN_T['LOGIC_DEL_FLG'] = 0
			dict_Db_RACE_ODDS_UMAREN_T['INS_PID'] = 'RID13'
			dict_Db_RACE_ODDS_UMAREN_T['UPD_PID'] = 'RID13'
			dict_Db_RACE_ODDS_UMAREN_T['RACE_ID'] = raceId
			
			# 対象馬の1つを取得する。
			targetStartNum = numAndOdds.find('th',{'class':'title'}).string.strip()
			
			# 対象馬のもう1つを取得する。
			targetStartNumList = numAndOdds.find_all('th',{'class':'thubn'})
			for startNum in targetStartNumList:
				startNumList.append(startNum.string.strip())
			
			# 配当を取得する。
			oddsPreList = numAndOdds.find_all('td',{'class': re.compile('^tdoz.*$')})
			for odds in oddsPreList:
				oddsList.append(odds.string.strip())
				
			
			# DB格納値を確定させる。
			for index in range(len(oddsList)):
				# 変数初期化
				target2StartNum = 0
				oddsVal = 0
				
				target2StartNum = startNumList[index]
				oddsVal = oddsList[index]

				if (not oddsVal[0:1].isdigit()):
					oddsVal = 0
				
				# DBに格納する。
				dict_Db_RACE_ODDS_UMAREN_T['TARGET_STARTNUM'] = targetStartNum
				dict_Db_RACE_ODDS_UMAREN_T['TARGET2_STARTNUM'] = target2StartNum
				dict_Db_RACE_ODDS_UMAREN_T['ODDS_REFUND'] = float(oddsVal)
				
				
				# DB へのInsert
				if updateFlg == 0:
					self.daoClass.insert('POST_RACE_ODDS_UMAREN_T',dict_Db_RACE_ODDS_UMAREN_T)
				else:
					where = "WHERE RACE_ID ='%s' AND TARGET_STARTNUM ='%s' AND TARGET2_STARTNUM ='%s'"% (raceId,targetStartNum,target2StartNum)
					self.daoClass.update('POST_RACE_ODDS_UMAREN_T',dict_Db_RACE_ODDS_UMAREN_T,where)




		# 終了ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,1)


	##################################################################
	###### 引数1:race_id
	###### 引数2:soup
	###### 戻り値:なし
	###### 概要:引数で取得したrace_idのレース詳細情報を更新する
	###### 
	##################################################################
	def race_umatan_t(self,soup):
		# メソッドの名
		methodname = sys._getframe().f_code.co_name
		# メソッド開始ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,0)
		self.utilClass.logging('target race is ' + race_id,2)


		# レースIDを取得するための処理を記述する。
		racePlaceDate = soup.find('td',{'class':'cTtl headerOdds'}).text.strip() 
		racePlace = self.racePlaceGet(racePlaceDate)
		raceDate = self.raceDateGet(racePlaceDate)
		if soup.find('td',{'class':'TtlNMnonDK headerOdds4'}) is None:
			raceName = soup.find('td',{'class':'TtlNMWIN5DK headerOdds4'}).text.strip() 
		else:
			raceName = soup.find('td',{'class':'TtlNMnonDK headerOdds4'}).text.strip() 
		raceNo = self.raceNoGet(raceName)
	
		# レースIDを取得する。
		raceId = 'R0100' + raceDate + racePlace + raceNo
	
		# スクレイピングを開始する。
		raceOddsList = soup.find_all('table',{'class':'ozUmatanUmaINTable'})
		
		

		# DBにすでに情報がある場合は更新する。
		selectPostRaceUmatan = ["WHERE RACE_ID = '%s'"% raceId]
		result = self.daoClass.selectQuery(selectPostRaceUmatan,'selectPostRaceUmatan')
		updateFlg = 1
		if result[0][0] == 0:
			updateFlg = 0
		
		# 取得したリスト毎に処理を進める。
		for numAndOdds in raceOddsList:
			# 変数初期化
			goldNum = 0
			silverNum = 0
			oddsList = []
			startNumList = []
			dict_Db_RACE_ODDS_UMATAN_T = {}
			
			# DB格納値の固定値
			dict_Db_RACE_ODDS_UMATAN_T['LOGIC_DEL_FLG'] = 0
			dict_Db_RACE_ODDS_UMATAN_T['INS_PID'] = 'RID13'
			dict_Db_RACE_ODDS_UMATAN_T['UPD_PID'] = 'RID13'
			dict_Db_RACE_ODDS_UMATAN_T['RACE_ID'] = raceId
			
			# 対象馬の1つを取得する。
			goldNum = numAndOdds.find('th',{'class':'title'}).string.strip()
			
			# 対象馬のもう1つを取得する。
			silverNumList = numAndOdds.find_all('th',{'class':'thubn'})
			for silverNumVal in silverNumList:
				startNumList.append(silverNumVal.string.strip())
			
			# 配当を取得する。
			oddsPreList = numAndOdds.find_all('td',{'class': re.compile('^tdoz.*$')})
			for odds in oddsPreList:
				oddsList.append(odds.string.strip())
			
			# DB格納値を確定させる。
			for index in range(len(oddsList)):
				# 変数初期化
				silverNum = 0
				oddsVal = 0
				
				silverNum = startNumList[index]
				oddsVal = oddsList[index]
				
				# DBに格納する。
				dict_Db_RACE_ODDS_UMATAN_T['GOLD_OF_STARTNUM'] = goldNum
				dict_Db_RACE_ODDS_UMATAN_T['SILVER_OF_STARTNUM'] = silverNum
				# 数字出ない場合はを格納
				if (not oddsVal[0:1].isdigit()):
					oddsVal = 0
				
				dict_Db_RACE_ODDS_UMATAN_T['ODDS_REFUND'] = float(oddsVal)
				
				# DB へのInsert
				if updateFlg == 0:
					INSERTDICT.MySQL('POST_RACE_ODDS_UMATAN_T',dict_Db_RACE_ODDS_UMATAN_T)
					self.daoClass.insert('POST_RACE_ODDS_UMATAN_T',dict_Db_RACE_ODDS_UMATAN_T)
				else:
					where = "WHERE RACE_ID ='%s' AND GOLD_OF_STARTNUM ='%s' AND SILVER_OF_STARTNUM ='%s'"% (raceId,goldNum,silverNum)
					self.daoClass.update('POST_RACE_ODDS_UMATAN_T',dict_Db_RACE_ODDS_UMATAN_T,where)

		# 終了ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,1)


	##################################################################
	###### 引数1:race_id
	###### 引数2:soup
	###### 戻り値:なし
	###### 概要:引数で取得したrace_idのレース詳細情報を更新する
	###### 
	##################################################################
	def race_wide_t(self,soup):
		# メソッドの名
		methodname = sys._getframe().f_code.co_name
		# メソッド開始ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,0)
		self.utilClass.logging('target race is ' + race_id,2)
		# レースIDを取得するための処理を記述する。
		racePlaceDate = soup.find('td',{'class':'cTtl headerOdds'}).text.strip() 
		racePlace = self.racePlaceGet(racePlaceDate)
		raceDate = self.raceDateGet(racePlaceDate)
		if soup.find('td',{'class':'TtlNMnonDK headerOdds4'}) is None:
			raceName = soup.find('td',{'class':'TtlNMWIN5DK headerOdds4'}).text.strip() 
		else:
			raceName = soup.find('td',{'class':'TtlNMnonDK headerOdds4'}).text.strip() 
		raceNo = self.raceNoGet(raceName)
	
		# レースIDを取得する。
		raceId = 'R0100' + raceDate + racePlace + raceNo
	
		# スクレイピングを開始する。
		raceOddsList = soup.find_all('table',{'class':'ozWideUmaINTable'})
		
		# 取得したリスト毎に処理を進める。
		for numAndOdds in raceOddsList:
			# 変数初期化
			targetStartNum = 0
			target2StartNum = 0
			wideMinList = []
			wideMaxList = []
			startNumList = []
			dict_Db_POST_RACE_ODDS_WIDE_T = {}
			
			# DB格納値の固定値
			dict_Db_POST_RACE_ODDS_WIDE_T['LOGIC_DEL_FLG'] = 0
			dict_Db_POST_RACE_ODDS_WIDE_T['INS_PID'] = 'RID12'
			dict_Db_POST_RACE_ODDS_WIDE_T['UPD_PID'] = 'RID12'
			dict_Db_POST_RACE_ODDS_WIDE_T['RACE_ID'] = raceId
			
			# 対象馬の1つを取得する。
			targetStartNum = numAndOdds.find('th',{'class':'title'}).string.strip()
			
			# 対象馬のもう1つを取得する。
			targetStartNumList = numAndOdds.find_all('th',{'class':'thubn'})
			for startNum in targetStartNumList:
				startNumList.append(startNum.string.strip())
			
			# ワイドの最低配当を取得する。
			widePreMinList = numAndOdds.find_all('td',{'class':'wideMin'})
			for wideMin in widePreMinList:
				wideMinList.append(wideMin.string.strip())
	
			# ワイドの最高配当を取得する。
			widePreMaxList = numAndOdds.find_all('td',{'class':'wideMax'})
			for wideMax in widePreMaxList:
				wideMaxList.append(wideMax.string.strip())
			
			
			# DB格納値を確定させる。
			for index in range(len(wideMaxList)):
				# 変数初期化
				target2StartNum = 0
				wideMinVal = 0
				wideMaxVal = 0
				
				target2StartNum = startNumList[index]
				wideMinVal = wideMinList[index]
				wideMaxVal = wideMaxList[index]
				
				# 数字出ない場合は、０を格納
				if (not wideMinVal[0:1].isdigit()):
					wideMinVal = 0
			
				# 数字出ない場合は、０を格納
				if (not wideMaxVal[0:1].isdigit()):
					wideMaxVal = 0
					
				# すでに情報を取得した場合は、DBを更新する。
				selectPostRaceOddsWide = ["WHERE TARGET_STARTNUM IN ('%s') AND TARGET2_STARTNUM = '%s'"% (targetStartNum,target2StartNum),"AND RACE_ID = '%s'"% raceId]
				result = self.daoClass.selectQuery(selectPostRaceOddsWide,'selectPostRaceOddsWide')
				if result[0][0] == 1:
					where = "WHERE TARGET_STARTNUM IN ('%s') AND TARGET2_STARTNUM = '%s' AND RACE_ID = '%s'"% (targetStartNum,target2StartNum,raceId)
					dict_Db_POST_RACE_ODDS_WIDE_T['ODDS_FROM'] = float(wideMinVal)
					dict_Db_POST_RACE_ODDS_WIDE_T['ODDS_TO'] = float(wideMaxVal)
					# DB更新処理
					self.daoClass.update('POST_RACE_ODDS_WIDE_T',dict_Db_RACE_ODDS_WIDE_T,where)
				else:
					# DBに格納する。
					dict_Db_POST_RACE_ODDS_WIDE_T['TARGET_STARTNUM'] = targetStartNum
					dict_Db_POST_RACE_ODDS_WIDE_T['TARGET2_STARTNUM'] = target2StartNum
					dict_Db_POST_RACE_ODDS_WIDE_T['ODDS_FROM'] = float(wideMinVal)
					dict_Db_POST_RACE_ODDS_WIDE_T['ODDS_TO'] = float(wideMaxVal)
				
					# DB へのInsert
					self.daoClass.insert('POST_RACE_ODDS_WIDE_T',dict_Db_RACE_ODDS_WIDE_T)

		# 終了ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,1)

	##################################################################
	###### 引数1:race_id
	###### 引数2:soup
	###### 戻り値:なし
	###### 概要:引数で取得したrace_idのレース詳細情報を更新する
	###### 
	##################################################################
	def race_3renpuku_t(self,soup):
		# メソッドの名
		methodname = sys._getframe().f_code.co_name
		# メソッド開始ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,0)
		self.utilClass.logging('target race is ' + race_id,2)

		# レースIDを取得するための処理を記述する。
		racePlaceDate = soup.find('td',{'class':'cTtl headerOdds'}).text.strip() 
		racePlace = self.racePlaceGet(racePlaceDate)
		raceDate = self.raceDateGet(racePlaceDate)
		if soup.find('td',{'class':'TtlNMnonDK headerOdds4'}) is None:
			raceName = soup.find('td',{'class':'TtlNMWIN5DK headerOdds4'}).text.strip() 
		else:
			raceName = soup.find('td',{'class':'TtlNMnonDK headerOdds4'}).text.strip() 
		raceNo = self.raceNoGet(raceName)
	
		# レースIDを取得する。
		raceId = 'R0100' + raceDate + racePlace + raceNo
	
		# スクレイピングを開始する。
		raceOddsList = soup.find_all('div',{'class':'ozSanrenUmaOutTableArea'})
		
		# 更新するか判断する。
		# DBにすでに情報がある場合は更新する。
		selectPostRentan = ["WHERE RACE_ID = '%s'"% raceId]
		result = self.daoClass.selectQuery(selectPostRentan,'selectPostRentan')
		updateFlg = 1
		if result[0][0] == 0:
			updateFlg = 0
		
		for index in range(len(raceOddsList)):
			goalList = raceOddsList[index]
			
			# 1着/2着/3着馬　及び　払い戻しが格納されたリストを取得する。
			StartNumAndOddsist = goalList.find_all('table',{'class':'ozSanrenUmaINTable sanren_All'})
			
			# ループして1着/2着/3着馬　及び　払い戻しを取得する。
			for outRoopIndex in range(len(StartNumAndOddsist)):
				val = StartNumAndOddsist[outRoopIndex]
				
				# 変数初期化
				bronzeList = []
				oddsList = []
				
				# 変数初期化
				target1StartNum = 0
				target2StartNum = 0
				target3StartNum = 0
				oddsRefund = 0
				
				# DB 格納用辞書　初期化
				dict_Db_RACE_ODDS_3RENPUKU_T = {}
				# DB格納値の固定値
				dict_Db_RACE_ODDS_3RENPUKU_T['LOGIC_DEL_FLG'] = 0
				dict_Db_RACE_ODDS_3RENPUKU_T['INS_PID'] = 'RID11'
				dict_Db_RACE_ODDS_3RENPUKU_T['UPD_PID'] = 'RID11'
				dict_Db_RACE_ODDS_3RENPUKU_T['RACE_ID'] = raceId
				
				# 1着・2着を取得する。
				goldAndSilver = val.find('th',{'class':'title'}).text.split("-")
				target1StartNum = goldAndSilver[0].strip()
				target2StartNum = goldAndSilver[1].strip()
				
				# 3着を取得する。
				bronzePreList = val.find_all('th',{'class':'thubn'})
				for bronze in bronzePreList:
					bronzeList.append(bronze.string.strip())
				
				
				# オッズを取得する。
				oddsPreList = val.find_all('td',{'class': re.compile('^tdoz.*$')})
				for odds in oddsPreList:
					oddsList.append(odds.string.strip())
					
				
				# DB格納値を確定させる。
				for inRoopIndex in range(len(oddsPreList)):
					target3StartNum = bronzeList[inRoopIndex]
					oddsRefund = oddsList[inRoopIndex]
					if (not oddsRefund[0:1].isdigit()):
						oddsRefund = 0
						
					# DBに格納する。
					dict_Db_RACE_ODDS_3RENPUKU_T['TARGET_STARTNUM'] = target1StartNum
					dict_Db_RACE_ODDS_3RENPUKU_T['TARGET2_STARTNUM'] = target2StartNum
					dict_Db_RACE_ODDS_3RENPUKU_T['TARGET3_STARTNUM'] = target3StartNum
					dict_Db_RACE_ODDS_3RENPUKU_T['ODDS_REFUND'] = float(oddsRefund)
					
					# DBに挿入する。
					
					# DB へのInsert
					if updateFlg == 0:
						self.daoClass.insert('POST_RACE_ODDS_3RENPUKU_T',dict_Db_RACE_ODDS_3RENPUKU_T)
					else:
						where = "WHERE RACE_ID ='%s' AND TARGET_STARTNUM ='%s' AND TARGET2_STARTNUM ='%s' AND TARGET3_STARTNUM ='%s'"% (raceId,target1StartNum,target2StartNum,target3StartNum)
						self.daoClass.update('POST_RACE_ODDS_3RENPUKU_T',dict_Db_RACE_ODDS_3RENPUKU_T,where)

		# 終了ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,1)


	##################################################################
	###### 引数1:race_id
	###### 引数2:soup
	###### 戻り値:なし
	###### 概要:引数で取得したrace_idのレース詳細情報を更新する
	###### 
	##################################################################
	def race_3rentan_t(self,soup):
		# メソッドの名
		methodname = sys._getframe().f_code.co_name
		# メソッド開始ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,0)
		self.utilClass.logging('target race is ' + race_id,2)

		# レースIDを取得するための処理を記述する。
		racePlaceDate = soup.find('td',{'class':'cTtl headerOdds'}).text.strip() 
		racePlace = self.racePlaceGet(racePlaceDate)
		raceDate = self.raceDateGet(racePlaceDate)
		if soup.find('td',{'class':'TtlNMnonDK headerOdds4'}) is None:
			raceName = soup.find('td',{'class':'TtlNMWIN5DK headerOdds4'}).text.strip() 
		else:
			raceName = soup.find('td',{'class':'TtlNMnonDK headerOdds4'}).text.strip() 
		raceNo = self.raceNoGet(raceName)
	
		# レースIDを取得する。
		raceId = 'R0100' + raceDate + racePlace + raceNo
	
		# スクレイピングを開始する。
		raceOddsList = soup.find_all('table',{'class':'santanOddsHyo'})
		

	
		for index in range(len(raceOddsList)):

			# 1着リストと2着リストを取得する。########
			goldList = []
			silverList = []
			goalList = raceOddsList[index].find_all('tr')
			for goal in goalList:
				if goal.find('th',{'class':'rank'}) is not None:
					if '1着' in goal.find('th',{'class':'rank'}).string:
						valList = goal.find_all('th',{'class':'ubn2'})
						for goal in valList:
							goldList.append(goal.string.strip())
							
					elif '2着' in goal.find('th',{'class':'rank'}):
						valList = goal.find_all('th',{'class':'ubn2'})
						for goal in valList:
							silverList.append(goal.string.strip())
					else:
						continue
				else:
					continue
			
			
			# 1着リストと2着リストをループして3着とオッズの組み合わせを取得する。#########
			# 変数初期化
			goldStartNum = 0
			silverStartNum = 0
			bronzeStartNum = 0
			refundOdds = 0
			
			# DB格納用の辞書を作成する。
			dict_Db_POST_RACE_ODDS_3RENTAN_T = {}
			
			# DB格納値の固定値
			dict_Db_POST_RACE_ODDS_3RENTAN_T['LOGIC_DEL_FLG'] = 0
			dict_Db_POST_RACE_ODDS_3RENTAN_T['INS_PID'] = 'RID10'
			dict_Db_POST_RACE_ODDS_3RENTAN_T['UPD_PID'] = 'RID10'
			dict_Db_POST_RACE_ODDS_3RENTAN_T['RACE_ID'] = raceId
			
			# 3着とオッズリストが入った情報リストを取得する。
			bronzeAndOddsList = raceOddsList[index].find_all('table',{'class':'oddsTbl'})
			
			# 
			for outRoopIndex in range(len(bronzeAndOddsList)):
				# 3着とオッズのリストを取得する。
				bronzeList = bronzeAndOddsList[outRoopIndex].find_all('th')
				oddsList = bronzeAndOddsList[outRoopIndex].find_all('td')
				
				for inRoopIndex in range(len(oddsList)):
					# DB格納値を確定させる。
					goldStartNum = goldList[outRoopIndex]
					silverStartNum = silverList[outRoopIndex]
					bronzeStartNum = bronzeList[inRoopIndex].string.strip()
					refundOdds = oddsList[inRoopIndex].string.strip()
					if (not refundOdds[0:1].isdigit()):
						refundOdds = 0
					refundOdds = float(refundOdds)
					
					# DEにすでに情報がある場合は更新する。
					selectPostRaceOdds3rentanT = ["WHERE RACE_ID = '%s' AND GOLD_OF_STARTNUM = '%s' AND SILVER_OF_STARTNUM = '%s' AND BRONZE_OF_STARTNUM = '%s'"% (raceId,goldStartNum,silverStartNum,bronzeStartNum)]
					result = self.daoClass.selectQuery(selectPostRaceOdds3rentanT,'selectPostRaceOdds3rentanT')
					
					# 所得結果がある場合は更新
					if result[0][0] == 1:
						where = "WHERE RACE_ID = '%s' AND GOLD_OF_STARTNUM = '%s' AND SILVER_OF_STARTNUM = '%s' AND BRONZE_OF_STARTNUM = '%s'"% (raceId,goldStartNum,silverStartNum,bronzeStartNum)
						dict_Db_POST_RACE_ODDS_3RENTAN_T['REFUND_ODDS'] = refundOdds
						# DB更新処理
						self.daoClass.update('POST_RACE_ODDS_3RENTAN_T',dict_Db_POST_RACE_ODDS_3RENTAN_T,where)
					else:
						# DBに格納する。
						dict_Db_POST_RACE_ODDS_3RENTAN_T['GOLD_OF_STARTNUM'] = goldStartNum
						dict_Db_POST_RACE_ODDS_3RENTAN_T['SILVER_OF_STARTNUM'] = silverStartNum
						dict_Db_POST_RACE_ODDS_3RENTAN_T['BRONZE_OF_STARTNUM'] = bronzeStartNum
						dict_Db_POST_RACE_ODDS_3RENTAN_T['REFUND_ODDS'] = refundOdds
					
						# DBに挿入する。
						self.daoClass.insert('POST_RACE_ODDS_3RENTAN_T',dict_Db_POST_RACE_ODDS_3RENTAN_T)
		# 終了ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,1)




	##################################################################
	###### 引数1:race_id
	###### 引数2:起動種別
	###### 戻り値:soup
	###### 概要:引数で取得したrace_idと起動種別を元にリクエストを実施しhtml情報を取得する
	###### 
	##################################################################
	def getHtml(self,race_id,type):
		# メソッドの名
		methodname = sys._getframe().f_code.co_name
		# メソッド開始ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,0)
		self.utilClass.logging('target race is ' + race_id + 'and type is ' + str(type),2)

		# 返却IF
		retunrDict = {}
		retunrDict['resultCode'] = 0


		# DBよりパラむ情報を取得する
		where = ["WHERE RACE_ID = '%s'"% race_id]
		result = self.daoClass.selectQuery(where,'getparam')

		# まだparamを取得していない場合はreturnする
		if len(result) == 0:
			retunrDict['resultCode'] = 1
			msg = race_id + ' have not got param yet so return'
			retunrDict['msg'] = msg
			self.utilClass.loggingWarn(race_id + ' have not got param yet so return')
			return retunrDict

		# 起動種別により取得するパラムを選定する
		param = ''
		if type == 1: # detail
			param = result[0][0]
		elif type == 2: # 単勝・複勝
			param = result[0][0]
		elif type == 3: # 馬連
			param = result[0][1]
		elif type == 4: # 馬単
			param = result[0][2]
		elif type == 5: # ワイド
			param = result[0][3]
		elif type == 6: # 3連複
			param = result[0][4]
		elif type == 7: # 3連単
			param = result[0][5]


		# リクエストして情報を抜き取る
		params = {}
		params['cname'] = param
		response = requests.post('http://www.jra.go.jp/JRADB/accessO.html',data = params)
		response.encoding = response.apparent_encoding
		htmlsource = response.text

		soup = BeautifulSoup(htmlsource,'html.parser')

		# 終了ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,1)
		retunrDict['soup'] = soup
		return retunrDict



	# レースの開催日付を取得する。
	def raceDateGet(self,raceDate):
		# 月が10以上フラグ
		month10Flg = 1
		
		# 西暦を取得する。
		yesrStr = raceDate[0:4]
		
		# 月を取得する。
		monthStr = raceDate[5:7]
		if '月' in monthStr:
			month10Flg = 0
			monthStr = '0' + monthStr[0:1]
		
		# 日を取得する
		if month10Flg == 0:
			dayStr = raceDate[7:9]
			if '日' in dayStr:
				dayStr = '0' + dayStr[0:1]
		else:
			dayStr = raceDate[8:10]
			if '日' in dayStr:
				dayStr = '0' + dayStr[0:1]
		
		return yesrStr + monthStr + dayStr
	
	# 競馬場を取得する。
	def racePlaceGet(self,racePlaceDate):
		if '札幌' in racePlaceDate:
			return '01'
		elif '函館' in racePlaceDate:
			return '02'
		elif '福島' in racePlaceDate:
			return '03'
		elif '新潟' in racePlaceDate:
			return '04'
		elif '東京' in racePlaceDate:
			return '05'
		elif '中山' in racePlaceDate:
			return '06'
		elif '中京' in racePlaceDate:
			return '07'
		elif '京都' in racePlaceDate:
			return '08'
		elif '阪神' in racePlaceDate:
			return '09'
		elif '小倉' in racePlaceDate:
			return '10'
		else:
			return '00'

	# 何レースか取得する。
	def raceNoGet(self,raceNeme):
		raceNeme = raceNeme[0:2]
		if 'R' in raceNeme:
			return '0' + raceNeme[0:1]
		else:
			return raceNeme
