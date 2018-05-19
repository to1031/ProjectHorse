#coding: utf-8
# 概要
# オッズ情報のスクレイピング
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

class RaceResultOdds(object):
	# 初期化処理
	def __init__(self,dict):
		# 環境変数を取得する。
		self.homeDir = os.environ["APPHORSE"]

		# iniconfigファイルを読み出す。
		self.inifile = dict['util'].inifile

		# 当サービスの機能IDを取得する。
		self.pid = 'JraResult'

		# 呼び出し元も機能ID
		self.call_pid = dict['pid']

		# util
		self.utilClass = dict['util']

		# dao
		self.daoClass = dict['dao']


	##################################################################
	###### 引数1:html情報
	###### 概要:引数で取得したhtml情報をもとにスクレイピングする
	###### 
	##################################################################
	def jraResultOdds_main(self,htmlinfo,type):
		# 当メソッドの名前を取得する。
		methodname = sys._getframe().f_code.co_name

		# 処理開始ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,0)

		# BeautifulSoupオブジェクトに変換
		soup = BeautifulSoup(htmlinfo,'html.parser')

		# 終了コード
		returnCode = 0

		try:
			if type == 1: # 単勝・複勝
				self.odds(soup)
			elif type == 2: # 馬連
				self.odds_umaren(soup)
			elif type == 3: # 馬単
				self.odds_umatan(soup)
			elif type == 4: # ワイド
				self.odds_wide(soup)
			elif type == 5: # 3連服
				self.odds_3renpuku(soup)
			elif type == 6: # 3連単
				self.odds_3rentan(soup)

		except:
			# リターンコードを設定する。
			import traceback
			returnCode = 9
			error_text = traceback.format_exc()
			self.utilClass.loggingError(error_text)

		finally:
			self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,1)
			# 処理を返す。
			return returnCode



	##################################################################
	###### 引数1:html情報
	###### 概要:引数で取得したhtml情報をもとにスクレイピングする
	###### 
	##################################################################
	def odds(self,soup):

		#########################前処理
		#########################
		# メソッド名取得
		methodname = sys._getframe().f_code.co_name
		# メソッド開始ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,0)

		# 内部関数定義
		# レースの開催日付を取得する。
		def raceDateGet(raceDate):
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
		def racePlaceGet(racePlaceDate):
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
		def raceNoGet(raceNeme):
			raceNeme = raceNeme[0:2]
			if 'R' in raceNeme:
				return '0' + raceNeme[0:1]
			else:
				return raceNeme


		#########################主処理
		#########################
		# レースIDを取得するための処理を記述する。
		racePlaceDate = soup.find('td',{'class':'cTtl headerOdds'}).text.strip() 
		racePlace = racePlaceGet(racePlaceDate)
		raceDate = raceDateGet(racePlaceDate)
		if soup.find('td',{'class':'TtlNMnonDK headerOdds4'}) is None:
			raceName = soup.find('td',{'class':'TtlNMWIN5DK headerOdds4'}).text.strip() 
		else:
			raceName = soup.find('td',{'class':'TtlNMnonDK headerOdds4'}).text.strip() 
		raceNo = raceNoGet(raceName)
		
		
		
		raceOdds = soup.find('div',{'class':'ozTanfukuTableUma'})
		raceOdds = raceOdds.find_all('tr')
		wkcount = 1
		

		for i in range(len(raceOdds)):
			if raceOdds[i].td is None:
				continue
			
			# 枠を取得する。
			waku = 'waku waku' + str(wkcount)
			if raceOdds[i].find('th',{'class':waku}) is None:
				wkcount = wkcount - 1
				waku = 'waku waku' + str(wkcount)
				if raceOdds[i-1].find('th',{'class':waku}) is None:
					startFrame = raceOdds[i-2].find('th',{'class':waku}).string.strip()
					wkcount = wkcount + 1
				else:
					startFrame = raceOdds[i-1].find('th',{'class':waku}).string.strip()
					wkcount = wkcount + 1
			else:
				wkcount = wkcount + 1
				startFrame = raceOdds[i].find('th',{'class': waku }).string.strip()
			
			# 馬番を取得する。
			startNum = raceOdds[i].find('th',{'class': 'umaban' }).string.strip()
			
			# 馬名を取得する。
			condHorseName = raceOdds[i].find('td',{'class':'bamei'})
			condHorseNameIf = condHorseName.find('a')
			if condHorseName is None:
				horceName = condHorseName.find('td').string.strip()
			else:
				horceName = condHorseName.find('a').string.strip()
			
			# 単勝オッズを取得する。
			condwinName = raceOdds[i].find('td',{'class':'oztan oddsJyuBaiMiman'})
			if condwinName is None:
				# 取り消しの場合スキップ
				if '取' in raceOdds[i].find('td',{'class':'oztan'}).string.strip():
					continue
				winOdds = float(raceOdds[i].find('td',{'class':'oztan'}).string.strip())
			else:
				winOdds = float(condwinName.string.strip())
				
			# 複勝オッズを取得する。
			if raceOdds[i].find('td',{'class':'fukuMin'}) is None:
				multWinOddsFrom = 0
				multWinOddsTo = 0
			else:
				multWinOddsFrom = float(raceOdds[i].find('td',{'class':'fukuMin'}).string.strip())
				multWinOddsTo =  float(raceOdds[i].find('td',{'class':'fukuMax'}).string.strip())
			
			# レースIDを取得する。
			raceId = 'R0100' + raceDate + racePlace + raceNo
			
			# レースID がすでにある場合はスキップする。
			getRaceId = ["WHERE RACE_ID = '%s'" % raceId,"AND START_NUM ='%s'"% startNum]
			confirmRaceId = self.daoClass.selectQuery(getRaceId,'raceOddsTExistConfirm')
			
			if confirmRaceId[0][0] > 0:
				#処理を返す。
				return
			
			if raceId == 'R0100200402150803':
				return
			
			# DB格納用の辞書を作成する。
			dict_Db_RACE_ODDS_T = {}
			dict_Db_RACE_ODDS_T['LOGIC_DEL_FLG'] = '0'
			dict_Db_RACE_ODDS_T['INS_PID'] = 'RID04'
			dict_Db_RACE_ODDS_T['UPD_PID'] = 'RID04'
			dict_Db_RACE_ODDS_T['RACE_ID'] = raceId
			dict_Db_RACE_ODDS_T['START_FRAME'] = startFrame
			dict_Db_RACE_ODDS_T['START_NUM'] = startNum
			dict_Db_RACE_ODDS_T['HORCE_NAME'] = horceName
			dict_Db_RACE_ODDS_T['WIN_ODDS'] = winOdds
			dict_Db_RACE_ODDS_T['MULT_WIN_ODDS_FROM'] = multWinOddsFrom
			dict_Db_RACE_ODDS_T['MULT_WIN_ODDS_TO'] = multWinOddsTo
			
			# DBにアクセスする処理
			self.daoClass.insert('RACE_ODDS_T',dict_Db_RACE_ODDS_T)


		#########################後処理
		#########################
		self.utilClass.logging('############# ' + raceId + ' #############',2)
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,1)

	##################################################################
	###### 引数1:html情報
	###### 戻り値:RACE_ID
	###### 概要:引数で取得したhtml情報をもとに馬連のオッズ情報を取得する
	###### 
	##################################################################
	def odds_umaren(self,soup):

		#########################前処理
		#########################
		# メソッド名取得
		methodname = sys._getframe().f_code.co_name
		# メソッド開始ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,0)

		# 内部関数定義
		# レースの開催日付を取得する。
		def raceDateGet(raceDate):
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
		def racePlaceGet(racePlaceDate):
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
		def raceNoGet(raceNeme):
			raceNeme = raceNeme[0:2]
			if 'R' in raceNeme:
				return '0' + raceNeme[0:1]
			else:
				return raceNeme


		#########################主処理
		#########################

		# レースIDを取得するための処理を記述する。
		racePlaceDate = soup.find('td',{'class':'cTtl headerOdds'}).text.strip() 
		racePlace = racePlaceGet(racePlaceDate)
		raceDate = raceDateGet(racePlaceDate)
		if soup.find('td',{'class':'TtlNMnonDK headerOdds4'}) is None:
			raceName = soup.find('td',{'class':'TtlNMWIN5DK headerOdds4'}).text.strip() 
		else:
			raceName = soup.find('td',{'class':'TtlNMnonDK headerOdds4'}).text.strip() 
		raceNo = raceNoGet(raceName)
	
		# レースIDを取得する。
		raceId = 'R0100' + raceDate + racePlace + raceNo
	
		# スクレイピングを開始する。
		raceOddsList = soup.find_all('table',{'class':'ozUmarenUmaINTable'})
		
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
				self.daoClass.insert('RACE_ODDS_UMAREN_T',dict_Db_RACE_ODDS_UMAREN_T)
			

		#########################後処理
		#########################
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,1)
		


	##################################################################
	###### 引数1:html情報
	###### 概要:引数で取得したhtml情報をもとに馬単の情報を取得する。
	###### 
	##################################################################
	def odds_umatan(self,soup):

		#########################前処理
		#########################
		# メソッド名取得
		methodname = sys._getframe().f_code.co_name

		# メソッド開始ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,0)

		# 内部関数定義
		# レースの開催日付を取得する。
		def raceDateGet(raceDate):
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
		def racePlaceGet(racePlaceDate):
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
		def raceNoGet(raceNeme):
			raceNeme = raceNeme[0:2]
			if 'R' in raceNeme:
				return '0' + raceNeme[0:1]
			else:
				return raceNeme


		#########################前処理
		#########################
		
		# レースIDを取得するための処理を記述する。
		racePlaceDate = soup.find('td',{'class':'cTtl headerOdds'}).text.strip() 
		racePlace = racePlaceGet(racePlaceDate)
		raceDate = raceDateGet(racePlaceDate)
		if soup.find('td',{'class':'TtlNMnonDK headerOdds4'}) is None:
			raceName = soup.find('td',{'class':'TtlNMWIN5DK headerOdds4'}).text.strip() 
		else:
			raceName = soup.find('td',{'class':'TtlNMnonDK headerOdds4'}).text.strip() 
		raceNo = raceNoGet(raceName)
	
		# レースIDを取得する。
		raceId = 'R0100' + raceDate + racePlace + raceNo
	
		# スクレイピングを開始する。
		raceOddsList = soup.find_all('table',{'class':'ozUmatanUmaINTable'})
		
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
				# 数字出ない場合は、０を格納
				if (not oddsVal[0:1].isdigit()):
					oddsVal = 0
				
				dict_Db_RACE_ODDS_UMATAN_T['ODDS_REFUND'] = float(oddsVal)
				
				# DB へのInsert
				self.daoClass.insert('RACE_ODDS_UMATAN_T',dict_Db_RACE_ODDS_UMATAN_T)			


		#########################後処理
		#########################
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,1)

	##################################################################
	###### 引数1:html情報
	###### 概要:引数で取得したhtml情報をもとにワイドの情報を取得する・
	###### 
	##################################################################
	def odds_wide(self,soup):

		#########################前処理
		#########################
		# メソッド名取得
		methodname = sys._getframe().f_code.co_name
		# メソッド開始ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,0)

		# 内部関数定義
		# レースの開催日付を取得する。
		def raceDateGet(raceDate):
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
		def racePlaceGet(racePlaceDate):
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
		def raceNoGet(raceNeme):
			raceNeme = raceNeme[0:2]
			if 'R' in raceNeme:
				return '0' + raceNeme[0:1]
			else:
				return raceNeme

		#########################主処理
		#########################
		
		# レースIDを取得するための処理を記述する。
		racePlaceDate = soup.find('td',{'class':'cTtl headerOdds'}).text.strip() 
		racePlace = racePlaceGet(racePlaceDate)
		raceDate = raceDateGet(racePlaceDate)
		if soup.find('td',{'class':'TtlNMnonDK headerOdds4'}) is None:
			raceName = soup.find('td',{'class':'TtlNMWIN5DK headerOdds4'}).text.strip() 
		else:
			raceName = soup.find('td',{'class':'TtlNMnonDK headerOdds4'}).text.strip() 
		raceNo = raceNoGet(raceName)
	
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
			dict_Db_RACE_ODDS_WIDE_T = {}
			
			# DB格納値の固定値
			dict_Db_RACE_ODDS_WIDE_T['LOGIC_DEL_FLG'] = 0
			dict_Db_RACE_ODDS_WIDE_T['INS_PID'] = 'RID12'
			dict_Db_RACE_ODDS_WIDE_T['UPD_PID'] = 'RID12'
			dict_Db_RACE_ODDS_WIDE_T['RACE_ID'] = raceId
			
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
				
				# DBに格納する。
				dict_Db_RACE_ODDS_WIDE_T['TARGET_STARTNUM'] = targetStartNum
				dict_Db_RACE_ODDS_WIDE_T['TARGET2_STARTNUM'] = target2StartNum
				dict_Db_RACE_ODDS_WIDE_T['ODDS_FROM'] = float(wideMinVal)
				dict_Db_RACE_ODDS_WIDE_T['ODDS_TO'] = float(wideMaxVal)
				
				# DB へのInsert
				self.daoClass.insert('RACE_ODDS_WIDE_T',dict_Db_RACE_ODDS_WIDE_T)


		#########################後処理
		#########################
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,1)




	##################################################################
	###### 引数1:html情報
	###### 戻り値:RACE_ID
	###### 概要:引数で取得したhtml情報をもとにスクレイピングする
	###### 
	##################################################################
	def odds_3renpuku(self,soup):

		#########################前処理
		#########################
		# メソッド名取得
		methodname = sys._getframe().f_code.co_name
		# メソッド開始ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,0)

		# 内部関数定義
		# レースの開催日付を取得する。
		def raceDateGet(raceDate):
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
		def racePlaceGet(racePlaceDate):
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
		def raceNoGet(raceNeme):
			raceNeme = raceNeme[0:2]
			if 'R' in raceNeme:
				return '0' + raceNeme[0:1]
			else:
				return raceNeme

		#########################主処理
		#########################
		
		# レースIDを取得するための処理を記述する。
		racePlaceDate = soup.find('td',{'class':'cTtl headerOdds'}).text.strip() 
		racePlace = racePlaceGet(racePlaceDate)
		raceDate = raceDateGet(racePlaceDate)
		if soup.find('td',{'class':'TtlNMnonDK headerOdds4'}) is None:
			raceName = soup.find('td',{'class':'TtlNMWIN5DK headerOdds4'}).text.strip() 
		else:
			raceName = soup.find('td',{'class':'TtlNMnonDK headerOdds4'}).text.strip() 
		raceNo = raceNoGet(raceName)
	
		# レースIDを取得する。
		raceId = 'R0100' + raceDate + racePlace + raceNo
	
		# スクレイピングを開始する。
		raceOddsList = soup.find_all('div',{'class':'ozSanrenUmaOutTableArea'})
		
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
					self.daoClass.insert('RACE_ODDS_3RENPUKU_T',dict_Db_RACE_ODDS_3RENPUKU_T)


		#########################後処理
		#########################
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,0)


	##################################################################
	###### 引数1:html情報
	###### 概要:引数で取得したhtml情報をもとに3連単の情報を取得する。
	###### 
	##################################################################
	def odds_3rentan(self,soup):

		#########################前処理
		#########################
		# メソッド名取得
		methodname = sys._getframe().f_code.co_name
		# メソッド開始ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,0)

		# 内部関数定義
		# レースの開催日付を取得する。
		def raceDateGet(raceDate):
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
		def racePlaceGet(racePlaceDate):
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
		def raceNoGet(raceNeme):
			raceNeme = raceNeme[0:2]
			if 'R' in raceNeme:
				return '0' + raceNeme[0:1]
			else:
				return raceNeme

		#########################主処理
		#########################
		
		# レースIDを取得するための処理を記述する。
		racePlaceDate = soup.find('td',{'class':'cTtl headerOdds'}).text.strip() 
		racePlace = racePlaceGet(racePlaceDate)
		raceDate = raceDateGet(racePlaceDate)
		if soup.find('td',{'class':'TtlNMnonDK headerOdds4'}) is None:
			raceName = soup.find('td',{'class':'TtlNMWIN5DK headerOdds4'}).text.strip() 
		else:
			raceName = soup.find('td',{'class':'TtlNMnonDK headerOdds4'}).text.strip() 
		raceNo = raceNoGet(raceName)
	
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
			dict_Db_RACE_ODDS_3RENTAN_T = {}
			
			# DB格納値の固定値
			dict_Db_RACE_ODDS_3RENTAN_T['LOGIC_DEL_FLG'] = 0
			dict_Db_RACE_ODDS_3RENTAN_T['INS_PID'] = 'RID10'
			dict_Db_RACE_ODDS_3RENTAN_T['UPD_PID'] = 'RID10'
			dict_Db_RACE_ODDS_3RENTAN_T['RACE_ID'] = raceId
			
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
					
					# DBに格納する。
					dict_Db_RACE_ODDS_3RENTAN_T['GOLD_OF_STARTNUM'] = goldStartNum
					dict_Db_RACE_ODDS_3RENTAN_T['SILVER_OF_STARTNUM'] = silverStartNum
					dict_Db_RACE_ODDS_3RENTAN_T['BRONZE_OF_STARTNUM'] = bronzeStartNum
					dict_Db_RACE_ODDS_3RENTAN_T['REFUND_ODDS'] = refundOdds
					
					# DBに挿入する。
					self.daoClass.insert('RACE_ODDS_3RENTAN_T',dict_Db_RACE_ODDS_3RENTAN_T)


		#########################後処理
		#########################
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,0)



