import plotly.graph_objs as go
from dash import dcc

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
            x=sel_strat_ss.daily_df.index,  # Datetime is the Index
            y=sel_strat_ss.daily_df['Cum. net profit'],
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