#coding: utf-8
# 概要
# accessO.htmlからRace情報を取得する。
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

class PostRaceInfo(object):
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
	def jraInfo_main(self,htmlinfo,type):
		# 当メソッドの名前を取得する。
		methodname = sys._getframe().f_code.co_name

		# 処理開始ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,0)

		# BeautifulSoupオブジェクトに変換
		soup = BeautifulSoup(htmlinfo,'html.parser')

		# 終了コード
		returnCode = 0

		try:

			if type == 0: # post_race
				self.post_race_t(soup)
			elif type == 1: # 単勝・複勝
				self.post_race_detail_t(soup)
				self.odds_and_param(soup)

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
	###### 戻り値:RACE_ID
	###### 概要:引数で取得したhtml情報をもとにスクレイピングする
	###### 
	##################################################################
	def post_race_t(self,soup):

		#########################前処理
		#########################
		# メソッド名取得
		methodname = sys._getframe().f_code.co_name
		# メソッド開始ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,0)

		# 内部関数定義
		# レース条件を取得する。(負荷重量・年齢・混合条件・参加条件)
		def raceCond3Get(raceCond3):
			if '新馬' in raceCond3:
				raceCondMoney = '01'
			elif '未勝利' in raceCond3:
				raceCondMoney = '02'
			elif 'オープン' in raceCond3:
				raceCondMoney = '03'
			elif '500万' in raceCond3:
				raceCondMoney = '04'
			elif '1000万' in raceCond3:
				raceCondMoney = '05'
			elif '600万' in raceCond3:
				raceCondMoney = '06'
			else:
				raceCondMoney = '00'
			
			if '混合' in raceCond3:
				raceCondSex = '01'
			elif '牡' in raceCond3:
				raceCondSex = '02'
			elif '牝' in raceCond3:
				raceCondSex = '03'
			else:
				raceCondSex = '04'
			
			# 年齢の取得
			if '4歳以上' in raceCond3:
				raceCondOld = '04'
			elif '3歳以上' in raceCond3:
				raceCondOld = '03'
			elif '3歳' in raceCond3:
					raceCondOld = '02'
			elif'2歳' in raceCond3:
				raceCondOld = '01'
			else:
				raceCondOld = '00'
			
			if '定量' in raceCond3:
				raceWeight = '01'
			elif '別定' in raceCond3:
				raceWeight = '02'
			elif 'ハンデ' in raceCond3:
				raceWeight = '03'
			elif '馬齢' in raceCond3:
				raceWeight = '04'
			else:
				raceWeight = '00'
			
			# 障害区分を取得する
			if '障害' in raceCond3:
				raceShogaiFlg = '1'
			else:
				raceShogaiFlg = '0'
			
			dict_cond3 = {}
			dict_cond3['raceCondMoney'] = raceCondMoney
			dict_cond3['raceCondSex'] = raceCondSex
			dict_cond3['raceCondOld'] = raceCondOld
			dict_cond3['raceWeight'] = raceWeight
			dict_cond3['raceShogaiFlg'] = raceShogaiFlg
			return dict_cond3
		
		# レース条件を取得する。(障害・年齢・芝orダート)
		def raceCond1Get(raceCond1):	
			# 距離を取得する
			raceRange = raceCond1[0:4]
			
			# 芝かダートか取得する
			if '芝' in raceCond1:
				raceGroundFlg = '0'
			else:
				raceGroundFlg = '1'
			
			# 右 or 左　周りかどうか取得する
			if '外' in raceCond1:
				raceTurnFlg = '1'
			else:
				raceTurnFlg = '0'
			
			dict_cond1 ={}
			dict_cond1['raceRange'] = raceRange
			dict_cond1['raceGroundFlg'] = raceGroundFlg
			dict_cond1['raceTurnFlg'] = raceTurnFlg
			return dict_cond1
			
		
		# レース出走時間を取得する。
		def raceTimeGet(raceTime):
			if ' ' in raceTime:
				hourStr = raceTime[1:2]
			else:
				hourStr = raceTime[0:2]
			
			minuteStr = raceTime[3:5]
			hourInt = int(hourStr)
			minuteInt = int(minuteStr)
			
			# datetime型に変換して返す
			raceTime = datetime.time(hourInt,minuteInt,0,0)
			return raceTime
		
		
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
		
		# レースグレードを取得する。
		def receGradeCond(raceNeme):
			if 'GⅠ' in raceNeme:
				return '1'
			elif 'GⅡ' in raceNeme:
				return '2'
			elif 'GⅢ' in raceNeme:
				return '3'
			else:
				return '4'

		#########################主処理
		#########################
		
		# レース名を取得する。
		raceNeme = soup.find( class_ = 'heading2Font')
		glade = raceNeme.find('img')
		gladeStr = ''
		if glade is not None:
			gladeStr = glade.attrs['src']
			if 'g1' in gladeStr:
				gladeStr = 'GⅠ'
			elif 'g2' in gladeStr:
				gladeStr = 'GⅡ'
			elif 'g3' in gladeStr:
				gladeStr = 'GⅢ'
		
		raceNeme = soup.find( class_ = 'heading2Font').text.strip()
		raceNeme = raceNeme + gladeStr
		
		# raceNemeからG1,G2,G3,その他区分を選択する。
		raceGlade = receGradeCond(raceNeme)
		
		# raceNoを取得する。
		raceNo = raceNoGet(raceNeme)
		
		# rece開催場所を取得する。
		racePlaceDate = soup.find( class_ = 'heading1Font').string.strip()
		racePlace = racePlaceGet(racePlaceDate)
		
		# rece開催日付を取得する。
		raceDate = raceDateGet(racePlaceDate)
		
		# RACEの賞金を取得する。
		raceTimeMoney = soup.find_all('td',{'class':'amt'})
		racePrize1 = 0
		racePrize2 = 0
		racePrize3 = 0
		racePrize4 = 0
		racePrize5 = 0
		if len(raceTimeMoney) > 0:
			racePrize1 = raceTimeMoney[0].string.strip()
		if len(raceTimeMoney) > 1:
			racePrize2 = raceTimeMoney[1].string.strip()
		if len(raceTimeMoney) > 2:
			racePrize3 = raceTimeMoney[2].string.strip()
		if len(raceTimeMoney) > 3:
			racePrize4 = raceTimeMoney[3].string.strip()
		if len(raceTimeMoney) > 4:
			racePrize5 = raceTimeMoney[4].string.strip()

		
		# レースの情報を取得する。(障害区分、年齢、レース条件区分（年齢条件）、レース条件区分（獲得賞金区分）、混合区分（レース条件）、負担重量区分)
		raceCondInfoList = soup.find('div',{'class' : 'raceInfoAreaCellLeftDiv'})
		raceCondInfoStr1 = raceCondInfoList.string.strip()
		race_cond_text = raceCondInfoStr1
		raceCondInfoStr1 = raceCond3Get(raceCondInfoStr1)
		raceWeight = raceCondInfoStr1['raceWeight']
		raceCondSex = raceCondInfoStr1['raceCondSex']
		raceCondOld = raceCondInfoStr1['raceCondOld']
		raceCondMoney = raceCondInfoStr1['raceCondMoney']
		raceShogaiFlg = raceCondInfoStr1['raceShogaiFlg']
		
		# 発送時刻を取得する。
		raceTimeInfoStr = soup.findAll('div',{'class' : 'raceInfoAreaCellRightDiv'})
		for info in raceTimeInfoStr:
			if info.string is None or info.string == '':
				continue
			if '発走' in info.string.strip():
				raceTimeText = info.string.strip()
				raceTime = raceTimeText[-5:].strip()
		
		# レースの情報を取得する。(距離、芝・ダート区分、回り区分)
		raceCondInfoStr2 = soup.find('div',{'class' : 'raceInfoAreaCellRightDiv'}).text.replace('コース','').strip()
		raceCondInfoStr2 = raceCond1Get(raceCondInfoStr2)
		raceGroundFlg = raceCondInfoStr2['raceGroundFlg']
		raceRange = raceCondInfoStr2['raceRange']
		raceTurnFlg = raceCondInfoStr2['raceTurnFlg']
	
		# レースIDを取得する.
		raceId = 'R0100' + raceDate + racePlace + raceNo
		
		# すでにPOST_RACE_Tに情報がある場合は、UPDATE,ない場合はINSERTを実施する。
		existPosetRaceT = ["WHERE RACE_ID IN ('%s')"% raceId]
		result = self.daoClass.selectQuery(existPosetRaceT,'existPosetRaceT')

		if result[0][0] == 1:
			# POST_RACE_Tに更新
			where = "WHERE RACE_ID = '%s'"% raceId
			dict_Db_POST_RACE_T = {}
			dict_Db_POST_RACE_T['UPD_PID'] = 'RID03'
			dict_Db_POST_RACE_T['RACE_DATE']=raceDate
			dict_Db_POST_RACE_T['RACE_PLACE']=racePlace
			dict_Db_POST_RACE_T['RACE_NO']=raceNo
			dict_Db_POST_RACE_T['RACE_GROUND_FLG']=raceGroundFlg
			dict_Db_POST_RACE_T['RACE_RANGE']=raceRange
			dict_Db_POST_RACE_T['RACE_TURN_FLG']=raceTurnFlg
			dict_Db_POST_RACE_T['RACE_GLADE']=raceGlade
			dict_Db_POST_RACE_T['RACE_WEIGHT']=raceWeight
			dict_Db_POST_RACE_T['RACE_COND_SEX']=raceCondSex
			dict_Db_POST_RACE_T['RACE_SHOGAI_FLG']=raceShogaiFlg
			dict_Db_POST_RACE_T['RACE_COND_OLD']=raceCondOld
			dict_Db_POST_RACE_T['RACE_COND_MONEY']=raceCondMoney
			dict_Db_POST_RACE_T['RACE_NAME']=raceNeme
			dict_Db_POST_RACE_T['RACE_TIME']=raceTime
			dict_Db_POST_RACE_T['RACE_COND_TEXT']=race_cond_text
			dict_Db_POST_RACE_T['RACE_PRIZE_1']=racePrize1
			dict_Db_POST_RACE_T['RACE_PRIZE_2']=racePrize2
			dict_Db_POST_RACE_T['RACE_PRIZE_3']=racePrize3
			dict_Db_POST_RACE_T['RACE_PRIZE_4']=racePrize4
			dict_Db_POST_RACE_T['RACE_PRIZE_5']=racePrize5
			dict_Db_POST_RACE_T['RACE_WEATHER']=''
			dict_Db_POST_RACE_T['RACE_CONDITION']=''
			self.daoClass.update('POST_RACE_T',dict_Db_POST_RACE_T,where)
		else:
			# POST_RACE_Tにインサートする。
			# DBに格納する辞書を作成する。
			dict_Db_POST_RACE_T = {}
			dict_Db_POST_RACE_T['LOGIC_DEL_FLG']='0'
			dict_Db_POST_RACE_T['INS_PID']='RID01'
			dict_Db_POST_RACE_T['UPD_PID']='RID01'
			dict_Db_POST_RACE_T['RACE_ID']=raceId
			dict_Db_POST_RACE_T['RACE_DATE']=raceDate
			dict_Db_POST_RACE_T['RACE_PLACE']=racePlace
			dict_Db_POST_RACE_T['RACE_NO']=raceNo
			dict_Db_POST_RACE_T['RACE_GROUND_FLG']=raceGroundFlg
			dict_Db_POST_RACE_T['RACE_RANGE']=raceRange
			dict_Db_POST_RACE_T['RACE_TURN_FLG']=raceTurnFlg
			dict_Db_POST_RACE_T['RACE_GLADE']=raceGlade
			dict_Db_POST_RACE_T['RACE_WEIGHT']=raceWeight
			dict_Db_POST_RACE_T['RACE_COND_SEX']=raceCondSex
			dict_Db_POST_RACE_T['RACE_SHOGAI_FLG']=raceShogaiFlg
			dict_Db_POST_RACE_T['RACE_COND_OLD']=raceCondOld
			dict_Db_POST_RACE_T['RACE_COND_MONEY']=raceCondMoney
			dict_Db_POST_RACE_T['RACE_NAME']=raceNeme
			dict_Db_POST_RACE_T['RACE_TIME']=raceTime
			dict_Db_POST_RACE_T['RACE_COND_TEXT']=race_cond_text
			dict_Db_POST_RACE_T['RACE_PRIZE_1']=racePrize1
			dict_Db_POST_RACE_T['RACE_PRIZE_2']=racePrize2
			dict_Db_POST_RACE_T['RACE_PRIZE_3']=racePrize3
			dict_Db_POST_RACE_T['RACE_PRIZE_4']=racePrize4
			dict_Db_POST_RACE_T['RACE_PRIZE_5']=racePrize5
			dict_Db_POST_RACE_T['RACE_WEATHER']=''
			dict_Db_POST_RACE_T['RACE_CONDITION']=''
			self.daoClass.insert('POST_RACE_T',dict_Db_POST_RACE_T)

		#########################後処理
		self.utilClass.logging('############ ' + raceId + ' ############' ,2)
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,1)

        ##################################################################
        ###### 引数1:html情報
        ###### 戻り値:RACE_ID
        ###### 概要:引数で取得したhtml情報をもとにスクレイピングする
        ###### 
        ##################################################################
	def post_race_detail_t(self,soup):

		#########################前処理	
		#########################
		# メソッド名取得
		methodname = sys._getframe().f_code.co_name
		# メソッド開始ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,0)

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
	
		
		
		# レースのオッズとレース詳細を情報を取得する。
		raceOdds = soup.find('div',{'class':'ozTanfukuTableUma'})
		raceOdds = raceOdds.find_all('tr')
		wkcount = 1
		
		# レースの単勝オッズと人気順を取得するために一時的に単勝オッズと順番の組み合わせを種臆する。
		popWinOddsList = soup.find_all('td',{'class':'oztan'})
		popList = []
		for info in popWinOddsList:
			if info.string.strip().encode('utf-8').isalnum():
				popList.append(float(info.string.strip()))
			else:
				try:
					popList.append(float(info.string.strip()))
				except ValueError:
					popList.append(10000.0)
					

		# そーと
		popList.sort()
		
		popWinOddsDist = {}
		for index in range(len(popList)):
			popWinOddsDist['%s'% str(popList[index])] = index + 1
		
		# レースのオッズとレース詳細を情報を取得する。
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
				if '取' in raceOdds[i].find('td',{'class':'oztan'}).string.strip() or '票数' in raceOdds[i].find('td',{'class':'oztan'}).string.strip():
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
	
			# レース詳細情報用の情報を取得する。
			# 性別と年齢を取得する。
			horseSexAndOld = raceOdds[i].find('td',{'class':'seirei'}).string.strip()
			if '牝' in horseSexAndOld:
				horceSex = '2'
			elif '牡' in horseSexAndOld:
				horceSex = '1'
			elif 'せん' in horseSexAndOld:
				horceSex = '3'
			else:
				horceSex = '0'
			
			if 'せん' in horseSexAndOld:
				horceOld = horseSexAndOld[2:3]
			else:
				horceOld = horseSexAndOld[1:2]
			
			
			# 馬体重と前回体重差を取得する。
			horseWeightInfo = raceOdds[i].find('td',{'class':'batai'}).string
			if horseWeightInfo is None or horseWeightInfo == '':
				horseWeight = '未取得'
				horseWeightDis = '未取得'
			else:
				horseWeightInfo = horseWeightInfo.strip()
				horseWeight = horseWeightInfo[0:3]
				horseWeightDis = horseWeightInfo[4:]
				horseWeightDis = horseWeightDis[:-1]
				
			# 騎手名を取得する。
			condjockerName = raceOdds[i].find('td',{'class':'kishu'})
			condjockerNameIf = condjockerName.a
			if condjockerNameIf is None:
				jockerName = condjockerName.string.strip()
			else:
				jockerName = condjockerName.find('a').string.strip()
			
			# 騎手名の不要な文字を除去する。　☆△▲　が含まれる場合はその文字を除去
			if '▲' in jockerName or '△' in jockerName or '☆' in jockerName:
				jockerName = jockerName[1:]
			
				
			# 負担重量を取得する。
			loadInfo = raceOdds[i].find('td',{'class':'futan'})
			load = float(loadInfo.string.strip())
			
			# 単勝人気を取得する。
			poplarityWinOdds = popWinOddsDist[str(winOdds)]
			
			# すでにRACE_IDとHORCE_NAMEがある場合はUPDATE,ない場合はINSERT
			existPosetRaceDetailT = ["WHERE RACE_ID IN ('%s') AND HORCE_NAME = '%s'"% (raceId,horceName)]
			result = self.daoClass.selectQuery(existPosetRaceDetailT,'existPosetRaceDetailT')
			
			if result[0][0] == 0:
				# 挿入
				dict_Db_POST_RACE_DETAIL_T = {}
				dict_Db_POST_RACE_DETAIL_T['LOGIC_DEL_FLG'] = 0
				dict_Db_POST_RACE_DETAIL_T['INS_PID'] = 'RID02'
				dict_Db_POST_RACE_DETAIL_T['UPD_PID'] = 'RID02'
				dict_Db_POST_RACE_DETAIL_T['RACE_ID'] = raceId
				dict_Db_POST_RACE_DETAIL_T['START_FRAME'] = startFrame
				dict_Db_POST_RACE_DETAIL_T['START_NUM'] = startNum
				dict_Db_POST_RACE_DETAIL_T['HORCE_NAME'] = horceName
				dict_Db_POST_RACE_DETAIL_T['HORCE_SEX'] = horceSex
				dict_Db_POST_RACE_DETAIL_T['HORCE_OLD'] = horceOld
				dict_Db_POST_RACE_DETAIL_T['LOAD_W'] = load
				dict_Db_POST_RACE_DETAIL_T['JOCKER_NAME'] = jockerName
				dict_Db_POST_RACE_DETAIL_T['WEIRHT_HORSE'] = horseWeight
				dict_Db_POST_RACE_DETAIL_T['BERORE_DISTANCE'] = horseWeightDis
				dict_Db_POST_RACE_DETAIL_T['POPULARITY_WIN_ODDS'] = poplarityWinOdds
				self.daoClass.insert('POST_RACE_DETAIL_T',dict_Db_POST_RACE_DETAIL_T)
			else:
				# 更新
				where = "WHERE RACE_ID IN ('%s') AND HORCE_NAME = '%s'"% (raceId,horceName)
				dict_Db_POST_RACE_DETAIL_T = {}
				dict_Db_POST_RACE_DETAIL_T['LOGIC_DEL_FLG'] = 0
				dict_Db_POST_RACE_DETAIL_T['UPD_PID'] = 'RID03'
				dict_Db_POST_RACE_DETAIL_T['START_FRAME'] = startFrame
				dict_Db_POST_RACE_DETAIL_T['START_NUM'] = startNum
				dict_Db_POST_RACE_DETAIL_T['LOAD_W'] = load
				dict_Db_POST_RACE_DETAIL_T['WEIRHT_HORSE'] = horseWeight
				dict_Db_POST_RACE_DETAIL_T['BERORE_DISTANCE'] = horseWeightDis
				dict_Db_POST_RACE_DETAIL_T['POPULARITY_WIN_ODDS'] = poplarityWinOdds	
				self.daoClass.update('POST_RACE_DETAIL_T',dict_Db_POST_RACE_DETAIL_T,where)


		#########################後処理
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,1)

        ##################################################################
        ###### 引数1:html情報
        ###### 戻り値:RACE_ID
        ###### 概要:引数で取得したhtml情報をもとにスクレイピングする
        ###### 
        ##################################################################
	def odds_and_param(self,soup):

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
		

		
		horseNum = 0
		updateFlg = 0
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
			
			# DBにすでに情報がある場合は更新する。
			selectPostRaceOddsT = ["WHERE RACE_ID = '%s'"% raceId,"AND HORCE_NAME = '%s'"% horceName]
			result = self.daoClass.selectQuery(selectPostRaceOddsT,'selectPostRaceOddsT')
			updateFlg = result[0][0]
			
			if result[0][0] == 1:
				where = "WHERE RACE_ID IN ('%s') AND HORCE_NAME = '%s'"% (raceId,horceName)
				dict_Db_POST_RACE_ODDS_T = {}
				dict_Db_POST_RACE_ODDS_T['UPD_PID'] = 'RID03'
				dict_Db_POST_RACE_ODDS_T['START_FRAME'] = startFrame
				dict_Db_POST_RACE_ODDS_T['START_NUM'] = startNum
				dict_Db_POST_RACE_ODDS_T['WIN_ODDS'] = winOdds
				dict_Db_POST_RACE_ODDS_T['MULT_WIN_ODDS_FROM'] = multWinOddsFrom
				dict_Db_POST_RACE_ODDS_T['MULT_WIN_ODDS_TO'] = multWinOddsTo
				# DB更新処理
				self.daoClass.update('POST_RACE_ODDS_T',dict_Db_POST_RACE_ODDS_T,where)
				horseNum = horseNum + 1
			else:
				# DB格納用の辞書を作成する。
				dict_Db_POST_RACE_ODDS_T = {}
				dict_Db_POST_RACE_ODDS_T['LOGIC_DEL_FLG'] = '0'
				dict_Db_POST_RACE_ODDS_T['INS_PID'] = 'RID04'
				dict_Db_POST_RACE_ODDS_T['UPD_PID'] = 'RID04'
				dict_Db_POST_RACE_ODDS_T['RACE_ID'] = raceId
				dict_Db_POST_RACE_ODDS_T['START_FRAME'] = startFrame
				dict_Db_POST_RACE_ODDS_T['START_NUM'] = startNum
				dict_Db_POST_RACE_ODDS_T['HORCE_NAME'] = horceName
				dict_Db_POST_RACE_ODDS_T['WIN_ODDS'] = winOdds
				dict_Db_POST_RACE_ODDS_T['MULT_WIN_ODDS_FROM'] = multWinOddsFrom
				dict_Db_POST_RACE_ODDS_T['MULT_WIN_ODDS_TO'] = multWinOddsTo
				horseNum = horseNum + 1
				# DBにアクセスする処理
				self.daoClass.insert('POST_RACE_ODDS_T',dict_Db_POST_RACE_ODDS_T)
		
		############################################ LINK 取得開始
		self.utilClass.logging('[' + self.pid + '][' + methodname + '] get param info' ,0)
		# 変数宣言
		tanfuku =''
		wakuren =''
		umaren =''
		wide =''
		umatan =''
		renpuku =''
		rentan =''
		
		raceOddsList = soup.find('div',{'class':'oddslist'})
		raceOddsList = raceOddsList.find_all('a')
		for tags in raceOddsList:
			if '単勝' in tags.text:
				tanfuku = tags['onclick'].strip().replace("return doAction('/JRADB/accessO.html','",'')[:-3]
			elif '枠' in tags.text:
				wakuren = tags['onclick'].strip().replace("return doAction('/JRADB/accessO.html','",'')[:-3]
			elif 'ワイド' in tags.text:
				wide = tags['onclick'].strip().replace("return doAction('/JRADB/accessO.html','",'')[:-3]
			elif '馬連' in tags.text:
				umaren = tags['onclick'].strip().replace("return doAction('/JRADB/accessO.html','",'')[:-3]
			elif '馬単' in tags.text:
				umatan = tags['onclick'].strip().replace("return doAction('/JRADB/accessO.html','",'')[:-3]
			elif '連複' in tags.text:
				renpuku = tags['onclick'].strip().replace("return doAction('/JRADB/accessO.html','",'')[:-3]
			elif '連単' in tags.text:
				rentan = tags['onclick'].strip().replace("return doAction('/JRADB/accessO.html','",'')[:-3]
				
		raceFinishFlg = 0
		raceFinish = soup.find('img',{'class':'DKbtn'})
		
		if raceFinish is not None:
			raceFinishFlg = 1
		
		parama_tDict ={}
		parama_tDict['LOGIC_DEL_FLG'] ='0'
		parama_tDict['INS_PID'] ='TE001'
		parama_tDict['UPD_PID'] ='TE001'
		parama_tDict['RACE_ID'] = raceId
		parama_tDict['TANFUKU_LINK'] = tanfuku
		parama_tDict['WAKUREN_LINK'] = wakuren
		parama_tDict['UMAREN_LINK'] = umaren
		parama_tDict['WIDE_LINK'] = wide
		parama_tDict['UMATAN_LINK'] = umatan
		parama_tDict['RENPUKU_LINK'] = renpuku
		parama_tDict['RENTAN_LINK'] = rentan
		parama_tDict['HORSE_NUM'] = horseNum
		parama_tDict['RACE_FINISH_FLG'] = raceFinishFlg
		
		if updateFlg != 0 :
			where = "WHERE RACE_ID IN ('%s')"% (raceId)
			self.daoClass.update('POST_RACE_PARAM_T',parama_tDict,where)
		else:
			self.daoClass.insert('POST_RACE_PARAM_T',parama_tDict)
		self.utilClass.logging('[' + self.pid + '][' + methodname + '] get param info' ,1)
		############################################ LINK 取得終了

		#########################後処理
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,1)
