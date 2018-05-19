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
import os
from sklearn.ensemble import RandomForestClassifier


# main処理
def main():
    # 1時的に環境変数にパスを追加する。
    import sys
    sys.path.append('../')
    from dataBaseAccessDNN import INSERTDICT
    from dataBaseAccessDNN import SELECTGET
    from dataBaseAccessDNN import UPDATEDICT
    
    # 計算するクラスを取得する。
    # POST_RACE_Tから予想すべきレースを取得する。
    where = ["WHERE RACE_DATE > '20180216' AND RACE_COND_MONEY != '01' AND RACE_SHOGAI_FLG != '1' AND RACE_NO = '10'",
                   " GROUP BY RACE_RANGE,RACE_PLACE,RACE_GROUND_FLG,RACE_TURN_FLG"]
    raceIdList = SELECTGET.MySQLselect('postraceid_group').selectexe(where)

    # レースID毎に処理をする。
    for raceInfo in raceIdList:
        # 情報を取得する。
        race_range = raceInfo[0]
        race_place = raceInfo[1]
        race_ground_flg = raceInfo[2]
        race_turn_flg = raceInfo[3]
        
       # コースIDの生成
        # 新潟：2000、京都：1400、京都：1600の場合は外か内かもつける。
        turn_flg_list = ['2000040','1400080','1600080']
        class_id = race_range + race_place + race_ground_flg
        if class_id in turn_flg_list:
            class_id = class_id + race_turn_flg
   
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
 


        ##=====================================================
        ## 機械学習結果がない場合はスキップする。
        if not os.path.exists('./relu_DNN/' +  class_id + '/checkpoint'):
            print('skip because relu_DNN not exist')
            continue

        if not os.path.exists('./relu_DNN_notwithOdds/' +  class_id + '/checkpoint'):
            print('skip because relu_DNN not exist')
            continue

        if not os.path.exists('./sigmoid_DNN/' +  class_id + '/checkpoint'):
            print('skip because relu_DNN not exist')
            continue

        if not os.path.exists('./sigmoid_DNN_notwithOdds/' +  class_id + '/checkpoint'):
            print('skip because relu_DNN not exist')
            continue

        if not os.path.exists('./sigmoid_after_DNN/' +  class_id + '/checkpoint'):
            print('skip because relu_DNN not exist')
            continue



       
        
        # 着順予想を取得する。POST_RACE_DETAIL_Tから条件に合うレースを取得する。
        where = ["WHERE RACE_PLACE = '%s' AND RACE_GROUND_FLG = '%s' AND RACE_RANGE_VALUE = '%s'"% (race_place,race_ground_flg,race_range)]
        paramObj_k = SELECTGET.MySQLselect('dnnpara2').selectexe(where)
        
        ##====================================================
        ## 準備
        # 格納する番号を列挙する。
        dnnList = [65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,84]
        rftList = [65,71,76,77,78,79,84,106,101,98,67,68,69,70,66,89,90,91]
        # デバッグ
        input_num = 0
        
        # 格納するリスト
        dnn_X_test = []
        rft_X_test = []
        
        # レースIDとスタートの順番
        keyList = []
        # テストデータを格納する。
        for i in range(len(paramObj_k)):
            dnn = []
            rft = []
            for j in range(1,85):
                if j in dnnList:
                    dnn.append(paramObj_k[i][j])

            for j in range(1,107):
                if j in rftList:
                    rft.append(paramObj_k[i][j])
            
            input_num = len(dnn)
            dnn_X_test.append(dnn)
            rft_X_test.append(rft)
            keyList.append([paramObj_k[i][83],paramObj_k[i][0]])
        
        
        #  馬番とレースIDのみ最初にinsertしておく。
        for key in keyList:
            raceid = key[0]
            startnum = key[1]
            where = ["WHERE RACE_ID = '%s' AND START_NUM = '%s'"% (raceid,startnum)]
            result = SELECTGET.MySQLselect('getnumindex').selectexe(where)
            if result[0][0] != 0:
                continue
            insertDict = {}
            insertDict['LOGIC_DEL_FLG'] = '0'
            insertDict['INS_PID'] = 'masuyama'
            insertDict['UPD_PID'] = 'masuyama'
            insertDict['RACE_ID'] = raceid
            insertDict['START_NUM'] = startnum
            INSERTDICT.MySQL('POST_RACE_INDEX_T',insertDict)
        
        ##=====================================================
        ## 着順の予想を取得する。
        if not os.path.exists('./relu_DNN/' +  class_id + '/checkpoint'):
            print('skip because relu_DNN not exist')
        
        # relu をいんぽーと
        sys.path.append('./')
        from relu_DNN import DNN_class as relu
        model = relu.DNN(n_in = input_num,n_hiddens=[1000,1500,1000],n_out = 1)
        dnnResult = model.getRestore(dnn_X_test,'relu_DNN/' + class_id)
        for i in range(len(dnnResult)):
            raceid = keyList[i][0]
            startnum = keyList[i][1]
            value = dnnResult[i][0]
            updateDict = {}
            updateDict['GOAL_NUM_RELU'] = value
            where = "WHERE RACE_ID = '%s' AND START_NUM = '%s'"% (raceid,startnum)
            UPDATEDICT.MySQLUpdate('POST_RACE_INDEX_T',updateDict,where)
        ##=====================================================
        ##=====================================================
        ## 4割いないかどうか
        if not os.path.exists('./sigmoid_DNN/' +  class_id + '/checkpoint'):
            print('skip because relu_DNN not exist')
        
        # relu をいんぽーと
        sys.path.append('./')
        from sigmoid_DNN import DNN_class as sigmoid1
        model = sigmoid1.DNN(n_in = input_num,n_hiddens=[2000,3000,2000],n_out = 1)
        dnnResult = model.getRestore(dnn_X_test,'sigmoid_DNN/' + class_id)
        for i in range(len(dnnResult)):
            raceid = keyList[i][0]
            startnum = keyList[i][1]
            value = dnnResult[i][0]
            updateDict = {}
            updateDict['GOAL_NUM_SIG'] = value
            where = "WHERE RACE_ID = '%s' AND START_NUM = '%s'"% (raceid,startnum)
            UPDATEDICT.MySQLUpdate('POST_RACE_INDEX_T',updateDict,where)
        ##=====================================================
        ##=====================================================
        ## 6割以上かかどうか
        if not os.path.exists('./sigmoid_after_DNN/' +  class_id + '/checkpoint'):
            print('skip because sigmoid_after_DNN not exist')
        
        # relu をいんぽーと
        sys.path.append('./')
        from sigmoid_after_DNN import DNN_class as sigmoid2
        model = sigmoid2.DNN(n_in = input_num,n_hiddens=[2000,3000,2000],n_out = 1)
        dnnResult = model.getRestore(dnn_X_test,'sigmoid_after_DNN/' + class_id)
        for i in range(len(dnnResult)):
            raceid = keyList[i][0]
            startnum = keyList[i][1]
            value = dnnResult[i][0]
            updateDict = {}
            updateDict['AFTER_ORNOT_SIG'] = value
            where = "WHERE RACE_ID = '%s' AND START_NUM = '%s'"% (raceid,startnum)
            UPDATEDICT.MySQLUpdate('POST_RACE_INDEX_T',updateDict,where)
        ##=====================================================
        #　ここからランダムフォレスト
        #    ハイパーパラメータの用意
        data_num = 10000
        # DBからパラメータを取得する。
        where = [whereStr," ORDER BY RACE_ID,STAN_START_NUM DESC LIMIT %s"% data_num]
        paramObj_t = SELECTGET.MySQLselect('dnnpara1').selectexe(where)

        print(len(paramObj_t))
        ##=====================================================
        ## RFTの3着以内かどう
        class_num = 81
        x_predate = []
        y_predate = []
        # テスとデータを調整する。
        for i in range(len(paramObj_t)):
            paramlist = []
            resultlist = []
            for j in range(1,108):
                if j in rftList:
                    paramlist.append(paramObj_t[i][j])
            
            x_predate.append(paramlist)
            y_predate.append(paramObj_t[i][class_num])
        
        X_train = np.array(x_predate)
        Y_train = np.array(y_predate)
        # 学習させる
        clf = None
        clf = RandomForestClassifier(n_estimators=350, random_state=0)
        #clf = RandomForestClassifier(n_estimators=400, random_state=0)
        clf.fit(X_train, Y_train)
        rftResult = clf.predict(rft_X_test)

        for i in range(len(rftResult)):
            raceid = keyList[i][0]
            startnum = keyList[i][1]
            value = rftResult[i]
            updateDict = {}
            updateDict['FUKU_ORNOT_RFT'] = value
            where = "WHERE RACE_ID = '%s' AND START_NUM = '%s'"% (raceid,startnum)
            UPDATEDICT.MySQLUpdate('POST_RACE_INDEX_T',updateDict,where)
        
        X_train = None
        Y_train = None
        ##=====================================================
        ##=====================================================
        ## RFTの前半かどうか
        class_num = 80
        x_predate = []
        y_predate = []
        # テスとデータを調整する。
        for i in range(len(paramObj_t)):
            paramlist = []
            resultlist = []
            for j in range(1,108):
                if j in rftList:
                    paramlist.append(paramObj_t[i][j])
            
            x_predate.append(paramlist)
            y_predate.append(paramObj_t[i][class_num])
        
        X_train = np.array(x_predate)
        Y_train = np.array(y_predate)
        # 学習させる
        clf = None
        clf = RandomForestClassifier(n_estimators=350, random_state=0)
        #clf = RandomForestClassifier(n_estimators=400, random_state=0)
        clf.fit(X_train, Y_train)
        rftResult = clf.predict(rft_X_test)

        for i in range(len(rftResult)):
            raceid = keyList[i][0]
            startnum = keyList[i][1]
            value = rftResult[i]
            updateDict = {}
            updateDict['HALF_ORNOT_RFT'] = value
            where = "WHERE RACE_ID = '%s' AND START_NUM = '%s'"% (raceid,startnum)
            UPDATEDICT.MySQLUpdate('POST_RACE_INDEX_T',updateDict,where)
        
        X_train = None
        Y_train = None
        ##=====================================================

       # オッズなしのパターンを計算する。





        ##====================================================
        ## 準備
        # 格納する番号を列挙する。
        dnnList = [65,66,67,68,69,70,72,73,74,75,76,77,78,79,84]
        rftList = [65,76,77,78,79,84,106,101,98,67,68,69,70,66,89,90,91]
        # デバッグ
        input_num = 0

        # 格納するリスト
        dnn_X_test = []
        rft_X_test = []

        # レースIDとスタートの順番
        keyList = []
        # テストデータを格納する。
        for i in range(len(paramObj_k)):
            dnn = []
            rft = []
            for j in range(1,85):
                if j in dnnList:
                    dnn.append(paramObj_k[i][j])

            for j in range(1,107):
                if j in rftList:
                    rft.append(paramObj_k[i][j])

            input_num = len(dnn)
            dnn_X_test.append(dnn)
            rft_X_test.append(rft)
            keyList.append([paramObj_k[i][83],paramObj_k[i][0]])




        ##=====================================================

        ##=====================================================
        ## 4割いないかどうか(オッズなし)
        if not os.path.exists('./sigmoid_DNN_notwithOdds/' +  class_id + '/checkpoint'):
            print('skip because relu_DNN not exist')

        # sigmoid をいんぽーと
        sys.path.append('./')
        from sigmoid_DNN_notwithOdds import DNN_class as sigmoid3
        model = sigmoid3.DNN(n_in = input_num,n_hiddens=[2000,3000,2000],n_out = 1)
        dnnResult = model.getRestore(dnn_X_test,'sigmoid_DNN_notwithOdds/' + class_id)
        for i in range(len(dnnResult)):
            raceid = keyList[i][0]
            startnum = keyList[i][1]
            value = dnnResult[i][0]
            updateDict = {}
            updateDict['GOAL_NUM_SIG_NOODDS'] = value
            where = "WHERE RACE_ID = '%s' AND START_NUM = '%s'"% (raceid,startnum)
            UPDATEDICT.MySQLUpdate('POST_RACE_INDEX_T',updateDict,where)
        ##=====================================================
        ## 着順の予想を取得する。（オッズなし）
        if not os.path.exists('./relu_DNN_notwithOdds/' +  class_id + '/checkpoint'):
            print('skip because relu_DNN not exist')

        # relu をいんぽーと
        sys.path.append('./')
        from relu_DNN_notwithOdds import DNN_class as relu1
        model = relu1.DNN(n_in = input_num,n_hiddens=[1000,1500,1000],n_out = 1)
        dnnResult = model.getRestore(dnn_X_test,'relu_DNN_notwithOdds/' + class_id)
        for i in range(len(dnnResult)):
            raceid = keyList[i][0]
            startnum = keyList[i][1]
            value = dnnResult[i][0]
            updateDict = {}
            updateDict['GOAL_NUM_RELU_NOODDS'] = value
            where = "WHERE RACE_ID = '%s' AND START_NUM = '%s'"% (raceid,startnum)
            UPDATEDICT.MySQLUpdate('POST_RACE_INDEX_T',updateDict,where)


        ## RFTの前半かどうか
        class_num = 81
        x_predate = []
        y_predate = []
        # テスとデータを調整する。
        for i in range(len(paramObj_t)):
            paramlist = []
            resultlist = []
            for j in range(1,108):
                if j in rftList:
                    paramlist.append(paramObj_t[i][j])
            
            x_predate.append(paramlist)
            y_predate.append(paramObj_t[i][class_num])
        
        X_train = np.array(x_predate)
        Y_train = np.array(y_predate)
        # 学習させる
        clf = None
        clf = RandomForestClassifier(n_estimators=350, random_state=0)
        #clf = RandomForestClassifier(n_estimators=400, random_state=0)
        clf.fit(X_train, Y_train)
        rftResult = clf.predict(rft_X_test)
            
        for i in range(len(rftResult)):
            raceid = keyList[i][0]
            startnum = keyList[i][1]
            value = rftResult[i]
            updateDict = {}
            updateDict['FUKU_ORNOT_RFT_NOODDS'] = value
            where = "WHERE RACE_ID = '%s' AND START_NUM = '%s'"% (raceid,startnum)
            UPDATEDICT.MySQLUpdate('POST_RACE_INDEX_T',updateDict,where)
        

        ## RFTの前半かどうか
        class_num = 80
        x_predate = []
        y_predate = []
        # テスとデータを調整する。
        for i in range(len(paramObj_t)):
            paramlist = []
            resultlist = []
            for j in range(1,108):
                if j in rftList:
                    paramlist.append(paramObj_t[i][j])

            x_predate.append(paramlist)
            y_predate.append(paramObj_t[i][class_num])

        X_train = np.array(x_predate)
        Y_train = np.array(y_predate)
        # 学習させる
        clf = None
        clf = RandomForestClassifier(n_estimators=350, random_state=0)
        #clf = RandomForestClassifier(n_estimators=400, random_state=0)
        clf.fit(X_train, Y_train)
        rftResult = clf.predict(rft_X_test)

        for i in range(len(rftResult)):
            raceid = keyList[i][0]
            startnum = keyList[i][1]
            value = rftResult[i]
            updateDict = {}
            updateDict['HALF_ORNOT_RFT_NOODDS'] = value
            where = "WHERE RACE_ID = '%s' AND START_NUM = '%s'"% (raceid,startnum)
            UPDATEDICT.MySQLUpdate('POST_RACE_INDEX_T',updateDict,where)

        X_train = None
        Y_train = None


if __name__ == '__main__':
    main()
