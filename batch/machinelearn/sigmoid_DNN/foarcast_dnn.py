#coding: utf-8

# 処理概要　「各レースの機械学習結果をDBに登録する」
# 機能名　「各レースの機械学習結果をDBに登録する」
# 変更日 2018/01/13
'''
ディープラーニングの実行python

'''

##---------------------------
## ディープラーニングの雛形
##---------------------------

from sklearn.model_selection import train_test_split
from sklearn import datasets
import numpy as np
import tensorflow as tf
import os,sys
from sklearn.ensemble import RandomForestClassifier
import DNN_class
import configparser

# main処理
def main():


    # 環境変数を取得する。
    homeDir = os.environ["APPMONEYTRADE"]

    # log用の文字列準備
    pid = os.path.basename(__file__)[0:4] # 機能IDの取得

    # 1時的に環境変数を追加する。
    sys.path.append(homeDir)
    from util import Util
    from util import JsonParse
    from bitflyer import BitflyerApi_STRE
    from dataBaseAccess import Dao
    from service import DTMDataMining
    from service import MASSMailSendService
    from service import TradeDecision


    # utilクラスのオブジェクト取得
    utilClass = Util.Util(pid)

    # daoクラスのオブジェクトを取得する。
    dao = Dao.Dao(pid)
    # utilクラス、propatiesファイル、DBアクセスクラスまでのpathを取得する。
    condigPath = homeDir + 'conf'

    # configファイルから情報を抜き出す.
    inifile = configparser.ConfigParser()
    inifile.read(condigPath + '/config.ini', 'UTF-8')


    # ハイパーパラメータ(検証用)
    data_num = 10000
    result_column = 143
    class_id = 'FLG_UPDOWN_2MINUTE'
    kensho_num = 10000
    n_in = 0
    n_out = 0
    input_num = 103

    # 検証用データ取得
    # DBより学習データを取得する。
    where = ["WHERE DATA_MINING_RESULT_T.DATA_TIME >= '201707010000' AND DATA_MINING_RESULT_T.DATA_TIME < '2017080100000'"]
    dataList = dao.selectQuery(where,'machinelearn')

    # 各パラメータをの配列を初期化する.
    x_predate = []
    y_predate = []


    # レースID毎に処理をする。
    for datainfo in dataList:
    
        # 格納しない番号を列強する。
        ifList = [0,1,11,41,42,43,44,45,55,56,57,58,59,60,75,90,105]

        # 初期化
        paramlist = []
        resultlist = []

        # skipFlg
        skipFlg = 0

        # テストデータを格納する。
        for i in range(len(datainfo)):

            # 答えデータを取得する。ただし、答えデータが 9 の場合は格納しない
            if result_column == i and datainfo[result_column] == 9:
                skipFlg = 1
                continue
            elif result_column == i:
                resultlist.append(datainfo[result_column])
            
            # 学習データ格納
            if i not in ifList and i <= 119:
                paramlist.append(datainfo[i])
            

        if skipFlg == 1:
            continue
    
        x_predate.append(paramlist)
        y_predate.append(resultlist)


    # デバッグ


    # DNNで読み取れるデータに変換
    X_train = np.array(x_predate)
    Y_train = np.array(y_predate)

    print(X_train)
    print(input_num)
    #
    model = DNN_class.DNN(n_in = input_num,n_hiddens=[2000,3000,2000],n_out = 1)
    dnnResult = model.getRestore(X_train,homeDir + 'machinelearn/sigmoid_DNN/' + class_id)
    # count
    count_sekai = 0 #普通の正解
    count_husekai = 0 # 普通の不正解

    # 60%以上の時
    count_60sekai = 0
    count_60husekai = 0

    # 70%以上の時
    count_70sekai = 0 
    count_70husekai = 0

    # 80%以上の時
    count_80sekai = 0
    count_80husekai = 0

    # 40%以下の時
    count_40sekai = 0
    count_40husekai = 0

    count_30sekai = 0
    count_30husekai = 0

    count_20sekai = 0
    count_20husekai = 0

    for i in range(len(dnnResult)):
        if dnnResult[i][0] >= 0.5:
            if Y_train[i] == 1:
                count_sekai = count_sekai + 1
            else:
                count_husekai = count_husekai + 1
 
        if dnnResult[i][0] < 0.5:
            if Y_train[i] == 1:
                count_husekai = count_husekai + 1
            else:
                count_sekai = count_sekai + 1

        if dnnResult[i][0] < 0.4:
            if Y_train[i] == 1:
                count_40husekai = count_40husekai + 1
            else:
                count_40sekai = count_40sekai + 1

        if dnnResult[i][0] < 0.3:
            if Y_train[i] == 1:
                count_30husekai = count_30husekai + 1
            else:
                count_30sekai = count_30sekai + 1

        if dnnResult[i][0] < 0.2:
            if Y_train[i] == 1:
                count_20husekai = count_20husekai + 1
            else:
                count_20sekai = count_20sekai + 1

        if dnnResult[i][0] >= 0.6:
            if Y_train[i] == 1:
                count_60sekai = count_60sekai + 1
            else:
                count_60husekai = count_60husekai + 1

        if dnnResult[i][0] >= 0.7:
            if Y_train[i] == 1:
                count_70sekai = count_70sekai + 1
            else:
                count_70husekai = count_70husekai + 1

        if dnnResult[i][0] >= 0.8:
            if Y_train[i] == 1:
                count_80sekai = count_80sekai + 1
            else:
                count_80husekai = count_80husekai + 1


    print('普通の正解====' + str(count_sekai/(count_sekai + count_husekai)))

    print('80の正解====正解数:' + str(count_80sekai) + ' 不正解数:' + str(count_80husekai))
    #print('80の正解====' + str(count_80sekai/(count_80sekai + count_80husekai)))

    print('70の正解====正解数:' + str(count_70sekai) + ' 不正解数:' + str(count_70husekai))
    #print('70の正解====' + str(count_70sekai/(count_70sekai + count_70husekai)))

    print('60の正解====正解数:' + str(count_60sekai) + ' 不正解数:' + str(count_60husekai))
    #print('60の正解====' + str(count_60sekai/(count_60sekai + count_60husekai)))

    print('40の正解====正解数:' + str(count_40sekai) + ' 不正解数:' + str(count_40husekai))
    #print('40の正解====' + str(count_40sekai/(count_40sekai + count_40husekai)))

    print('30の正解====正解数:' + str(count_30sekai) + ' 不正解数:' + str(count_30husekai))
    #print('30の正解====' + str(count_30sekai/(count_30sekai + count_30husekai)))

    print('20の正解====正解数:' + str(count_20sekai) + ' 不正解数:' + str(count_20husekai))
    #print('20の正解====' + str(count_20sekai/(count_20sekai + count_20husekai)))



if __name__ == '__main__':
    main()
