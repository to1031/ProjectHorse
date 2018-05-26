# coding: utf-8
# JOC_MSTに格納するクラス


################ 変更履歴 ######################
## 2017/05/05 作成

###############################################

import itertools
import datetime
import math
import os
import sys

class JocAnalyze(object):
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


	def jocAnalyze(self):
		# メソッド名取得
		methodname = sys._getframe().f_code.co_name
                # メソッド開始ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,0)
		
		# 最大値を崇徳する。
		macDate = self.daoClass.selectQuery('','maceDate')
		macDate = macDate[0][0]
		
		postFlg = 0
		RACEDATE = ''
		# 処理対象のRACE_IDを取得する。
		selectWhere = ["WHERE RACE_DATE > '%s'" % macDate,
						 "AND RACE_SHOGAI_FLG != '1' GROUP BY RACE_DATE,RACE_PLACE,RACE_GROUND_FLG ORDER BY RACE_DATE,RACE_PLACE,RACE_GROUND_FLG"]
		rargetYmdList = self.daoClass.selectQuery(selectWhere,'targetYm')
		if len(rargetYmdList) < 1:
			postFlg = 1
			rargetYmdList = self.daoClass.selectQuery(selectWhere,'targetYm_post')

		# 取得した年月毎に処理を進める。
		for tergetYmd in rargetYmdList:
	
			# 処理対象のレース年月日、レース会場、グランドを取得する。
			raceDate = tergetYmd[0]
			racePlace = tergetYmd[1]
			raceGroudFlg = tergetYmd[2]
			
			if postFlg == 0:
				self.utilClass.logging('calc from past race' ,2)
			
				# targetMonthに出走した騎手を全て取得する。
				# 処理対象のRACE_IDを取得する。
				selectJocWhere = ["WHERE RACE_T.RACE_DATE = '%s'"% raceDate,"AND RACE_T.RACE_PLACE = '%s'"% racePlace,
								"AND RACE_T.RACE_GROUND_FLG = '%s'"% raceGroudFlg,
								"GROUP BY RACE_DETAIL_T.JOCKER_NAME"]
				jocNameList = self.daoClass.selectQuery(selectJocWhere,'jocName')
			else:
				self.utilClass.logging('calc from post race' ,2)
				# targetMonthに出走した騎手を全て取得する。
				# 処理対象のRACE_IDを取得する。
				selectJocWhere = ["WHERE POST_RACE_T.RACE_DATE = '%s'"% raceDate,"AND POST_RACE_T.RACE_PLACE = '%s'"% racePlace,
								"AND POST_RACE_T.RACE_GROUND_FLG = '%s'"% raceGroudFlg,
								"GROUP BY POST_RACE_DETAIL_T.JOCKER_NAME"]
				jocNameList = self.daoClass.selectQuery(selectJocWhere,'jocName_post')
			# カウンターを準備する。
			count = 0
			# jocName毎に処理を進める。
			self.insert(jocNameList,raceDate,racePlace,raceGroudFlg,count)
			
			
			if RACEDATE != raceDate:
				# 初期化する。
				raceAllNum = 0
				goalWinNum = 0
				goal2WinNum = 0
				goal3WinNum = 0
				goal3inRate = 0
				goal3incount = 0
				goal3inRateNonPop = 0
				goal3inRateNonPopCount = 0
				fukuRefundRate = 0
				winRefundRate = 0
				winRefund = 0
				winin3Refund = 0
				# targetMonthに出走した騎手を全て取得する。
				# 処理対象のRACE_IDを取得する。
				if postFlg == 0:
					selectJocWhereToku = ["WHERE RACE_T.RACE_DATE = '%s'"% raceDate]
					jocNameListToku = self.daoClass.selectQuery(selectJocWhereToku,'jocNameDis')
				else:
					selectJocWhereToku = ["WHERE POST_RACE_T.RACE_DATE = '%s'"% raceDate]
					jocNameListToku = self.daoClass.selectQuery(selectJocWhereToku,'jocNameDis_post')
				# jocName毎に条件'000'の場合の処理を行う。
				targetCond = '000'
				for jocNameInfo in jocNameListToku:
					jocName = jocNameInfo[0]
					selectJocResult = ["WHERE RACE_T.RACE_DATE < '%s'"% raceDate, "AND RACE_DETAIL_T.JOCKER_NAME = '%s'"% jocName,
										"AND RACE_DETAIL_T.GOAL_NUM != '中止'"," ORDER BY RACE_DATE DESC LIMIT 50"]
					jocResultList = self.daoClass.selectQuery(selectJocResult,'jocResult')
					# 初期化する。
					raceAllNum = 0
					goalWinNum = 0
					goal2WinNum = 0
					goal3WinNum = 0
					goal3inRate = 0
					goal3incount = 0
					goal3inRateNonPop = 0
					goal3inRateNonPopCount = 0
					fukuRefundRate = 0
					winRefundRate = 0
					winRefund = 0
					winin3Refund = 0
					# 取得した結果を元にレース結果を取得し値を格納する。
					for resultInfo in jocResultList:
						# レース総数を取得する。
						raceAllNum = raceAllNum + 1
					
						# 1位の数を取得する。
						if resultInfo[1] == '1':
							goalWinNum = goalWinNum + 1
							# 6版人気以上であればカウントする。
							if int(resultInfo[2]) >= 6:
								goal3inRateNonPopCount = goal3inRateNonPopCount + 1
						
							# 1着の単勝払い戻しを取得する。
							winRefund = winRefund + resultInfo[3]
		
							# 1着の複勝払い戻しを取得する。
							winin3Refund = winin3Refund + resultInfo[4]				
						
						# 2位の数を取得する。
						if resultInfo[1] == '2':
							goal2WinNum = goal2WinNum + 1
							# 6版人気以上であればカウントする。
							if int(resultInfo[2]) >= 6:
								goal3inRateNonPopCount = goal3inRateNonPopCount + 1
		
							# 2着の複勝払い戻しを取得する。
							winin3Refund = winin3Refund + resultInfo[5]	
							
						# 3位の数を取得する。
						if resultInfo[1] == '3':
							goal3WinNum = goal3WinNum + 1
							# 6版人気以上であればカウントする。
							if int(resultInfo[2]) >= 6:
								goal3inRateNonPopCount = goal3inRateNonPopCount + 1
				
							# 3着の複勝払い戻しを取得する。
							winin3Refund = winin3Refund + resultInfo[6]
				
					# 取得した結果を元に値を整理する。
					if goal3inRateNonPopCount != 0:
						goal3inRateNonPop = goal3inRateNonPopCount / raceAllNum
					if (goalWinNum + goal2WinNum + goal3WinNum) != 0:
						goal3inRate = (goalWinNum + goal2WinNum + goal3WinNum) / raceAllNum
					if winin3Refund != 0:
						fukuRefundRate = winin3Refund / raceAllNum / 100
					if winRefund != 0:
						winRefundRate = winRefund / raceAllNum / 100		
					# 取得した結果を格納する。
					self.insert_dict(raceDate,jocName,targetCond,raceAllNum,goalWinNum,goal2WinNum,goal3WinNum,goal3inRate,goal3inRateNonPop,fukuRefundRate,winRefundRate)
	
			#基準日を取得する。
			RACEDATE = raceDate
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,1)
	
	def insert(self,jocNameList,raceDate,racePlace,raceGroudFlg,count):
		
		# DBからジョッキーの最新のレース
		for jocNameInfo in jocNameList:
			# ジョッキーの名前を取得する。
			jocName = jocNameInfo[0]
			targetYmd = raceDate
			targetCond = racePlace + raceGroudFlg
			raceAllNum = 0
			goalWinNum = 0
			goal2WinNum = 0
			goal3WinNum = 0
			goal3inRate = 0
			goal3incount = 0
			goal3inRateNonPop = 0
			goal3inRateNonPopCount = 0
			fukuRefundRate = 0
			winRefundRate = 0
			winRefund = 0
			winin3Refund = 0
	
			# 条件毎に処理をしていく。
			targetCond = racePlace + raceGroudFlg
			selectJocResult = ["WHERE RACE_T.RACE_DATE < '%s'"% raceDate, "AND RACE_DETAIL_T.JOCKER_NAME = '%s'"% jocName,
								"AND RACE_DETAIL_T.GOAL_NUM != '中止'","AND RACE_T.RACE_PLACE = '%s'"% racePlace,"AND RACE_T.RACE_GROUND_FLG = '%s'"% raceGroudFlg,
								" ORDER BY RACE_DATE DESC LIMIT 50"]
			jocResultList = self.daoClass.selectQuery(selectJocResult,'jocResult')
			# 取得した結果を元にレース結果を取得し値を格納する。
			for resultInfo in jocResultList:
				# レース総数を取得する。
				raceAllNum = raceAllNum + 1
				
				# 1位の数を取得する。
				if resultInfo[1] == '1':
					goalWinNum = goalWinNum + 1
					# 6版人気以上であればカウントする。
					if int(resultInfo[2]) >= 6:
						goal3inRateNonPopCount = goal3inRateNonPopCount + 1
					
					# 1着の単勝払い戻しを取得する。
					winRefund = winRefund + resultInfo[3]
	
					# 1着の複勝払い戻しを取得する。
					winin3Refund = winin3Refund + resultInfo[4]				
					
				# 2位の数を取得する。
				if resultInfo[1] == '2':
					goal2WinNum = goal2WinNum + 1
					# 6版人気以上であればカウントする。
					if int(resultInfo[2]) >= 6:
						goal3inRateNonPopCount = goal3inRateNonPopCount + 1
	
					# 2着の複勝払い戻しを取得する。
					winin3Refund = winin3Refund + resultInfo[5]	
						
				# 3位の数を取得する。
				if resultInfo[1] == '3':
					goal3WinNum = goal3WinNum + 1
					# 6版人気以上であればカウントする。
					if int(resultInfo[2]) >= 6:
						goal3inRateNonPopCount = goal3inRateNonPopCount + 1
			
					# 3着の複勝払い戻しを取得する。
					winin3Refund = winin3Refund + resultInfo[6]
			
			# 取得した結果を元に値を整理する。
			if goal3inRateNonPopCount != 0:
				goal3inRateNonPop = goal3inRateNonPopCount / raceAllNum
			if (goalWinNum + goal2WinNum + goal3WinNum) != 0:
				goal3inRate = (goalWinNum + goal2WinNum + goal3WinNum) / raceAllNum
			if winin3Refund != 0:
				fukuRefundRate = winin3Refund / raceAllNum / 100
			if winRefund != 0:
				winRefundRate = winRefund / raceAllNum / 100		
			# 取得した結果を格納する。
			self.insert_dict(targetYmd,jocName,targetCond,raceAllNum,goalWinNum,goal2WinNum,goal3WinNum,goal3inRate,goal3inRateNonPop,fukuRefundRate,winRefundRate)


	# DBに格納する。
	def insert_dict(self,targetYmd,jocName,targetCond,raceAllNum,goalWinNum,goal2WinNum,goal3WinNum,goal3inRate,goal3inRateNonPop,fukuRefundRate,winRefundRate):
		
		dict_JOCKEY_M = {}
		dict_JOCKEY_M['LOGIC_DEL_FLG'] = '0'
		dict_JOCKEY_M['INS_PID'] = 'M0002'
		dict_JOCKEY_M['UPD_PID'] = 'M0002'
		dict_JOCKEY_M['TARGET_YMD'] = targetYmd
		dict_JOCKEY_M['JOCKEY_NAME'] = jocName
		dict_JOCKEY_M['TREGET_COND'] = targetCond
		dict_JOCKEY_M['RACE_ALLNUM'] = raceAllNum
		dict_JOCKEY_M['GOAL_WIN_NUM'] = goalWinNum
		dict_JOCKEY_M['GOAL_2WIN_NUM'] = goal2WinNum
		dict_JOCKEY_M['GOAL_3WIN_NUM'] = goal3WinNum
		dict_JOCKEY_M['GOAL_3IN_RATE'] = goal3inRate
		dict_JOCKEY_M['GOAL_3IN_RATE_NONPOP'] = goal3inRateNonPop
		dict_JOCKEY_M['FUKU_REFUND_RATE'] = fukuRefundRate
		dict_JOCKEY_M['WIN_REFUND_RATE'] = winRefundRate
		self.daoClass.insert('JOCKEY_M',dict_JOCKEY_M)

