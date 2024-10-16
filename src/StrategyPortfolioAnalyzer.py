import os
import pandas as pd
from datetime import datetime
import numpy as np
import plotly.graph_objects as go
import plotly.figure_factory as ff

# How to put the CSV file of all the trades from your back test in the same folder
# ENSURE YOU ARE IN THE FILE DIRECTORY THAT YOU THINK YOU ARE. DIFFERENT IDE'S DO DIFFERENTLY. 
print("Working directory: ", os.getcwd())


# Setup 
files = os.listdir() # list of files in current directory
dfm = pd.DataFrame() # will hold the dataset that we're constructing
dfc = pd.DataFrame() # will hold the dataset that we're constructing 
content = [] # to be list of DataFrames later to be concatenated 

# Function to convert the date/time strings (that NinjaTrader exports) to datetime objects
# ---------------------------------------------------------------------------------------------
def convert_datetime(x):
    date_format = '%m/%d/%Y %H:%M:%S %p'
    date = datetime.strptime(x, date_format)
    return date
# ---------------------------------------------------------------------------------------------
# Function to convert NinjaTrader currency strings to numbers that we can work with
def convert_profit(x):
    x = x.replace('$','')
    x = x.replace('(','-')
    x = x.replace(')','')
    return x
# ---------------------------------------------------------------------------------------------
# FUNCTION FOR CALCULATING CUMULATIVE DRAWDOWN 
def calc_cum_drawdown(cum_profit_series, profit_after_commission):

    # cum_profit_series: pandas Series (e.g. 'cumsum' column in above df)
    # profit_after_commission: pandas Series (e.g. 'Profit after Commission' in above df) 

    # Setup / Initialization 
    cum_drawdown = np.array([]) # The data that we're interested in calculating with this function 
    current_drawdown = 0 
    prev_cum_profits = np.array([]) 
    loop_len = len(cum_profit_series.index)

    # Calculation 
    for i in range(loop_len):

        current_cum_profit = cum_profit_series.iloc[i]
        prev_cum_profits = np.append(prev_cum_profits, current_cum_profit)

        if current_cum_profit == max(prev_cum_profits): # We're at an all time high on equity curve
            cum_drawdown = np.append(cum_drawdown, 0)   # then cumulative drawdown is zero. 
        else:                                           # Otherwise, we're in a drawdown...  
            # ...so current drawdown is prior cumulative drawdown + P/L of current trade. 
            cum_drawdown = np.append(cum_drawdown,  cum_drawdown[-1]+profit_after_commission.iloc[i]  )
    
    return cum_drawdown
# ---------------------------------------------------------------------------------------------

# =============================================================================================
# Create dataset (pandas DataFrame) for each csv file.
print("Making calculations.")
for file in files:   
    ext = os.path.splitext(file)[-1].lower() # gets file extension 
    if ext == ".csv": # we want to process all the .csv's in folder that we're working in. 
        _ = pd.read_csv(file, index_col=None) # don't think we need index_col param.
        content.append(_) # creating list of DataFrames

# =============================================================================================
# Create a correlation matrix (pandas DataFrame) for all of the strategies.
for i, df in enumerate(content):
    df_strat = df['Strategy'][0]
    df = df[['Exit time','Profit']]
    df['Exit time'] = pd.to_numeric(df['Exit time'].apply(convert_datetime))   
    df['Exit time'] = pd.to_datetime(df['Exit time'])
    df['Profit'] = pd.to_numeric(df['Profit'].apply(convert_profit))
    df = df.rename(columns = {'Profit': df_strat})
    if i == 0:
        dfm = df
    else:
        dfm = pd.merge(dfm,df, on='Exit time', how='outer')

dfm = dfm.set_index('Exit time').resample('ME').sum()
corrMatrixP = dfm.corr(method='pearson')
corrMatrixS = dfm.corr(method='spearman')

# =============================================================================================
# Create dataset (pandas DataFrame) of all strategies, concatenated together.
dfc = pd.concat(content).reindex() # concatenate DataFrames for each strategy into one huge DataFrame
dfc = dfc.drop(columns=['Cum. net profit']) # Remove 'Cum. net profit' column, because it's no longer correct. 


# =============================================================================================
# Use above function to fix date/time data 
dfc['Exit time'] = dfc['Exit time'].apply(convert_datetime)
dfc['Entry time'] = dfc['Entry time'].apply(convert_datetime)
dfc = dfc.sort_values(by=['Exit time']) # Sort trades by exit time
# =============================================================================================


# =============================================================================================
# Use above function to fix currency/accounting data 
cols = ['Profit', 'Commission', 'ETD', 'MAE', 'MFE']
for col in cols:    
    dfc[col] = pd.to_numeric(dfc[col].apply(convert_profit))
# =============================================================================================


# =============================================================================================
# Redo PROFIT/LOSS calculation on whole portfolio - now that strategies are combined. 
dfc['Profit after Commission'] = dfc['Profit'] - dfc['Commission']
dfc['cumsum'] = dfc['Profit after Commission'].cumsum() # Cumulative sum of Profits after Commission
# =============================================================================================


# =============================================================================================
# -------------------------------------- Plotting ---------------------------------------------

print("Plotting data.")
fig = go.Figure()  # Equity curve
fig2 = go.Figure() # Drawdown plot
fig3 = go.Figure() # Correlation Matrix Pearson
fig4 = go.Figure() # Correlation Matrix Spearman

# For full portfolio of strategies, plot equity curve and drawdown 
# Plot equity curve 
fig.add_trace(go.Scatter(x=dfc['Exit time'], y=dfc['cumsum'],
                    mode='markers+lines',
                    name='Total'))
# Calculate drawdown with above function 
cum_drawdown = calc_cum_drawdown(dfc['cumsum'], dfc['Profit after Commission'])
dfc['cum drawdown'] = cum_drawdown
# Plot drawdown 
fig2.add_trace(go.Scatter(x=dfc['Exit time'], y=dfc['cum drawdown'],
                    mode='markers+lines',
                    name='Total'))

# Plot Correlation Matrix
fig3.add_trace(go.Heatmap(x = corrMatrixP.columns, y = corrMatrixP.index, z = np.array(corrMatrixP), text = corrMatrixP.values, texttemplate = '%{text:.2f}'))
fig3.update_yaxes(autorange = 'reversed')
fig3.update_xaxes(side="top")

fig4.add_trace(go.Heatmap(x = corrMatrixS.columns, y = corrMatrixS.index, z = np.array(corrMatrixS), text = corrMatrixS.values, texttemplate = '%{text:.2f}'))
fig4.update_yaxes(autorange = 'reversed')
fig4.update_xaxes(side="top")

histogram_label = []
histogram_data = []
for strategy, strategies in dfm.items():
    histogram_label.append(strategy)
    data = dfm[strategy].to_numpy()
    histogram_data.append(data)

fig5 = ff.create_distplot(histogram_data, histogram_label, bin_size = 100) # Distribution plot 


# For each strategy, plot equity curve and drawdown 
for strategy in dfc['Strategy'].unique():
    # Query for an individual strategy 
    df_strat = dfc.query(f'Strategy == "{strategy}"')
    # Sort queried trades by exit time 
    df_strat = df_strat.sort_values(by=['Exit time'])
    # Redo cumulative P/L calculation for queried strategy 
    df_strat['cumsum'] = df_strat['Profit after Commission'].cumsum()
    # Plot equity curve 
    fig.add_trace(go.Scatter(x=df_strat['Exit time'], y=df_strat['cumsum'],
                        mode='markers+lines',
                        name=strategy))
    # Calculate drawdown with above function 
    cum_drawdown = calc_cum_drawdown(df_strat['cumsum'], df_strat['Profit after Commission'])
    df_strat['cum drawdown'] = cum_drawdown
    # Plot drawdown 
    fig2.add_trace(go.Scatter(x=df_strat['Exit time'], y=df_strat['cum drawdown'],
                        mode='markers+lines',
                        name=strategy))


# ---------------------------------- Plot Formatting ------------------------------------------

# Equity curve 
fig.update_layout(
    title='Algorithmic Strategy Portfolio Equity Curve(s)',
    title_x=0.5,
    hovermode="x unified",
    legend_traceorder="normal",
    xaxis_rangeslider_visible=False,
    plot_bgcolor='rgba(0, 0, 0, 0)',
    paper_bgcolor='rgba(0, 0, 0, 0)'
)
fig.update_xaxes(
    minor=dict(ticks="inside", showgrid=True),
    mirror=True,
    showline=True,
    gridcolor='lightgrey',
    linecolor='black',
)
fig.update_yaxes(
    title='Profit/Loss [$,USD]',
    mirror=True,
    showline=True,
    gridcolor='lightgrey',
    linecolor='black',
)

# Drawdown plot
fig2.update_layout(
    title='Algorithmic Strategy Portfolio Drawdown(s)',
    title_x=0.5,
    hovermode="x unified",
    legend_traceorder="normal",
    xaxis_rangeslider_visible=False,
    plot_bgcolor='rgba(0, 0, 0, 0)',
    paper_bgcolor='rgba(0, 0, 0, 0)'
)
fig2.update_xaxes(
    minor=dict(ticks="inside", showgrid=True),
    mirror=True,
    showline=True,
    gridcolor='lightgrey',
    linecolor='black',
)
fig2.update_yaxes(
    title='Profit/Loss [$,USD]',
    mirror=True,
    showline=True,
    gridcolor='lightgrey',
    linecolor='black',
)

# Correlation matrix plot
fig3.update_layout(
    title='Pearson Correlation Matrix'
)
fig4.update_layout(
    title='Spearman Correlation Matrix'
)
fig5.update_layout(
    title='Strategy Return Distibution'
)

# Save to single html
with open('StrategyPortfolio.html', 'a') as f:
    f.write(fig.to_html(full_html = False, include_plotlyjs = 'cdn'))
    f.write(fig2.to_html(full_html = False, include_plotlyjs = 'cdn'))
    f.write(fig5.to_html(full_html = False, include_plotlyjs = 'cdn'))
    f.write(fig3.to_html(full_html = False, include_plotlyjs = 'cdn'))
    f.write(fig4.to_html(full_html = False, include_plotlyjs = 'cdn'))
    
print("Done running script.")