# coding: utf-8
from datetime import datetime
import sys
import os
import configparser
import traceback
from time import sleep

def main():
	# デバッグ
	starttime = datetime.now()
	print(starttime)
	# 基準年月日時分を取得する。
	standardTime = starttime.strftime('%Y%m%d%H%M')
	# 環境変数を取得する。
	homeDir = os.environ["APPMONEYTRADE"]

	# log用の文字列準備
	exefile = os.path.basename(__file__)
	pid = os.path.basename(__file__)[0:4] # 機能IDの取得

        # 1時的に環境パスを追加する。
	sys.path.append(homeDir)
	from initialize import Initialize

	# 初期化クラスのオブエクトか
	object_dict = {}
	object_dict['pid'] = pid
	Initializer = Initialize.Initialize(object_dict)

	# utilクラスのオブジェクト取得
	utilClass = Initializer.utilClass
	# daoクラスのオブジェクトを取得する。
	daoClass = Initializer.daoClass
	# メール送信クラスを取得する
	MASSClass = Initializer.MASSClass
	object_dict['util'] = utilClass
	object_dict['dao'] = daoClass
	object_dict['mass'] = MASSClass


	# 各クラスのオブジェクト化
	# ビットフライヤークラス
	bitflyerClass = Initializer.class_ins('BitflyerApi_STRE',object_dict)
	# データマイニングクラスを取得する。
	DTMClass = Initializer.class_ins('DTMDataMining',object_dict)
	# トレード決定サービスクラスを取得する。
	TradeClass = Initializer.class_ins('TradeDecision',object_dict)
	# 機械学習(sigmoid)を呼び出す
	DNNSigmoidClass = Initializer.class_ins('DNNSDNNSigmoid',object_dict)
	# データ収集クラスを呼び出す。
	DataGatherSaveClass = Initializer.class_ins('DGGSDataGatherSave',object_dict)

	# configファイルから情報を抜き出す.
	inifile = utilClass.inifile

	# APIキーを取得する。
	key=inifile.get('apikey','bitflyer')
	secret=inifile.get('apikey','private')

	# # バッチのログを出力する.
	utilClass.logging('System Trade is begun and STANDARDTIME IS [' + standardTime + ']',0)

	# システムトレード中止/再開メール確認サービス前回実行時間を取得する。
	exestsc = inifile.get('tradedicition','msscServicemin')
	f = open(homeDir + inifile.get('tradedicition','msscServicetxt'), "r")
	exetime = f.read()[0:12]
	f.close()

	if exetime == '' or exetime is None or utilClass.strDateMinus(standardTime,exetime) > int(exestsc) * 60:
		# システムトレード中止/再開メール確認サービス前回実行時間を取得する。
		resultmssc = MASSClass.msscService(standardTime)

		# 状況確認サービス制御ファイル書き込み
		f = open(homeDir + inifile.get('tradedicition','msscServicetxt'), "w")
		f.write(standardTime)
		f.close()

		# 再開の場合
		if resultmssc['sysdradeTodo'] == 2:
			# バッチのログを出力する.
			utilClass.loggingWarn('MASSClass.msscService has result theirs is restart')
			# エラー管理ービスを呼び出す
			service = 'msscService'
			TradeClass.ercrService('21',className=exefile,service=service,msg=inifile.get('service',service) + 'サービスの結果が「再開」でした')

		# 中止の場合
		if resultmssc['sysdradeTodo'] == 1:
			# バッチのログを出力する.
			utilClass.loggingWarn('MASSClass.msscService has result theirs is stop')
			# エラー管理ービスを呼び出す
			service = 'msscService'
			TradeClass.ercrService('81',className=exefile,service=service,msg=inifile.get('service',service) + 'サービスの結果が「中止」でした')

			# 終了処理
			dofinish(utilClass,TradeClass,MASSClass,bitflyerClass,standardTime,daoClass)



	# 最も最近のエラー管理情報を取得する。
	resultercr = TradeClass.ercrService('00')
	if len(resultercr) >= 1 and resultercr['resultCode'] == 0 and int(resultercr['type'][0:1]) > 5:
		utilClass.loggingError('before systrade is abnormal ended. errortype is [' + resultercr['type'] + ']. id is [' + str(resultercr['id']) + ']')
		dofinish(utilClass,TradeClass,MASSClass,bitflyerClass,standardTime,daoClass)


	# 現在の最終取引価格を取得する。
	resultftpg = bitflyerClass.ftpgService(cointype='FX_BTC_JPY')
	if resultftpg is None or len(resultftpg) == 0 or resultftpg['resultCode'] == 9:
		# バッチのログを出力する.
		utilClass.loggingWarn('ftpgService is abnormal termination')
		# エラー管理テーブルを呼び出す
		service = 'ftpgService'
		TradeClass.ercrService('11',className=exefile,service=service,msg=inifile.get('service',service) + 'サービスのAPI通信が失敗しました')
		dofinish(utilClass,TradeClass,MASSClass,bitflyerClass,standardTime,daoClass)

	# バッチログ 現在の価格状況
	utilClass.logging('resultftpg is having ' + str(resultftpg),2)

	# 既存予約取引参照
	resultebtr = bitflyerClass.ebtrService(key,secret,cointype='FX_BTC_JPY',datanum=1)
	if resultebtr is None or len(resultebtr) == 0 or resultebtr['resultCode'] == 9:
		# バッチのログを出力する.
		utilClass.loggingWarn('ebtrService is abnormal termination')
		# エラー管理サービスを呼び出す
		service = 'ebtrService'
		TradeClass.ercrService('11',className=exefile,service=service,msg=inifile.get('service',service) + 'サービスのAPI通信が失敗しました')
		dofinish(utilClass,TradeClass,MASSClass,bitflyerClass,standardTime,daoClass)


	# 既存予約の確認
	utilClass.logging('resultebtr is having ' + str(resultebtr),2)


	# 既存の有効取引を取得する
	resultevtr = bitflyerClass.evtrService(key,secret,cointype='FX_BTC_JPY',datanum=1)
	if resultevtr is None or len(resultevtr) == 0 or resultevtr['resultCode'] == 9:
		# バッチのログを出力する.
		utilClass.loggingWarn('evtrService is abnormal termination')
		# エラー管理サービスを呼び出す
		service = 'evtrService'
		TradeClass.ercrService('11',className=exefile,service=service,msg=inifile.get('service',service) + 'サービスのAPI通信が失敗しました')
		dofinish(utilClass,TradeClass,MASSClass,bitflyerClass,standardTime,daoClass)

	# 既存有効取引結果をログ出力
	utilClass.logging('resultevtr is having ' + str(resultevtr),2)


	# 状況確認の前回実行時間を取得する。
	exestsc = inifile.get('tradedicition','stscServicemin')
	f = open(homeDir + inifile.get('tradedicition','stscServicetxt'), "r")
	exetime = f.read()[0:12]
	f.close()
	if exetime == '' or exetime is None or utilClass.strDateMinus(standardTime,exetime) > int(exestsc) * 60:
		# 状況確認サービス
		TradeClass.stscService(standardTime,resultebtr,resultevtr)
		# 状況確認サービス制御ファイル書き込み
		f = open(homeDir + inifile.get('tradedicition','stscServicetxt'), "w")
		f.write(standardTime)
		f.close()




	# データマイニングを実行する。
	loop_flg = True
	while loop_flg:
		resultdtm = DTMClass.dtmservice(standardTime,dict=resultftpg)
		if resultdtm is None or len(resultdtm) == 0 or resultdtm['resultCode'] == 9:
			# バッチのログを出力する.
			utilClass.loggingWarn('DTMClass.dtmservice is abnormal termination')
			# エラー管理サービスを呼び出す
			service = 'dtmService'
			TradeClass.ercrService('12',className=exefile,service=service,msg=inifile.get('service',service) + 'サービスのデータマイニングが失敗しました')
			# 終了処理
			dofinish(utilClass,TradeClass,MASSClass,bitflyerClass,standardTime,daoClass)

		elif resultdtm['resultCode'] == 0:
			loop_flg =False
		else:
			# バッチのログを出力する.
			utilClass.logging('DTMClass.dtmservice is return 1 so again call',2)


	# 機械学習系サービスクラス
	# ディープニューラルネットワークの分類を行う
	resultdnns = DNNSigmoidClass.dnnsService(standardTime)
	if resultdnns is None or len(resultdnns) == 0 or resultdnns['resultCode'] == 9:
		# バッチのログを出力する.
		utilClass.loggingWarn('DNNSigmoidClass.dnnsService is abnormal termination')
		# エラー管理サービスを呼び出す
		service = 'dnnsService'
		TradeClass.ercrService('91',className=exefile,service=service,msg=inifile.get('service',service) + 'サービスの機械学習(sigmoid)が失敗しました')
		dofinish(utilClass,TradeClass,MASSClass,bitflyerClass,standardTime,daoClass)


	# 機械学習結果
	utilClass.logging('resultdnns is having ' + str(resultdnns),2)

	# 機械学習結果とその時の値段を格納する
	DataGatherSaveClass.prssService(resultdnns['predict'],resultftpg['endTradePrice'])


	# 既存予約が1件以上の場合予約を取り消すか判定する
	if resultebtr['resultNum'] != 0:
		# 予約取引取消判定サービスを呼び出す。
		resultbtcd = TradeClass.btcdService(resultftpg,resultebtr,resultevtr,resultdnns)
		if resultbtcd is None or len(resultbtcd) == 0 or resultbtcd['resultCode'] == 9:
			# バッチのログを出力する.
			utilClass.loggingWarn('TradeClass.btcdService is abnormal termination')
			# エラー管理サービスを呼び出す
			service = 'ebtrService'
			TradeClass.ercrService('11',className=exefile,service=service,msg=inifile.get('service',service) + 'サービスが失敗しました')
			dofinish(utilClass,TradeClass,MASSClass,bitflyerClass,standardTime,daoClass)

		# 予約取引判定の結果
		utilClass.logging('resultbtcd is having ' + str(resultbtcd),2)

		# 予約を取り消す場合
		if resultbtcd['orderCancelFlg'] == 1:

			# 既存の予約を取り消す。
			resultebtc = bitflyerClass.ebtcService(key,secret,resultebtr['child_order_id'],cointype='FX_BTC_JPY')
			if 0 == resultebtc:
				# バッチのログを出力する。
				utilClass.logging('can not get bitflyerData so skiped' + ' data is ebtcService',2)
				# エラー管理サービスを呼び出す 
				service = 'ebtcService'
				TradeClass.ercrService('11',className=exefile,service=service,msg=inifile.get('service',service) + 'サービスが失敗しました')
				# 再度予約取消を呼び出す。
				resultebtc = bitflyerClass.ebtcService(key,secret,resultebtr['child_order_id'],cointype='FX_BTC_JPY')
	
			# 予約取消について再度確認
			if 0 == resultebtc:
				# バッチのログを出力する。
				utilClass.logging('can not get bitflyerData so skiped' + ' data is ebtcService',2)
				dofinish(utilClass,TradeClass,MASSClass,bitflyerClass,standardTime,daoClass)

	
			# 予約取消確認が取れるまで確認する。
			if resultebtc == 1:
				while(True):
					# 既存の予約を取得する。
					resultebtr2 = bitflyerClass.ebtrService(key,secret,cointype='FX_BTC_JPY',datanum=1)
					sleep(2)
					if len(resultebtr2) > 0 and resultebtr2['resultNum'] == 0:
						# 予約が取り消されたらメールで送信する。
						# メール送信を整える。
						dict = {}
						dict['subject'] = '予約取引取消完了通知'
						body =  ['取引予約が完了しました。']
						body.append('▼詳細情報')
						body.append('取消注文ID：' + resultebtr['child_order_id'])
						body.append('取消注文額:' + str(resultebtr['price']))
						body.append('取消注文サイド:' + resultebtr['side'])
						body.append('取消注文量:' + str(resultebtr['size']))
						dict['body'] = body
						MASSClass.massService(dict)
						break



			# 証拠金確認サービスを実行する
			call_cchrService(key,secret,utilClass,TradeClass,MASSClass,bitflyerClass)
			# 終了処理
			dofinish(utilClass,TradeClass,MASSClass,bitflyerClass,standardTime,daoClass)

		else:
			# 証拠金確認サービスを実行する。
			call_cchrService(key,secret,utilClass,TradeClass,MASSClass,bitflyerClass)
			# 終了処理
			dofinish(utilClass,TradeClass,MASSClass,bitflyerClass,standardTime,daoClass)


		

	# 既存の有効取引が存在する場合は損切り、利益確定判定を実施する。
	if resultevtr['resultNum'] != 0:
		# 損切り/利益確定判定を実施する。
		resultlptd = TradeClass.lptdService(resultftpg,resultevtr,resultdnns)
		if resultlptd is None or len(resultlptd) == 0 or resultlptd['resultCode'] == 9:
			utilClass.loggingWarn('TradeClass.lptdService is abnormal termination')
			# エラー管理サービスを呼び出す
			service = 'lptdService'
			TradeClass.ercrService('91',className=exefile,service=service,msg=inifile.get('service',service) + 'サービスが失敗しました')
			dofinish(utilClass,TradeClass,MASSClass,bitflyerClass,standardTime,daoClass)

		# 損切利益判定の処理結果をログに出力する。
		utilClass.logging('resultlptd is having ' + str(resultlptd),2)


		if resultlptd['executeflg'] == 1:
			# 新規取引と新規取引完了確認
			neworder(key,secret,resultlptd['side'],resultlptd['price'],resultlptd['size'],utilClass,TradeClass,MASSClass,bitflyerClass,standardTime,daoClass,exefile,inifile,resultevtr,resultlptd['lossgain'])

			# 証拠金変動確認と更新
			call_cchrService(key,secret,utilClass,TradeClass,MASSClass,bitflyerClass)
			# 終了処理
			dofinish(utilClass,TradeClass,MASSClass,bitflyerClass,standardTime,daoClass)
		else:
			# 証拠金変動確認と更新
			call_cchrService(key,secret,utilClass,TradeClass,MASSClass,bitflyerClass)
			# 終了処理
			dofinish(utilClass,TradeClass,MASSClass,bitflyerClass,standardTime,daoClass)



	# 新規取引判定を行う
	resultntrd = TradeClass.ntrdService(resultftpg,resultdnns)
	if resultntrd is None or len(resultntrd) == 0 or resultntrd['resultCode'] == 9:
		# 警告ログを出力する。
		utilClass.loggingWarn('DNNSigmoidClass.dnnsService is abnormal termination')
		# エラー管理サービス
		service = 'ntrdService'
		TradeClass.ercrService('91',className=exefile,service=service,msg=inifile.get('service',service) + 'サービスが失敗しました')
		dofinish(utilClass,TradeClass,MASSClass,bitflyerClass,standardTime,daoClass)

	# 新規取引判定結果ログ出力
	utilClass.logging('ntrdService is having ' + str(resultntrd),2)

	# 新規取引判定が有りの場合は新規予約取引サービスを呼び出す
	if resultntrd['newOrderFlg'] == 1:
		# 新規取引と新規取引完了確認
		neworder(key,secret,resultntrd['side'],resultntrd['price'],resultntrd['size'],utilClass,TradeClass,MASSClass,bitflyerClass,standardTime,daoClass,exefile,inifile,resultevtr,0)

	# 証拠金確認サービスを呼び出す.
	call_cchrService(key,secret,utilClass,TradeClass,MASSClass,bitflyerClass)

	# バッチ終了ログ
	dofinish(utilClass,TradeClass,MASSClass,bitflyerClass,standardTime,daoClass)


# 新規取引予約と新規取引予約完了確認
def neworder(key,secret,side,price,size,utilClass,TradeClass,MASSClass,bitflyerClass,standardTime,daoClass,exefile,inifile,resultevtr,lossgain):
	# 新規オーダ確認サービスを呼び出す
	resultnocc = bitflyerClass.noccService(key,secret,cointype='FX_BTC_JPY',datanum=1)
	utilClass.logging('resultnocc is having ' + str(resultnocc),2)

	# 結果がエラーの場合
	if resultnocc is None or len(resultnocc) == 0 or resultnocc['resultCode'] == 9:
		utilClass.loggingWarn('bitflyerClass.noccService is abnormal termination')
		# エラー管理サービスを呼び出す
		service = 'noccService'
		TradeClass.ercrService('11',className=exefile,service=service,msg=inifile.get('service',service) + 'サービスが失敗しました')
		dofinish(utilClass,TradeClass,MASSClass,bitflyerClass,standardTime,daoClass)
	elif resultnocc['resultCode'] == 1:
		# 既に予約が存在したので新規オーダーを行わない。
		dofinish(utilClass,TradeClass,MASSClass,bitflyerClass,standardTime,daoClass)
	elif resultnocc['resultCode'] == 2:
		# 新規オーダーが埋もれてしまったの一旦エラー管理サービスを呼び出す.
		service = 'noccService'
		TradeClass.ercrService('61',className=exefile,service=service,msg=inifile.get('service',service) + 'サービスにて確認できませんでした')
		dofinish(utilClass,TradeClass,MASSClass,bitflyerClass,standardTime,daoClass)


	# 新規オーダーサービスを実行する。
	resulttbke = bitflyerClass.tbkeService(key,secret,side,price,size,lossgain)
	if resulttbke is None or len(resulttbke) == 0 or resulttbke['resultCode'] == 9:
		utilClass.loggingWarn('bitflyerClass.tbkeService is abnormal termination')
		# エラー管理サービスを呼び出す
		service = 'tbkeService'
		TradeClass.ercrService('11',className=exefile,service=service,msg=inifile.get('service',service) + 'サービスが失敗しました')
		dofinish(utilClass,TradeClass,MASSClass,bitflyerClass,standardTime,daoClass)


	# メール送信サービスを呼び出す
	#メール送信を整える。
	dict={}
	dict['subject']='新規注文発注通知'
	body=['新規注文を発注しました']
	body.append('▼詳細情報')
	body.append('注文額：' + str(price))
	body.append('ポジション：' + side)
	body.append('注文量：' + str(size))

	# 既存の有効取引が存在する場合は既存有効取引情報も送信する
	if resultevtr['resultNum'] != 0:
		body.append('---既存の有効取引情報---')
		body.append('既存の取引額：' + str(resultevtr['price']))
		body.append('既存のポジション：' + resultevtr['side'])
		body.append('既存の取引量：' + str(resultevtr['size']))

		dict['body']=body
		#MASSClass.massService(dict)


	# 新規オーダ確認サービスを呼び出す
	resultnocc = bitflyerClass.noccService(key,secret,cointype='FX_BTC_JPY',datanum=1)
	utilClass.logging('resultnocc is having ' + str(resultnocc),2)
	if resultnocc is None or len(resultnocc) == 0 or resultnocc['resultCode'] == 9:
		utilClass.loggingWarn('bitflyerClass.noccService is abnormal termination')
		# エラー管理サービスを呼び出す
		service = 'noccService'
		TradeClass.ercrService('11',className=exefile,service=service,msg=inifile.get('service',service) + 'サービスが失敗しました')
		dofinish(utilClass,TradeClass,MASSClass,bitflyerClass,standardTime,daoClass)
	elif resultnocc['resultCode'] == 2:
		# 新規オーダーが埋もれてしまったの一旦エラー管理サービスを呼び出す.
		service = 'noccService'
		TradeClass.ercrService('61',className=exefile,service=service,msg=inifile.get('service',service) + 'サービスにて確認できませんでした')
		dofinish(utilClass,TradeClass,MASSClass,bitflyerClass,standardTime,daoClass)

	#メール送信サービスを呼び出す
	#メール送信を整える。
	dict['subject']='新規注文確定通知'
	body[0]='新規注文を予約注文として受付られました'
	dict['body']=body
	if resultevtr['resultNum'] != 0:
		MASSClass.massService(dict)


# 証拠金変動確認と証拠金更新サービス
def call_cchrService(key,secret,utilClass,TradeClass,MASSClass,bitflyerClass):
	# 証拠金確認サービスを呼び出す
	result = bitflyerClass.cchrService(key,secret,datanum=10)
	if result == 0:
		  utilClass.logging('can not get bitflyerData so skiped' + ' data is cchrService',2)
		  return

	if len(result) != 0 and result['resultnum'] != 0:
		  # 証拠金変動履歴サービスを呼び出す
		  servResult = TradeClass.gchuService(result['return_list'])

		  # 更新結果があった場合はメール送信サービスを呼び出す
		  if len(servResult) != 0 and servResult['updata'] != 0:
			    # メール送信を整える。
			    dict = {}
			    dict['subject'] = '証拠金変動通知'
			    body =  ['証拠金に変動がありました。']
			    body.append('▼詳細情報')
			    body.append('現在の証拠金：' + str(servResult['updatedict']['amount']))
			    body.append('変動額：' + str(servResult['updatedict']['change']))
			    dict['body'] = body
			    MASSClass.massService(dict)

# 終了処理
def dofinish(utilClass,TradeClass,MASSClass,bitflyerClass,standardTime,daoClass):
	# ログ出力
	utilClass.logging('System Trade is ended and STANDARDTIME IS [' + standardTime + ']',1)

	# daoのコネクション消去
	daoClass.closeConn()

	# 各オブジェクトのNone
	utilClass = None
	TradeClass = None
	MASSClass = None
	bitflyerClass = None
	# デバッグ
	print(datetime.now())
	# exit
	exit()


if __name__ == '__main__':
	main()
