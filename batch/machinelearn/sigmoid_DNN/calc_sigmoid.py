#coding: utf-8

# 処理概要　「着順の分類分析」
# 機能名　「着順の分類(4割以内かどうか分析」
# 変更日 2017/10/21
'''
ディープラーニングの実行python

'''

##---------------------------
## ディープラーニングの雛形
##---------------------------

from sklearn.model_selection import train_test_split
from sklearn import datasets
import DNN_class
import numpy as np
import tensorflow as tf
import os
import sys
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
    from dataBaseAccess import Dao
    # utilクラスのオブジェクト取得
    utilClass = Util.Util(pid) 
    daoClass = Dao.Dao(pid,utilClass)
    # utilクラス、propatiesファイル、DBアクセスクラスまでのpathを取得する。

    # configファイルから情報を抜き出す.
    inifile = utilClass.inifile

    # path用の辞書を取得
    pathdict = getpath('')

    # 機械学習モデル出力パス
    machinepath = inifile.get('filepath','model')


    # ハイパーパラメータ
    data_num = 10000
    result_column = 142
    kensho_num = 10000
    n_in = 0
    n_out = 0
    
    # DBより学習データを取得する。
    where = ["WHERE DATA_MINING_RESULT_T.DATA_TIME >= '201709010000' AND DATA_MINING_RESULT_T.DATA_TIME < '2017110100000'"]
    dataList = daoClass.selectQuery(where,'machinelearn')

    # かうんと
    print(len(dataList))

    #return
    # 各パラメータをの配列を初期化する.
    x_predate = []
    y_predate = []


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
                resultlist.append(datainfo[result_column])
            
            # 学習データ格納
            if i not in ifList and i <= 119:
                paramlist.append(datainfo[i])
            

        if skipFlg == 1:
            continue
    
        x_predate.append(paramlist)
        y_predate.append(resultlist)

        input_num = len(paramlist)   

    # デバッグ


    # DNNで読み取れるデータに変換
    X_train = np.array(x_predate)
    Y_train = np.array(y_predate)
    
    
    # 学習データの準備 n_in=入力の次元 n_out=出力個数
    model = DNN_class.DNN(n_in = input_num,n_hiddens=[200,300,200],n_out = 1)
    n_in = input_num
    n_out = 1
    #model = DNN_class.DNN(n_in = input_num,n_hiddens=[1000,1500,1000],n_out = 1)
    
    # パス名を取得する
    path = pathdict[result_column]

    # 最終定期なパスを取得する。
    path = homeDir + machinepath + path


    # モデルの実行
    history = model.fit(X_train,Y_train,epochs=1,batch_size=100,p_keep=0.5,path=path)



def getpath(oath):
    dict = {}
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
