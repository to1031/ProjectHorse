#coding: utf-8

# 処理概要　「着順の回帰分析」
# 機能名　「着順の回帰分析」
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

# main処理
def main():
    # 1時的に環境変数にパスを追加する。
    import sys
    sys.path.append('../../')
    from dataBaseAccessDNN import INSERTDICT
    from dataBaseAccessDNN import SELECTGET

    # ハイパーパラメータ
    data_num = 10000
    result_column = 88
    kensho_num = 10000
    n_in = 0
    n_out = 0
    
    # 計算するクラスを取得する。
    # POST_RACE_Tから予想すべきレースを取得する。
    where = ["WHERE RACE_DATE > '20170901' AND RACE_COND_MONEY != '01' AND RACE_SHOGAI_FLG != '1'"
                   " GROUP BY RACE_RANGE,RACE_PLACE,RACE_GROUND_FLG,RACE_TURN_FLG"]
    raceIdList = SELECTGET.MySQLselect('postraceid_group').selectexe(where)

    # レースID毎に処理をする。
    for raceInfo in raceIdList:
        # 情報を取得する。
        race_range = raceInfo[0]
        race_place = raceInfo[1]
        race_ground_flg = raceInfo[2]
        race_turn_flg = raceInfo[3]


        # 後で消す。一時的にスキップするものをつける
        if race_range + race_place + race_ground_flg == '1700011' or race_range + race_place + race_ground_flg == '20000100':
            print('temprary skip.leter delete')
            continue
        # コースIDの生成
        # 新潟：2000、京都：1400、京都：1600の場合は外か内かもつける。
        turn_flg_list = ['2000040','1400080','1600080']
        class_id = race_range + race_place + race_ground_flg
        if class_id in turn_flg_list:
            class_id = class_id + race_turn_flg
        
        # コースIDのディレクトリが存在しない場合は生成する。
        path = "./" + class_id
        if not os.path.exists(path):
            os.mkdir(path)
            
        
        # RACE_CLASS_Mから取得した情報をもとにテストでーた取得の条件を整える。
        where = ["WHERE CORSE_ID LIKE '%s'"% (class_id + '%')]
        raceClass = SELECTGET.MySQLselect('raceClass').selectexe(where)
    
        # 取得結果が 0000000 やない場合はskip
        if len(raceClass) == 0:
            print('skip because CLASS_VALUE is not getted from RACE_CLASS_M')
            continue
        else:
            if raceClass[0][0] == '00000000':
                print('skip because CLASS_VALUE is 00000000')
                continue
        # CLASS_VALUE から 取得すべきデータの条件文を整える。
        raceClassList = raceClass[0][0].split(',')
        orStr = ''
        for i in range(len(raceClassList)):
            orStr = orStr + "(RACE_PLACE = '%s' AND RACE_GROUND_FLG = '%s' AND RACE_RANGE_VALUE = '%s')" % (raceClassList[i][4:6],raceClassList[i][6:7],raceClassList[i][0:4])
            if i+1 != len(raceClassList):
                orStr = orStr + ' OR'
        
        whereStr = "WHERE LOGIC_DEL_FLG = '0' AND " + orStr
        print('selectstr is ' + whereStr)

        
        # DBからパラメータを取得する。
        where = [whereStr," ORDER BY RACE_ID DESC LIMIT %s"% data_num]
        paramObj_t = SELECTGET.MySQLselect('dnnpara1').selectexe(where)
   
        # 各パラメータをの配列を初期化する.
        x_predate = []
        y_predate = []
        
    
        # デバッグ テストタイプ
        argv = sys.argv
        testType = argv[1]
    
        # 引数チェック
        if testType == '' or testType is None:
            print('引数が設定されていないので処理を終了します。')
            return
    
    
        # 格納する番号を列挙する。
        ifList = [65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,84]
        # デバッグ
        input_num = 0
        # テストデータを格納する。
        for i in range(len(paramObj_t)):
            paramlist = []
            resultlist = []
            for j in range(1,85):
                if j in ifList:
                    paramlist.append(paramObj_t[i][j])
            
            resultlist.append(paramObj_t[i][result_column])
            input_num = len(paramlist)
    
            x_predate.append(paramlist)
            y_predate.append(resultlist)
     

        # DNNで読み取れるデータに変換
        X_train = np.array(x_predate)
        Y_train = np.array(y_predate)
    
    
        # デバッグ
        print(input_num)  
        # 学習データの準備 n_in=入力の次元 n_out=出力個数
        #model = DNN_class.DNN(n_in = input_num,n_hiddens=[2000,3000,2000],n_out = 1)
        n_in = input_num
        n_out = 1
        model = DNN_class.DNN(n_in = input_num,n_hiddens=[1000,1500,1000],n_out = 1)
    
    
        # モデルの実行
        history = model.fit(X_train,Y_train,epochs=100,batch_size=100,p_keep=0.5,path=path)

if __name__ == '__main__':
    main()
