import pandas as pd
import numpy as np
import datetime as dt
from pykrx import stock
from dateutil.relativedelta import relativedelta

period=[]
begin=dt.datetime(2010,1,7)
while begin < dt.datetime(2012,3,1):
    period.append(begin)
    begin=begin+relativedelta(months=1)


size_factor=pd.DataFrame()
for a in period:
    dummy_size=stock.get_market_cap(a)
    dummy_size.sort_values(by=['시가총액'])
    #비중 결정
    value_sum=sum(dummy_size['시가총액'])
    dummy_size['비중']=dummy_size['시가총액']/value_sum
    n=len(dummy_size)
    #롱숏 결정
    dummy_size['포지션'] = [1] * (n//2) + [-1] * (n-n//2)
    dummy_size['투자비중']=dummy_size['비중']*dummy_size['포지션']
    
    #가격 정보
    dummy_price=stock.get_market_price_change(a, a+relativedelta(months=1), market='ALL')

    #수익률 내적
    size_factor[a]=dummy_size['투자비중']*dummy_price['등락률']
    print(a)

size_factor.to_csv('test_3.csv')


    
