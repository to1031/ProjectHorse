# coding: utf-8

import sys
import datetime
import os

class RaceAnalyze(object):
	# 初期化処理
	def __init__(self,dict):
		# 環境変数を取得する。
		self.homeDir = os.environ["APPHORSE"]

		# iniconfigファイルを読み出す。
		self.inifile = dict['util'].inifile

		# 当サービスの機能IDを取得する。
		self.pid = 'RaceAnalyze'

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



	def raceAnalyze(self,form_date,to_date):
		# メソッド名取得
		methodname = sys._getframe().f_code.co_name
		# 開始ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,0)
	
		# 天気・馬場状態マスタテーブルより速度を取得する。
		dict_wheatherGet = {}
		wheatherGet = self.daoClass.selectQuery('','wheatherM')
		for dictFactor in wheatherGet:
			dict_wheatherGet[dictFactor[0] + '0'] = dictFactor[1]
			dict_wheatherGet[dictFactor[0] + '1'] = dictFactor[2]
			
			
		# 計算マスタより取得する値を格納する辞書
		dict_basisTime = {} # 初期化
		dict_aveTime = {} # 初期化
		
		# 1日変化するごとに指数計算基準タイムを取得するために基準日を保持する。
		raceDateForBacisTome = '' # 初期化
		
		targetRaceIdListGetSql = ["AND RACE_DATE > '%s' AND RACE_DATE < '%s' AND LOGIC_DEL_FLG != '1'" % (form_date,to_date)]
		targetRaceIdList = self.daoClass.selectQuery(targetRaceIdListGetSql,'allRaceIdForWeightForAnalyze')

		# 対象となるレース毎に処理を進める。
		# 処理対象のRACE_ID毎に処理を進める。
		for raceTInfo in targetRaceIdList:

			# RACE_IDとRACE_DATEを取得する。
			targetRaceId = raceTInfo[0]
			targetRaceDate = raceTInfo[1]
			targetRacePlace = raceTInfo[2]
			targetRaceRange = raceTInfo[3]
			targetRaceGlound = raceTInfo[4]
			targetRaceCond = targetRacePlace + targetRaceRange + targetRaceGlound
			
			# 更新フラグの宣言と初期化
			upDateFlg = 0
			
			# レースIDがすでにRACE_ANALYZE_T に格納されている場合か確認する。
			sqlCountSql = ["WHERE RACE_ID = '%s'" % targetRaceId]
			sqlCount = self.daoClass.selectQuery(sqlCountSql,'raceAnalyzeCount')

			# 取得結果が 0 以外の場合は更新フラグを立てる。
			if sqlCount[0][0] != 0:
				upDateFlg = 1
				
			if upDateFlg == 1:
				self.utilClass.logging(targetRaceId + 'is analyzed already',2)
				continue
			
			# 1日でも変化していたら指数基準タイムを取得し直す。
			if raceDateForBacisTome != targetRaceDate:
				raceDateForBacisTome = targetRaceDate
				resultListForBasicIndex = []
				resultListForBasicIndex = self.getMast(targetRaceDate)
				dict_basisTime = resultListForBasicIndex[0]
				dict_aveTime = resultListForBasicIndex[1]
				dict_upAveTime = resultListForBasicIndex[2]
		
			# RACE_DETAIL_Tより馬名を取得する。
			sqlForUmabanAndUmamei = ["WHERE RACE_ID = '%s'"% targetRaceId]
			getUmabanAndUmamei = self.daoClass.selectQuery(sqlForUmabanAndUmamei,'sqlForUmabanAndUmamei')

			# 取得した馬:騎手毎にDBに格納する値を確定させ、DBに挿入する。
			for receDetailInfo in getUmabanAndUmamei:
				# DB格納用の辞書を初期化
				dict_RACE_ANALYZE_T = {}			
				
				# 馬名を取得する。
				horseName = receDetailInfo[1]
				
				# 機種名を取得する。
				jocName = receDetailInfo[4]
				
				# 馬番を取得する。
				startNum = receDetailInfo[0]
				
				# 負担重量を取得する。
				load_w = int(receDetailInfo[5])
				
				# ゴールが中止の場合は挿入はしない。
				if '中' in receDetailInfo[6] or '取' in receDetailInfo[6] or '除' in receDetailInfo[6]:
					continue
				
				newInfoGet = [
							"WHERE RACE_T.RACE_SHOGAI_FLG != '1'",
							"AND RACE_T.RACE_DATE <= '%s'"% targetRaceDate,
							"AND RACE_DETAIL_T.HORCE_NAME = '%s'" % horseName,
							#"AND RACE_DETAIL_T.GOAL_NUM != '中止'",
							" ORDER BY CAST(RACE_T.RACE_DATE AS DATE) DESC LIMIT 2"
							]
				raceIdList = self.daoClass.selectQuery(newInfoGet,'newInfoGet')
				if len(raceIdList) == 0:
					continue
				
				# DB格納値の変数を初期化する。
				NumOfRest = 0 # 前回レースとの空き期間（日数）
				speedIndex = 0 # スピード指数
				uptimeIndex = 0 #　3ハロンタイム指数
				basicSpeedIndex = 0 # スピード指数
				basicUpTimeIndex = 0 # 3ハロンタイム
				
				# レース条件を取得する。
				raceId = raceIdList[0][0]
				racePlace = raceIdList[0][3]
				raceRange = raceIdList[0][1]
				raceGroundFlg = raceIdList[0][2]
				raceCondition = raceIdList[0][4]
				printRaceDate = raceIdList[0][6]
				raceweather = raceIdList[0][5]
				raceCond = racePlace + raceRange + raceGroundFlg
				radeCond_weather = raceweather + raceCondition + raceGroundFlg
				
				
				# 前回レース出走日付を取得する。
	
				
				# 変数初期化
				aveTime = 0
				intrestDays = 0
				
				# 過去のレースからの空き日数を取得する。
				if len(raceIdList) == 1:
					NumOfRest = 0
				else:
					raceDateForIndex = raceIdList[1][6]		
					NumOfRest = datetime.date( int(targetRaceDate[0:4]), int(targetRaceDate[4:6]), int(targetRaceDate[6:8])) - datetime.date( int(raceDateForIndex[0:4]), int(raceDateForIndex[4:6]), int(raceDateForIndex[6:8]))
					NumOfRest = NumOfRest.days
					
				# でばっぐ
				
				# レース条件から基準タイムを取得する。
				if raceCond in dict_basisTime:
					aveindextime = dict_basisTime[raceCond]
				else:
					# 基準タイムがないレースであるのでスキップする。
					race_t_update = {}
					race_t_update['LOGIC_DEL_FLG'] = '1'
					where = "WHERE RACE_ID = '%s'" % raceId
					self.daoClass.update('RACE_T',race_t_update,where)
					continue
				
				# レース条件から平均タイムを取得する。
				if raceCond in dict_aveTime:
					aveTime = dict_aveTime[raceCond]
				else:
					# 基準タイムがないレースであるのでスキップする。
					race_t_update = {}
					race_t_update['LOGIC_DEL_FLG'] = '1'
					where = "WHERE RACE_ID = '%s'" % raceId
					self.daoClass.update('RACE_T',race_t_update,where)
					continue
				
				# 天気・馬場により速度指数を取得
				disWeather = 0 # 初期化
				disWeather = dict_wheatherGet[radeCond_weather]
				
				# 平均タイムから秒速を求める。
				merter_per_sec = int(raceRange) / aveTime
				
				# 秒速に速度指数をプラスし、その時のレース所要時間を算出する。
				dis_merter_per_sec = merter_per_sec + disWeather
				image_costTime = int(raceRange) / dis_merter_per_sec
				
				# 実際の所要時間と想定所要時間との差を求めて馬場指数を取得する。
				babaindex = (image_costTime - aveTime) * 10
				
				# 走破タイムを取得する
				goulTimeindex = 0 # 初期化
				goulTimeindex = float(str(raceIdList[0][7].seconds) + '.' + str(raceIdList[0][7].microseconds)) * 10
					
				# スピード指数＝ (基準タイム－走破タイム + 馬場指数)×距離指数＋(斤量－５５)×２＋８０　西田式
				speedIndex = 0 # 初期化
				speedIndex = (aveindextime - goulTimeindex + babaindex)*(1 / aveindextime * 1000) + (raceIdList[0][8] - 55) * 2 + 80
	
				
				# 上がり3ハロンタイムを取得する。
				upTime = int(raceIdList[0][11][0:2])*10 + int(raceIdList[0][11][3:])
				
				# アップタイムの平均を取得する。
				uoAveTime = 0
				indexUpTime = 0
				uoAveTime = dict_upAveTime[raceCond]
				basicIndexUpTime = uoAveTime * 10
				
				# 上がりタイムの指数取得を行う。上がり3Fとは600mの秒数である。
				# 平均タイムから秒速を求める。
				merter_per_sec = 600 / uoAveTime
				
				# 秒速に速度指数をプラスし、その時のレース所要時間を算出する。
				dis_merter_per_sec = merter_per_sec + disWeather
				image_costTime = 600 / dis_merter_per_sec
				
				# 実際の所要時間と想定所要時間との差を求めて馬場指数を取得する。
				babaindexForUpTime = (image_costTime - uoAveTime)
			
				
				# 指数を取得する。
				uptimeIndex = basicIndexUpTime - upTime + babaindex + (raceIdList[0][8] - 55) * 1.5 + 20
				
				
				# 指数算出にしようした基準タイムを取得する。
				basicSpeedIndex = aveindextime
				
				# 指数算出にしようした基準タイムを取得する。
				basicUpTimeIndex = basicIndexUpTime
				
				#　更新フラグ1の場合はDBを更新する。それ以外の場合は挿入する。
				if upDateFlg == 1:
					where = "WHERE RACE_ID = '%s' AND HORCE_NAME = '%s'"%(raceId,horseName)
					dict_RACE_ANALYZE_T = {}
					dict_RACE_ANALYZE_T['SPEED_INDEX'] = speedIndex
					dict_RACE_ANALYZE_T['UPTIME_INDEX'] = uptimeIndex
					dict_RACE_ANALYZE_T['BASIC_TIME'] = basicSpeedIndex
					dict_RACE_ANALYZE_T['BACIC_UPTIME'] = basicUpTimeIndex
					dict_RACE_ANALYZE_T['REST_DAYS'] = NumOfRest
					self.daoClass.update('RACE_ANALYZE_T',dict_RACE_ANALYZE_T,where)
				else:
					# DBに格納する。
					dict_RACE_ANALYZE_T['LOGIC_DEL_FLG'] = '0'
					dict_RACE_ANALYZE_T['INS_PID'] = 'D0001'
					dict_RACE_ANALYZE_T['UPD_PID'] = 'D0001'
					dict_RACE_ANALYZE_T['RACE_ID'] = targetRaceId
					dict_RACE_ANALYZE_T['HORCE_NAME'] = horseName
					dict_RACE_ANALYZE_T['START_NUM'] = startNum
					dict_RACE_ANALYZE_T['SPEED_INDEX'] = speedIndex
					dict_RACE_ANALYZE_T['UPTIME_INDEX'] = uptimeIndex
					dict_RACE_ANALYZE_T['BASIC_TIME'] = basicSpeedIndex
					dict_RACE_ANALYZE_T['BACIC_UPTIME'] = basicUpTimeIndex
					dict_RACE_ANALYZE_T['REST_DAYS'] = NumOfRest
					self.daoClass.insert('RACE_ANALYZE_T',dict_RACE_ANALYZE_T)

			self.utilClass.logging(targetRaceId + 'is done',2)

		# 終了ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,1)



	def getMast(self,date):
		# 年毎に処理を行う。
		bacisDate = date
			
		# 競馬場、距離、馬場によって指数計算マスタを作成する。
		# 馬の過去レース結果から走破指数を取得する。
		racePlace = None
		raceRange = None
		raceGroundFlg = None
		raceCondQ = ["group by RACE_PLACE,RACE_RANGE,RACE_GROUND_FLG"]
		raceCondList = self.daoClass.selectQuery(raceCondQ,'raceCondList')		

		# dict初期化
		dict_basisTime = {}
		dict_aveTime = {}
		dict_upAveTime = {}
		
		dict_return = []
		for raceCond in raceCondList:
	
			# レース条件を取得する。
			racePlace = raceCond[0]
			raceRange = raceCond[1]
			raceGroundFlg = raceCond[2]
			
			race_Cond = racePlace + raceRange + raceGroundFlg
	
			# 基準タイムを取得する。(レースグレードを
			basistimeget = ["WHERE RACE_T.RACE_PLACE = '%s'"% racePlace,"AND RACE_DETAIL_T.GOAL_NUM IN ('1','2','3')",
										"AND RACE_T.RACE_RANGE = '%s'"% raceRange,"AND RACE_T.RACE_GROUND_FLG = '%s'"% raceGroundFlg,
										"AND RACE_T.RACE_DATE < '%s'"% bacisDate,
										"AND RACE_DETAIL_T.UP_TIME != '-'",
										"AND RACE_T.RACE_SHOGAI_FLG != '1'",
										"AND RACE_T.RACE_COND_MONEY IN ('05','04','')",
										"AND RACE_T.RACE_GLADE = '4'"
										"AND RACE_T.RACE_CONDITION = '01'"
										" ORDER BY CAST(RACE_T.RACE_DATE AS DATE) DESC LIMIT 100"
										]
			basisTimeList = self.daoClass.selectQuery(basistimeget,'basistimeget')

			if len(basisTimeList) < 10:
				continue
				
			# 基準タイム指数の平均値をとる。
			aveindextime = 0
			aveTime = 0
			upAveTime = 0
			for time in basisTimeList:
				# 暫定対応
				aveindextime = aveindextime + float(str(time[0].seconds) + '.' + str(time[0].microseconds))
				aveTime = aveTime + float(str(time[0].seconds) + '.' + str(time[0].microseconds))
				upAveTime = upAveTime + float(time[4][0:2] + '.' + time[4][3:])
				
			aveindextime = aveindextime / len(basisTimeList) * 10
			aveTime = aveTime / len(basisTimeList)
			upAveTime = upAveTime / len(basisTimeList)
				
			# レースの平均前半timeを取得する。
			aveHalfTime = 0
			for time in basisTimeList:
				aveHalfTime = aveHalfTime + float(str(time[2].seconds) + '.' + str(time[2].microseconds))
				
			aveHalfTime = aveHalfTime / len(basisTimeList)
			
			dict_basisTime[race_Cond] = aveindextime
			dict_aveTime[race_Cond] = aveTime
			dict_upAveTime[race_Cond] = upAveTime
		
		# 辞書を返す。
		dict_return.append(dict_basisTime)
		dict_return.append(dict_aveTime)
		dict_return.append(dict_upAveTime)
		return dict_return
