# coding: utf-8
# 指数計算を行い、指数と関連情報をDATA_MINING_Tに格納する処理


################ 変更履歴 ######################
## 2017/05/05 作成

###############################################

import itertools
import datetime
import math
from datetime import timedelta
import sys
import os
import numpy as np

class PostRaceForecast(object):
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



	##################################################################
	###### 引数1:html情報
	###### 概要:引数で取得したhtml情報をもとにスクレイピングする
	###### 
	##################################################################
	def postRaceForecast(self):
		# 当メソッドの名前を取得する。
		methodname = sys._getframe().f_code.co_name

		# 処理開始ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,0)

		# 終了コード
		returnCode = 0

		try:
			beforeday = self.getForecast()

			self.updateHorseIndex(beforeday)

			self.updateJocIndex(beforeday)

			self.updatelast(beforeday)

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
	###### 引数なし
	###### 戻り値:計算対象年月日
	###### 概要:レースの予想レース指数を出す
	###### 
	##################################################################

	def getForecast(self):
		# メソッド名取得
		methodname = sys._getframe().f_code.co_name
                # メソッド開始ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,0)

		
		#　本日の日付を取得する。
		today_date = datetime.datetime.today()
		beforeDay = today_date + timedelta(days=-8)
		beforeDay = beforeDay.strftime('%Y%m%d')



		# 全ての障害及び新馬戦以外の全てのレース結果を取得する。
		getTargetRaceId = ["AND RACE_COND_MONEY != '01' AND RACE_DATE >= '%s'"% beforeDay] #本物はこっち。　
		allRaceIdList = self.daoClass.selectQuery(getTargetRaceId,'selectPostRace')

		self.utilClass.logging('target day is from ' + beforeDay ,2)

		
		# 処理対象のRACE_ID毎に処理を進める。
		for raceTInfo in allRaceIdList:
			# RACE_IDとRACE_DATEを取得する。
			targetRaceId = raceTInfo[0]
			targetRaceDate = raceTInfo[1]
			targetRacePlace = raceTInfo[2]
			targetRaceRange = raceTInfo[3]
			targetRaceGlound = raceTInfo[4]
			targetRaceCond = targetRacePlace + targetRaceRange + targetRaceGlound
			
			# RACE_DETAIL_Tより馬名
			sqlForUmabanAndUmameiPostDetail = ["WHERE RACE_ID = '%s'"% targetRaceId]
			getUmabanAndUmamei = self.daoClass.selectQuery(sqlForUmabanAndUmameiPostDetail,'sqlForUmabanAndUmameiPostDetail')
			# updateか判断する。
			updateLogic = ["WHERE RACE_ID = '%s'"% targetRaceId]
			updateLogic = self.daoClass.selectQuery(updateLogic,'updateLogic')
			if updateLogic[0][0] > 0:
				continue

			self.utilClass.logging('target raceis from ' + targetRaceId ,2)
			
			# 取得した馬:騎手毎にDBに格納する値を確定させ、DBに挿入する。
			for receDetailInfo in getUmabanAndUmamei:
				
				
				# DB格納用の辞書を初期化
				dict_POST_RACE_FORCAST_T = {}			
				
				# 馬名を取得する。
				horseName = receDetailInfo[1]
				
				# 機種名を取得する。
				jocName = receDetailInfo[4]
	
				# 馬番を取得する。
				startNum = receDetailInfo[0]

				self.utilClass.logging('target is' + startNum + ':' + jocName + ':' + horseName ,2)				

				# 負担重量を取得する。
				load_w = int(receDetailInfo[5])
				
				# 前回体重差と当時体重を取得する。
				# 未取得の場合は０を投入する。
				if '未取得' in receDetailInfo[3]:
					horseWeight = 0
				else:
					horseWeight = int(receDetailInfo[3])
				horseWeightDis = receDetailInfo[2]
				
				# horseWeightDisが文字列なのでマイニングする。
				# 未取得の場合は処理しない。
				if '+' in horseWeightDis:
					horseWeightDis = int(horseWeightDis[1:])
				elif '-' in horseWeightDis:
					horseWeightDis = int(horseWeightDis[1:]) * (-1)
				else:
					horseWeightDis = 0
				
				# 馬の過去レース結果から走破指数を取得する。
				getIndexSql = ["WHERE RACE_T.RACE_DATE < '%s'"% targetRaceDate,
								"AND RACE_T.RACE_SHOGAI_FLG != '1'",
								"AND RACE_DETAIL_T.HORCE_NAME = '%s'"% horseName,
								"ORDER BY CAST(RACE_T.RACE_DATE AS DATE) DESC LIMIT 7"
								]
				raceIdList = self.daoClass.selectQuery(getIndexSql,'getIndexSql')
				# DB格納値の変数を初期化する。
				dict_POST_RACE_FORCAST_T = {}
				forcast_index = 0
				ave_speedindex_2th = 0
				pre_speed_index = 0
				pre2_speed_index = 0
				pre3_speed_index = 0
				pre4_speed_index = 0
				samecond_speed_index_ave = 0
				samecond_speed_index_max = 0
				speed_index_max = 0
				ave_uptimeindex_2th = 0
				pre_uptime_index = 0
				pre2_uptime_index = 0
				pre3_uptime_index = 0
				pre4_uptime_index = 0
				samecond_uptime_index_ave = 0
				samecond_uptime_index_max = 0
				uptime_index_max = 0
				uptime_index_max = 0
				forcat_runstyle = 0
				rest_days = 0
				remark_memo = ''
				
				# ループない値保存用リスト初期化
				speedIndexList = []
				sameCondSpeedIndexList = []
				upTimeIndexList = []
				sameCondupTimeIndexList = []
				runStyleList = []	
				
				# 最初のレースのみ休養期間を取得するためにループの回数の変数を準備する。
				NumOfRestForIndex = 0
				
				# 同条件取得用の変数を準備
				raceCount = 0
				
				# 馬に紐づくレース情報リストをループしデータマイニングする。
	
				for raceid in raceIdList:
					# レースカウントをインクリメントする。
					raceCount = raceCount + 1
					
					# ループ内での変数初期化処理
					raceId = 0
					racePlace = 0
					raceRange = 0
					raceGroundFlg = 0
					raceCondition = 0
					raceweather = 0
					raceDateForIndex = 0
					raceCond = 0
					radeCond_weather = 0
					speedIndex = 0
					upTimeIndex = 0
					runStyle = ''
					
					# レース条件を取得する。
					raceId = raceid[0]
					racePlace = raceid[3]
					raceRange = raceid[1]
					raceGroundFlg = raceid[2]
					raceCondition = raceid[4]
					raceweather = raceid[5]
					raceDateForIndex = raceid[6]
					raceCond = racePlace + raceRange + raceGroundFlg
					radeCond_weather = raceweather + raceCondition + raceGroundFlg
					speedIndex = raceid[7]
					upTimeIndex = raceid[8]
					runStyle = raceid[9]
					
					# 変数初期化
					aveTime = 0
					intrestDays = 0
					
					# 最初のレースのみ休養期間を取得するためにループの回数をインクリメントする。
					NumOfRestForIndex = NumOfRestForIndex + 1
					
					# 過去のレースからの空き日数を取得する。
					if NumOfRestForIndex == 1:
						NumOfRest = datetime.date( int(targetRaceDate[0:4]), int(targetRaceDate[4:6]), int(targetRaceDate[6:8])) - datetime.date( int(raceDateForIndex[0:4]), int(raceDateForIndex[4:6]), int(raceDateForIndex[6:8]))
						rest_days = NumOfRest.days
					
					# スピード指数の取得処理 #################################################################
					mainusPoint = 0
					if math.fabs(int(raceRange) - int(targetRaceRange)) > 249:
						mainusPoint = mainusPoint + math.fabs(int(raceRange) - int(targetRaceRange)) / 50
					if targetRaceGlound != raceGroundFlg:
						mainusPoint = mainusPoint + 13
					
					speedIndex = speedIndex - mainusPoint
					speedIndexList.append(speedIndex)
					upTimeIndexList.append(upTimeIndex)
					
					if math.fabs(int(raceRange) - int(targetRaceRange)) < 151 and targetRaceGlound == raceGroundFlg:
						if raceCount < 6:
							sameCondSpeedIndexList.append(speedIndex)
							sameCondupTimeIndexList.append(upTimeIndex)
					
					# マイナスした場合はメモを残す。
					if mainusPoint != 0 :
						remark_memo = remark_memo + str(NumOfRestForIndex) + ','
					
					# スピード指数の取得処理 #################################################################
					
					
					# 脚質を取得する。
					if raceCount < 6:
						runStyleList.append(runStyle)
				
				# ループから抜けたので、指数や着順の値を取得する。
				# 上げり3ハロン指数。#########################################################################
				for info in sameCondupTimeIndexList:
					samecond_uptime_index_ave = samecond_uptime_index_ave + info
					if info > samecond_uptime_index_max:
						samecond_uptime_index_max = info
				
				if len(sameCondSpeedIndexList) != 0:
					samecond_uptime_index_ave = samecond_uptime_index_ave / len(sameCondupTimeIndexList)
				
				# 上げり3ハロン指数を取得する。
				if len(upTimeIndexList) == 1:
					pre_uptime_index = upTimeIndexList[0]
					ave_uptimeindex_2th = upTimeIndexList[0]
				elif len(upTimeIndexList) == 2:
					pre_uptime_index = upTimeIndexList[0]
					pre2_uptime_index = upTimeIndexList[1]
					ave_uptimeindex_2th = (pre_uptime_index + pre2_uptime_index) / 2
				elif len(upTimeIndexList) == 3:
					pre_uptime_index = upTimeIndexList[0]
					pre2_uptime_index = upTimeIndexList[1]
					pre3_uptime_index = upTimeIndexList[2]
					ave_uptimeindex_2th = (pre_uptime_index + pre2_uptime_index) / 2	
				elif len(upTimeIndexList) > 3:
					pre_uptime_index = upTimeIndexList[0]
					pre2_uptime_index = upTimeIndexList[1]
					pre3_uptime_index = upTimeIndexList[2]
					pre4_uptime_index = upTimeIndexList[3]
					ave_uptimeindex_2th = (pre_uptime_index + pre2_uptime_index) / 2

				# 上げり3ハロン指数の最大値を取得する。
				maxList =[]
				maxList.append(pre_uptime_index)
				maxList.append(pre2_uptime_index)
				maxList.append(pre3_uptime_index)
				maxList.append(pre4_uptime_index)
				maxList.sort()
				maxList.reverse()
				uptime_index_max = maxList[0]
				#############################################################################################
				
				# スピード指数を取得する。#########################################################################
				for info in sameCondSpeedIndexList:
					samecond_speed_index_ave = samecond_speed_index_ave + info
					if info > samecond_speed_index_max:
						samecond_speed_index_max = info
				
				if len(sameCondSpeedIndexList) != 0:
					samecond_speed_index_ave = samecond_speed_index_ave / len(sameCondSpeedIndexList)
				
				# 同じ条件のレース指数を取得する。
				if len(speedIndexList) == 1:
					pre_speed_index = speedIndexList[0]
					ave_speedindex_2th = speedIndexList[0]
				elif len(speedIndexList) == 2:
					pre_speed_index = speedIndexList[0]
					pre2_speed_index = speedIndexList[1]
					ave_speedindex_2th = (pre_speed_index + pre2_speed_index) / 2
				elif len(speedIndexList) == 3:
					pre_speed_index = speedIndexList[0]
					pre2_speed_index = speedIndexList[1]
					pre3_speed_index = speedIndexList[2]
					ave_speedindex_2th = (pre_speed_index + pre2_speed_index) / 2	
				elif len(speedIndexList) > 3:
					pre_speed_index = speedIndexList[0]
					pre2_speed_index = speedIndexList[1]
					pre3_speed_index = speedIndexList[2]
					pre4_speed_index = speedIndexList[3]
					ave_speedindex_2th = (pre_speed_index + pre2_speed_index) / 2
				
				# スピード指数の最大値を取得する。
				maxList =[]
				maxList.append(pre_speed_index)
				maxList.append(pre2_speed_index)
				maxList.append(pre3_speed_index)
				maxList.append(pre4_speed_index)
				maxList.sort()
				maxList.reverse()
				speed_index_max = maxList[0]
				############################################################################################
				# メモの処理
				if remark_memo != '':
					remark_memo = remark_memo[:-1]
				
				
				####脚質を予想する。#############################################################################
				nigeCount = 0
				senkoCount = 0
				sashiCount = 0
				oiCount = 0
				for info in runStyleList:
					if info == '01':
						nigeCount = nigeCount + 1
					if info == '02':
						senkoCount = senkoCount + 1
					if info == '03':
						sashiCount = sashiCount + 1
					if info == '04':
						oiCount = oiCount + 1
						
				runStyleSortList = []
				runStyleSortList.append(nigeCount)
				runStyleSortList.append(senkoCount)
				runStyleSortList.append(sashiCount)
				runStyleSortList.append(oiCount)
				
				runStyleSortList.sort()
				runStyleSortList.reverse()
				
				if runStyleSortList[0] == nigeCount:
					if nigeCount == 0:
						forcat_runstyle = '00'
					forcat_runstyle = '01'
				elif runStyleSortList[0] == senkoCount:
					forcat_runstyle = '02'
				elif runStyleSortList[0] == sashiCount:
					forcat_runstyle = '03'
				elif runStyleSortList[0] == oiCount:
					forcat_runstyle = '04'
				
					
				####脚質を予想する。#############################################################################
				# DBに格納する。
				dict_POST_RACE_FORCAST_T['LOGIC_DEL_FLG'] = '0'
				dict_POST_RACE_FORCAST_T['INS_PID'] = 'D0001'
				dict_POST_RACE_FORCAST_T['UPD_PID'] = 'D0001'
				dict_POST_RACE_FORCAST_T['RACE_ID'] = targetRaceId
				dict_POST_RACE_FORCAST_T['HORCE_NAME'] = horseName
				dict_POST_RACE_FORCAST_T['JOCKER_NAME'] = jocName
				dict_POST_RACE_FORCAST_T['START_NUM'] = int(startNum)
				dict_POST_RACE_FORCAST_T['FORCAST_INDEX'] = forcast_index
				dict_POST_RACE_FORCAST_T['AVE_SPEEDINDEX_2TH'] = ave_speedindex_2th
				dict_POST_RACE_FORCAST_T['PRE_SPEED_INDEX'] = pre_speed_index
				dict_POST_RACE_FORCAST_T['PRE2_SPEED_INDEX'] = pre2_speed_index
				dict_POST_RACE_FORCAST_T['PRE3_SPEED_INDEX'] = pre3_speed_index
				dict_POST_RACE_FORCAST_T['PRE4_SPEED_INDEX'] = pre4_speed_index
				dict_POST_RACE_FORCAST_T['SAMECOND_SPEED_INDEX_AVE'] = samecond_speed_index_ave
				dict_POST_RACE_FORCAST_T['SAMECOND_SPEED_INDEX_MAX'] = samecond_speed_index_max
				dict_POST_RACE_FORCAST_T['SPEED_INDEX_MAX'] = speed_index_max
				dict_POST_RACE_FORCAST_T['AVE_UPTIMEINDEX_2TH'] = ave_uptimeindex_2th
				dict_POST_RACE_FORCAST_T['PRE_UPTIME_INDEX'] = pre_uptime_index
				dict_POST_RACE_FORCAST_T['PRE2_UPTIME_INDEX'] = pre2_uptime_index
				dict_POST_RACE_FORCAST_T['PRE3_UPTIME_INDEX'] = pre3_uptime_index
				dict_POST_RACE_FORCAST_T['PRE4_UPTIME_INDEX'] = pre4_uptime_index
				dict_POST_RACE_FORCAST_T['SAMECOND_UPTIME_INDEX_AVE'] = samecond_uptime_index_ave
				dict_POST_RACE_FORCAST_T['SAMECOND_UPTIME_INDEX_MAX'] = samecond_uptime_index_max
				dict_POST_RACE_FORCAST_T['UPTIME_INDEX_MAX'] = uptime_index_max
				dict_POST_RACE_FORCAST_T['FORCAST_RUNSTYLE'] = forcat_runstyle
				dict_POST_RACE_FORCAST_T['REST_DAYS'] = rest_days
				dict_POST_RACE_FORCAST_T['REMARK_MEMO'] = remark_memo
				
				self.daoClass.insert('POST_RACE_FORCAST_T',dict_POST_RACE_FORCAST_T)
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,1)
		return beforeDay



	##################################################################
	###### 引数:対象年月日
	###### 戻り値:なし
	###### 概要:引数で取得した対象年月日以上のデータを処理する
	###### 各指数の相対評価を行う
	##################################################################
	def updateHorseIndex(self,stanDate):
		# メソッドの名
		methodname = sys._getframe().f_code.co_name
		# メソッド開始ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,0)

		# 全ての障害及び新馬戦以外の全てのレース結果を取得する。　
		where = ["WHERE SUBSTRING(RACE_ID,6,8) > '%s'"% stanDate]
		allRaceIdList = self.daoClass.selectQuery(where,'post_forcastRaceId')
		# 処理対象のRACE_ID毎に処理を進める。
		for raceTInfo in allRaceIdList:
			# RACE_IDを取得する。
			targetRaceId = raceTInfo[0]
			
			
			# RACE_DETAIL_Tより馬名
			sqlForUmabanAndUmameiPostDetail = ["WHERE POST_RACE_FORCAST_T.RACE_ID = '%s'"% targetRaceId]
			getUmabanAndUmamei = self.daoClass.selectQuery(sqlForUmabanAndUmameiPostDetail,'post_updateForcast')
			# DB格納用の辞書を生成する。
			AVE_SPEEDINDEX_2TH_DICT = {}
			PRE_SPEED_INDEX_MAX = {}
			AVE_UPTIMEINDEX_SAMECOND_AVE = {}
			PRE_UPTIME_INDEX_MAX_DICT = {}
			
			# 取得した情報毎に処理する。
			for receDetailInfo in getUmabanAndUmamei:
				# 各辞書を格納していく。
				if receDetailInfo[1] != 0:
					AVE_SPEEDINDEX_2TH_DICT[receDetailInfo[0]] = receDetailInfo[1]
				if receDetailInfo[10] != 0:
					AVE_UPTIMEINDEX_SAMECOND_AVE[receDetailInfo[0]] = receDetailInfo[10]
				
				# 過去4レースの最大指数を取得する。
				maxSpeedIndexList = []
				maxSpeedIndexList.append(receDetailInfo[2])
				maxSpeedIndexList.append(receDetailInfo[3])
				maxSpeedIndexList.append(receDetailInfo[4])
				maxSpeedIndexList.append(receDetailInfo[5])
				maxSpeedIndexList.sort()
				maxSpeedIndexList.reverse()
				if maxSpeedIndexList[0] != 0:
					PRE_SPEED_INDEX_MAX[receDetailInfo[0]] = maxSpeedIndexList[0]
				
				# 過去レースのアップタイム指数の最大値を取得する。
				maxUptimeIndexList = []
				maxUptimeIndexList.append(receDetailInfo[6])
				maxUptimeIndexList.append(receDetailInfo[7])
				maxUptimeIndexList.append(receDetailInfo[8])
				maxUptimeIndexList.append(receDetailInfo[9])
				maxUptimeIndexList.sort()
				maxUptimeIndexList.reverse()
				if maxUptimeIndexList[0] != 0:
					PRE_UPTIME_INDEX_MAX_DICT[receDetailInfo[0]] = maxUptimeIndexList[0]
			
			if len(AVE_SPEEDINDEX_2TH_DICT) < 4 and len(PRE_SPEED_INDEX_MAX) < 4 and len(AVE_UPTIMEINDEX_SAMECOND_AVE) < 4 and len(PRE_UPTIME_INDEX_MAX_DICT) < 4:
				continue
			
			
			AVE_SPEEDINDEX_2TH_DICT_flg = 0
			PRE_SPEED_INDEX_MAX_flg = 0
			AVE_UPTIMEINDEX_SAMECOND_AVE_flg = 0
			PRE_UPTIME_INDEX_MAX_DICT_flg = 0
			
			if len(AVE_SPEEDINDEX_2TH_DICT) > 3:
				AVE_SPEEDINDEX_2TH_DICT_flg = 1
				# 取得した値を元に偏差値を取得する。
				standardList = []
				# 過去2レースの平均値の処理
				for k, v in AVE_SPEEDINDEX_2TH_DICT.items():
					standardList.append(v)
				
				x = np.array(standardList)
				ans = np.round_(50+10*(x-np.average(x))/np.std(x))
				count = 0
				for k, v in AVE_SPEEDINDEX_2TH_DICT.items():
					AVE_SPEEDINDEX_2TH_DICT[k] = ans[count]
					count = count + 1
	
			if len(PRE_SPEED_INDEX_MAX) > 3:
				PRE_SPEED_INDEX_MAX_flg = 1
				standardList = []
				count = 0
				x = None
				ans = None
				# 過去4レースの最大値の処理
				for k, v in PRE_SPEED_INDEX_MAX.items():
					standardList.append(v)
				
				x = np.array(standardList)
				ans = np.round_(50+10*(x-np.average(x))/np.std(x))
				count = 0
				for k, v in PRE_SPEED_INDEX_MAX.items():
					PRE_SPEED_INDEX_MAX[k] = ans[count]
					count = count + 1
	
			if len(AVE_UPTIMEINDEX_SAMECOND_AVE) > 3:
				AVE_UPTIMEINDEX_SAMECOND_AVE_flg = 1
				count = 0
				x = None
				ans = None
				# 過去レースの同条件平均の処理(uptime)
				for k, v in AVE_UPTIMEINDEX_SAMECOND_AVE.items():
					standardList.append(v)
				
				x = np.array(standardList)
				ans = np.round_(50+10*(x-np.average(x))/np.std(x))
				count = 0
				for k, v in AVE_UPTIMEINDEX_SAMECOND_AVE.items():
					AVE_UPTIMEINDEX_SAMECOND_AVE[k] = ans[count]
					count = count + 1
	
			if len(PRE_UPTIME_INDEX_MAX_DICT) > 3:
				PRE_UPTIME_INDEX_MAX_DICT_flg = 1
				standardList = []
				count = 0
				x = None
				ans = None
				# 過去4レースの最大値の処理(uptime_)
				for k, v in PRE_UPTIME_INDEX_MAX_DICT.items():
					standardList.append(v)
				
				x = np.array(standardList)
				ans = np.round_(50+10*(x-np.average(x))/np.std(x))
				count = 0
				for k, v in PRE_UPTIME_INDEX_MAX_DICT.items():
					PRE_UPTIME_INDEX_MAX_DICT[k] = ans[count]
					count = count + 1			
			
	
			# DBを更新する。
			updateList = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18']
			for startNum in updateList:
				# 更新値を初期化
				stanSpeedIndex2th = 0
				stanSpeedIndexMax = 0
				stanUptimeIndexSameAve = 0
				stanUptimeIndexMax = 0
				if startNum in AVE_SPEEDINDEX_2TH_DICT:
					stanSpeedIndex2th = AVE_SPEEDINDEX_2TH_DICT[startNum]
				if startNum in PRE_SPEED_INDEX_MAX:
					stanSpeedIndexMax = PRE_SPEED_INDEX_MAX[startNum]
				if startNum in AVE_UPTIMEINDEX_SAMECOND_AVE:
					stanUptimeIndexSameAve = AVE_UPTIMEINDEX_SAMECOND_AVE[startNum]
				if startNum in PRE_UPTIME_INDEX_MAX_DICT:
					stanUptimeIndexMax = PRE_UPTIME_INDEX_MAX_DICT[startNum]
					
				where = "WHERE RACE_ID IN ('%s') AND START_NUM = '%s'"% (targetRaceId,startNum)
				dict_Db_RACE_FORCAST_T = {}
				if AVE_SPEEDINDEX_2TH_DICT_flg == 1:
					dict_Db_RACE_FORCAST_T['STAN_SPEEDINDEX_2TH'] = stanSpeedIndex2th
				if PRE_SPEED_INDEX_MAX_flg == 1:
					dict_Db_RACE_FORCAST_T['STAN_SPEEDINDEX_MAX'] = stanSpeedIndexMax
				if AVE_UPTIMEINDEX_SAMECOND_AVE_flg == 1:
					dict_Db_RACE_FORCAST_T['STAN_UPTIMEINDEX_SAMEAVE'] = stanUptimeIndexSameAve
				if PRE_UPTIME_INDEX_MAX_DICT_flg == 1:
					dict_Db_RACE_FORCAST_T['STAN_UPTIMEINDEX_MAX'] = stanUptimeIndexMax
				self.daoClass.update('POST_RACE_FORCAST_T',dict_Db_RACE_FORCAST_T,where)

			self.utilClass.logging( targetRaceId + ' is done',2)

		# 終了ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,1)

	##################################################################
	###### 引数:対象年月日
	###### 戻り値:なし
	###### 概要:引数で取得した対象年月日以上のデータを処理する
	###### 各指数の相対評価を行う
	##################################################################
	def updateJocIndex(self,stanDate):
		# メソッドの名
		methodname = sys._getframe().f_code.co_name
		# メソッド開始ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,0)

		# 内部関数定義
		# 偏差値の入った辞書を返す。
		def call_dictMake(dict):
			# 取得した値を元に偏差値を取得する。
			standardList = []
			# 過去2レースの平均値の処理
			for k, v in dict.items():
				standardList.append(v)
			
			x = np.array(standardList)
			ans = np.round_(50+10*(x-np.average(x))/np.std(x))
			count = 0
			for k, v in dict.items():
				dict[k] = ans[count]
				count = count + 1
		
			return dict

		# 全ての障害及び新馬戦以外の全てのレース結果を取得する。
		where = ["WHERE POST_RACE_T.RACE_DATE > '%s'"% stanDate," group by POST_RACE_T.RACE_ID"]
		allRaceIdList = self.daoClass.selectQuery(where,'post_forcastRaceIdForJocIndex')
		# 処理対象のRACE_ID毎に処理を進める。
		for raceTInfo in allRaceIdList:
			# RACE_ID,日付、芝・ダート、競馬場を取得する。
			targetRaceId = raceTInfo[0]
			targetRaceDate = raceTInfo[1]
			targetRacePlace = raceTInfo[2]
			targetRaceGroundFlg = raceTInfo[3]
			targetCond = targetRacePlace + targetRaceGroundFlg
			
			
			# joc_mstとforcast_tを繋げて値を取得する。
			sqlForUmabanAndUmameiPostDetail = ["WHERE POST_RACE_FORCAST_T.RACE_ID = '%s'"% targetRaceId,"AND JOCKEY_M.TARGET_YMD = '%s'"% targetRaceDate,
												"AND JOCKEY_M.TREGET_COND = '%s'"% targetCond]
			getCondList = self.daoClass.selectQuery(sqlForUmabanAndUmameiPostDetail,'post_updateForcastJocIndex')
			# joc_mstとforcast_tを繋げて値を取得する。
			sqlForUmabanAndUmameiPostDetail = ["WHERE POST_RACE_FORCAST_T.RACE_ID = '%s'"% targetRaceId,"AND JOCKEY_M.TARGET_YMD = '%s'"% targetRaceDate,
												"AND JOCKEY_M.TREGET_COND = '000'"]
			getCondListNonCond = self.daoClass.selectQuery(sqlForUmabanAndUmameiPostDetail,'post_updateForcastJocIndex')
			
			# DB格納用の辞書を生成する。
			JOCINDEX_ALL_3IN_DUCT = {}
			JOCINDEX_ALL_3IN_REFUND_DUCT = {}
			JOCINDEX_ALL_WIN_REFUND_DUCT = {}
			JOCINDEX_TARGET_3IN_DUCT = {}
			JOCINDEX_TARGET_3IN_REFUND_DUCT = {}
			JOCINDEX_TARGET_WIN_REFUND_DUCT = {}
		
			
			# 取得した情報毎に処理する。
			for receDetailInfo in getCondList:
				# 各辞書を格納していく。
				JOCINDEX_TARGET_3IN_DUCT[receDetailInfo[0]] = receDetailInfo[2]
				# 各辞書を格納していく。
				JOCINDEX_TARGET_3IN_REFUND_DUCT[receDetailInfo[0]] = receDetailInfo[3]
				# 各辞書を格納していく。
				JOCINDEX_TARGET_WIN_REFUND_DUCT[receDetailInfo[0]] = receDetailInfo[4]
	
			# 取得した情報毎に処理する。
			for receDetailInfo in getCondListNonCond:
				# 各辞書を格納していく。
				JOCINDEX_ALL_3IN_DUCT[receDetailInfo[0]] = receDetailInfo[2]
				# 各辞書を格納していく。
				JOCINDEX_ALL_3IN_REFUND_DUCT[receDetailInfo[0]] = receDetailInfo[3]
				# 各辞書を格納していく。
				JOCINDEX_ALL_WIN_REFUND_DUCT[receDetailInfo[0]] = receDetailInfo[4]
			
	
	
			JOCINDEX_ALL_3IN_DUCT = call_dictMake(JOCINDEX_ALL_3IN_DUCT)
			JOCINDEX_ALL_3IN_REFUND_DUCT = call_dictMake(JOCINDEX_ALL_3IN_REFUND_DUCT)
			JOCINDEX_ALL_WIN_REFUND_DUCT = call_dictMake(JOCINDEX_ALL_WIN_REFUND_DUCT)
			JOCINDEX_TARGET_3IN_DUCT = call_dictMake(JOCINDEX_TARGET_3IN_DUCT)
			JOCINDEX_TARGET_3IN_REFUND_DUCT = call_dictMake(JOCINDEX_TARGET_3IN_REFUND_DUCT)
			JOCINDEX_TARGET_WIN_REFUND_DUCT = call_dictMake(JOCINDEX_TARGET_WIN_REFUND_DUCT)
		
			
			# DBを更新する。
			updateList = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18']
			for startNum in updateList:
				# 更新値を初期化
				joc_all_3in = 0
				joc_all_3in_refund = 0
				joc_all_win_refund = 0
				joc_ter_3in = 0
				joc_tar_3in_refund = 0
				joc_tar_win_refund = 0
				
				if startNum in JOCINDEX_ALL_3IN_DUCT:
					joc_all_3in = JOCINDEX_ALL_3IN_DUCT[startNum]
					
				if startNum in JOCINDEX_ALL_3IN_REFUND_DUCT:
					joc_all_3in_refund = JOCINDEX_ALL_3IN_REFUND_DUCT[startNum]
					
				if startNum in JOCINDEX_ALL_WIN_REFUND_DUCT:
					joc_all_win_refund = JOCINDEX_ALL_WIN_REFUND_DUCT[startNum]
					
				if startNum in JOCINDEX_TARGET_3IN_DUCT:
					joc_ter_3in = JOCINDEX_TARGET_3IN_DUCT[startNum]
					
				if startNum in JOCINDEX_TARGET_3IN_REFUND_DUCT:
					joc_tar_3in_refund = JOCINDEX_TARGET_3IN_REFUND_DUCT[startNum]
					
				if startNum in JOCINDEX_TARGET_WIN_REFUND_DUCT:
					joc_tar_win_refund = JOCINDEX_TARGET_WIN_REFUND_DUCT[startNum]
					
				where = "WHERE RACE_ID IN ('%s') AND START_NUM = '%s'"% (targetRaceId,startNum)
				dict_Db_RACE_FORCAST_T = {}
				dict_Db_RACE_FORCAST_T['JOCINDEX_ALL_3IN'] = joc_all_3in
				dict_Db_RACE_FORCAST_T['JOCINDEX_ALL_3IN_REFUND'] = joc_all_3in_refund
				dict_Db_RACE_FORCAST_T['JOCINDEX_ALL_WIN_REFUND'] = joc_all_win_refund
				dict_Db_RACE_FORCAST_T['JOCINDEX_TARGET_3IN'] = joc_ter_3in
				dict_Db_RACE_FORCAST_T['JOCINDEX_TARGET_3IN_REFUND'] = joc_tar_3in_refund
				dict_Db_RACE_FORCAST_T['JOCINDEX_TARGET_WIN_REFUND'] = joc_tar_win_refund
				self.daoClass.update('POST_RACE_FORCAST_T',dict_Db_RACE_FORCAST_T,where)

			self.utilClass.logging( targetRaceId + ' is done',2)

		# 終了ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,1)

	##################################################################
	###### 引数:対象年月日
	###### 戻り値:なし
	###### 概要:引数で取得した対象年月日以上のデータを処理する
	###### 各指数の相対評価を行う
	##################################################################
	def updatelast(self,stanDate):
		# メソッドの名
		methodname = sys._getframe().f_code.co_name
		# メソッド開始ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,0)

		# 内部関数定義
		def stanSpeedIndex2th(x,raceMonth,raceCondMoney,raceCondOld):
			if x is None:
				return 0
		
			if x == 0:
				return 0
			
			# 競馬場によって指数が変わる。
			if raceMonth =='01':
				y = 0.00831726841219436 * x -0.180083297004648
			elif raceMonth =='02':
				y = 0.009192251072708 * x -0.213650132549248
			elif raceMonth =='03':
				y = 0.00919687172155047 * x -0.204822277178665
			elif raceMonth =='04':
				y = 0.00864261907976181 * x -0.18548650764505
			elif raceMonth =='05':
				y = 0.00775514431507381 * x -0.147980761024971
			elif raceMonth =='06':
				y = 0.0105182740415212 * x -0.246996911066369
			elif raceMonth =='07':
				y = 0.00909097602124718 * x -0.198874902952183
			elif raceMonth =='08':
				y = 0.00893733731493792 * x -0.196616373897427
			elif raceMonth =='09':
				y = 0.00835794287803958 * x -0.180227532787342
			elif raceMonth =='10':
				y = 0.00758758081731968 * x -0.140072638236867
			elif raceMonth =='11':
				y = 0.00843207876399432 * x -0.185422343654678
			else:
				y = 0.00794599556521498 * x -0.174359042636806
		
			# 条件(賞金)によって指数が変わる。
			if raceCondMoney =='02':
				y = y + 0.0110319034964239 * x -0.263273067327988
			elif raceCondMoney =='03':
				y = y + 0.0068542408069837 * x -0.119703857601888
			elif raceCondMoney =='04':
				y = y + 0.00870573534535585 * x -0.194344351942176
			elif raceCondMoney =='05':
				y = y + 0.0075346597571067 * x -0.137400560515439
			else:
				y = y + 0.00668849397595832 * x -0.111188654110651
			
			if raceCondOld =='01':
				y = y + 0.00812745548638828 * x -0.178766456859341
			elif raceCondOld =='02':
				y = y + 0.0109106084152192 * x -0.265111841784534
			elif raceCondOld =='03':
				y = y + 0.00822106430326291 * x -0.171008308266431
			else:
				y = y + 0.00749822160278825 * x -0.147254247302226
			
			return y
			
		# 偏差値から値を取得する。(スピード指数のMAX)
		def stanSpeedIndexMax(x,raceMonth,raceCondMoney,raceCondOld):
			if x is None:
				return 0
			if x == 0:
				return 0
				
			# 競馬場によって指数が変わる。
			if raceMonth =='01':
				y = 0.00743531499382985 * x -0.154236481906996
			elif raceMonth =='02':
				y = 0.0071341207032387 * x -0.143557537878284
			elif raceMonth =='03':
				y = 0.0078214153006516 * x -0.165057530401693
			elif raceMonth =='04':
				y = 0.00768199500001058 * x -0.163564935072632
			elif raceMonth =='05':
				y = 0.00731244458695022 * x -0.144235830141211
			elif raceMonth =='06':
				y = 0.00838660083127017 * x -0.187980897289678
			elif raceMonth =='07':
				y = 0.00791021789597919 * x -0.16865651485675
			elif raceMonth =='08':
				y = 0.00726348957020265 * x -0.136683745292106
			elif raceMonth =='09':
				y = 0.00764521062017449 * x -0.160900258019472
			elif raceMonth =='10':
				y = 0.00815944014947498 * x -0.176952358377705
			elif raceMonth =='11':
				y = 0.00766480493267592 * x -0.158054408027249
			else:
				y = 0.00721240998057649 * x -0.151889956438625
		
			# 条件(賞金)によって指数が変わる。
			if raceCondMoney =='02':
				y = y + 0.010045253724072 * x -0.249140082067434
			elif raceCondMoney =='03':
				y = y + 0.00597361410120329 * x -0.0985749297343198
			elif raceCondMoney =='04':
				y = y + 0.00763150723710451 * x -0.161376184031598
			elif raceCondMoney =='05':
				y = y + 0.00650005528425117 * x -0.109140551142769
			else:
				y = y + 0.0049062582913894 * x -0.042980770207219
			
		
			if raceCondOld =='01':
				y = y + 0.0102549176076309 * x -0.245567161657498
			elif raceCondOld =='02':
				y = y + 0.00955838869993187 * x -0.230806726077528
			elif raceCondOld =='03':
				y = y + 0.00707230023042304 * x -0.136967323165951
			else:
				y = y + 0.00630960436177533 * x -0.11250492338665
				
			return y
			
		# 偏差値から値を取得する。(Uptime指数のMAX)
		def stanUptimeIndexMax(x,racePlace):
			if x is None:
				return 0
			
			# 競馬場
			if racePlace == '01':
				y = 0.00920331009732005 * x -0.194338894718261
			elif racePlace == '02':
				y = 0.00510768409611091 * x -0.0171218751987778
			elif racePlace == '03':
				y = 0.00545635794705101 * x -0.057037020225619
			elif racePlace == '04':
				y = 0.00499825984960554 * x -0.0463406666629652
			elif racePlace == '05':
				y = 0.00500268300178242 * x -0.0450452395448093
			elif racePlace == '06':
				y = 0.00480694745037345 * x -0.0422587351695344
			elif racePlace == '07':
				y = 0.00359152770807243 * x + 0.00740224370174092
			elif racePlace == '08':
				y = 0.00518039336330581 * x -0.0475326531670114
			elif racePlace == '09':
				y = 0.00531452418411263 * x -0.05715201798296
			else:
				y = 0.0047078658019393 * x -0.0432496630932752
			return y
		
		# 偏差値から値を取得する。(騎手指数の3in)
		def jocIndexAll3in(x,raceGlade,raceCondMoney,racePlace):
			if x is None:
				return 0
			
			# 競馬場
			if racePlace == '01':
				y = 0.00712614211634634 * x -0.194238110532962
			elif racePlace == '02':
				y = 0.0054351530010958 * x -0.111492183054241
			elif racePlace == '03':
				y = 0.00482944234971064 * x -0.100606147315345
			elif racePlace == '04':
				y = 0.0044712376236006 * x -0.0782664020519758
			elif racePlace == '05':
				y = 0.00585415994321501 * x -0.152130565552242
			elif racePlace == '06':
				y = 0.00606975138412263 * x -0.163150027494448
			elif racePlace == '07':
				y = 0.00466030156510614 * x -0.0991785525365366
			elif racePlace == '08':
				y = 0.00595621650227637 * x -0.147219645643135
			elif racePlace == '09':
				y = 0.0056717697604712 * x -0.138280834932976
			else:
				y = 0.00556336265810426 * x -0.128887506542048
		
			# 重賞
			if raceGlade == '01':
				y = y + 0.00669255601125756 * x -0.233136936156254
			elif raceGlade == '02':
				y = y + 0.00678330094954616 * x -0.220703022451407
			elif raceGlade == '03':
				y = y + 0.00582458733899905 * x -0.177036156212268
			else:
				y = y + 0.00558367193160864 * x -0.161657332593678
		
			# レース条件(賞金区分)
			if raceCondMoney == '02':
				y = y + 0.00665556749265147 * x -0.194621764871256
			elif raceCondMoney == '03':
				y = y + 0.00557454533527598 * x -0.136273325370299
			elif raceCondMoney == '04':
				y = y + 0.00548937967644435 * x -0.131853739056197
			elif raceCondMoney == '05':
				y = y + 0.00482231989713927 * x -0.10038272597453
			else:
				y = y + 0.00536926601800684 * x -0.127066751895036
		
		
			return y
		
		# 偏差値から値を取得する。(runStyle) グラウンドフラグ、場所、距離、スピード指数を取得数r。
		def runStyle(x,raceGoundFlg,racePlace,raceRange,preSpeedIndex):
			if preSpeedIndex == 0:
				return 0
			
			if x is None or x == '':
				return 0
			
			if x == '01':
				x = 1
			elif x == '02':
				x = 2
			elif x == '03':
				x = 3
			elif x == '04':
				x = 4
				
			raceCond = raceRange + raceGoundFlg
			
			# 競馬場
			if racePlace == '01':
				y = -0.0390738059149417 * x +0.321264000882919
			elif racePlace == '02':
				y = -0.0495236235822676 * x +0.352494230992547
			elif racePlace == '03':
				y = -0.0441286910190817 * x +0.314419709474296
			elif racePlace == '04':
				y = -0.0423849637187813 * x +0.30862348989268
			elif racePlace == '05':
				y = -0.0364939563006165 * x +0.291288355500962
			elif racePlace == '06':
				y = -0.0429114059122906 * x +0.310266723935827
			elif racePlace == '07':
				y = -0.0424775835356447 * x +0.299153951198189
			elif racePlace == '08':
				y = -0.0389651763739663 * x +0.302801256484682
			elif racePlace == '09':
				y = -0.0419292491991959 * x +0.310923646169074
			else:
				y = -0.047260058784618 * x +0.315882719899091	
		
			# 距離と馬場
			if raceCond == '10000':
				y = y  -0.0276615726876335 * x +0.25261606825289
			elif raceCond == '10001':
				y = y  -0.0408023512782213 * x +0.339876754213867
			elif raceCond == '11501':
				y = y  -0.021412630565319 * x +0.266304720355482
			elif raceCond == '12000':
				y = y  -0.0151801879775095 * x +0.241510122529
			elif raceCond == '12001':
				y = y  -0.0200154691732272 * x +0.265969084482381
			elif raceCond == '13001':
				y = y  -0.0158974312921859 * x +0.256711780915409
			elif raceCond == '14000':
				y = y  -0.00727170738617943 * x +0.223871823508353
			elif raceCond == '14001':
				y = y  -0.0126653477989459 * x +0.246129379699987
			elif raceCond == '15000':
				y = y  -0.00284189301183362 * x +0.243969240576749
			elif raceCond == '16000':
				y = y  -0.00207017566904132 * x +0.219945475465978
			elif raceCond == '16001':
				y = y  -0.01091996030372 * x +0.249803150864564
			elif raceCond == '17000':
				y = y + 0.00645678113771414 * x +0.230625824585556
			elif raceCond == '17001':
				y = y  -0.0117593868205796 * x +0.269414702314255
			elif raceCond == '18000':
				y = y  -0.00423176008099502 * x +0.239913082142617
			elif raceCond == '18001':
				y = y  -0.0107376519411328 * x +0.263688471619851
			elif raceCond == '19001':
				y = y  -0.0226799081235324 * x +0.29720886394139
			elif raceCond == '20000':
				y = y  -0.00167372769567712 * x +0.236489413458608
			elif raceCond == '20001':
				y = y  -0.0013839523706951 * x +0.241293598219905
			elif raceCond == '21001':
				y = y  -0.00726940656420792 * x +0.24380502141354
			elif raceCond == '22000':
				y = y + 2.32847976448014E-05 * x +0.233291496928691
			elif raceCond == '23000':
				y = y + 0.00668070168511514 * x +0.229978830217454
			elif raceCond == '23001':
				y = y  -0.00937640950758497 * x +0.236095968199886
			elif raceCond == '24000':
				y = y + 0.00568359525641271 * x +0.224280779159023
			elif raceCond == '24001':
				y = y  -0.00112333362231084 * x +0.251319967992222
			elif raceCond == '25000':
				y = y + 0.00827363617428123 * x +0.206792625874751
			elif raceCond == '25001':
				y = y + 0.0179210892126221 * x +0.177030583405085
			elif raceCond == '26000':
				y = y + 0.000587182071974482 * x +0.240736213398052
			elif raceCond == '30000':
				y = y  -0.00202984401090468 * x +0.225495178079039
			elif raceCond == '32000':
				y = y + 0.00634861140858143 * x +0.178660669665167
			elif raceCond == '34000':
				y = y + 0.00462830176841237 * x +0.179993621286678
			else:
				y = y + 0.0341397902857699 * x +0.104349779288253
			
			return y

		# 全ての障害及び新馬戦以外の全てのレース結果を取得する。　
		where = ["WHERE POST_RACE_T.RACE_DATE > '%s'" % stanDate]
		allRaceIdList = self.daoClass.selectQuery(where,'simulateForcast')
		
		# 処理対象のRACE_ID毎に処理を進める。
		for raceTInfo in allRaceIdList:
			# 変数初期化
			speedIndex2th = 0
			speedIndexMax = 0
			uptimeIndexMax = 0
			jocIndex = 0
			runstyleIndex = 0
			
			# RACE_ID,日付、芝・ダート、競馬場を取得する。
			targetRaceId = raceTInfo[0]
			targetStartNum = raceTInfo[1]
			targetRaceDate = raceTInfo[2]
			targetRaceGroundFlg = raceTInfo[4]
			targetRacePlace = raceTInfo[3]
			targetRaceRange = raceTInfo[5]
			targetRaceGlade = raceTInfo[6]
			targetRaceCondOld = raceTInfo[7]
			targetRaceCondMoney = raceTInfo[8]
			speedIndex2th = raceTInfo[9]
			speedIndexMax = raceTInfo[10]
			uptimeIndexMax = raceTInfo[11]
			jocIndex = raceTInfo[12]
			runstyleIndex = raceTInfo[13]
			preSpeedIndex = raceTInfo[14]
	
	
			# 平均2レース
			speedIndex2th = stanSpeedIndex2th(speedIndex2th,targetRaceDate[4:6],targetRaceCondMoney,targetRaceCondOld)
			
			# スピードマックス
			speedIndexMax = stanSpeedIndexMax(speedIndexMax,targetRaceDate[4:6],targetRaceCondMoney,targetRaceCondOld)
			
			# ランスタイル
			runstyleIndex = runStyle(runstyleIndex,targetRaceGroundFlg,targetRacePlace,targetRaceRange,preSpeedIndex)
			
			# 騎手
			jocIndex = jocIndexAll3in(jocIndex,targetRaceGlade,targetRaceCondMoney,targetRacePlace)
	
			# アップタイム
			uptimeIndexMax = stanUptimeIndexMax(uptimeIndexMax,targetRacePlace)
	
					
			where = "WHERE RACE_ID IN ('%s') AND START_NUM = '%s'"% (targetRaceId,targetStartNum)
			dict_Db_RACE_FORCAST_T = {}
			dict_Db_RACE_FORCAST_T['SPEED2TH_RATE'] = speedIndex2th
			dict_Db_RACE_FORCAST_T['SPEEDMAX_RATE'] = speedIndexMax
			dict_Db_RACE_FORCAST_T['UPTIMEMAX_RATE'] = uptimeIndexMax
			dict_Db_RACE_FORCAST_T['RUNSTYLE_RATE'] = runstyleIndex
			dict_Db_RACE_FORCAST_T['JOC_RATE'] = jocIndex
			self.daoClass.update('POST_RACE_FORCAST_T',dict_Db_RACE_FORCAST_T,where)

			self.utilClass.logging(targetRaceId +'is done',2)

		# 終了ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,1)

