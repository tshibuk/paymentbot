# coding: utf-8

from slackbot.bot import respond_to     # @botname: で反応するデコーダ
from slackbot.bot import listen_to      # チャネル内発言で反応するデコーダ
from slackbot.bot import default_reply  # 該当する応答がない場合に反応するデコーダ
import os
import pickle
import datetime
import pandas as pd
import numpy as np

#ID調査後、IDと名前を辞書配列で登録
ID_list = {'********':'Bob','*********':'Anne'}

#データをpickle化
def pickledata(data,directory,filename):
    if not os.path.isdir(directory):
        os.makedirs(directory)
    filepath = directory + '/' + filename + '.pickle'
    with open(filepath,'wb') as f:
        pickle.dump(data,f)

#pickleの読み出し
def unpickle(directory,filename):
    filepath = directory + '/' + filename + '.pickle'
    with open(filepath, 'rb') as f:
        loading = pickle.load(f)
    return loading

#ID調査
@respond_to('^ID')
def mention_func(message):
    userID = message.body['user']
    message.reply('Your ID:' + userID) #ID取得

#ディレクトリ作成
@respond_to(r'^make\s+\S.*')
def create_directory(message):
    text = message.body['text']
    message.reply(text)
    temp,directory = text.split(None,1)
    try:
        os.mkdir(directory)
        message.reply(directory + ' created')
    except:
        message.reply('error')
        
#支払情報登録
@listen_to(r'^pay\s+\S.*')
def save_payment(message):
    now = datetime.datetime.now()
    year_real = now.year
    month_real = now.month
    str_now = now.strftime('%Y/%m/%d')
    
    try:
        month_data = unpickle('payments','month')
        if month_data == month_real:
            now_dir = 'payments/' + '%04d' % year_real + '_' + '%02d' % month_real
            try:
                dataframe = unpickle(now_dir,'dataframe')
            except:
                dataframe = pd.DataFrame(index=[],columns=['Date','User','Money','Usage'])
        else:
            now_dir = 'payments/' + '%04d' % year_real + '_' + '%02d' % month_real
            os.mkdir(now_dir)
            dataframe = pd.DataFrame(index=[],columns=['Date','User','Money','Usage'])
            pickledata(month_real,'payments','month')
            message.reply(year_real + '_' + month_real + 'directory created')
    except:
        now_dir = 'payments/' + '%04d' % year_real + '_' + '%02d' % month_real
        os.mkdir(now_dir)
        dataframe = pd.DataFrame(index=[],columns=['Date','User','Money','Usage'])
        pickledata(month_real,'payments','month')
        message.reply('%04d' % year_real + '_' + '%02d' % month_real + ' directory created')
    
    text = message.body['text']
    userID = message.body['user']
    user = ID_list[userID]
    temp,money,usage = text.split(None,2)
    newdata = pd.DataFrame([[str_now,user,money,usage]],columns=['Date','User','Money','Usage'])
    dataframe = dataframe.append(newdata,ignore_index=True)
    pickledata(dataframe,now_dir,'dataframe')
    dataframe.to_csv(now_dir + '/payments.txt', encoding='cp932')
    dataframe.to_csv(now_dir + '/payments.csv', encoding='cp932')
    message.reply(str_now + ' ' + money + ' ' + usage + ' added')
    
#全員の支払い情報をチェック
@listen_to(r'^check')
def check_payment(message):
    now = datetime.datetime.now()
    year_real = now.year
    month_real = now.month
    now_dir = 'payments/' + '%04d' % year_real + '_' + '%02d' % month_real
    f = open(now_dir + '/payments.txt','r',encoding='cp932')
    msg = 'Your payments \n```' + f.read() + '```'
    message.reply(msg)
    f.close()
 
#支払情報を削除
@listen_to(r'^delete\s+\S.*')
def delete_data(message):
    userID = message.body['user']
    user = ID_list[userID]
    now = datetime.datetime.now()
    year_real = now.year
    month_real = now.month
    now_dir = 'payments/' + '%04d' % year_real + '_' + '%02d' % month_real
    dataframe = unpickle(now_dir,'dataframe')
    text = message.body['text']
    temp,index = text.split(None,1)
    index = int(index)
    if user != dataframe.loc[index,'User']:
        message.reply("You can't change other's data")
    else:
        dataframe = dataframe.drop(index)
        pickledata(dataframe,now_dir,'dataframe')
        dataframe.to_csv(now_dir + '/payments.txt', encoding='cp932')
        dataframe.to_csv(now_dir + '/payments.csv', encoding='cp932')
        f = open(now_dir + '/payments.txt','r',encoding='cp932')
        msg = 'data number ' + str(index) + ' deleted \n```' + f.read() + '```'
        message.reply(msg)
        f.close()

#支払情報を変更    
@listen_to(r'^change\s+\S.*')
def change_data(message):
    userID = message.body['user']
    user = ID_list[userID]
    now = datetime.datetime.now()
    year_real = now.year
    month_real = now.month
    now_dir = 'payments/' + '%04d' % year_real + '_' + '%02d' % month_real
    dataframe = unpickle(now_dir,'dataframe')
    text = message.body['text']
    temp,index,column,changedata = text.split(None,3)
    index = int(index)
    if user != dataframe.loc[index,'User']:
        message.reply("You can't change other's data")
    else:
        dataframe.loc[index,column] = changedata
        pickledata(dataframe,now_dir,'dataframe')
        dataframe.to_csv(now_dir + '/payments.txt', encoding='cp932')
        dataframe.to_csv(now_dir + '/payments.csv', encoding='cp932')
        f = open(now_dir + '/payments.txt','r',encoding='cp932')
        msg = 'data number ' + str(index) + ' changed \n```' + f.read() + '```'
        message.reply(msg)
        f.close()

#支払情報を変更(他人のも変更可能)
@listen_to(r'^change_master\s+\S.*')
def change_master(message):
    userID = message.body['user']
    user = ID_list[userID]
    now = datetime.datetime.now()
    year_real = now.year
    month_real = now.month
    now_dir = 'payments/' + '%04d' % year_real + '_' + '%02d' % month_real
    dataframe = unpickle(now_dir,'dataframe')
    text = message.body['text']
    temp,index,column,changedata = text.split(None,3)
    index = int(index)
    dataframe.loc[index,column] = changedata
    pickledata(dataframe,now_dir,'dataframe')
    dataframe.to_csv(now_dir + '/payments.txt', encoding='cp932')
    dataframe.to_csv(now_dir + '/payments.csv', encoding='cp932')
    f = open(now_dir + '/payments.txt','r',encoding='cp932')
    msg = 'data number ' + str(index) + ' changed \n```' + f.read() + '```'
    message.reply(msg)
    f.close()   

#自分の支払い情報を確認
@listen_to(r'^my_payments\s+\S.*')
def my_payments(message):
    userID = message.body['user']
    user = ID_list[userID]
    text = message.body['text']
    temp,year,month = text.split(None,2)
    year = int(year)
    month = int(month)
    now_dir = 'payments/' + '%04d' % year + '_' + '%02d' % month
    my_dir = 'users/' + user + '/' + now_dir
    try:
        dataframe = unpickle(now_dir,'dataframe')
        my_data = dataframe[dataframe['User'] == user]
        pickledata(my_data,my_dir,'my_data')
        payments = my_data['Money'].astype(np.int64)
        total_payment = payments.sum()
        my_data.to_csv(my_dir + '/payments.txt', encoding='cp932')
        my_data.to_csv(my_dir + '/payments.csv', encoding='cp932')
        f = open(my_dir + '/payments.txt','r',encoding='cp932')
        msg = user + ' ' + '%04d' % year + '_' + '%02d' % month + ' payments \n```' + f.read() + '\n Total Payment:' + str(total_payment) + '```'
        message.reply(msg)
        f.close()
    except:
        message.reply('No data for that month')
        