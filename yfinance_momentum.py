import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 애플 주가 데이터 다운로드
ticker = 'AAPL'
data = yf.download(ticker, start='2018-01-01', end='2018-12-31')

# 20일 이동 평균(SMA) 설정
sma_window = 20

# SMA 계산
data['SMA20'] = data['Close'].rolling(window=sma_window, min_periods=1).mean()

# 매수/매도 신호 생성
data['Signal'] = 0
data['Signal'][sma_window:] = np.where(data['Close'][sma_window:] > data['SMA20'][sma_window:], 1, 0)
data['Position'] = data['Signal'].diff()

# 전략 수익률 계산
data['Daily_Return'] = data['Close'].pct_change()

# 포지션 보유 상태를 반영
data['Position_Holding'] = data['Signal'].shift(1)

# 매수 및 매도 시점에서의 수익 계산
data['Entry_Price'] = np.where(data['Position'] == 1, data['Close'], np.nan)
data['Entry_Price'] = data['Entry_Price'].fillna(method='ffill')

data['Strategy_Return'] = np.where(data['Position_Holding'] == 1,
                                   (data['Close'] - data['Entry_Price']) / data['Entry_Price'],
                                   0)

# 매도 시점에서 수익률을 계산
data['Strategy_Return'] = np.where(data['Position'] == -1, (data['Close'] - data['Entry_Price']) / data['Entry_Price'], data['Strategy_Return'])
data['Strategy_Return'] = np.where(data['Position'] == 1, np.nan, data['Strategy_Return'])

# 누적 수익률 계산
data['Cumulative_Strategy_Return'] = (1 + data['Strategy_Return']).cumprod() - 1

# 결과 출력
data.to_csv('result.csv')


# 결과 출력
print(data[['Close', 'SMA20', 'Signal', 'Position', 'Strategy_Return', 'Cumulative_Strategy_Return']].tail())

# 시각화
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12), sharex=True)

# 첫 번째 플롯: 주가와 이동 평균, 매수 및 매도 신호
ax1.plot(data.index, data['Close'], label='Close Price', color='black', alpha=0.5)
ax1.plot(data.index, data['SMA20'], label='20-Day SMA', color='blue', alpha=0.75)
ax1.plot(data[data['Position'] == 1].index, 
         data['Close'][data['Position'] == 1], 
         '^', markersize=10, color='g', label='Buy Signal')
ax1.plot(data[data['Position'] == -1].index, 
         data['Close'][data['Position'] == -1], 
         'v', markersize=10, color='r', label='Sell Signal')

ax1.set_title('Apple Stock Price and 20-Day SMA with Buy/Sell Signals')
ax1.set_ylabel('Price')
ax1.legend(loc='upper left')
ax1.grid(True)

# 두 번째 플롯: 전략의 누적 수익률
ax2.plot(data.index, data['Cumulative_Strategy_Return'], label='Cumulative Strategy Return', color='green', linestyle='--')
ax2.set_title('Cumulative Strategy Return')
ax2.set_xlabel('Date')
ax2.set_ylabel('Cumulative Return')
ax2.legend(loc='upper left')
ax2.grid(True)

plt.tight_layout()
plt.show()

