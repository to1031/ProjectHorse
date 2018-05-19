# coding: utf-8

# 処理概要　「DeepNeralNetworkClass」
# 機能名　「ディープラーニングクラス」
# 変更日 2017/12/12
'''
ランダムフォレストのクラス化

'''
from sklearn.model_selection import train_test_split
from sklearn import datasets
import numpy as np
import os
import sys
import configparser
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
import sklearn.cross_validation as crv
from sklearn.metrics import accuracy_score
from sklearn.datasets import load_iris
from sklearn.externals import joblib
from collections import OrderedDict

class RFT(object):

    #初期化処理
    def __init__(self,pid):
        # プロジェクトのホームディレクトリを取得する。
        self.homeDir = os.environ["APPMONEYTRADE"]

        # iniconfigファイルを読み出す。
        condigPath = self.homeDir + 'conf'
        inifile = configparser.ConfigParser()
        inifile.read(condigPath + '/config.ini', 'UTF-8')
        self.inifile = inifile

        # 当サービスの機能IDを取得する。
        self.pid = pid

        # 呼び出し元も機能ID
        self.callel_pid =  __name__[0:3]


    # 引数 -> 学習データ(特徴,答え),モデルの保存先のパス
    def randomForestMikeModel_Class(self,X_train,Y_train,path,n_estimators=350, random_state=0):

        # 学習結果モデルの保存先のパスが存在するか確認する.
        # ここ後々実装させるかどうか

        # モデルを作成する。
        clf = RandomForestClassifier(n_estimators=n_estimators, random_state=random_state)
        clf.fit(X_train, Y_train)

        # ディレクトリが存在しない場合ディレクトリを作成する
        if not os.path.exists(path):
            os.mkdir(path)

        # 学習モデルを保存する.
        joblib.dump(clf, path + '/clf.pkl')

        # 学習結果を返却する。
        return clf


    # 学習モデルのロード
    def randomForestModelload(self,path):
        #学習モデルをロードする。
        clf = joblib.load(path + '/clf.pkl')

        # 学習結果を返す.
        return clf


    # 学習モデルの確からしさを確認する。
    def randomForestModelAccuracy(self,clf,X_test,Y_test):
        # モデルの予測結果を取得する。
        y_predict = clf.predict(X_test)

        # デバッグ
        print(y_predict)

        # accuracy_score
        resultScore = accuracy_score(Y_test, y_predict)

        # 返却する
        return resultScore


    # 特等量の影響度を取得する。-> [特徴量の格納]:[影響度]
    def randomForestModelImportance(self,clf):

        # 特徴量の影響度を取得する。
        feature = clf.feature_importances_
       
        # 特徴量の配列をループさせて辞書を作成する。
        dict = {}
        for i in range(len(feature)):
            dict[i] = feature[i]

        # 取得した辞書を影響度に高い順に変更する。
        dict = OrderedDict(sorted(dict.items(), key=lambda x:-x[1]))

        # 返却
        return dict
