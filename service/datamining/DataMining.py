#coding: utf-8
# 概要
# データマイニング
################ 変更履歴 ######################
## 2017/09/13 作成

###############################################
import datetime
import sys
import os
import math
import numpy as np

class DataMining(object):
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
	###### 引数2:type
	###### 概要:引数で取得したレースIDのDataMiningを実施す
	###### の情報を更新する。
	##################################################################
	def execute(self,race_id,type):
		# 当メソッドの名前を取得する。
		methodname = sys._getframe().f_code.co_name

		# 処理開始ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,0)

		# 終了コード
		returnDict = {}
		returnDict['returnCode'] = 0

		try:

			if type == 1: # past
				self.past_data_mining(race_id)
			elif type == 2: # post
				self.post_data_mining(race_id)

		except:
			# リターンコードを設定する。
			import traceback
			returnDict['returnCode'] = 9
			error_text = traceback.format_exc()
			self.utilClass.loggingError(error_text)
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
	def post_data_mining(self,race_id):
		# メソッドの名
		methodname = sys._getframe().f_code.co_name
		# メソッド開始ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,0)
		self.utilClass.logging('target race is ' + race_id,2)
		
		where =["WHERE POST_RACE_T.RACE_ID = '%s'"% race_id ," GROUP BY POST_RACE_T.RACE_ID"]
		raceIdInfo = self.daoClass.selectQuery(where,'posttargetraceId')

		# updateフラグを取得する。 updateFlg = が1のときは　更新
		updateFlg = 1
		if raceIdInfo[0][1] == 1:
			updateFlg = 0
		
		# データベースより情報を取得する。
		where =["WHERE POST_RACE_T.RACE_DATE >='20040101' AND POST_RACE_T.RACE_ID ='%s'" % race_id ," ORDER BY POST_RACE_T.RACE_ID, CAST(POST_RACE_DETAIL_T.START_NUM AS SIGNED)"]
		pramget = self.daoClass.selectQuery(where,'postparaget')


		# 取得結果が 0 件の場合は次のレースIDに処理を遷移する。
		if len(pramget) ==0:
			return

		# 標準化するための配列を初期化
		start_num_list = []
		start_frame_list = []
		horse_weight_list = []
		dis_weight_list = []
		win_odd_list =[]
		rest_day_list =[]
		load_w_list =[]

		# ランダムフォレスト用
		dis_weight_list_forest = []
		
		slipFlg = 0
		# 標準化用に一回ループする。
		load_w_sameFlg = 0
		pre_load = pramget[0][16]
		for para in pramget:
			#　馬番を格納する。
			start_num_list.append(int(para[11]))
			start_frame_list.append(int(para[12]))
			if para[13] == '未取得':
				slipFlg = 1
				break
			horse_weight_list.append(int(para[13]))			
			if '+' in para[14]:
				num = para[14].replace('+','')
				num = int(num) 
				dis_weight_list.append(num)
				dis_weight_list_forest.append(num)
			elif '-' in para[14]:
				num = para[14].replace('-','')
				num = int(num) * -1
				dis_weight_list.append(num)
				dis_weight_list_forest.append(num)
			else:
				dis_weight_list.append(0)
				dis_weight_list_forest.append(0)
			win_odd_list.append(int(para[22]))
			rest_day_list.append(int(para[15]))
			load_w_list.append(int(para[16]))
			if pre_load != para[16]:
				load_w_sameFlg = 1

		# スキップフラグ
		if slipFlg == 1:
			return



		# 馬番
		x = np.array(start_num_list)
		ans = np.round_(50+10*(x-np.average(x))/np.std(x))
		start_num_list = []
		for fac in ans:
			start_num_list.append(fac * 0.01)
			
		# 枠番
		x = np.array(start_frame_list)
		ans = np.round_(50+10*(x-np.average(x))/np.std(x))
		start_frame_list = []
		for fac in ans:
			start_frame_list.append(fac * 0.01)

		# 体重
		x = np.array(horse_weight_list)
		ans = np.round_(50+10*(x-np.average(x))/np.std(x))
		horse_weight_list = []
		for fac in ans:
			horse_weight_list.append(fac * 0.01)

		# 体じゅうさ
		x = np.array(dis_weight_list)
		ans = np.round_(50+10*(x-np.average(x))/np.std(x))
		dis_weight_list = []
		for fac in ans:
			dis_weight_list.append(fac * 0.01)
			
			
		# オーズ
		x = np.array(win_odd_list)
		ans = np.round_(50+10*(x-np.average(x))/np.std(x))
		win_odd_list = []
		for fac in ans:
			win_odd_list.append(fac * 0.01)
			
		# 休養
		x = np.array(rest_day_list)
		ans = np.round_(50+10*(x-np.average(x))/np.std(x))
		rest_day_list = []
		for fac in ans:
			rest_day_list.append(fac * 0.01)
			
		# 斤量
		x = np.array(load_w_list)
		ans = np.round_(50+10*(x-np.average(x))/np.std(x))
		load_w_list = []
		for fac in ans:
			if load_w_sameFlg == 1:
				load_w_list.append(fac * 0.01)
			else:
				load_w_list.append(50 * 0.01)

		for i in range(len(pramget)):
			# 変数初期化
			dict_DATA_MINING_T = {}
			dict_DATA_MINING_T['RACE_MONTH_01'] = 0
			dict_DATA_MINING_T['RACE_MONTH_02'] = 0
			dict_DATA_MINING_T['RACE_MONTH_03'] = 0
			dict_DATA_MINING_T['RACE_MONTH_04'] = 0
			dict_DATA_MINING_T['RACE_MONTH_05'] = 0
			dict_DATA_MINING_T['RACE_MONTH_06'] = 0
			dict_DATA_MINING_T['RACE_MONTH_07'] = 0
			dict_DATA_MINING_T['RACE_MONTH_08'] = 0
			dict_DATA_MINING_T['RACE_MONTH_09'] = 0
			dict_DATA_MINING_T['RACE_MONTH_10'] = 0
			dict_DATA_MINING_T['RACE_MONTH_11'] = 0
			dict_DATA_MINING_T['RACE_MONTH_12'] = 0
			dict_DATA_MINING_T['RACE_PLACE_01'] = 0
			dict_DATA_MINING_T['RACE_PLACE_02'] = 0
			dict_DATA_MINING_T['RACE_PLACE_03'] = 0
			dict_DATA_MINING_T['RACE_PLACE_04'] = 0
			dict_DATA_MINING_T['RACE_PLACE_05'] = 0
			dict_DATA_MINING_T['RACE_PLACE_06'] = 0
			dict_DATA_MINING_T['RACE_PLACE_07'] = 0
			dict_DATA_MINING_T['RACE_PLACE_08'] = 0
			dict_DATA_MINING_T['RACE_PLACE_09'] = 0
			dict_DATA_MINING_T['RACE_PLACE_10'] = 0
			dict_DATA_MINING_T['RACE_NO_01'] = 0
			dict_DATA_MINING_T['RACE_NO_02'] = 0
			dict_DATA_MINING_T['RACE_NO_03'] = 0
			dict_DATA_MINING_T['RACE_NO_04'] = 0
			dict_DATA_MINING_T['RACE_NO_05'] = 0
			dict_DATA_MINING_T['RACE_NO_06'] = 0
			dict_DATA_MINING_T['RACE_NO_07'] = 0
			dict_DATA_MINING_T['RACE_NO_08'] = 0
			dict_DATA_MINING_T['RACE_NO_09'] = 0
			dict_DATA_MINING_T['RACE_NO_10'] = 0
			dict_DATA_MINING_T['RACE_NO_11'] = 0
			dict_DATA_MINING_T['RACE_NO_12'] = 0
			dict_DATA_MINING_T['RACE_GROUND_00'] = 0
			dict_DATA_MINING_T['RACE_GROUND_01'] = 0
			dict_DATA_MINING_T['RACE_RANGE'] = 0
			dict_DATA_MINING_T['RACE_GLADE_01'] = 0
			dict_DATA_MINING_T['RACE_GLADE_02'] = 0
			dict_DATA_MINING_T['RACE_GLADE_03'] = 0
			dict_DATA_MINING_T['RACE_GLADE_04'] = 0
			dict_DATA_MINING_T['RACE_WEIGHT_01'] = 0
			dict_DATA_MINING_T['RACE_WEIGHT_02'] = 0
			dict_DATA_MINING_T['RACE_WEIGHT_03'] = 0
			dict_DATA_MINING_T['RACE_WEIGHT_04'] = 0
			dict_DATA_MINING_T['RACE_COND_OLD_01'] = 0
			dict_DATA_MINING_T['RACE_COND_OLD_02'] = 0
			dict_DATA_MINING_T['RACE_COND_OLD_03'] = 0
			dict_DATA_MINING_T['RACE_COND_OLD_04'] = 0
			dict_DATA_MINING_T['RACE_COND_MONEY_02'] = 0
			dict_DATA_MINING_T['RACE_COND_MONEY_03'] = 0
			dict_DATA_MINING_T['RACE_COND_MONEY_04'] = 0
			dict_DATA_MINING_T['RACE_COND_MONEY_05'] = 0
			dict_DATA_MINING_T['RACE_COND_MONEY_06'] = 0
			dict_DATA_MINING_T['RACE_WEATHER_01'] = 0
			dict_DATA_MINING_T['RACE_WEATHER_02'] = 0
			dict_DATA_MINING_T['RACE_WEATHER_03'] = 0
			dict_DATA_MINING_T['RACE_WEATHER_04'] = 0
			dict_DATA_MINING_T['RACE_WEATHER_05'] = 0
			dict_DATA_MINING_T['RACE_WEATHER_06'] = 0
			dict_DATA_MINING_T['RACE_CONDITION_01'] = 0
			dict_DATA_MINING_T['RACE_CONDITION_02'] = 0
			dict_DATA_MINING_T['RACE_CONDITION_03'] = 0
			dict_DATA_MINING_T['RACE_CONDITION_04'] = 0
			dict_DATA_MINING_T['RUN_STYLE_01'] = 0
			dict_DATA_MINING_T['RUN_STYLE_02'] = 0
			dict_DATA_MINING_T['RUN_STYLE_03'] = 0
			dict_DATA_MINING_T['RUN_STYLE_04'] = 0
			logic_del_flg = '0'
			# RACEの月を取得する。
			dict_DATA_MINING_T['RACE_MONTH_' + pramget[i][0][4:6]] = 1
			
			# 場所を取得する。
			dict_DATA_MINING_T['RACE_PLACE_' + pramget[i][1]] = 1

			# RACE_NOを取得する。
			dict_DATA_MINING_T['RACE_NO_' + pramget[i][2]] = 1
			
			# RACEのばばを取得する。
			dict_DATA_MINING_T['RACE_GROUND_0' + pramget[i][3]] = 1
			
			# RACEの距離を取得する。
			dict_DATA_MINING_T['RACE_RANGE'] =  (int(pramget[i][4]) - 1000) / 2600
			
			# RACEの格を取得する。
			dict_DATA_MINING_T['RACE_GLADE_0' + pramget[i][5]] = 1
			
			# RACEの体重のハンデを取得する。
			dict_DATA_MINING_T['RACE_WEIGHT_' + pramget[i][6]] = 1
			
			# RACEの馬年齢条件を取得する。
			dict_DATA_MINING_T['RACE_COND_OLD_' + pramget[i][7]] = 1
			
			# RACEの賞金条件を取得する。
			dict_DATA_MINING_T['RACE_COND_MONEY_' + pramget[i][8]] = 1
			
			# RACEの天気を取得する。
			#dict_DATA_MINING_T['RACE_WEATHER_' + pramget[i][9]] = 1
			
			# RACEの馬場状態を取得する。
			#dict_DATA_MINING_T['RACE_CONDITION_' + pramget[i][10]] = 1
			
			# 馬番の偏差値を取得する。
			dict_DATA_MINING_T['STAN_START_NUM'] = start_num_list[i]

			# 枠番の偏差値を取得する。
			dict_DATA_MINING_T['STAN_START_FRAME'] = start_frame_list[i]
			
			# 馬体重の偏差値を取得する。
			dict_DATA_MINING_T['HORSE_WEIGHT'] = horse_weight_list[i]
			
			# 体重差の偏差値を取得する。
			dict_DATA_MINING_T['DIS_WEIGHT'] = dis_weight_list[i]
		
			# 休養日数の偏差値を取得する。
			restday = 50.0
			if rest_day_list[i] == rest_day_list[i]:
				restday = rest_day_list[i]
			else:
				logic_del_flg = '1'
			dict_DATA_MINING_T['REST_DAY'] = restday
			
			# 斤量の偏差値を取得する。
			dict_DATA_MINING_T['LOAD_W'] = load_w_list[i]
			
			# 単勝オッズの偏差値を取得する。
			dict_DATA_MINING_T['WIN_ODDS'] = win_odd_list[i]

			# 脚質の偏差値を取得する。
			dict_DATA_MINING_T['RUN_STYLE_' + pramget[i][17]] = 1
			
			# 2回平均スピード指数の偏差値を取得する。
			th2_index =pramget[i][18]
			if th2_index is None:
				th2_index = 50
				logic_del_flg = '1'
				dict_DATA_MINING_T['SPEED_INDEX_2TH'] = 50 * 0.01
			else:
				dict_DATA_MINING_T['SPEED_INDEX_2TH'] = pramget[i][18] * 0.01
			
			# マックスの偏差値を取得する。
			th2_index =pramget[i][19]
			if th2_index is None:
				th2_index = 50
				logic_del_flg = '1'
				dict_DATA_MINING_T['SPEED_INDEX_MAX'] = 50 * 0.01
			else:
				dict_DATA_MINING_T['SPEED_INDEX_MAX'] = pramget[i][19] * 0.01


			# 3ハロンの偏差値を取得する。
			th2_index =pramget[i][20]
			if th2_index is None:
				th2_index = 50
				logic_del_flg = '1'
				dict_DATA_MINING_T['UPTIME_INDEX_MAX'] = 50 * 0.01
			else:
				dict_DATA_MINING_T['UPTIME_INDEX_MAX'] = pramget[i][20] * 0.01	


			# 機種の偏差値を取得する。
			th2_index =pramget[i][21]
			if th2_index is None:
				th2_index = 50
				logic_del_flg = '1'
				dict_DATA_MINING_T['JOC_INDEX'] = 50 * 0.01
			else:
				dict_DATA_MINING_T['JOC_INDEX'] = pramget[i][21] * 0.01


			
			# 着順が前半か後半か判断する。
			tanshoFlg = 0
			fukushoFlg = 0
			halfFlg = 0
			dict_DATA_MINING_T['CORRECT_GOAL'] = halfFlg
			dict_DATA_MINING_T['TANSHO_FLG'] = tanshoFlg
			dict_DATA_MINING_T['FUKUSHO_FLG'] = fukushoFlg

			# DNNに投入させるデータか判断する。 2回以上走っていない馬は論理削除を立てる。
			if pramget[i][24] == 0.0 :
				logic_del_flg = '1'
			
			dict_DATA_MINING_T['LOGIC_DEL_FLG'] = logic_del_flg
			
			# 出走数を取得する。
			dict_DATA_MINING_T['HORSE_NUM'] = len(pramget) / 18
	
			# 着順を指数化する。
			dict_DATA_MINING_T['GOAL_NUM_INDEX'] = 0
			dict_DATA_MINING_T['GOAL_NUM_CLASS'] = 0
			
			# スピード指数を取得する.
			dict_DATA_MINING_T['RESULT_SPEED_INDEX'] = 0
			# 着順を種臆する
			dict_DATA_MINING_T['GOAL_NUM'] = 0
			
			# 共通処理
			dict_DATA_MINING_T['INS_PID'] = 'D0001'
			dict_DATA_MINING_T['UPD_PID'] = 'D0001'
			dict_DATA_MINING_T['RACE_ID'] = race_id
			dict_DATA_MINING_T['START_NUM'] = pramget[i][11]


			# ランダムフォレスト用のデータを準備する。

			dict_DATA_MINING_T['RACE_MONTH'] = int(pramget[i][0][4:6]) 
			dict_DATA_MINING_T['RACE_NO'] = int(pramget[i][2])
			dict_DATA_MINING_T['RACE_PLACE'] = int(pramget[i][1])
			dict_DATA_MINING_T['RACE_GROUND_FLG'] = int(pramget[i][3]) 
			dict_DATA_MINING_T['RACE_RANGE_VALUE'] = int(pramget[i][4])
			dict_DATA_MINING_T['RACE_GLADE'] = int(pramget[i][5])
			dict_DATA_MINING_T['RACE_WEIGHT'] = int(pramget[i][6])
			dict_DATA_MINING_T['RACE_COND_SEX'] = int(pramget[i][30])
			dict_DATA_MINING_T['RACE_COND_OLD'] = int(pramget[i][7])
			dict_DATA_MINING_T['RACE_COND_MONEY'] = int(pramget[i][8])
			dict_DATA_MINING_T['RACE_WEATHER'] = 0
			dict_DATA_MINING_T['RACE_CONDITION'] = 0
			dict_DATA_MINING_T['RACE_PRIZE_1'] = int(pramget[i][29])
			dict_DATA_MINING_T['HORCE_SEX'] = int(pramget[i][26])
			dict_DATA_MINING_T['WEIRHT_HORSE'] = int(pramget[i][13])
			dict_DATA_MINING_T['BERORE_DISTANCE'] = dis_weight_list_forest[i]
			dict_DATA_MINING_T['POPULARITY_WIN_ODDS'] = int(pramget[i][28])
			dict_DATA_MINING_T['RUN_STYLE'] = int(pramget[i][17])
			dict_DATA_MINING_T['HORSE_OLD'] = int(pramget[i][27])

			logStr = race_id + ':' + pramget[i][11] + 'のデータ'
			if updateFlg == 1:
				where = "WHERE RACE_ID = '%s' AND START_NUM = '%s'" %( race_id,pramget[i][11])
				self.daoClass.update('POST_DATA_MINING_T',dict_DATA_MINING_T,where)
			else:
				self.daoClass.insert('POST_DATA_MINING_T',dict_DATA_MINING_T)

			if i != len(pramget) - 1:
				continue


			# 最後だけそのレース自体を全て論理削除するか判断する。
			where = ["WHERE RACE_ID = '%s'"% race_id,"AND LOGIC_DEL_FLG = '1'"]
			logidelflg_datamining = self.daoClass.selectQuery(where,'logidelflg_datamining')
			if logidelflg_datamining[0][0]/len(pramget) > 0.3:
				# 一つでも論理削除されていたらそのレースの全ての馬を論理削除する。
				logic_del_flg_dict = {}
				logic_del_flg_dict['LOGIC_DEL_FLG'] = '1'
				where ="WHERE RACE_ID = '%s'" %race_id
				self.daoClass.update('POST_DATA_MINING_T',logic_del_flg_dict,where)

		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,1)

	##################################################################
	###### 引数1:race_id
	###### 戻り値:なし
	###### 概要:引数で取得したrace_idのレース詳細情報を更新する
	###### 
	##################################################################
	def past_data_mining(self,race_id):
		# メソッドの名
		methodname = sys._getframe().f_code.co_name
		# メソッド開始ログ
		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,0)
		self.utilClass.logging('target race is ' + race_id,2)

		where =["WHERE RACE_T.RACE_ID = '%s'" % race_id," GROUP BY RACE_T.RACE_ID"]
		targetRaceIdList = self.daoClass.selectQuery(where,'targetraceId')

		# updateフラグを取得する。 updateFlg = が1のときは　更新
		updateFlg = 1
		if targetRaceIdList[0][1] == 1:
			updateFlg = 0
		
		# データベースより情報を取得する。
		where =["WHERE RACE_T.RACE_DATE >='20040101' AND RACE_T.RACE_ID ='%s'" % race_id ," ORDER BY RACE_T.RACE_ID, CAST(RACE_DETAIL_T.START_NUM AS SIGNED)"]
		pramget = self.daoClass.selectQuery(where,'paraget')

		
		# 取得結果が 0 件の場合は次のレースIDに処理を遷移する。
		if len(pramget) ==0:
			return

		# 標準化するための配列を初期化
		start_num_list = []
		start_frame_list = []
		horse_weight_list = []
		dis_weight_list = []
		win_odd_list =[]
		rest_day_list =[]
		load_w_list =[]

		# ランダムフォレスト用
		dis_weight_list_forest = []
		
		# 標準化用に一回ループする。
		load_w_sameFlg = 0
		pre_load = pramget[0][16]
		for para in pramget:
			#　馬番を格納する。
			start_num_list.append(int(para[11]))
			start_frame_list.append(int(para[12]))
			horse_weight_list.append(int(para[13]))
			
			if '+' in para[14]:
				num = para[14].replace('+','')
				num = int(num) 
				dis_weight_list.append(num)
				dis_weight_list_forest.append(num)
			elif '-' in para[14]:
				num = para[14].replace('-','')
				num = int(num) * -1
				dis_weight_list.append(num)
				dis_weight_list_forest.append(num)
			else:
				dis_weight_list.append(0)
				dis_weight_list_forest.append(0)
			win_odd_list.append(int(para[22]))
			rest_day_list.append(int(para[15]))
			load_w_list.append(int(para[16]))
			if pre_load != para[16]:
				load_w_sameFlg = 1

		# 馬番
		x = np.array(start_num_list)
		ans = np.round_(50+10*(x-np.average(x))/np.std(x))
		start_num_list = []
		for fac in ans:
			start_num_list.append(fac * 0.01)
			
		# 枠番
		x = np.array(start_frame_list)
		ans = np.round_(50+10*(x-np.average(x))/np.std(x))
		start_frame_list = []
		for fac in ans:
			start_frame_list.append(fac * 0.01)

		# 体重
		x = np.array(horse_weight_list)
		ans = np.round_(50+10*(x-np.average(x))/np.std(x))
		horse_weight_list = []
		for fac in ans:
			horse_weight_list.append(fac * 0.01)

		# 体じゅうさ
		x = np.array(dis_weight_list)
		ans = np.round_(50+10*(x-np.average(x))/np.std(x))
		dis_weight_list = []
		for fac in ans:
			dis_weight_list.append(fac * 0.01)
			
			
		# オーズ
		x = np.array(win_odd_list)
		ans = np.round_(50+10*(x-np.average(x))/np.std(x))
		win_odd_list = []
		for fac in ans:
			win_odd_list.append(fac * 0.01)
			
		# 休養
		x = np.array(rest_day_list)
		ans = np.round_(50+10*(x-np.average(x))/np.std(x))
		rest_day_list = []
		for fac in ans:
			rest_day_list.append(fac * 0.01)
			
		# 斤量
		x = np.array(load_w_list)
		ans = np.round_(50+10*(x-np.average(x))/np.std(x))
		load_w_list = []
		for fac in ans:
			if load_w_sameFlg == 1:
				load_w_list.append(fac * 0.01)
			else:
				load_w_list.append(50 * 0.01)

		for i in range(len(pramget)):
			# 変数初期化
			dict_DATA_MINING_T = {}
			dict_DATA_MINING_T['RACE_MONTH_01'] = 0
			dict_DATA_MINING_T['RACE_MONTH_02'] = 0
			dict_DATA_MINING_T['RACE_MONTH_03'] = 0
			dict_DATA_MINING_T['RACE_MONTH_04'] = 0
			dict_DATA_MINING_T['RACE_MONTH_05'] = 0
			dict_DATA_MINING_T['RACE_MONTH_06'] = 0
			dict_DATA_MINING_T['RACE_MONTH_07'] = 0
			dict_DATA_MINING_T['RACE_MONTH_08'] = 0
			dict_DATA_MINING_T['RACE_MONTH_09'] = 0
			dict_DATA_MINING_T['RACE_MONTH_10'] = 0
			dict_DATA_MINING_T['RACE_MONTH_11'] = 0
			dict_DATA_MINING_T['RACE_MONTH_12'] = 0
			dict_DATA_MINING_T['RACE_PLACE_01'] = 0
			dict_DATA_MINING_T['RACE_PLACE_02'] = 0
			dict_DATA_MINING_T['RACE_PLACE_03'] = 0
			dict_DATA_MINING_T['RACE_PLACE_04'] = 0
			dict_DATA_MINING_T['RACE_PLACE_05'] = 0
			dict_DATA_MINING_T['RACE_PLACE_06'] = 0
			dict_DATA_MINING_T['RACE_PLACE_07'] = 0
			dict_DATA_MINING_T['RACE_PLACE_08'] = 0
			dict_DATA_MINING_T['RACE_PLACE_09'] = 0
			dict_DATA_MINING_T['RACE_PLACE_10'] = 0
			dict_DATA_MINING_T['RACE_NO_01'] = 0
			dict_DATA_MINING_T['RACE_NO_02'] = 0
			dict_DATA_MINING_T['RACE_NO_03'] = 0
			dict_DATA_MINING_T['RACE_NO_04'] = 0
			dict_DATA_MINING_T['RACE_NO_05'] = 0
			dict_DATA_MINING_T['RACE_NO_06'] = 0
			dict_DATA_MINING_T['RACE_NO_07'] = 0
			dict_DATA_MINING_T['RACE_NO_08'] = 0
			dict_DATA_MINING_T['RACE_NO_09'] = 0
			dict_DATA_MINING_T['RACE_NO_10'] = 0
			dict_DATA_MINING_T['RACE_NO_11'] = 0
			dict_DATA_MINING_T['RACE_NO_12'] = 0
			dict_DATA_MINING_T['RACE_GROUND_00'] = 0
			dict_DATA_MINING_T['RACE_GROUND_01'] = 0
			dict_DATA_MINING_T['RACE_RANGE'] = 0
			dict_DATA_MINING_T['RACE_GLADE_01'] = 0
			dict_DATA_MINING_T['RACE_GLADE_02'] = 0
			dict_DATA_MINING_T['RACE_GLADE_03'] = 0
			dict_DATA_MINING_T['RACE_GLADE_04'] = 0
			dict_DATA_MINING_T['RACE_WEIGHT_01'] = 0
			dict_DATA_MINING_T['RACE_WEIGHT_02'] = 0
			dict_DATA_MINING_T['RACE_WEIGHT_03'] = 0
			dict_DATA_MINING_T['RACE_WEIGHT_04'] = 0
			dict_DATA_MINING_T['RACE_COND_OLD_01'] = 0
			dict_DATA_MINING_T['RACE_COND_OLD_02'] = 0
			dict_DATA_MINING_T['RACE_COND_OLD_03'] = 0
			dict_DATA_MINING_T['RACE_COND_OLD_04'] = 0
			dict_DATA_MINING_T['RACE_COND_MONEY_02'] = 0
			dict_DATA_MINING_T['RACE_COND_MONEY_03'] = 0
			dict_DATA_MINING_T['RACE_COND_MONEY_04'] = 0
			dict_DATA_MINING_T['RACE_COND_MONEY_05'] = 0
			dict_DATA_MINING_T['RACE_COND_MONEY_06'] = 0
			dict_DATA_MINING_T['RACE_WEATHER_01'] = 0
			dict_DATA_MINING_T['RACE_WEATHER_02'] = 0
			dict_DATA_MINING_T['RACE_WEATHER_03'] = 0
			dict_DATA_MINING_T['RACE_WEATHER_04'] = 0
			dict_DATA_MINING_T['RACE_WEATHER_05'] = 0
			dict_DATA_MINING_T['RACE_WEATHER_06'] = 0
			dict_DATA_MINING_T['RACE_CONDITION_01'] = 0
			dict_DATA_MINING_T['RACE_CONDITION_02'] = 0
			dict_DATA_MINING_T['RACE_CONDITION_03'] = 0
			dict_DATA_MINING_T['RACE_CONDITION_04'] = 0
			dict_DATA_MINING_T['RUN_STYLE_01'] = 0
			dict_DATA_MINING_T['RUN_STYLE_02'] = 0
			dict_DATA_MINING_T['RUN_STYLE_03'] = 0
			dict_DATA_MINING_T['RUN_STYLE_04'] = 0
			logic_del_flg = '0'
			# RACEの月を取得する。
			dict_DATA_MINING_T['RACE_MONTH_' + pramget[i][0][4:6]] = 1
			
			# 場所を取得する。
			dict_DATA_MINING_T['RACE_PLACE_' + pramget[i][1]] = 1

			# RACE_NOを取得する。
			dict_DATA_MINING_T['RACE_NO_' + pramget[i][2]] = 1
			
			# RACEのばばを取得する。
			dict_DATA_MINING_T['RACE_GROUND_0' + pramget[i][3]] = 1
			
			# RACEの距離を取得する。
			dict_DATA_MINING_T['RACE_RANGE'] =  (int(pramget[i][4]) - 1000) / 2600
			
			# RACEの格を取得する。
			dict_DATA_MINING_T['RACE_GLADE_0' + pramget[i][5]] = 1
			
			# RACEの体重のハンデを取得する。
			dict_DATA_MINING_T['RACE_WEIGHT_' + pramget[i][6]] = 1
			
			# RACEの馬年齢条件を取得する。
			dict_DATA_MINING_T['RACE_COND_OLD_' + pramget[i][7]] = 1
			
			# RACEの賞金条件を取得する。
			dict_DATA_MINING_T['RACE_COND_MONEY_' + pramget[i][8]] = 1
			
			# RACEの天気を取得する。
			dict_DATA_MINING_T['RACE_WEATHER_' + pramget[i][9]] = 1
			
			# RACEの馬場状態を取得する。
			dict_DATA_MINING_T['RACE_CONDITION_' + pramget[i][10]] = 1
			
			# 馬番の偏差値を取得する。
			dict_DATA_MINING_T['STAN_START_NUM'] = start_num_list[i]

			# 枠番の偏差値を取得する。
			dict_DATA_MINING_T['STAN_START_FRAME'] = start_frame_list[i]
			
			# 馬体重の偏差値を取得する。
			dict_DATA_MINING_T['HORSE_WEIGHT'] = horse_weight_list[i]
			
			# 体重差の偏差値を取得する。
			dict_DATA_MINING_T['DIS_WEIGHT'] = dis_weight_list[i]
		
			# 休養日数の偏差値を取得する。
			restday = 50.0
			if rest_day_list[i] == rest_day_list[i]:
				restday = rest_day_list[i]
			else:
				logic_del_flg = '1'
			dict_DATA_MINING_T['REST_DAY'] = restday
			
			# 休養日数の偏差値を取得する。
			dict_DATA_MINING_T['LOAD_W'] = load_w_list[i]
			
			# 単勝オッズの偏差値を取得する。
			dict_DATA_MINING_T['WIN_ODDS'] = win_odd_list[i]

			# 脚質の偏差値を取得する。
			dict_DATA_MINING_T['RUN_STYLE_' + pramget[i][17]] = 1
			
			# 2回平均スピード指数の偏差値を取得する。
			th2_index =pramget[i][18]
			if th2_index is None:
				th2_index = 50
				logic_del_flg = '1'
				dict_DATA_MINING_T['SPEED_INDEX_2TH'] = 50 * 0.01
			else:
				dict_DATA_MINING_T['SPEED_INDEX_2TH'] = pramget[i][18] * 0.01
			
			# マックスの偏差値を取得する。
			th2_index =pramget[i][19]
			if th2_index is None:
				th2_index = 50
				logic_del_flg = '1'
				dict_DATA_MINING_T['SPEED_INDEX_MAX'] = 50 * 0.01
			else:
				dict_DATA_MINING_T['SPEED_INDEX_MAX'] = pramget[i][19] * 0.01


			# 3ハロンの偏差値を取得する。
			th2_index =pramget[i][20]
			if th2_index is None:
				th2_index = 50
				logic_del_flg = '1'
				dict_DATA_MINING_T['UPTIME_INDEX_MAX'] = 50 * 0.01
			else:
				dict_DATA_MINING_T['UPTIME_INDEX_MAX'] = pramget[i][20] * 0.01	


			# 機種の偏差値を取得する。
			th2_index =pramget[i][21]
			if th2_index is None:
				th2_index = 50
				logic_del_flg = '1'
				dict_DATA_MINING_T['JOC_INDEX'] = 50 * 0.01
			else:
				dict_DATA_MINING_T['JOC_INDEX'] = pramget[i][21] * 0.01


			
			# 着順が前半か後半か判断する。
			goalNum = '18'
			if pramget[i][23].encode('utf-8').isalnum():
				goalNum = pramget[i][23]
			else:
				logic_del_flg = '1'
			goalNum = int(goalNum)
			halfNum = len(pramget) / 2
			tanshoFlg = 0
			fukushoFlg = 0
			halfFlg = 0
			if goalNum <= halfNum:
				halfFlg = 1
			else:
				halfFlg = 0
			dict_DATA_MINING_T['CORRECT_GOAL'] = halfFlg
			
			# 単勝を買ったかどうか判断する。
			if goalNum == 1:
				tanshoFlg = 1
			dict_DATA_MINING_T['TANSHO_FLG'] = tanshoFlg

			# 複勝を買ったかどうか判断する。
			if goalNum <= 3:
				fukushoFlg = 1
			dict_DATA_MINING_T['FUKUSHO_FLG'] = fukushoFlg

			# DNNに投入させるデータか判断する。 2回以上走っていない馬は論理削除を立てる。
			if pramget[i][24] == 0.0 :
				logic_del_flg = '1'
			
			dict_DATA_MINING_T['LOGIC_DEL_FLG'] = logic_del_flg
			
			# 出走数を取得する。
			dict_DATA_MINING_T['HORSE_NUM'] = len(pramget) / 18
	
			# 着順を指数化する。
			cond_goal = 1 - ( goalNum / len(pramget))
			dict_DATA_MINING_T['GOAL_NUM_INDEX'] = 1 - ( goalNum / len(pramget))

			if cond_goal <= 0.2:
				cond_goal = 5
			elif cond_goal <= 0.4:
				cond_goal = 4
			elif cond_goal <= 0.6:
				cond_goal = 3
			elif cond_goal <= 0.8:
				cond_goal = 2
			else:
				cond_goal = 1


			dict_DATA_MINING_T['GOAL_NUM_CLASS'] = cond_goal
			
			# スピード指数を取得する.
			dict_DATA_MINING_T['RESULT_SPEED_INDEX'] = pramget[i][25]
			# 着順を種臆する
			dict_DATA_MINING_T['GOAL_NUM'] = goalNum
			
			# 共通処理
			dict_DATA_MINING_T['INS_PID'] = 'D0001'
			dict_DATA_MINING_T['UPD_PID'] = 'D0001'
			dict_DATA_MINING_T['RACE_ID'] = race_id
			dict_DATA_MINING_T['START_NUM'] = pramget[i][11]


			# ランダムフォレスト用のデータを準備する。

			dict_DATA_MINING_T['RACE_MONTH'] = int(pramget[i][0][4:6]) 
			dict_DATA_MINING_T['RACE_NO'] = int(pramget[i][2])
			dict_DATA_MINING_T['RACE_PLACE'] = int(pramget[i][1])
			dict_DATA_MINING_T['RACE_GROUND_FLG'] = int(pramget[i][3]) 
			dict_DATA_MINING_T['RACE_RANGE_VALUE'] = int(pramget[i][4])
			dict_DATA_MINING_T['RACE_GLADE'] = int(pramget[i][5])
			dict_DATA_MINING_T['RACE_WEIGHT'] = int(pramget[i][6])
			dict_DATA_MINING_T['RACE_COND_SEX'] = int(pramget[i][30])
			dict_DATA_MINING_T['RACE_COND_OLD'] = int(pramget[i][7])
			dict_DATA_MINING_T['RACE_COND_MONEY'] = int(pramget[i][8])
			dict_DATA_MINING_T['RACE_WEATHER'] = int(pramget[i][9])
			dict_DATA_MINING_T['RACE_CONDITION'] = int(pramget[i][10])
			dict_DATA_MINING_T['RACE_PRIZE_1'] = int(pramget[i][29])
			dict_DATA_MINING_T['HORCE_SEX'] = int(pramget[i][26])
			dict_DATA_MINING_T['WEIRHT_HORSE'] = int(pramget[i][13])
			dict_DATA_MINING_T['BERORE_DISTANCE'] = dis_weight_list_forest[i]
			dict_DATA_MINING_T['POPULARITY_WIN_ODDS'] = int(pramget[i][28])
			dict_DATA_MINING_T['RUN_STYLE'] = int(pramget[i][17])
			dict_DATA_MINING_T['HORSE_OLD'] = int(pramget[i][27])

			logStr = race_id + ':' + pramget[i][11] + 'のデータ'
			if updateFlg == 1:
				where = "WHERE RACE_ID = '%s' AND START_NUM = '%s'" %( race_id,pramget[i][11])
				self.daoClass.insert('DATA_MINING_T',dict_DATA_MINING_T,where)
			else:
				self.daoClass.insert('DATA_MINING_T',dict_DATA_MINING_T)

			if i != len(pramget) - 1:
				continue


			# 最後だけそのレース自体を全て論理削除するか判断する。
			where = ["WHERE RACE_ID = '%s'"% race_id,"AND LOGIC_DEL_FLG = '0'"]
			logidelflg_datamining = SELECTGET.MySQLselect('logidelflg_datamining').selectexe(where)
			if logidelflg_datamining[0][0]/len(pramget) < 0.6:
				# 一つでも論理削除されていたらそのレースの全ての馬を論理削除する。
				logic_del_flg_dict = {}
				logic_del_flg_dict['LOGIC_DEL_FLG'] = '1'
				where ="WHERE RACE_ID = '%s'" %race_id
				self.daoClass.insert('DATA_MINING_T',logic_del_flg_dict,where)


		self.utilClass.logging('[' + self.pid + '][' + methodname + ']' ,1)
