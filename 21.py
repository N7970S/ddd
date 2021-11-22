import time
import datetime
import pyupbit
import pandas as pd
k=pd.Series()

x = 30
minimum = 10000
limit = 20
ratio = 2
now = datetime.datetime.now()

access = "9k5gGxbmhqBuXXPlZsu9s57AJi3kTojPfh6wShQ5"
secret = "NyoLuuB2UxGnBo3WYXNtGL2Kzz9loOSmNtp456my"

price = pyupbit.get_current_price
upbit = pyupbit.Upbit(access, secret)
tickers=pyupbit.get_tickers(fiat="KRW") 


while True:
    try:
        
        now = datetime.datetime.now()
        nowm = now.strftime('%M')
        
        ########## 업비트 현재가로 평가금 확인, 미체결 금액 확인
        if x-2 < int(nowm) :
            upbit.get_order("KRW-BTC")

            if x-1 < int(nowm) :

                quity = 0
                tailtotal = 0
                for ticker in tickers :
                    v=price(ticker)*upbit.get_balance(ticker)
                    quity += v
                    pending = upbit.get_order(ticker)
                    if len(pending) > 0 :
                        for o in range(0,len(pending)) :
                            tail = float(pending[o]['remaining_volume'])*float(pending[o]['price'])
                            tailtotal += tail
                upbitjango = upbit.get_balance("KRW") + quity + tailtotal

                nowf = now.strftime('%Y-%m-%d %H:%M') 
                T = nowf+"\nUpbit : "+str(int(upbitjango))
                time.sleep(3300-(int(nowm)-x)*60)
    
        tickers=pyupbit.get_tickers(fiat="KRW")
        for ticker1 in tickers :
            pending1 = upbit.get_order(ticker1)
            lp1=len(pending1)
            tailtotal = 0
            if lp1 > 0 :
                tail = 0
                tails = 0
                for o in range(0,lp1) :
                    now = datetime.datetime.now()
                    nowDatetime = now.strftime('%Y-%m-%d %H:%M:%S')
                    tail = int(float(pending1[o]['remaining_volume'])*float(pending1[o]['price'])+0.1)
                    tails += tail
                tailtotal += tails
                ##print(nowDatetime,ticker1,"미체결 수 :", str(len(pending1)),"미체결 금액 :", str(tails))
            time.sleep(0.4)
        ################ 미체결 끝 ###############
        
        ###print("###### 거래량 상위 시작 ######")
        for ticker2 in tickers:
           df = pyupbit.get_ohlcv(ticker2,interval="minute240",count=4)
           Coins = 35
           q=upbit.get_balance(ticker2)
           p = float(df['close'][3])
           v = float(df['value'][0]) + float(df['value'][1]) + float(df['value'][2]) + float(df['value'][3])
           if (1000< p <2500) or (100< p <500) or (10< p <50) or (1< p <5) or (0.1< p <0.5) or (p <0.05) :
               v2=0
           else :
               v2=v
           k[ticker2]=float(v2)
           l=k.sort_values(ascending=False)
           vsup=l[0:Coins]
        
        for ticker2 in tickers:
            df2 = pyupbit.get_ohlcv(ticker2,interval="minute240",count=4)
            v = float(df2['value'][0]) + float(df2['value'][1]) + float(df2['value'][2]) + float(df2['value'][3])
            k[ticker2] = float(v)
            time.sleep(0.2)
            
        l=k.sort_values(ascending=False)
        vsup2=l[0:Coins]
        vinf2=l[Coins:len(l)]

        ##### print("###### 비중 조절 시작 ######")
        for b in range(0,Coins) :
            ticker3=vsup2.index[b]
            p=pyupbit.get_current_price(ticker3)
            q=upbit.get_balance(ticker3)
            time.sleep(0.2)
            ##print(b, ticker3, "현재 종가",str(p), "현재 평가금",str(p*q) )
                 
            if p*q > minimum * (1-limit/100) / ratio :
                print(ticker3,p*q)

            else :                    
                if p*q > minimum * (1+limit/100):
                    upbit.sell_limit_order(ticker3,p,q-minimum/p)
                    ## print(ticker3,"기본 금액 제외 매도") 
                    tickers=pyupbit.get_tickers(fiat="KRW")
                    for ticker3 in tickers:
                        pending3 = upbit.get_order(ticker3)
                        lp3=len(pending3)
                        ## print(ticker3,lp3)
                        if lp3 > 0 :
                            for o3 in range(0,lp3) :
                                if ( str(pending3[o3]['side']) == 'ask' ) and ( str(pending3[o3]['state']) == 'wait' ) :
                                    upbit.cancel_order(pending3[o3]['uuid'])
                                    ticP = pyupbit.get_tick_size(pyupbit.get_current_price(ticker3) * 0.90)
                                    upbit.sell_limit_order(ticker3, ticP, float(pending3[o3]['remaining_volume']))                                                   
                
                if p*q< minimum * (1-limit/100) :
                    upbit.buy_limit_order(ticker3,p,minimum/p-q)

        ############### 자산재분배 ###################################
        for s in range(0,len(l)-Coins) :
            ticker4=vinf2.index[s]
            p= pyupbit.get_current_price(ticker4)
            q=upbit.get_balance(ticker4)
            ## print(s, ticker4, "현재 종가",str(p), "현재 평가금",str(p*q) )

            if q > 0 :
                if p*q> ((1-limit/100) / ratio) * minimum:
                    print(ticker4,p*q)
                else :
                    if 1+limit/100<p*q/minimum<((1-limit/100)/ratio):
                        ##print(ticker4,"자산 일부 매도")
                        upbit.sell_limit_order(ticker4, p,(1+limit/100)*minimum/p)
                    else:
                        if p*q - limit/100 * minimum< 5000 :
                            ##print(ticker4,"자산 전체 매도")
                            upbit.sell_limit_order(ticker4,p,q)
                        else :
                            ##print(ticker4,"자산 최소 금액 * ",str(limit),"% 매도")
                            upbit.sell_limit_order(ticker4,p,limit*minimum/(100*p))
                
    except Exception as err:
        print(err)
    time.sleep(10)