#coding: utf-8

# 処理概要　「着順の分類分析」
# 機能名　「着順の分類(4割以内かどうか分析」
# 変更日 2017/10/21
'''
ランダムフォレストの実行python

'''

##---------------------------
## ディープラーニングの雛形
##---------------------------

from sklearn.model_selection import train_test_split
from sklearn import datasets
import numpy as np
import tensorflow as tf
import os
import sys
import configparser
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
import sklearn.cross_validation as crv
from sklearn.metrics import accuracy_score
from sklearn.datasets import load_iris


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

    # path用の辞書を取得
    pathdict = getpath('')

    # ハイパーパラメータ
    data_num = 10000
    result_column = 142
    kensho_num = 10000
    n_in = 0
    n_out = 0
    
    # DBより学習データを取得する。
    where = ["WHERE DATA_MINING_RESULT_T.DATA_TIME >= '201704010000' AND DATA_MINING_RESULT_T.DATA_TIME < '2017070100000'"]
    dataList = dao.selectQuery(where,'machinelearn')

    # 各パラメータをの配列を初期化する.
    x_predate = []
    y_predate = []

    # dict
    dataDict = {}

    # レースID毎に処理をする。
    for datainfo in dataList:

        # 格納しない番号を列強する。
        ifList = [0,1,11,41,42,43,44,45,55,56,57,58,59,60,75,90,105]
        # 格納する番号
        inlist = [10,12,13,14,15,16,17,21,22,23,28,29,30,40,52,53,54,61,62,63,64,65,66,74,76,77,78,79,80,81,82,88,89,91,92,93,94,95,96,103,104,106,107,108,109,110,111,112,118]

        # デバッグ
        input_num = 0

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
            if i not in ifList and i <= 119 and i in inlist:
                dataDict[len(paramlist) + 1] = i
                paramlist.append(datainfo[i])
            

        if skipFlg == 1:
            continue
    
        x_predate.append(paramlist)
        y_predate.append(resultlist[0])

        input_num = len(paramlist)   

    # デバッグ


    # DNNで読み取れるデータに変換
    X_train = np.array(x_predate)
    Y_train = np.array(y_predate)
    

    # RFTで予想
    clf = RandomForestClassifier(n_estimators=350, random_state=0)
    clf.fit(X_train, Y_train)
    
#########################################################################################################
#########################################################################################################
#########################################################################################################
    where = ["WHERE DATA_MINING_RESULT_T.DATA_TIME >= '201707010000' AND DATA_MINING_RESULT_T.DATA_TIME < '2017080100000'"]
    dataList = dao.selectQuery(where,'machinelearn')

    # 各パラメータをの配列を初期化する.
    x_predate = []
    y_predate = []

    # デバッグ用
    countA = 0
    countB = 0

    # レースID毎に処理をする。
    for datainfo in dataList:

        # 格納しない番号を列強する。
        ifList = [0,1,11,41,42,43,44,45,55,56,57,58,59,60,75,90,105]
        # デバッグ
        input_num = 0

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
                if datainfo[result_column] == 1:
                    countA = countA + 1
                countB = countB + 1
                resultlist.append(datainfo[result_column])

            # 学習データ格納
            if i not in ifList and i <= 119 and i in inlist:
                paramlist.append(datainfo[i])


        if skipFlg == 1:
            continue

        x_predate.append(paramlist)
        y_predate.append(resultlist[0])

        input_num = len(paramlist)


    # DNNで読み取れるデータに変換
    X_test = np.array(x_predate)
    Y_test = np.array(y_predate)

    y_predict = clf.predict(X_test)
    print(accuracy_score(Y_test, y_predict))

    # 特徴量の重要度
    feature = clf.feature_importances_ 
   
    # デバッグ
    print('countA:' + str(countA))
    print('countB:' + str(countB))

    # 
    for i in range(len(feature)):
       if feature[i] > 0.009:
           print(str(dataDict[i]) + '/' + pathdict[dataDict[i]] + ':' + str(feature[i]))

    print(feature)



def getpath(oath):
    dict = {}
    dict[0] = 'DATA_TIME'
    dict[1] = 'WHAT_DAY'
    dict[2] = 'DAY_MONDAY'
    dict[3] = 'DAY_TUESDAY'
    dict[4] = 'DAY_WEDNESDAY'
    dict[5] = 'DAY_THURSDAY'
    dict[6] = 'DAY_FRIDAY'
    dict[7] = 'DAY_SATURDAY'
    dict[8] = 'DAY_SUNDAY'
    dict[9] = 'WEEK_DAY'
    dict[10] = 'DAY_OF_TIME'
    dict[11] = 'FINAL_TRANS_PRICE'
    dict[12] = 'FTP_DIS_1MINUTE'
    dict[13] = 'FTP_DIS_2MINUTES'
    dict[14] = 'FTP_DIS_3MINUTES'
    dict[15] = 'FTP_DIS_4MINUTES'
    dict[16] = 'FTP_DIS_5MINUTES'
    dict[17] = 'FTP_DIS_6MINUTES'
    dict[18] = 'FTP_DIS_7MINUTES'
    dict[19] = 'FTP_DIS_8MINUTES'
    dict[20] = 'FTP_DIS_9MINUTES'
    dict[21] = 'FTP_DIS_10MINUTES'
    dict[22] = 'FTP_DIS_30MINUTES'
    dict[23] = 'FTP_DIS_60MINUTES'
    dict[24] = 'FTP_DIS_2HOURS'
    dict[25] = 'FTP_DIS_3HOURS'
    dict[26] = 'FTP_DIS_4HOURS'
    dict[27] = 'FTP_DIS_5HOURS'
    dict[28] = 'FTP_DIS_6HOURS'
    dict[29] = 'FTP_DIS_12HOURS'
    dict[30] = 'FTP_DIS_18HOURS'
    dict[31] = 'FTP_DIS_24HOURS'
    dict[32] = 'FTP_DIS_10M_HIGH'
    dict[33] = 'FTP_DIS_1H_HIGH'
    dict[34] = 'FTP_DIS_2H_HIGH'
    dict[35] = 'FTP_DIS_3H_HIGH'
    dict[36] = 'FTP_DIS_4H_HIGH'
    dict[37] = 'FTP_DIS_5H_HIGH'
    dict[38] = 'FTP_DIS_6H_HIGH'
    dict[39] = 'FTP_DIS_12H_HIGH'
    dict[40] = 'FTP_DIS_24H_HIGH'
    dict[41] = 'FTP_DIS_2D_HIGH'
    dict[42] = 'FTP_DIS_4D_HIGH'
    dict[43] = 'FTP_DIS_7D_HIGH'
    dict[44] = 'FTP_DIS_14D_HIGH'
    dict[45] = 'FTP_DIS_28D_HIGH'
    dict[46] = 'FTP_DIS_10M_LOW'
    dict[47] = 'FTP_DIS_1H_LOW'
    dict[48] = 'FTP_DIS_2H_LOW'
    dict[49] = 'FTP_DIS_3H_LOW'
    dict[50] = 'FTP_DIS_4H_LOW'
    dict[51] = 'FTP_DIS_5H_LOW'
    dict[52] = 'FTP_DIS_6H_LOW'
    dict[53] = 'FTP_DIS_12H_LOW'
    dict[54] = 'FTP_DIS_24H_LOW'
    dict[55] = 'FTP_DIS_2D_LOW'
    dict[56] = 'FTP_DIS_4D_LOW'
    dict[57] = 'FTP_DIS_7D_LOW'
    dict[58] = 'FTP_DIS_14D_LOW'
    dict[59] = 'FTP_DIS_28D_LOW'
    dict[60] = 'FINAL_SELL_COUNT'
    dict[61] = 'FSC_SUMIN_1MINUTE'
    dict[62] = 'FSC_SUMIN_2MINUTES'
    dict[63] = 'FSC_SUMIN_3MINUTES'
    dict[64] = 'FSC_SUMIN_4MINUTES'
    dict[65] = 'FSC_SUMIN_5MINUTES'
    dict[66] = 'FSC_SUMIN_10MINUTES'
    dict[67] = 'FSC_SUMIN_60MINUTES'
    dict[68] = 'FSC_SUMIN_2HOURS'
    dict[69] = 'FSC_SUMIN_3HOURS'
    dict[70] = 'FSC_SUMIN_4HOURS'
    dict[71] = 'FSC_SUMIN_5HOURS'
    dict[72] = 'FSC_SUMIN_6HOURS'
    dict[73] = 'FSC_SUMIN_12HOURS'
    dict[74] = 'FSC_SUMIN_24HOURS'
    dict[75] = 'FINAL_SELL_AMMOUNT'
    dict[76] = 'FSA_SUMIN_1MINUTE'
    dict[77] = 'FSA_SUMIN_2MINUTES'
    dict[78] = 'FSA_SUMIN_3MINUTES'
    dict[79] = 'FSA_SUMIN_4MINUTES'
    dict[80] = 'FSA_SUMIN_5MINUTES'
    dict[81] = 'FSA_SUMIN_10MINUTES'
    dict[82] = 'FSA_SUMIN_60MINUTES'
    dict[83] = 'FSA_SUMIN_2HOURS'
    dict[84] = 'FSA_SUMIN_3HOURS'
    dict[85] = 'FSA_SUMIN_4HOURS'
    dict[86] = 'FSA_SUMIN_5HOURS'
    dict[87] = 'FSA_SUMIN_6HOURS'
    dict[88] = 'FSA_SUMIN_12HOURS'
    dict[89] = 'FSA_SUMIN_24HOURS'
    dict[90] = 'FINAL_BUY_COUNT'
    dict[91] = 'FBC_SUMIN_1MINUTE'
    dict[92] = 'FBC_SUMIN_2MINUTES'
    dict[93] = 'FBC_SUMIN_3MINUTES'
    dict[94] = 'FBC_SUMIN_4MINUTES'
    dict[95] = 'FBC_SUMIN_5MINUTES'
    dict[96] = 'FBC_SUMIN_10MINUTES'
    dict[97] = 'FBC_SUMIN_60MINUTES'
    dict[98] = 'FBC_SUMIN_2HOURS'
    dict[99] = 'FBC_SUMIN_3HOURS'
    dict[100] = 'FBC_SUMIN_4HOURS'
    dict[101] = 'FBC_SUMIN_5HOURS'
    dict[102] = 'FBC_SUMIN_6HOURS'
    dict[103] = 'FBC_SUMIN_12HOURS'
    dict[104] = 'FBC_SUMIN_24HOURS'
    dict[105] = 'FINAL_BUY_AMMOUNT'
    dict[106] = 'FBA_SUMIN_1MINUTE'
    dict[107] = 'FBA_SUMIN_2MINUTES'
    dict[108] = 'FBA_SUMIN_3MINUTES'
    dict[109] = 'FBA_SUMIN_4MINUTES'
    dict[110] = 'FBA_SUMIN_5MINUTES'
    dict[111] = 'FBA_SUMIN_10MINUTES'
    dict[112] = 'FBA_SUMIN_60MINUTES'
    dict[113] = 'FBA_SUMIN_2HOURS'
    dict[114] = 'FBA_SUMIN_3HOURS'
    dict[115] = 'FBA_SUMIN_4HOURS'
    dict[116] = 'FBA_SUMIN_5HOURS'
    dict[117] = 'FBA_SUMIN_6HOURS'
    dict[118] = 'FBA_SUMIN_12HOURS'
    dict[119] = 'FBA_SUMIN_24HOURS'
    dict[120] = 'FTP_DIS_1MINUTE'
    dict[121] = 'FTP_DIS_2MINUTE'
    dict[122] = 'FTP_DIS_3MINUTE'
    dict[123] = 'FTP_DIS_4MINUTE'
    dict[124] = 'FTP_DIS_5MINUTE'
    dict[125] = 'FTP_DIS_6MINUTE'
    dict[126] = 'FTP_DIS_7MINUTE'
    dict[127] = 'FTP_DIS_8MINUTE'
    dict[128] = 'FTP_DIS_9MINUTE'
    dict[129] = 'FTP_DIS_10MINUTE'
    dict[130] = 'FTP_DIS_15MINUTE'
    dict[131] = 'FTP_DIS_20MINUTE'
    dict[132] = 'FTP_DIS_30MINUTE'
    dict[133] = 'FTP_DIS_60MINUTE'
    dict[134] = 'FTP_DIS_2HOUR'
    dict[135] = 'FTP_DIS_3HOUR'
    dict[136] = 'FTP_DIS_4HOUR'
    dict[137] = 'FTP_DIS_5HOUR'
    dict[138] = 'FTP_DIS_6HOUR'
    dict[139] = 'FTP_DIS_12HOUR'
    dict[140] = 'FTP_DIS_18HOUR'
    dict[141] = 'FTP_DIS_24HOUR'
    dict[142] = 'FLG_UPDOWN_1MINUTE'
    dict[143] = 'FLG_UPDOWN_2MINUTE'
    dict[144] = 'FLG_UPDOWN_3MINUTE'
    dict[145] = 'FLG_UPDOWN_4MINUTE'
    dict[146] = 'FLG_UPDOWN_5MINUTE'
    dict[147] = 'FLG_UPDOWN_6MINUTE'
    dict[148] = 'FLG_UPDOWN_7MINUTE'
    dict[149] = 'FLG_UPDOWN_8MINUTE'
    dict[150] = 'FLG_UPDOWN_9MINUTE'
    dict[151] = 'FLG_UPDOWN_10MINUTE'
    dict[152] = 'FLG_UPDOWN_15MINUTE'
    dict[153] = 'FLG_UPDOWN_20MINUTE'
    dict[154] = 'FLG_UPDOWN_30MINUTE'
    dict[155] = 'FLG_UPDOWN_60MINUTE'
    dict[156] = 'FLG_UPDOWN_2HOUR'
    dict[157] = 'FLG_UPDOWN_3HOUR'
    dict[158] = 'FLG_UPDOWN_4HOUR'
    dict[159] = 'FLG_UPDOWN_5HOUR'
    dict[160] = 'FLG_UPDOWN_6HOUR'
    dict[161] = 'FLG_UPDOWN_12HOUR'
    dict[162] = 'FLG_UPDOWN_18HOUR'
    dict[163] = 'FLG_UPDOWN_24HOUR'
    dict[164] = 'LOW_5MINUTE'
    dict[165] = 'LOW_10MINUTE'
    dict[166] = 'LOW_15MINUTE'
    dict[167] = 'LOW_20MINUTE'
    dict[168] = 'LOW_30MINUTE'
    dict[169] = 'LOW_60MINUTE'
    dict[170] = 'LOW_2HOUR'
    dict[171] = 'LOW_3HOUR'
    dict[172] = 'LOW_4HOUR'
    dict[173] = 'LOW_5HOUR'
    dict[174] = 'LOW_6HOUR'
    dict[175] = 'LOW_12HOUR'
    dict[176] = 'LOW_18HOUR'
    dict[177] = 'LOW_24HOUR'
    dict[178] = 'HIGH_5MINUTE'
    dict[179] = 'HIGH_10MINUTE'
    dict[180] = 'HIGH_15MINUTE'
    dict[181] = 'HIGH_20MINUTE'
    dict[182] = 'HIGH_30MINUTE'
    dict[183] = 'HIGH_60MINUTE'
    dict[184] = 'HIGH_2HOUR'
    dict[185] = 'HIGH_3HOUR'
    dict[186] = 'HIGH_4HOUR'
    dict[187] = 'HIGH_5HOUR'
    dict[188] = 'HIGH_6HOUR'
    dict[189] = 'HIGH_12HOUR'
    dict[190] = 'HIGH_18HOUR'
    dict[191] = 'HIGH_24HOUR'
    return dict




if __name__ == '__main__':
    main()
