# coding: utf-8

# 処理概要　「DeepNeralNetworkClass」
# 機能名　「ディープラーニングクラス」
# 変更日 2017/12/12
'''
 ニューラルネットワークのクラス化

'''
import numpy as np
import tensorflow as tf
from  sklearn.utils import shuffle


class DNN(object):

    #初期化処理
    def __init__(self,n_in,n_hiddens, n_out):
        self.n_in = n_in
        self.n_hiddens = n_hiddens
        self.n_out = n_out
        self.weights = []
        self.biases = []
        self.x_ = None
        self.t_ = None
        self.y_ = None
        self.keep_prob = None
        self.acuracy_ = None
        self._sess = None
        self._history = {
                  'loss' : [],
                  'acuracy' : [],
                  'class':[]
             }
        tf.reset_default_graph()
         
    # 重みの設定
    def weight_variable(self,shape,name=None):
        initial = tf.truncated_normal( shape , stddev = 0.01)
        return tf.Variable(initial,name=name)


    # バイアスの設定
    def bias_variable(self,shape,name=None):
        initial = tf.zeros(shape)
        return tf.Variable(initial,name=name)


    # モデルの定義
    def interface(self,x,keep_prob):
        # 入力層・隠れ層 / 隠れ層・隠れ層
        for i , n_hidden in enumerate(self.n_hiddens):
            if i == 0:
                # 入力層
                input = x
                input_dim = self.n_in
            else:
                # 隠れ層 / 隠れ層 
                input = output
                input_dim = self.n_hiddens[i - 1]
    
            self.weights.append(self.weight_variable([input_dim,n_hidden],name='W_{}'.format(i)))
            self.biases.append(self.bias_variable([n_hidden],name='b_{}'.format(i)))
    
    
            h = tf.nn.relu(tf.matmul(input,self.weights[-1]) + self.biases[-1])
            output = tf.nn.dropout(h , keep_prob)
    
    
        # 隠れ層 / 出力層 
        self.weights.append(self.weight_variable([self.n_hiddens[-1],self.n_out],name='W_{}'.format(len(self.n_hiddens))))
        self.biases.append(self.bias_variable([self.n_out],name='b_{}'.format(len(self.n_hiddens))))
         
        # 計算
        # y = tf.nn.softmax(tf.matmul(output,self.weights[-1]) + self.biases[-1])
        # シグモイド関数で実装する。
        # y = tf.nn.sigmoid(tf.matmul(output,self.weights[-1]) + self.biases[-1])
        # 双曲線関数を利用
        # y = tf.nn.tanh(tf.matmul(output,self.weights[-1]) + self.biases[-1])
        y = tf.nn.relu(tf.matmul(output,self.weights[-1]) + self.biases[-1])
        return y


    # 誤差関数の定義
    def loss(self , y ,t):
          # cross_entropy = tf.reduce_mean(-tf.reduce_sum(t * tf.log(y),reduction_indices=[1]))
          # cross_entropy = - tf.reduce_sum(t * tf.log(y)+ ( 1- t )*tf.log(1-y))
          cross_entropy = tf.reduce_sum(tf.square(y - t))
          return cross_entropy
    

    # 学習アルゴリズの定義
    def training(self,loss):
        #optimaizer = tf.train.GradientDescentOptimizer(0.01)
        optimaizer = tf.train.AdagradOptimizer(0.01)
        
        train_step = optimaizer.minimize(loss)
        return train_step


    # 学習の評価
    def acuracy(self,y,t):
        # correct_prediction = tf.equal(tf.argmax(y,1),tf.argmax(t,1))
        correct_prediction = tf.equal(tf.to_float(tf.greater(y,0.5)),t)
        acuracy = tf.reduce_mean(tf.cast(correct_prediction,tf.float32)) 
        return acuracy



    # 学習の処
    def fit(self,X_train,Y_train,epochs=100,batch_size=100,p_keep=0.5,verbose=1,path=None):
        x = tf.placeholder(tf.float32, shape=[None,self.n_in],name='input')
        t = tf.placeholder(tf.float32, shape=[None,self.n_out])
        keep_prob = tf.placeholder(tf.float32)        

        self.x_ = x
        self.t_ = t
        self.keep_prob = keep_prob


        y = self.interface(x,keep_prob)
        self.y_ = y 
        loss = self.loss(y,t)
        train_step = self.training(loss)
        acuracy = self.acuracy(y,t)
        self.acuracy_ = acuracy

        init = tf.global_variables_initializer()
        sess = tf.Session()
        sess.run(init)

        self._sess = sess
        
        # モデルの保村
        saver = tf.train.Saver()       
        

        N_train = len(X_train)
        n_batches = N_train // batch_size
        
        for epoch in range(epochs):
            X_,Y_ = shuffle(X_train,Y_train)
            
            for i in range(n_batches):
                start = i * batch_size
                end = start + batch_size
    
    
    
                sess.run(train_step,feed_dict = {
                    x : X_[start:end],
                    t : Y_[start:end],
                    keep_prob : p_keep
                })
    
            loss_ = loss.eval(session=sess,feed_dict = {
                    x : X_train,
                    t : Y_train,
                    keep_prob : 0.5
                })
    
    
            acuracy_ = acuracy.eval(session=sess,feed_dict = {
                    x : X_train,
                    t : Y_train,
                    keep_prob : 0.5
                })

            self._history['acuracy'].append(acuracy_)
            self._history['loss'].append(loss_)
    
            if verbose:
                print('epoch:',epoch,' loss:',loss_,' acuracy:',acuracy_)
        
        # モデルの保存
        saver.save(sess, path + "/model.ckpt")    
        return self._history


    # 学習の評価処理
    def evaluate(self,X_test,Y_test):
        return self.acuracy_.eval(session=self._sess,feed_dict = {
                self.x_ : X_test,
                self.t_ : Y_test,
                self.keep_prob : 0.5
               })


    # 学習結果からの確立を取得する。
    def getrate(self,X_test):
         prob = self.y_.eval(session=self._sess,feed_dict = {
             self.x_ : X_test,
             self.keep_prob : 1.0
             })
         self._sess.close
         return prob


    # 学習結果を復元する。
    def getRestore(self,X_test,path):
        tf.reset_default_graph()
        x = tf.placeholder(tf.float32, shape=[None,self.n_in],name='input')
        t = tf.placeholder(tf.float32, shape=[None,self.n_out])
        keep_prob = tf.placeholder(tf.float32)        

        self.x_ = x
        self.t_ = t
        self.keep_prob = keep_prob


        y = self.interface(x,keep_prob)
        loss = self.loss(y,t)
        train_step = self.training(loss)
        acuracy = self.acuracy(y,t)
        self.acuracy_ = acuracy

        saver = tf.train.Saver()
        sess = tf.Session()
        self._sess = sess
           
        saver.restore(sess, "./" + path + "/model.ckpt") 
        result_prob2 = y.eval(session=sess,feed_dict = {
             x : X_test,
             keep_prob : 1.0
             })
        return result_prob2
