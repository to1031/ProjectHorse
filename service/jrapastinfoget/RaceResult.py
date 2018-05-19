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

class RaceResult(object):
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
	def jraResult_main(self,htmlinfo):
		# 当メソッドの名前を取得する。
		methodname = sys._getframe().f_code.co_name

		# 処理開始ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,0)

		# BeautifulSoupオブジェクトに変換
		soup = BeautifulSoup(htmlinfo,'html.parser')

		# 終了コード
		returnCode = 0

		try:
			# 1.rece_info
			race_id = self.race_t(soup)

			if 'skip' in race_id:
				self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,1)
				return

			# 2.race_detail_t
			self.race_detail_t(soup,race_id)

			# 2.5.race_detail_tの脚質更新
			self.race_detail_t_update(soup,race_id)
			
			# 3.race_result_t
			self.race_result_t(soup,race_id)
			
			# 4.race_param_t
			self.race_param_t(soup,race_id)

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
	def race_t(self,soup):

		#########################前処理
		#########################
		# メソッド名取得
		methodname = sys._getframe().f_code.co_name
		# メソッド開始ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,0)

		# 内部関数定義
		# レース条件を取得する。(負荷重量・年齢・混合条件・参加条件)
		def raceCond3Get(raceCond3_fuka,raceCond3_oth,raceCondOld):
			
			if '新馬' in raceCond3_oth:
				raceCondMoney = '01'
			elif '未勝利' in raceCond3_oth:
				raceCondMoney = '02'
			elif 'オープン' in raceCond3_oth:
				raceCondMoney = '03'
			elif '500万' in raceCond3_oth:
				raceCondMoney = '04'
			elif '1000万' in raceCond3_oth:
				raceCondMoney = '05'
			elif '600万' in raceCond3_oth:
				raceCondMoney = '06'
			else:
				raceCondMoney = '00'
			
			if '混合' in raceCond3_oth:
				raceCondSex = '01'
			elif '牡' in raceCond3_oth:
				raceCondSex = '02'
			elif '牝' in raceCond3_oth:
				raceCondSex = '03'
			else:
				raceCondSex = '04'
			
			# 年齢がraceCond1Getにて取得できていなかった場合
			if raceCondOld == '00':
				if '4歳以上' in raceCondOld:
					raceCondOld = '04'
				elif '3歳以上' in raceCondOld:
					raceCondOld = '03'
				elif '3歳' in raceCondOld:
						raceCondOld = '02'
				elif'2歳' in raceCondOld:
					raceCondOld = '01'
				else:
					raceCondOld = '00'
			
			if '定量' in raceCond3_fuka:
				raceWeight = '01'
			elif '別定' in raceCond3_fuka:
				raceWeight = '02'
			elif 'ハンデ' in raceCond3_fuka:
				raceWeight = '03'
			elif '馬齢' in raceCond3_fuka:
				raceWeight = '04'
			else:
				raceWeight = '00'
			
			dict_cond3 = {}
			dict_cond3['raceCondMoney'] = raceCondMoney
			dict_cond3['raceCondSex'] = raceCondSex
			dict_cond3['raceCondOld'] = raceCondOld
			dict_cond3['raceWeight'] = raceWeight
			return dict_cond3
				
		# レースの天候とコンディションを取得する。
		def raceCond2Get(raceCond2):
			# グランド状態を取得する
			if '不良' in raceCond2:
				raceCondition = '04'
			elif '稍重' in raceCond2:
				raceCondition = '02'
			elif '重' in raceCond2:
				raceCondition = '03'
			elif '良' in raceCond2:
				raceCondition = '01'
			else:
				raceCondition = '00'
			
			# 天候を取得する。
			if '晴' in raceCond2:
				raceWeather = '01'
			elif '曇' in raceCond2:
				raceWeather = '02'
			elif '小雨' in raceCond2:
				raceWeather = '03'
			elif '雨' in raceCond2:
				raceWeather = '04'
			elif '小雪' in raceCond2:
				raceWeather = '05'	
			elif '雪' in raceCond2:
				raceWeather = '06'
			else:
				raceWeather = '00'
			
			dict_cond2 ={}
			dict_cond2['raceCondition'] =  raceCondition
			dict_cond2['raceWeather'] =  raceWeather
			return dict_cond2
		
		# レース条件を取得する。(障害・年齢・芝orダート)
		def raceCond1Get(raceCond1):
			
			# 障害区分を取得する
			shogaiAndOld = raceCond1[0].string.strip()
			if '障害' in shogaiAndOld:
				raceShogaiFlg = '1'
			else:
				raceShogaiFlg = '0'
			
			# 年齢を取得する
			if '4歳以上' in shogaiAndOld:
				raceCondOld = '04'
			elif '3歳以上' in shogaiAndOld:
				raceCondOld = '03'
			elif '3歳' in shogaiAndOld:
				raceCondOld = '02'
			elif'2歳' in shogaiAndOld:
				raceCondOld = '01'
			else:
				raceCondOld = '00'
			
			# 距離を取得する
			raceRange = raceCond1[1].string.replace('コース','').strip()
			raceRange = raceRange[0:4]
			
			# 芝かダートか取得する
			ground = raceCond1[1].string.strip()
			if '芝' in ground:
				raceGroundFlg = '0'
			else:
				raceGroundFlg = '1'
			
			# 右 or 左　周りかどうか取得する
			if '外' in ground:
				raceTurnFlg = '1'
			else:
				raceTurnFlg = '0'
			
			dict_cond1 ={}
			dict_cond1['raceShogaiFlg'] = raceShogaiFlg
			dict_cond1['raceCondOld'] = raceCondOld
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
			gladeStr = glade.attrs['alt']
		
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
		
		
		# レース出走時刻,賞金情報を取得する。
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
		
		# レース出走時刻を取得する
		raceTime = soup.find('div',{'class':'raceHassou'}).text
		raceTime = raceTime[-5:]
		raceTime = raceTimeGet(raceTime)
		
		# レースの天候とコンディションを取得する。
		raceCond2 = soup.find('div',{'class':'raceTenkou'}).text
		raceCond2 = raceCond2Get(raceCond2)
		raceWeather = raceCond2['raceWeather']
		raceCondition = raceCond2['raceCondition']
		
		# レース条件を取得する。(障害・年齢・芝orダート・周回方向)
		raceCond1 = [soup.find('div',{'class':'raceSyubetsu'}),soup.find('div',{'class':'raceKyoriTrack'})]
		raceCond1 = raceCond1Get(raceCond1)
		raceGroundFlg = raceCond1['raceGroundFlg']
		raceRange = raceCond1['raceRange']
		raceTurnFlg = raceCond1['raceTurnFlg']
		raceShogaiFlg = raceCond1['raceShogaiFlg']
		raceCondOld = raceCond1['raceCondOld']
		

		
		# レース条件を取得する。(負荷重量・年齢・混合条件・参加条件)
		raceCond3_fuka = soup.find('div',{'class':'raceJuryou'}).text.strip()
		raceCond3_oth = soup.find('div',{'class':'raceJoken'}).text.strip()
		raceCond3 = raceCond3Get(raceCond3_fuka,raceCond3_oth,raceCondOld)
		
		raceWeight = raceCond3['raceWeight']
		raceCondSex = raceCond3['raceCondSex']
		raceCondOld = raceCond3['raceCondOld']
		raceCondMoney = raceCond3['raceCondMoney']
		
		# レースIDを取得する.
		raceId = 'R0100' + raceDate + racePlace + raceNo
		
		# レースID がすでにある場合はスキップする。
		where = ["WHERE RACE_ID = '%s'" % raceId]
		confirmRaceId = self.daoClass.selectQuery(where,'raceTExistConfirm')
		
		if confirmRaceId[0][0] >= 1:
			#処理を返す。
			self.utilClass.logging('this raceid have done already.' ,2)
			self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,1)
			return 'skip'
		
		# ペースを取得するためにレースのペースを取得する。
		racePaceTime = soup.find_all('tr')
		halfTime =''
		halfAfterTime =''
		timeOf4F =''
		timeOf3F =''
		if raceShogaiFlg == '1':
			halfTime = 0
			halfAfterTime = 0
			timeOf4F = 0
			timeOf3F = 0
		else:
			for index in range(len(racePaceTime)):
				if racePaceTime[index].find('th') is None:
					continue
				if racePaceTime[index].find('th').text is None:
					continue
				
				if racePaceTime[index].find('th').string is None:
					contunue
				
				if racePaceTime[index].find('th').string.strip() == 'ハロンタイム':
					paceList = racePaceTime[index].find('td').string.split('-')
					# 200で距離が割り切れる場合
					if int(raceRange) % 200 == 0:
						halfNum = len(paceList) / 2
						halfTime = datetime.timedelta()
						halfAfterTime = datetime.timedelta()
						if len(paceList) % 2 == 0:
							for factor in range(0,int(halfNum)):
								spripstr = paceList[factor].strip()
								if len(spripstr) == 3:
									intseconds = int(spripstr[0:1])
									millsecs = int(spripstr[2:])
								else:
									intseconds = int(spripstr[0:2])
									millsecs = int(spripstr[3:])
								halfTimept = datetime.timedelta(days=0, seconds=intseconds, milliseconds=millsecs*100)
								halfTime = halfTime + halfTimept
							
							for factor in range(int(halfNum),len(paceList)):
								spripstr = paceList[factor].strip()
								if len(spripstr) == 3:
									intseconds = int(spripstr[0:1])
									millsecs = int(spripstr[2:])
								else:
									intseconds = int(spripstr[0:2])
									millsecs = int(spripstr[3:])
								halfTimept = datetime.timedelta(days=0, seconds=intseconds, milliseconds=millsecs*100)
								halfAfterTime = halfAfterTime + halfTimept
						
							if halfTime.seconds > 119:
								halfTime = datetime.time(0,2,halfTime.seconds -120,halfTime.microseconds)
							elif halfTime.seconds > 59:
								halfTime = datetime.time(0,1,halfTime.seconds -60,halfTime.microseconds)
							else:
								halfTime = datetime.time(0,0,halfTime.seconds,halfTime.microseconds)
							
							if halfAfterTime.seconds > 119:
								halfAfterTime = datetime.time(0,2,halfAfterTime.seconds -120,halfAfterTime.microseconds)
							elif halfAfterTime.seconds > 59:
								halfAfterTime = datetime.time(0,1,halfAfterTime.seconds -60,halfAfterTime.microseconds)
							else:
								halfAfterTime = datetime.time(0,0,halfAfterTime.seconds,halfAfterTime.microseconds)
						else:
							halfNum = halfNum - 0.5
							for factor in range(len(paceList)):
								if factor < halfNum:
									spripstr = paceList[factor].strip()
									if len(spripstr) == 3:
										intseconds = int(spripstr[0:1])
										millsecs = int(spripstr[2:])
									else:
										intseconds = int(spripstr[0:2])
										millsecs = int(spripstr[3:])
									halfTimept = datetime.timedelta(days=0, seconds=intseconds, milliseconds=millsecs*100)
									halfTime = halfTime + halfTimept					
								
								if factor == halfNum:
									spripstr = paceList[factor].strip()
									if len(spripstr) == 3:
										intseconds = int(spripstr[0:1])
										millsecs = int(spripstr[2:])
									else:
										intseconds = int(spripstr[0:2])
										millsecs = int(spripstr[3:])
									halfJustTime = datetime.timedelta(days=0, seconds=intseconds, milliseconds=millsecs*100)
									halfJustTime = halfJustTime / 2
								
								if factor > halfNum:
									spripstr = paceList[factor].strip()
									if len(spripstr) == 3:
										intseconds = int(spripstr[0:1])
										millsecs = int(spripstr[2:])
									else:
										intseconds = int(spripstr[0:2])
										millsecs = int(spripstr[3:])
									halfTimept = datetime.timedelta(days=0, seconds=intseconds, milliseconds=millsecs*100)
									halfAfterTime = halfAfterTime + halfTimept
							
							halfTime = halfTime + halfJustTime
							halfAfterTime = halfAfterTime + halfJustTime
								
							if halfTime.seconds > 119:
								halfTime = datetime.time(0,2,halfTime.seconds -120,halfTime.microseconds)
							elif halfTime.seconds > 59:
								halfTime = datetime.time(0,1,halfTime.seconds -60,halfTime.microseconds)
							else:
								halfTime = datetime.time(0,0,halfTime.seconds,halfTime.microseconds)
							
							if halfAfterTime.seconds > 119:
								halfAfterTime = datetime.time(0,2,halfAfterTime.seconds -120,halfAfterTime.microseconds)
							elif halfAfterTime.seconds > 59:
								halfAfterTime = datetime.time(0,1,halfAfterTime.seconds -60,halfAfterTime.microseconds)
							else:
								halfAfterTime = datetime.time(0,0,halfAfterTime.seconds,halfAfterTime.microseconds)	
	
					else: # 距離が１ハロンで割り切れない時
						halfTime = datetime.timedelta()
						halfAfterTime = datetime.timedelta()
						halfNum = len(paceList) / 2
						if len(paceList) % 2 == 0:
							for factor in range(len(paceList)):
								if factor < halfNum:
									if factor == 0:
										continue
									spripstr = paceList[factor].strip()
									if len(spripstr) == 3:
										intseconds = int(spripstr[0:1])
										millsecs = int(spripstr[2:])
									else:
										intseconds = int(spripstr[0:2])
										millsecs = int(spripstr[3:])
									halfTimept = datetime.timedelta(days=0, seconds=intseconds, milliseconds=millsecs*100)
									halfTime = halfTime + halfTimept					
								
								if factor == halfNum:
									spripstr = paceList[factor].strip()
									if len(spripstr) == 3:
										intseconds = int(spripstr[0:1])
										millsecs = int(spripstr[2:])
									else:
										intseconds = int(spripstr[0:2])
										millsecs = int(spripstr[3:])
									halfJustTime = datetime.timedelta(days=0, seconds=intseconds, milliseconds=millsecs*100)
									halfJustTime = halfJustTime / 2
								
								if factor > halfNum:
									spripstr = paceList[factor].strip()
									if len(spripstr) == 3:
										intseconds = int(spripstr[0:1])
										millsecs = int(spripstr[2:])
									else:
										intseconds = int(spripstr[0:2])
										millsecs = int(spripstr[3:])
									halfTimept = datetime.timedelta(days=0, seconds=intseconds, milliseconds=millsecs*100)
									halfAfterTime = halfAfterTime + halfTimept
							
							halfTime = halfTime + halfJustTime
							halfAfterTime = halfAfterTime + halfJustTime
								
							if halfTime.seconds > 119:
								halfTime = datetime.time(0,2,halfTime.seconds -120,halfTime.microseconds)
							elif halfTime.seconds > 59:
								halfTime = datetime.time(0,1,halfTime.seconds -60,halfTime.microseconds)
							else:
								halfTime = datetime.time(0,0,halfTime.seconds,halfTime.microseconds)
							
							if halfAfterTime.seconds > 119:
								halfAfterTime = datetime.time(0,2,halfAfterTime.seconds -120,halfAfterTime.microseconds)
							elif halfAfterTime.seconds > 59:
								halfAfterTime = datetime.time(0,1,halfAfterTime.seconds -60,halfAfterTime.microseconds)
							else:
								halfAfterTime = datetime.time(0,0,halfAfterTime.seconds,halfAfterTime.microseconds)	
							
						else:
							halfNum = halfNum + 0.5
							for factor in range(1,int(halfNum)):
								spripstr = paceList[factor].strip()
								if len(spripstr) == 3:
									intseconds = int(spripstr[0:1])
									millsecs = int(spripstr[2:])
								else:
									intseconds = int(spripstr[0:2])
									millsecs = int(spripstr[3:])
								halfTimept = datetime.timedelta(days=0, seconds=intseconds, milliseconds=millsecs*100)
								halfTime = halfTime + halfTimept
							
							for factor in range(int(halfNum),len(paceList)):
								spripstr = paceList[factor].strip()
								if len(spripstr) == 3:
									intseconds = int(spripstr[0:1])
									millsecs = int(spripstr[2:])
								else:
									intseconds = int(spripstr[0:2])
									millsecs = int(spripstr[3:])
								halfTimept = datetime.timedelta(days=0, seconds=intseconds, milliseconds=millsecs*100)
								halfAfterTime = halfAfterTime + halfTimept
						
							if halfTime.seconds > 119:
								halfTime = datetime.time(0,2,halfTime.seconds -120,halfTime.microseconds)
							elif halfTime.seconds > 59:
								halfTime = datetime.time(0,1,halfTime.seconds -60,halfTime.microseconds)
							else:
								halfTime = datetime.time(0,0,halfTime.seconds,halfTime.microseconds)
							
							if halfAfterTime.seconds > 119:
								halfAfterTime = datetime.time(0,2,halfAfterTime.seconds -120,halfAfterTime.microseconds)
							elif halfAfterTime.seconds > 59:
								halfAfterTime = datetime.time(0,1,halfAfterTime.seconds -60,halfAfterTime.microseconds)
							else:
								halfAfterTime = datetime.time(0,0,halfAfterTime.seconds,halfAfterTime.microseconds)
							
						
				# 残り4F,3Fのタイムを取得する。
				if racePaceTime[index].find('th').string.strip() == '上り':
					leaveFList = racePaceTime[index].find('td').string.split('-')
					timeOf4Fstr = leaveFList[0].strip()
					timeOf3Fstr = leaveFList[1].strip()
					timeOf4Fstr = timeOf4Fstr[-4:]
					timeOf3Fstr = timeOf3Fstr[-4:]
					timeOf4F = datetime.time(0,0,int(timeOf4Fstr[0:2]),int(timeOf4Fstr[3:])*100000)
					timeOf3F = datetime.time(0,0,int(timeOf3Fstr[0:2]),int(timeOf3Fstr[3:])*100000)
		
		
		
		
		# DBに格納する辞書を作成する。
		dict_Db_RACE_T = {}
		dict_Db_RACE_T['LOGIC_DEL_FLG']='0'
		dict_Db_RACE_T['INS_PID']='RID01'
		dict_Db_RACE_T['UPD_PID']='RID01'
		dict_Db_RACE_T['RACE_ID']=raceId
		dict_Db_RACE_T['RACE_NEME']=raceNeme
		dict_Db_RACE_T['RACE_DATE']=raceDate
		dict_Db_RACE_T['RACE_TIME']=raceTime
		dict_Db_RACE_T['RACE_PLACE']=racePlace
		dict_Db_RACE_T['RACE_NO']=raceNo
		dict_Db_RACE_T['RACE_GROUND_FLG']=raceGroundFlg
		dict_Db_RACE_T['RACE_RANGE']=raceRange
		dict_Db_RACE_T['RACE_TURN_FLG']=raceTurnFlg
		dict_Db_RACE_T['RACE_GLADE']=raceGlade
		dict_Db_RACE_T['RACE_WEIGHT']=raceWeight
		dict_Db_RACE_T['RACE_COND_SEX']=raceCondSex
		dict_Db_RACE_T['RACE_SHOGAI_FLG']=raceShogaiFlg
		dict_Db_RACE_T['RACE_COND_OLD']=raceCondOld
		dict_Db_RACE_T['RACE_COND_MONEY']=raceCondMoney
		dict_Db_RACE_T['RACE_WEATHER']=raceWeather
		dict_Db_RACE_T['RACE_CONDITION']=raceCondition
		dict_Db_RACE_T['RACE_PRIZE_1']=racePrize1
		dict_Db_RACE_T['RACE_PRIZE_2']=racePrize2
		dict_Db_RACE_T['RACE_PRIZE_3']=racePrize3
		dict_Db_RACE_T['RACE_PRIZE_4']=racePrize4
		dict_Db_RACE_T['RACE_PRIZE_5']=racePrize5
		dict_Db_RACE_T['HALF_TIME']=halfTime
		dict_Db_RACE_T['HALF_AFTER_TIME']=halfAfterTime
		dict_Db_RACE_T['TIME_OF4F']=timeOf4F
		dict_Db_RACE_T['TIME_OF3F']=timeOf3F
		#DBにアクセスする。
		self.daoClass.insert('RACE_T',dict_Db_RACE_T)

		#########################終処理
		########################
		self.utilClass.logging('############ ' + raceId + ' ###################',2)
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,1)
		return raceId


	##################################################################
	###### 引数1:html情報
	###### 引数2:RACE_ID
	###### 概要:引数で取得したhtml情報をもとにスクレイピングする
	###### 
	##################################################################
	def race_detail_t(self,soup,race_id):

		#########################前処理
		#########################
		# メソッド名取得
		methodname = sys._getframe().f_code.co_name
		# メソッド開始ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,0)

		#########################主処理
		#########################
		# レース結果の詳細情報を取得する。
		raceResult = soup.find('table', {'class' : 'mainList'})
		raceResult = raceResult.find_all('tr')	
		
		# <tr>毎に着順別の情報が格納されているのでループで取得DB格納する。
		ifint = 0
		for raceResultDetail in raceResult:
			# o番目の要素はスキップする。
			if ifint == 0:
				ifint = ifint + 1
				continue
			
			raceResultInfo = raceResultDetail.find_all('td')
			
			# 取り消しの場合、スキップ(要検討)
			goalNum = raceResultInfo[0].string.strip()
			if not goalNum.isdigit():
				# 中止のうまが存在する場合の処理
				if '中止' in goalNum:
					goalNum = '中止'
				else:
					continue
			startFrame = raceResultInfo[1].img['alt'][1:2]
			startNum = raceResultInfo[2].string.strip()
			
			# 馬名にリンクがない場合の処理
			noneCondHorceName = raceResultInfo[3].a
			horceName = ''
			if noneCondHorceName is None:
				horceName = raceResultInfo[3].string.strip()
			else:
				horceName = raceResultInfo[3].a.string.strip()
				
			# 牝と年齢を取得する処理
			if '牝' in raceResultInfo[4].string.strip():
				horceSex = '2'
			elif '牡' in raceResultInfo[4].string.strip():
				horceSex = '1'
			elif 'せん' in raceResultInfo[4].string.strip():
				horceSex = '3'
			else:
				horceSex = '0'
			
			if 'せん' in raceResultInfo[4].string.strip():
				horceOld = raceResultInfo[4].string.strip()[2:3]
			else:
				horceOld = raceResultInfo[4].string.strip()[1:2]
			
			load = float(raceResultInfo[5].string.strip())
			
			# 騎手にリンクがなかった場合の処理
			noneCondJockerName = raceResultInfo[7].a
			if noneCondJockerName is None:
				jockerName = raceResultInfo[7].string.strip()
			else:
				jockerName = raceResultInfo[7].a.string.strip()
			
			# 中止の場合の処理追加
			if goalNum == '中止':
				goalTime = datetime.time(0,0,0,0)
			else:
				goalMin = int(raceResultInfo[8].string.strip()[0:1])
				goalSec = int(raceResultInfo[8].string.strip()[2:4])
				goalSecMini = int(raceResultInfo[8].string.strip()[5:])
				goalTime = datetime.time(0,goalMin,goalSec,goalSecMini*100000)
			
			ifConf = raceResultInfo[9].string
			if ifConf == '　':
				# 中止の時の処理追加
				if goalNum == '中止':
					goalDistance = '-'
				else:
					goalDistance = '0'
			else:
				if ifConf is None:
					goalDistance = raceResultInfo[9].text.strip()
					if len(goalDistance) > 8:
						goalDistance = goalDistance[0:7]
				else:
					goalDistance = raceResultInfo[9].string.strip()
					if len(goalDistance) > 8:
						goalDistance = goalDistance[0:7]					
			
			if goalNum == '中止':
				upTime = '-'
			else:
				if goalDistance == '大差':
					if raceResultInfo[10].string is None:
						upTime = '-'
					else:
						upTime = raceResultInfo[10].string.strip()
				else:
					upTime = raceResultInfo[10].string.strip()
			weight = raceResultInfo[11].string.strip()
			
			# 計測不可能だった場合
			if raceResultInfo[12].string is None:
				beroreDistance = '計不'
			else:
				beroreDistance = raceResultInfo[12].string.strip()
			
			# 調教師にリンクがなかった場合の処理
			noneCondTrainerName = raceResultInfo[13].a
			if noneCondTrainerName is None:
				trainerName = raceResultInfo[13].string.strip()
				if len(trainerName) > 10:
					trainerName = trainerName[0:9]
			else:
				trainerName = raceResultInfo[13].a.string.strip()
			popularity = raceResultInfo[14].string.strip()
			
			dict_Db_RACE_DETAIL_T = {}
			dict_Db_RACE_DETAIL_T['LOGIC_DEL_FLG'] = 0
			dict_Db_RACE_DETAIL_T['INS_PID'] = 'RID02'
			dict_Db_RACE_DETAIL_T['UPD_PID'] = 'RID02'
			dict_Db_RACE_DETAIL_T['RACE_ID'] = race_id
			dict_Db_RACE_DETAIL_T['GOAL_NUM'] = goalNum
			dict_Db_RACE_DETAIL_T['START_FRAME'] = startFrame
			dict_Db_RACE_DETAIL_T['START_NUM'] = startNum
			dict_Db_RACE_DETAIL_T['HORCE_NAME'] = horceName
			dict_Db_RACE_DETAIL_T['HORCE_SEX'] = horceSex
			dict_Db_RACE_DETAIL_T['HORCE_OLD'] = horceOld
			dict_Db_RACE_DETAIL_T['LOAD_W'] = load
			dict_Db_RACE_DETAIL_T['JOCKER_NAME'] = jockerName
			dict_Db_RACE_DETAIL_T['GOAL_TIME'] = goalTime
			dict_Db_RACE_DETAIL_T['GOAL_DISTANCE'] = goalDistance
			dict_Db_RACE_DETAIL_T['UP_TIME'] = upTime
			dict_Db_RACE_DETAIL_T['WEIRHT_HORSE'] = weight
			dict_Db_RACE_DETAIL_T['BERORE_DISTANCE'] = beroreDistance
			dict_Db_RACE_DETAIL_T['TRAINER_NAME'] = trainerName
			dict_Db_RACE_DETAIL_T['POPULARITY_WIN_ODDS'] = popularity
			
			# DBにアクセスする処理
			self.daoClass.insert('RACE_DETAIL_T',dict_Db_RACE_DETAIL_T)


		#########################終処理
		#########################
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,1) 

	##################################################################
	###### 引数1:html情報
	###### 引数2:RACE_ID
	###### 概要:引数で取得したhtml情報をもとにスクレイピングする
	###### 
	##################################################################
	def race_detail_t_update(self,soup,race_id):
		#########################前処理
		#########################
		# メソッド名取得
		methodname = sys._getframe().f_code.co_name
		# メソッド開始ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,0)

		# 3コーナー通過順位から脚質を取得する。
		NIGE = '01'
		SENKO = '02'
		SASHI = '03'
		OI = '04'
		
		startNum1RunStyle = 0
		startNum2RunStyle = 0
		startNum3RunStyle = 0
		startNum4RunStyle = 0
		startNum5RunStyle = 0
		startNum6RunStyle = 0
		startNum7RunStyle = 0
		startNum8RunStyle = 0
		startNum9RunStyle = 0
		startNum10RunStyle = 0
		startNum11RunStyle = 0
		startNum12RunStyle = 0
		startNum13RunStyle = 0
		startNum14RunStyle = 0
		startNum15RunStyle = 0
		startNum16RunStyle = 0
		startNum17RunStyle = 0
		startNum18RunStyle = 0


		#########################主処理
		#########################
		# gray12を持つタグを全て取得する.
		table_run_style = soup.find('table', {'class' : 'cornerJuniList'})
		textStr = ''
		infoExistCount = ''
		if table_run_style is not None:
			runStyleGetInfo = table_run_style.find_all('tr')
			for index in range(0, len(runStyleGetInfo)):
				textStr = runStyleGetInfo[index].th.text
				if '3コーナー' in textStr:
					infoExistCount = index
		
		if infoExistCount != '':
			runstr = runStyleGetInfo[infoExistCount].td.text
			runstr = runstr.replace('(',',')
			runstr = runstr.replace(')',',')
			runstr = runstr.replace('-',',')
			runstr = runstr.replace('*','')
			runstr = runstr.replace('=',',')
			runstr = runstr.replace(',,',',')
			infoList = runstr.split(',')
			infoListResult = []
			for info in infoList:
				if info != '':
					info = info.strip()
					if info.isdigit():
						infoListResult.append(info)

			allNnm = len(infoListResult)
			# 上位20%を逃げ、50%を先行、80%を差し、後方20を追いとする。
			nigeBorder = math.floor(allNnm * 0.2)
			senkoBorder = math.floor(allNnm * 0.5)
			sashiBorder = math.floor(allNnm * 0.8)
			# 数字のみの配列にする。
			counter = 0
			resuldict = {}
			for info in infoListResult:
				if counter < nigeBorder:
					resuldict[info] = NIGE
				elif counter < senkoBorder:
					resuldict[info] = SENKO
				elif counter < sashiBorder:
					resuldict[info] = SASHI
				else:
					resuldict[info] = OI
				counter = counter + 1
			
			
			# レース結果の詳細情報を取得する。
			raceResult = soup.find('table', {'class' : 'mainList'})
			raceResult = raceResult.find_all('tr')	
			
			# <tr>毎に着順別の情報が格納されているのでループで取得DB格納する。
			ifint = 0
			for raceResultDetail in raceResult:
				# o番目の要素はスキップする。
				if ifint == 0:
					ifint = ifint + 1
					continue
				
				raceResultInfo = raceResultDetail.find_all('td')
				
				# 取り消しの場合、スキップ(要検討)
				goalNum = raceResultInfo[0].string.strip()
				if not goalNum.isdigit():
					# 中止のうまが存在する場合の処理
					if '中止' in goalNum:
						goalNum = '中止'
					else:
						continue
				startFrame = raceResultInfo[1].img['alt'][1:2]
				startNum = raceResultInfo[2].string.strip()
				
				# 馬名にリンクがない場合の処理
				noneCondHorceName = raceResultInfo[3].a
				horceName = ''
				if noneCondHorceName is None:
					horceName = raceResultInfo[3].string.strip()
				else:
					horceName = raceResultInfo[3].a.string.strip()
				
				# 騎手にリンクがなかった場合の処理
				noneCondJockerName = raceResultInfo[7].a
				if noneCondJockerName is None:
					jockerName = raceResultInfo[7].string.strip()
				else:
					jockerName = raceResultInfo[7].a.string.strip()
				
				where = "WHERE RACE_ID IN ('%s') AND HORCE_NAME = '%s'"% (race_id,horceName)
				dict_Db_RACE_DETAIL_T = {}
				if '中止' in goalNum:
					dict_Db_RACE_DETAIL_T['RUN_STYLE'] = '00'
				else:
					dict_Db_RACE_DETAIL_T['RUN_STYLE'] = resuldict[startNum]
				self.daoClass.update('RACE_DETAIL_T',dict_Db_RACE_DETAIL_T,where)
		else:
			where = "WHERE RACE_ID IN ('%s')"% (self.race_id)
			dict_Db_RACE_DETAIL_T = {}
			dict_Db_RACE_DETAIL_T['RUN_STYLE'] = '00'
			self.daoClass.update('RACE_DETAIL_T',dict_Db_RACE_DETAIL_T,where)

		#########################終処理
		#########################
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,1) 


	##################################################################
	###### 引数1:html情報
	###### 引数2:RACE_ID
	###### 概要:引数で取得したhtml情報をもとにスクレイピングする
	###### 
	##################################################################
	def race_result_t(self,soup,race_id):
		#########################前処理
		#########################
		# メソッド名取得
		methodname = sys._getframe().f_code.co_name
		# メソッド開始ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,0)

		# ローカル変数を定義する。
		winY1Odds = None
		winY2OddsPop = None
		winY3Odds = None
		winY3OddsPop = None
		winmultiYOdds = None
		winmultiYOddsPop = None
		wakurenYOdds = None
		wakurenYOddsPop = None
		umarenYOdds = None
		umarenYOddsPop = None
		umatanYOdds = None
		umatanYOddsPop = None
		wideY1Odds = None
		wideY1OddsPop = None
		wideY2Odds = None
		wideY2OddsPop = None
		renpukuYOdds = None
		renpukuYOddsPop = None
		rentanYOdds = None
		rentanYOddsPop = None
		winmulti3Odds = None
		winmulti3OddsPop = None

		#########################主処理
		#########################
		raceResultInfo = soup.find_all('table', { 'class':'haraimodoshiList'})
		for InfoValue in raceResultInfo:
			
			InfoValue = InfoValue.find_all('tr')
			length = len(InfoValue)
			for i in range(len(InfoValue)):
				
				if InfoValue[i].th is None:
					continue

				# 単勝オッズとその人気を取得する。
				if '単勝' in InfoValue[i].th.string.strip():
					winOddsStr = InfoValue[i].find_all('td')[1].text.strip().split('円')
					for index in range(len(winOddsStr)):
						if index == 0:
							winOdds = int(winOddsStr[0].replace(',','').strip())
						elif index == 1:
							if winOddsStr[index].strip() == '':
								break
							winY1Odds = int(winOddsStr[1].replace(',','').strip())
						elif index == 2:
							if winOddsStr[index].strip() == '':
								break
							winY3Odds = int(winOddsStr[2].replace(',','').strip())
						else:
							break
					
					
					winOddsPopStr = InfoValue[i].find_all('td')[2].text.strip().split('番人気')
					for index in range(len(winOddsPopStr)):
						if index == 0:
							winOddsPop = int(winOddsPopStr[0].replace(',','').strip())
						elif index == 1:
							if winOddsPopStr[index].strip() == '':
								break
							winY2OddsPop = int(winOddsPopStr[1].replace(',','').strip())
						elif index == 2:
							if winOddsPopStr[index].strip() == '':
								break
							winY3OddsPop = int(winOddsPopStr[2].replace(',','').strip())
						else:
							break
					continue

				if '馬連' in InfoValue[i].th.string.strip():
					umarenOddsStr = InfoValue[i].find_all('td')[1].text.strip().split('円')
					if umarenOddsStr[0].replace(',','').strip() == '':
						umarenOdds = 0
						umarenYOdds = 0
						umarenOddsPop = 0
						umarenYOddsPop = 0
						continue
					for index in range(len(umarenOddsStr)):
						if index == 0:
							umarenOdds = int(umarenOddsStr[0].replace(',','').strip())
						elif index == 1:
							if umarenOddsStr[index].strip() == '':
								break
							umarenYOdds = int(umarenOddsStr[1].replace(',','').strip())
						else:
							break
					
					umarenOddsPopStr = InfoValue[i].find_all('td')[2].text.strip().split('番人気')
					for index in range(len(umarenOddsPopStr)):
						if index == 0:
							umarenOddsPop = int(umarenOddsPopStr[0].replace(',','').strip())
						elif index == 1:
							if umarenOddsPopStr[index].strip() == '':
								break
							umarenYOddsPop = int(umarenOddsPopStr[1].replace(',','').strip())
						else:
							break
					continue
				
				# 馬単オッズとその人気を取得する。
				if '馬単' in InfoValue[i].th.string.strip():
					umatanOddsStr = InfoValue[i].find_all('td')[1].text.strip().split('円')
					for index in range(len(umatanOddsStr)):
						if index == 0:
							umatanOdds = int(umatanOddsStr[0].replace(',','').strip())
						elif index == 1:
							if umatanOddsStr[index].strip() == '':
								break
							umatanYOdds = int(umatanOddsStr[1].replace(',','').strip())
						else:
							break

					umatanOddsPopStr = InfoValue[i].find_all('td')[2].text.strip().split('番人気')
					for index in range(len(umatanOddsPopStr)):
						if index == 0:
							umatanOddsPop = int(umatanOddsPopStr[0].replace(',','').strip())
						elif index == 1:
							if umatanOddsPopStr[index].strip() == '':
								break
							umatanYOddsPop = int(umatanOddsPopStr[1].replace(',','').strip())
						else:
							break
					continue
				
				# 複勝オッズがない場合はスキップする。
				if '複勝' in InfoValue[i]:
					if InfoValue[i + 2].text.strip() == '':
						winmulti1Odds = 0
						winmulti2Odds = 0
						winmulti3Odds = 0
						winmultiYOdds = 0
						winmulti1OddsPop = 0
						winmulti2OddsPop = 0
						winmulti3OddsPop = 0
						winmultiYOddsPop = 0
						continue
				
				# 複勝オッズとその人気を取得する。
				if '複勝' in InfoValue[i].th.string.strip():
					winmulti = InfoValue[i].find_all('td')[1].text.strip()
					if i + 1 < length:
						winmulti = winmulti + InfoValue[i + 1].find_all('td')[1].text.strip()
					
					if i + 2 < length:
						winmulti = winmulti + InfoValue[i + 2].find_all('td')[1].text.strip()
					
					winmulti = winmulti.split('円')
					
					for index in range(len(winmulti)):
						if index == 0:
							winmulti1Odds = int(winmulti[0].replace(',','').strip())
						elif index == 1:
							winmulti2Odds = int(winmulti[1].replace(',','').strip())
						elif index == 2:
							if winmulti[index].strip() == '':
								break
							winmulti3Odds = int(winmulti[2].replace(',','').strip())
						elif index == 3:
							if winmulti[index].strip() == '':
								break
							winmultiYOdds = int(winmulti[3].replace(',','').strip())
						else:
							break
					
					
					winmultiddsPop = InfoValue[i].find_all('td')[2].text.strip()
					if i + 1 < length:
						winmultiddsPop = winmultiddsPop + InfoValue[i + 1].find_all('td')[2].text.strip()
					
					if i + 2 < length:
						winmultiddsPop = winmultiddsPop + InfoValue[i + 2].find_all('td')[2].text.strip()
						
					winmultiddsPop = winmultiddsPop.split('番人気')

					for index in range(len(winmultiddsPop)):
						if index == 0:
							winmulti1OddsPop = int(winmultiddsPop[0].replace(',','').strip())
						elif index == 1:
							winmulti2OddsPop = int(winmultiddsPop[1].replace(',','').strip())
						elif index == 2:
							if winmultiddsPop[index].strip() == '':	
								break
							winmulti3OddsPop = int(winmultiddsPop[2].replace(',','').strip())
						elif index == 3:
							if winmultiddsPop[index].strip() == '':
								break
							winmultiYOddsPop = int(winmultiddsPop[3].replace(',','').strip())
						else:
							break
					continue
				
				if 'ワイド' in InfoValue[i].th.string.strip():
					wideddsStr = InfoValue[i].find_all('td')[1].text.strip()
					if i + 1 < length:
						wideddsStr = wideddsStr + InfoValue[i + 1].find_all('td')[1].text.strip()
					
					if i + 2 < length:
						wideddsStr = wideddsStr + InfoValue[i + 2].find_all('td')[1].text.strip()
					
					wideddsStr = wideddsStr.split('円')
					if wideddsStr[0].replace(',','').strip() == '':
						wide12Odds = 0
						wide23Odds = 0
						wide13Odds = 0
						wideY2Odds = 0
						wideY1Odds = 0
						wide12OddsPop = 0
						wide13OddsPop = 0
						wide23OddsPop = 0
						wideY1OddsPop = 0
						wideY2OddsPop = 0
						continue
					for index in range(len(wideddsStr)):
						if index == 0:
							wide12Odds = int(wideddsStr[0].replace(',','').strip())
						elif index == 1:
							wide13Odds = int(wideddsStr[1].replace(',','').strip())
						elif index == 2:
							wide23Odds = int(wideddsStr[2].replace(',','').strip())
						elif index == 3:
							if wideddsStr[index].strip() == '':
								break
							wideY1Odds = int(wideddsStr[3].replace(',','').strip())
						elif index == 4:
							if wideddsStr[index].strip() == '':
								break
							wideY2Odds = int(wideddsStr[4].replace(',','').strip())
						else:
							break
			
					wideddsPopStr = InfoValue[i].find_all('td')[2].text.strip()
					if i + 1 < length:
						wideddsPopStr = wideddsPopStr + InfoValue[i + 1].find_all('td')[2].text.strip()
					
					if i + 2 < length:
						wideddsPopStr = wideddsPopStr + InfoValue[i + 2].find_all('td')[2].text.strip()
					
					wideddsPopStr = wideddsPopStr.split('番人気')
					
					for index in range(len(wideddsPopStr)):
						if index == 0:
							wide12OddsPop = int(wideddsPopStr[0].replace(',','').strip())
						elif index == 1:
							wide13OddsPop = int(wideddsPopStr[1].replace(',','').strip())
						elif index == 2:
							wide23OddsPop = int(wideddsPopStr[2].replace(',','').strip())
						elif index == 3:
							if wideddsPopStr[index].strip() == '':
								break
							wideY1OddsPop = int(wideddsPopStr[3].replace(',','').strip())
						elif index == 4:
							if wideddsPopStr[index].strip() == '':
								break
							wideY2OddsPop = int(wideddsPopStr[4].replace(',','').strip())
						else:
							break
					continue
			
				# 3連複オッズとその人気を取得する。
				if '連複' in InfoValue[i].th.string.strip():
					renpukuOddsStr = InfoValue[i].find_all('td')[1].text.strip().split('円')
					for index in range(len(renpukuOddsStr)):
						if index == 0:
							renpukuOdds = int(renpukuOddsStr[0].replace(',','').strip())
						elif index == 1:
							if renpukuOddsStr[index].strip() == '':
								break
							renpukuYOdds = int(renpukuOddsStr[1].replace(',','').strip())
						else:
							break
					renpukuOddsPopStr = InfoValue[i].find_all('td')[2].text.strip().split('番人気')
					for index in range(len(renpukuOddsPopStr)):
						if index == 0:
							renpukuOddsPop = int(renpukuOddsPopStr[0].replace(',','').strip())
						elif index == 1:
							if renpukuOddsPopStr[index].strip() == '':
								break
							renpukuYOddsPop = int(renpukuOddsPopStr[1].replace(',','').strip())
						else:
							break
					continue
				
				# 3連単オッズとその人気を取得する。
				if '連単' in InfoValue[i].th.string.strip():
					rentanOddsStr = InfoValue[i].find_all('td')[1].text.strip().split('円')
					# 結果が空白の場合、処理をスキップする。
					if rentanOddsStr[0].replace(',','').strip() == '':
						rentanOdds = 0
						rentanYOdds = 0
						rentanOddsPop = 0
						rentanYOddsPop = 0
						continue
					
					for index in range(len(rentanOddsStr)):
						if index == 0:
							rentanOdds = int(rentanOddsStr[0].replace(',','').strip())
						elif index == 1:
							if rentanOddsStr[index].strip() == '':
								break
							rentanYOdds = int(rentanOddsStr[1].replace(',','').strip())
						else:
							break
					
					rentanOddsPopStr = InfoValue[i].find_all('td')[2].text.strip().split('番人気')
					for index in range(len(rentanOddsPopStr)):
						if index == 0:
							rentanOddsPop = int(rentanOddsPopStr[0].replace(',','').strip())
						elif index == 1:
							if rentanOddsPopStr[index].strip() == '':
								break
							rentanYOddsPop = int(rentanOddsPopStr[1].replace(',','').strip())
						else:
							break
					continue
					
				if '枠連' in InfoValue[i].th.string.strip():
					wakurenOdds = 0
					wakurenYOdds = 0
					wakurenOddsPop = 0
					wakurenYOddsPop = 0
					continue
						
					wakurenOddsStr = InfoValue[i].find_all('td')[1].text.strip().split('円')
					for index in range(len(wakurenOddsStr)):
						if index == 0:
							wakurenOdds = int(wakurenOddsStr[0].replace(',','').strip())
						elif index == 1:
							if wakurenOddsStr[index].strip() == '':
								break
							wakurenYOdds = int(wakurenOddsStr[1].replace(',','').strip())
						else:
							break
					wakurenOddsPopStr = InfoValue[i].find_all('td')[2].text.strip().split('番人気')
					for index in range(len(wakurenOddsPopStr)):
						if index == 0:
							wakurenOddsPop = int(wakurenOddsPopStr[0].replace(',','').strip())
						elif index == 1:
							if wakurenOddsPopStr[index].strip() == '':
								break
							wakurenYOddsPop = int(wakurenOddsPopStr[1].replace(',','').strip())
						else:
							break
					continue
		
					
		# DBに格納するための辞書を作成する。
		dict_Db_RACE_RESULT_T = {}
		dict_Db_RACE_RESULT_T['LOGIC_DEL_FLG'] = '0'
		dict_Db_RACE_RESULT_T['INS_PID'] = 'RID03'
		dict_Db_RACE_RESULT_T['UPD_PID'] = 'RID03'
		dict_Db_RACE_RESULT_T['RACE_ID'] = race_id
		dict_Db_RACE_RESULT_T['WIN_ODDS'] = winOdds
		dict_Db_RACE_RESULT_T['WIN_ODDS_POP'] = winOddsPop
		if winY1Odds is None:
			dict_Db_RACE_RESULT_T['WIN_Y1_ODDS'] = 0
		else:
			dict_Db_RACE_RESULT_T['WIN_Y1_ODDS'] = winY1Odds
		
		if winY2OddsPop is None:
			dict_Db_RACE_RESULT_T['WIN_Y2_ODDS_POP'] = 0
		else:
			dict_Db_RACE_RESULT_T['WIN_Y2_ODDS_POP'] = winY2OddsPop
		
		if winY3Odds is None:
			dict_Db_RACE_RESULT_T['WIN_Y3_ODDS'] = 0
		else:
			dict_Db_RACE_RESULT_T['WIN_Y3_ODDS'] = winY3Odds
		
		if winY3OddsPop is None:
			dict_Db_RACE_RESULT_T['WIN_Y3_ODDS_POP'] = 0
		else:
			dict_Db_RACE_RESULT_T['WIN_Y3_ODDS_POP'] = winY3OddsPop
			
		dict_Db_RACE_RESULT_T['WINMULTI_1_ODDS'] = winmulti1Odds
		dict_Db_RACE_RESULT_T['WINMULTI_1_ODDS_POP'] = winmulti1OddsPop
		dict_Db_RACE_RESULT_T['WINMULTI_2_ODDS'] = winmulti2Odds
		dict_Db_RACE_RESULT_T['WINMULTI_2_ODDS_POP'] = winmulti2OddsPop
		
		if winmulti3Odds is None:
			dict_Db_RACE_RESULT_T['WINMULTI_3_ODDS'] = 0
		else:
			dict_Db_RACE_RESULT_T['WINMULTI_3_ODDS'] = winmulti3Odds
		
		if winmulti3OddsPop is None:
			dict_Db_RACE_RESULT_T['WINMULTI_3_ODDS_POP'] = 0
		else:
			dict_Db_RACE_RESULT_T['WINMULTI_3_ODDS_POP'] = winmulti3OddsPop
		
		if winmultiYOdds is None:
			dict_Db_RACE_RESULT_T['WINMULTI_Y_ODDS'] = 0
		else:
			dict_Db_RACE_RESULT_T['WINMULTI_Y_ODDS'] = winmultiYOdds
		
		if winmultiYOddsPop is None:
			dict_Db_RACE_RESULT_T['WINMULTI_Y_ODDS_POP'] = 0
		else:
			dict_Db_RACE_RESULT_T['WINMULTI_Y_ODDS_POP'] = winmultiYOddsPop
		
		dict_Db_RACE_RESULT_T['WAKUREN_ODDS'] = wakurenOdds
		dict_Db_RACE_RESULT_T['WAKUREN_ODDS_POP'] = wakurenOddsPop
		
		if wakurenYOdds is None:
			dict_Db_RACE_RESULT_T['WAKUREN_Y_ODDS'] = 0
		else:
			dict_Db_RACE_RESULT_T['WAKUREN_Y_ODDS'] = wakurenYOdds
		
		if wakurenYOddsPop is None:
			dict_Db_RACE_RESULT_T['WAKUREN_Y_ODDS_POP'] = 0
		else:
			dict_Db_RACE_RESULT_T['WAKUREN_Y_ODDS_POP'] = wakurenYOddsPop
		
		dict_Db_RACE_RESULT_T['UMAREN_ODDS'] = umarenOdds
		dict_Db_RACE_RESULT_T['UMAREN_ODDS_POP'] = umarenOddsPop
		
		if umarenYOdds is None:
			dict_Db_RACE_RESULT_T['UMAREN_Y_ODDS'] = 0
		else:
			dict_Db_RACE_RESULT_T['UMAREN_Y_ODDS'] = umarenYOdds
		
		if umarenYOddsPop is None:
			dict_Db_RACE_RESULT_T['UMAREN_Y_ODDS_POP'] = 0
		else:
			dict_Db_RACE_RESULT_T['UMAREN_Y_ODDS_POP'] = umarenYOddsPop
		
		dict_Db_RACE_RESULT_T['UMATAN_ODDS'] = umatanOdds
		dict_Db_RACE_RESULT_T['UMATAN_ODDS_POP'] = umatanOddsPop
		
		if umatanYOdds is None:
			dict_Db_RACE_RESULT_T['UMATAN_Y_ODDS'] = 0
		else:
			dict_Db_RACE_RESULT_T['UMATAN_Y_ODDS'] = umatanYOdds
		
		if umatanYOddsPop is None:
			dict_Db_RACE_RESULT_T['UMATAN_Y_ODDS_POP'] = 0
		else:
			dict_Db_RACE_RESULT_T['UMATAN_Y_ODDS_POP'] = umatanYOddsPop
		
		dict_Db_RACE_RESULT_T['WIDE_12_ODDS'] = wide12Odds
		dict_Db_RACE_RESULT_T['WIDE_12_ODDS_POP'] = wide12OddsPop
		dict_Db_RACE_RESULT_T['WIDE_13_ODDS'] = wide13Odds
		dict_Db_RACE_RESULT_T['WIDE_13_ODDS_POP'] = wide13OddsPop
		dict_Db_RACE_RESULT_T['WIDE_23_ODDS'] = wide23Odds
		dict_Db_RACE_RESULT_T['WIDE_23_ODDS_POP'] = wide23OddsPop
		
		if wideY1Odds is None:
			dict_Db_RACE_RESULT_T['WIDE_Y1_ODDS'] = 0
		else:
			dict_Db_RACE_RESULT_T['WIDE_Y1_ODDS'] = wideY1Odds
		
		if wideY1OddsPop is None:
			dict_Db_RACE_RESULT_T['WIDE_Y1_ODDS_POP'] = 0
		else:
			dict_Db_RACE_RESULT_T['WIDE_Y1_ODDS_POP'] = wideY1OddsPop
		
		if wideY2Odds is None:
			dict_Db_RACE_RESULT_T['WIDE_Y2_ODDS'] = 0
		else:
			dict_Db_RACE_RESULT_T['WIDE_Y2_ODDS'] = wideY2Odds
		
		if wideY2OddsPop is None:
			dict_Db_RACE_RESULT_T['WIDE_Y2_ODDS_POP'] = 0
		else:
			dict_Db_RACE_RESULT_T['WIDE_Y2_ODDS_POP'] = wideY2OddsPop
		
		dict_Db_RACE_RESULT_T['RENPUKU_ODDS'] = renpukuOdds
		dict_Db_RACE_RESULT_T['RENPUKU_ODDS_POP'] = renpukuOddsPop
		
		if renpukuYOdds is None:
			dict_Db_RACE_RESULT_T['RENPUKU_Y_ODDS'] = 0
		else:
			dict_Db_RACE_RESULT_T['RENPUKU_Y_ODDS'] = renpukuYOdds
		
		if renpukuYOddsPop is None:
			dict_Db_RACE_RESULT_T['RENPUKU_Y_ODDS_POP'] = 0
		else:
			dict_Db_RACE_RESULT_T['RENPUKU_Y_ODDS_POP'] = renpukuYOddsPop
		
		dict_Db_RACE_RESULT_T['RENTAN_ODDS'] = rentanOdds
		dict_Db_RACE_RESULT_T['RENTAN_ODDS_POP'] = rentanOddsPop
		
		if rentanYOdds is None:
			dict_Db_RACE_RESULT_T['RENTAN_Y_ODDS'] = 0
		else:
			dict_Db_RACE_RESULT_T['RENTAN_Y_ODDS'] = rentanYOdds
		
		if rentanYOddsPop is None:
			dict_Db_RACE_RESULT_T['RENTAN_Y_ODDS_POP'] = 0
		else:
			dict_Db_RACE_RESULT_T['RENTAN_Y_ODDS_POP'] = rentanYOddsPop
		# DBにアクセスする処理
		self.daoClass.insert('RACE_RESULT_T',dict_Db_RACE_RESULT_T)

		#########################後処理
		#########################
		# メソッド終了ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,1)



	##################################################################
	###### 引数1:html情報
	###### 引数2:RACE_ID
	###### 概要:引数で取得したhtml情報をもとにスクレイピングする
	###### 
	##################################################################
	def race_param_t(self,soup,race_id):
		#########################前処理
		#########################
		# メソッド名取得
		methodname = sys._getframe().f_code.co_name
		# メソッド開始ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,0)

		race_no = race_id[15:17]
		race_id = race_id[0:15]
		link = None


		#########################主処理
		#########################
		# race_no が1 の場合は1レース以外の全てを処理する。
		# race_no が2 の場合は1レースのみを処理する.
		# race_no が1,2以外の場合処理しない
		if not (int(race_no) == 1 or int(race_no) == 2):
			self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,1)
			return
		raceList = soup.find('div',{'class':'raceSelect'})
		raceList = raceList.find_all('a')
		for tags in raceList:

			race_str = tags.find('img').attrs['alt']
			link = tags['onclick'].strip().replace("return doAction('/JRADB/accessS.html','",'')[:-3]
			if '1レース' == race_str:
				race_id = race_id + '01'
			elif '2レース' == race_str:
				race_id = race_id + '02'
				
			elif '3レース' == race_str:
				race_id = race_id + '03'

			elif '4レース' == race_str:
				race_id = race_id + '04'

			elif '5レース' == race_str:
				race_id = race_id + '05'

			elif '6レース' == race_str:
				race_id = race_id + '06'

			elif '7レース' == race_str:
				race_id = race_id + '07'

			elif '8レース' == race_str:
				race_id = race_id + '08'

			elif '9レース' == race_str:
				race_id = race_id + '09'


			elif '10レース' == race_str:
				race_id = race_id + '10'

			elif '11レース' == race_str:
				race_id = race_id + '11'
			elif '12レース' == race_str:
				race_id = race_id + '12'


			# DBinsert
			insert_dict = {}
			insert_dict['LOGIC_DEL_FLG'] = 0
			insert_dict['INS_PID'] = 'RID04'
			insert_dict['UPD_PID'] = 'RID04'
			insert_dict['RACE_ID'] = race_id	
			insert_dict['INFO_LINK'] = link
			self.daoClass.insert('RACE_PARAM_T',insert_dict)

			race_id = race_id[0:15]
			
			if int(race_no) == 2:
				break

		#########################終処理
		#########################
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,1) 


