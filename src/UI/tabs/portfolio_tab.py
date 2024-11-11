import dash
from dash import html, dcc, Input, dash_table, Output, State, callback
from dash.dcc import RadioItems
from dash.exceptions import PreventUpdate
from datetime import date, datetime

from src.conf_setup import logger
from src.data.analyzers.portfolio_calculator import PortfolioCalculator
from src.data.types.data_trades import DataTrades

"""Portfolio Tab Dash Page"""

TAB_LABEL = 'Portfolio Calculator'
HEADER = html.H3(children=TAB_LABEL, style={"textAlign": "center"}, )
MARGIN_LEFT = '80%'

data_trades = DataTrades()
current_time: datetime = datetime.now()
# Optimized Strategy Holder as we can't pass Complex Classes in dcc.Store
opt_strategies: dict[str, dict] = {}


def load_page() -> list:
    """Returns PortfolioTab's layout"""
    return [HEADER, get_strat_dropdown_button(), get_portfolio_stats_table()]

def get_opt_strats(sess_id: str, option: str = None) -> PortfolioCalculator | dict:
    """
    Get Optimized Strategy Option
    :param sess_id: String for the 'session_id'
    :param option: [Optional] String Representing the Option Name for the Radio Button. Default is ALL options
    :return: A PortfolioCalculator Object with the optimized Strategies
    """
    if option is None:
        return opt_strategies[sess_id]
    return opt_strategies[sess_id][option]

def reset_opt_strats(sess_id: str):
    """
    Clear old Optimization Results for the session_id if it exists. For when we click the Optimization Button a 2nd time
    :param sess_id: Session ID string
    """
    try:
        opt_strategies[sess_id].clear()
    except KeyError:
        logger.debug(f"Session ID: {sess_id} doesn't exit. Current Session IDs: {opt_strategies.keys()}")

def set_opt_strats(sess_id: str, option: str, p_calc: PortfolioCalculator):
    """
    Setter for Optimization Results for the session_id if it exists
    :param sess_id: String for the 'session_id'
    :param option: String Representing the Option Name for the Radio Button
    :param p_calc: PortfolioCalculator Object that stores the Optimized Portfolio of Strategies
    """
    if sess_id not in opt_strategies.keys():
        opt_strategies[sess_id] = {option: p_calc}
    else:
        opt_strategies[sess_id].update({option: p_calc})


def get_date_picker():
    """:return: A Date Picker. Used to select Analysis or Optimization Dates"""
    return dcc.DatePickerRange(
        id='analysis-opt-date-range',
        min_date_allowed=date(1995, 8, 5),
        initial_visible_month=date(current_time.year - 2, 1, 1),
        clearable=True
    )


def get_strat_list() -> list: return sorted(data_trades.strats_to_list())


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
            clearable=True
        ),
        get_date_picker(),
        html.Button('Analysis', id='analysis-button-val', n_clicks=0),
        html.Button('Optimize', id='optimize-button-val', n_clicks=0),
        html.Div(id='dyn-opt-radio-opts'),
    ],
        style={'margin-left': MARGIN_LEFT}
    )


@callback(
    Output('dyn-opt-radio-opts', 'children'),
    Input('optimize-button-val', 'n_clicks'),
    State('session-id', 'data'),
    State('analysis-opt-date-range', 'start_date'),
    State('analysis-opt-date-range', 'end_date'),
    prevent_initial_call=True
)
def update_opt_button(n_clicks: int, session_id: str, start_date: str = None, end_date: str = None) -> RadioItems:
    """
    Optimization Button - Finds best Optimizations, creates Radio buttons for them, & stores them in a global dict under
    the session-id
    :param n_clicks: Amount of clicks from Optimization Button
    :param session_id: Session ID of the Session
    :param start_date: [Optional] Starting date to select from dataframe. Default: ALL Dates
    :param end_date: [Optional] End Date to select from dataframe. Default: ALL Dates
    :return: Output from hitting the Optimize Button
    """
    # Clear any Old Optimized Strategies from Memory
    reset_opt_strats(sess_id=session_id)
    top_performers = data_trades.optimize_portfolio(start_date=start_date, end_date=end_date)
    opt_options = []
    logger.debug("Top Strategy Performers:")
    for count, top_pc in enumerate(top_performers, 1):
        opt_options.append(
            {'label': f'{count}. Return To DD: {top_pc.return_to_dd}, Strategies: {len(top_pc.strat_names)}',
             'value': f'opt_{count}'})
        # Add to Optimized Strategies Dictionary
        set_opt_strats(session_id, f'opt_{count}', top_pc)
        logger.debug(
            f"{count}. Return to DD: {top_pc.return_to_dd}. Strategy Names: {top_pc.strat_names}, Option: opt_{count}")
    return RadioItems(options=opt_options, id='opt-radio-items')

def _update_opt_table_stats(strats_obj: PortfolioCalculator | list, start_date: str = None, end_date: str = None) -> list:
    """
    Update Table Statistics & Graphs based on an Optimized Portfolio PortfolioCalculator Object
    :param strats_obj: An Optimized PortfolioCalculator Object or a List of Strategies
    :param start_date: [Optional] Date to start selection of statistics. Default: ALL Dates
    :param end_date: [Optional] Date to end selection of statistics. Default: ALL Dates
    :return: 
    """
    portfolio_stats = strats_obj
    if isinstance(strats_obj, list):
        portfolio_stats = data_trades.get_portfolio_calc_stats(strat_names=strats_obj, start_date=start_date, 
                                                               end_date=end_date)
    stat_table = [
        dict(Statistic='Net Profit', Value=f"${portfolio_stats.net_profit:,.2f}"),
        dict(Statistic='Max Drawdown', Value=f"${portfolio_stats.max_drawdown:,.2f}"),
        dict(Statistic='Return to Drawdown', Value=f"{portfolio_stats.return_to_dd:,.2f}")
    ]
    logger.debug(f"Strategy Statistics: {portfolio_stats.strat_names}\nTable: {stat_table}")
    return stat_table
    
    
@callback(
    Output("portfolio-stat-table", "data", allow_duplicate=True),
    Input('analysis-button-val', 'n_clicks'),
    State('strategy-dropdown', 'value'),
    State('analysis-opt-date-range', 'start_date'),
    State('analysis-opt-date-range', 'end_date'),
    prevent_initial_call='initial_duplicate'
)
def update_analysis_click(n_clicks: int, strats_chosen: list, start_date: str, end_date: str) -> list:
    """
    Update the Statistics Table when a New Strategy Combination is chosen or the optimize button is hit
    :param n_clicks: Amount of times button is clicked
    :param strats_chosen: A list of strings of Strategies Chosen
    :param start_date: [Optional] Date to start selection of statistics. Default: ALL Dates
    :param end_date: [Optional] Date to end selection of statistics. Default: ALL Dates
    :return: A list containing dicts to update each row in the Statistics Table
    """
    logger.debug(
        f"n_clicks: {n_clicks}. Getting Statistics for\n Strategies: {strats_chosen}\nStart Date: {start_date}\nEnd Date: {end_date}")
    return _update_opt_table_stats(strats_obj=strats_chosen, start_date=start_date, end_date=end_date)

@callback(
    [Output('strategy-dropdown', 'value'), Output("portfolio-stat-table", "data", allow_duplicate=True)],
    Input('opt-radio-items', 'value'),
    State('session-id', 'data'),
    prevent_initial_call=True
)
def sel_radio_opt(option: str, session_id: str):
    """
    Called when a Radio Button is Selected from "Optimized Strategies"
    :param option: Name of Option
    :param session_id: Current Session ID
    :return: (A list of Strategy Names), Statistics Table
    """
    if option is not None:
        p_calc = get_opt_strats(session_id, option)
        stats_table = _update_opt_table_stats(strats_obj=p_calc)
        return sorted(p_calc.strat_names), stats_table
    else:  # No reason to update anything on Initial loading of Optimize Radio buttons when value = None
        raise PreventUpdate