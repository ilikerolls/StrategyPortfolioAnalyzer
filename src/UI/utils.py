from tracemalloc import Statistic

import plotly.graph_objs as go
from dash import dcc, html, dash_table

from src.data.analyzers.portfolio_calculator import PortfolioCalculator


def create_equity_graph(p_obj: PortfolioCalculator, id_name: str, height: int = 750) -> list:
    """
    Create an Equity Graph based on a Portfolio Calculator object
    :param p_obj: PortfolioCalculator object of different strategies
    :param id_name: A name to give the id of the graph for Dash
    :param height: [Optional] The height in pixels Default: 750
    :return: A list containing a Dash Graph that can be outputted to a Div's children
    """
    traces = [
        go.Scatter(
            x=sel_strat_ss.strats_df.index,  # Datetime is the Index
            y=sel_strat_ss.strats_df['Cum. net profit'],
            mode='lines+markers',
            name=sel_strat_ss.name,
        )
        for sel_strat_ss in p_obj.sel_strats_ss
    ]
    # Add Total strategy Equity Curve if we have more than 1 Strategy Selected
    if len(traces) > 1:
        traces.append(go.Scatter(
            x=p_obj.combined_strats_df.index,  # Assuming Date is represented by index
            y=p_obj.combined_strats_df['Cum. net profit'],
            mode='lines+markers',
            name='Total',
            line=dict(dash='dash')  # Different line style for combined strategy
        ))

    return [
        dcc.Graph(
            id=id_name,
            figure={
                'data': traces,
                'layout': go.Layout(
                    title='Algorithmic Strategy Portfolio Equity Curve(s)',
                    xaxis={'title': 'Date'},
                    yaxis={'title': 'Profit and Loss $USD'},
                    height=height,
                    hovermode='x unified',
                    plot_bgcolor='rgba(0, 0, 0, 0)',
                    paper_bgcolor='rgba(0, 0, 0, 0)'
                )
            }
        )
    ]

def get_portfolio_stats_table(id_name: str, style_table: dict) -> html.Div:
    """
    Create a Portfolio Statistics Table containing things like Net Profit, Max DD., Daily Win Rate
    :param id_name: A name to give the id of the graph for Dash
    :param style_table: Ex: style_table={'margin-left': '75%', 'width': '25%'}
    :return: Portfolio Statistics Table
    """
    return html.Div(children=[
        dash_table.DataTable(
            id=id_name,
            data=[
                dict(Statistic='Net Profit', Value='$0.00'),
                dict(Statistic='Max Drawdown', Value='$0.00'),
                dict(Statistic='Return to Drawdown', Value=0.00),
                dict(Statistic='Daily Win Rate', Value=0.00),
                dict(Statistic='Capital Required Day Trade Margin', Value=0.00)
            ],
            columns=[
                dict(id='Statistic', name='Statistic'),
                dict(id='Value', name='Value', type='numeric')
            ],
            style_cell={'textAlign': 'right'},
            style_header={
                'border': '3px solid black',
                'backgroundColor': 'rgb(255, 165, 0)',
                'fontWeight': 'bold'
            },
            style_data={
                'border': '1px solid black',
                'color': 'black',
                'backgroundColor': 'yellow'
            },
            style_table=style_table
        )
    ]
    )

def update_opt_table_stats(p_obj: PortfolioCalculator) -> list:
    """
    Update Table Statistics on an Optimized Portfolio PortfolioCalculator Object
    :param p_obj: A PortfolioCalculator Object
    :return: A list of dicts for the Statistics Table
    """
    return [
        dict(Statistic='Net Profit', Value=f"${p_obj.net_profit:,.2f}"),
        dict(Statistic='Max Drawdown', Value=f"${p_obj.max_drawdown:,.2f}"),
        dict(Statistic='Return to Drawdown', Value=f"{p_obj.return_to_dd:,.2f}"),
        dict(Statistic='Daily Win Rate', Value=f"{p_obj.daily_win_rate:,.2f}%"),
        dict(Statistic='Capital Required Day Trade Margin', Value=f"${p_obj.req_cap_daytrade:,.2f}")
    ]