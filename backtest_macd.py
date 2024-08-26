import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Function to calculate MACD (unchanged)
def calculate_macd(data, fast_period=12, slow_period=26, signal_period=9):
    ema_fast = data['Close'].ewm(span=fast_period, adjust=False).mean()
    ema_slow = data['Close'].ewm(span=slow_period, adjust=False).mean()
    macd = ema_fast - ema_slow
    signal = macd.ewm(span=signal_period, adjust=False).mean()
    histogram = macd - signal
    return macd, signal, histogram

# Updated function to backtest the MACD strategy
def backtest_macd_strategy(symbol, start_date, end_date, initial_fund, risk_percent=1, risk_reward_ratio=1.5):
    # Fetch historical data
    data = yf.download(symbol, start=start_date, end=end_date, interval="1h")
    
    # Calculate MACD
    data['MACD'], data['Signal'], data['Histogram'] = calculate_macd(data)
    
    # Initialize variables
    position = 0
    entry_price = 0
    stop_loss = 0
    take_profit = 0
    trades = []
    current_fund = initial_fund
    
    # Iterate through the data
    for i in range(1, len(data)):
        if position == 0:
            if data['MACD'].iloc[i] > data['Signal'].iloc[i] and data['MACD'].iloc[i-1] <= data['Signal'].iloc[i-1]:
                # Buy signal
                position = 1
                entry_price = data['Close'].iloc[i]
                risk_amount = current_fund * (risk_percent / 100)
                position_size = risk_amount / (entry_price * 0.01)  # 1% stop loss
                stop_loss = entry_price * 0.99
                take_profit = entry_price * (1 + risk_reward_ratio / 100)
        elif position == 1:
            if data['Close'].iloc[i] <= stop_loss or data['Close'].iloc[i] >= take_profit or (data['MACD'].iloc[i] < data['Signal'].iloc[i] and data['MACD'].iloc[i-1] >= data['Signal'].iloc[i-1]):
                # Close position
                exit_price = data['Close'].iloc[i]
                profit = (exit_price - entry_price) * position_size
                current_fund += profit
                trades.append({'Entry': entry_price, 'Exit': exit_price, 'Profit': profit, 'Fund': current_fund})
                position = 0
    
    return trades, current_fund

# Run backtest
symbol = "BTC-USD"
start_date = datetime.now() - timedelta(days=365)  # 1 year of data
end_date = datetime.now()
initial_fund = 500  # Starting fund of 500 USD

trades, final_fund = backtest_macd_strategy(symbol, start_date, end_date, initial_fund)

# Calculate performance metrics
total_trades = len(trades)
winning_trades = sum(1 for trade in trades if trade['Profit'] > 0)
losing_trades = total_trades - winning_trades
win_rate = winning_trades / total_trades if total_trades > 0 else 0
average_profit = sum(trade['Profit'] for trade in trades) / total_trades if total_trades > 0 else 0

print(f"Initial fund: ${initial_fund}")
print(f"Final fund: ${final_fund:.2f}")
print(f"Total profit/loss: ${final_fund - initial_fund:.2f}")
print(f"Total trades: {total_trades}")
print(f"Winning trades: {winning_trades}")
print(f"Losing trades: {losing_trades}")
print(f"Win rate: {win_rate:.2%}")
print(f"Average profit per trade: ${average_profit:.2f}")