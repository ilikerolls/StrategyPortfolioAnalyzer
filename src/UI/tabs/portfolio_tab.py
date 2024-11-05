from dash import html, dcc, Input, dash_table, Output, callback
from dash.dcc import RadioItems
from dash.exceptions import PreventUpdate

from src.conf_setup import logger
from src.data.analyzers.portfolio_calculator import PortfolioCalculator
from src.data.types.data_trades import DataTrades

"""Portfolio Tab Dash Page"""

TAB_LABEL = 'Portfolio Calculator'
HEADER = html.H3(children=TAB_LABEL, style={"textAlign": "center"}, )
MARGIN_LEFT = '80%'

data_trades = DataTrades()
# Hold the stat_table globally. sel_radio_but will send None when 1st created. This keeps us from accidentally updating
# the stat_table when the radio buttons are 1st created instead of being selected
#stat_table: list = []

def load_page() -> list:
    """Returns PortfolioTab's layout"""
    return [HEADER, get_strat_dropdown_button(), get_portfolio_stats_table()]

def get_strat_list() -> list:
    return data_trades.strats_to_list()

def get_portfolio_stats_table() -> html.Div:
    """:return: Portfolio Statistics Table"""
    return html.Div(children=[
            dash_table.DataTable(
                id='portfolio-stat-table',
                data=[
                    dict(Statistic='Net Profit', Value='$0.00'),
                    dict(Statistic='Max Drawdown', Value='$0.00'),
                    dict(Statistic='Return to Drawdown', Value=0.00)
                ],
                columns=[
                    dict(id='Statistic', name='Statistic'),
                    dict(id='Value', name='Value', type='numeric')
                ],
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
                style_table={
                    'margin-left': MARGIN_LEFT,
                    'width': '20%'
                }
            )
        ]
    )

def get_strat_dropdown_button() -> html.Div:
    """:return: Return Strategy Drop Down Menu and Optimize Portfolio button"""
    return html.Div(children=[
        html.Div("Choose Strategies:"),
        dcc.Dropdown(
            id="strategy-dropdown",
            value=get_strat_list(),
            options=get_strat_list(),
            multi=True,
        ),
        html.Button('Optimize', id='optimize-button-val', n_clicks=0),
        html.Div(id='container-opt-button'),
    ],
        style={'margin-left': MARGIN_LEFT}
    )

@callback(
    Output('container-opt-button', 'children'),
    Input('optimize-button-val', 'n_clicks'),
    prevent_initial_call=True
)
def update_opt_button(value: int) -> RadioItems:
    """
    Updates from Optimization Button
    :param value: Amount of clicks from Optimization Buttion
    :return: Output from hitting the Optimize Button
    """
    top_performers = data_trades.optimize_portfolio()
    opt_options = []
    logger.debug("Top Strategy Performers:")
    for count, top_pc in enumerate(top_performers, 1):
        opt_options.append(
            {'label': f'{count}. Return To DD: {top_pc.return_to_dd}, Strategies: {len(top_pc.strat_names)}',
             'value': top_pc.strat_names})
        logger.debug(f"{count}. Return to DD: {top_pc.return_to_dd}. Strategy Names: {top_pc.strat_names}")
    return RadioItems(options=opt_options, id='opt-radio-items')

@callback(
    Output("portfolio-stat-table", "data"),
    Input("strategy-dropdown", "value")
)
def update_table_stats(strats_chosen: list) -> list:
    """
    Update the Statistics Table when a New Strategy Combination is chosen or the optimize button is hit
    :param strats_chosen: A list of strings of Strategies Chosen
    :return: A list containing dicts to update each row in the Statistics Table
    """
    portfolio_stats: PortfolioCalculator = data_trades.get_portfolio_calc_stats(strat_names=strats_chosen)

    stat_table = [
        dict(Statistic='Net Profit', Value=f"${portfolio_stats.net_profit:,.2f}"),
        dict(Statistic='Max Drawdown', Value=f"${portfolio_stats.max_drawdown:,.2f}"),
        dict(Statistic='Return to Drawdown', Value=f"{portfolio_stats.return_to_dd:,.2f}")
    ]
    logger.debug(f"Strategy Dropdown: values chosen: {strats_chosen}\nTable: {stat_table}")
    return stat_table

@callback(
    Output('strategy-dropdown', 'value'),
    Input('opt-radio-items', 'value'),
    prevent_initial_call=True
)
def sel_radio_but(value: list) -> list:
    """
    Called when a Radio Button is Selected from "Optimized Strategies"
    :param value: Name of Option put in Dict, so we can retrieve its strategy list
    :return: A list of Strategy Names
    """
    if isinstance(value, list):
        return value
    else: # No reason to update anything on Initial loading of Optimize Radio buttons when value = None
        raise PreventUpdate