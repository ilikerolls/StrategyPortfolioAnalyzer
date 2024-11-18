from dash import html, dcc, Input, dash_table, Output, State, callback
from dash.dcc import RadioItems
from dash.exceptions import PreventUpdate
import plotly.graph_objs as go
from datetime import date, datetime

from src.conf_setup import logger
from src.data.analyzers.portfolio_calculator import PortfolioCalculator
from src.data.types.data_trades import DataTrades

"""Portfolio Tab Dash Page"""

TAB_LABEL = 'Portfolio Calculator'
HEADER = html.H3(children=TAB_LABEL, style={"textAlign": "center"}, )
MARGIN_LEFT = '75%'
TABLE_WIDTH = '25%'
GRAPH_HEIGHT = 750

data_trades = DataTrades()
current_time: datetime = datetime.now()
# Optimized Strategy Holder as we can't pass Complex Classes in dcc.Store
opt_strategies: dict[str, dict] = {}


def load_page() -> list:
    """Returns PortfolioTab's layout"""
    return [HEADER, get_strat_dropdown_button(), get_portfolio_stats_table(), get_graphs()]

def get_opt_strats(sess_id: str, option: str = None) -> PortfolioCalculator | dict:
    """
    Get Optimized Strategy Option
    :param sess_id: String for the 'session_id'
    :param option: [Optional] String Representing the Option Name for the Radio Button. Default is ALL options
    :return: A PortfolioCalculator Object with the optimized Strategies or Dict of optimized Strats if option = None
    """
    return opt_strategies[sess_id] if option is None else opt_strategies[sess_id][option]

def reset_opt_strats(sess_id: str):
    """
    Clear old Optimization Results for the session_id if it exists. For when we click the Optimization Button a 2nd time
    :param sess_id: Session ID string
    """
    opt_strategies.get(sess_id, {}).clear()

def set_opt_strats(sess_id: str, option: str, p_calc: PortfolioCalculator):
    """
    Setter for Optimization Results for the session_id if it exists
    :param sess_id: String for the 'session_id'
    :param option: String Representing the Option Name for the Radio Button
    :param p_calc: PortfolioCalculator Object that stores the Optimized Portfolio of Strategies
    """
    opt_strategies.setdefault(sess_id, {})[option] = p_calc

def get_date_picker():
    """:return: A Date Picker. Used to select Analysis or Optimization Dates"""
    return dcc.DatePickerRange(
        id='analysis-opt-date-range',
        min_date_allowed=date(1995, 8, 5),
        initial_visible_month=date(current_time.year - 2, 1, 1),
        clearable=True
    )

def get_graphs() -> html.Div: return html.Div(id='calc-graphs')

def get_portfolio_obj(p_obj: list | PortfolioCalculator, start_date: str = None, end_date: str = None) -> PortfolioCalculator:
    """
    Retrieves the portfolio calculator object based on selected strategies and date range.
    :param p_obj: An Optimized PortfolioCalculator Object or a List of Strategies
    :param start_date: [Optional] Date to start selection of statistics. Default: ALL Dates
    :param end_date: [Optional] Date to end selection of statistics. Default: ALL Dates
    :return: PortfolioCalculator based on options passed. If already a PortfolioCalculator object, then just return strats_obj.
    """
    if isinstance(p_obj, list):
        return data_trades.get_portfolio_calc_stats(strat_names=p_obj, start_date=start_date, end_date=end_date)
    elif isinstance(p_obj, PortfolioCalculator):
        return p_obj
    else:
        logger.error(f"Failed to retrieve a PortfolioCalculator Object for parameters passed\n{p_obj}\nstart_date: {start_date}\nend_date: {end_date}")

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
            style_table={
                'margin-left': MARGIN_LEFT,
                'width': TABLE_WIDTH
            }
        )
    ]
    )

def get_strat_dropdown_button() -> html.Div:
    """:return: Return Strategy Drop Down Menu and Optimize Portfolio button"""
    return html.Div(children=[
            html.Div(children=[
                "Choose Strategies:",
                dcc.Dropdown(
                    id="strategy-dropdown",
                    value=get_strat_list(),
                    options=get_strat_list(),
                    multi=True,
                    clearable=True
                )]
            ),
            html.Div(children=[
                get_date_picker(),
                html.Button('Analysis', id='analysis-button', n_clicks=0),
                html.Button('Optimize', id='optimize-button', n_clicks=0),
                html.Div(id='dyn-opt-radio-opts')
                ],
                style={'margin-left': MARGIN_LEFT}
            )
        ])

def _update_graphs(p_obj: PortfolioCalculator) -> list:
    # Create traces for each Strategy
    traces = []
    for sel_strat_ss in p_obj.sel_strats_ss:
        traces.append(go.Scatter(
            x=sel_strat_ss.daily_df.index,  # Datetime is the Index
            y=sel_strat_ss.daily_df['Cum. net profit'],
            mode='lines+markers',
            name=sel_strat_ss.name
        ))
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
            id='equity-curve',
            figure={
                'data': traces,
                'layout': go.Layout(
                    title='Algorithmic Strategy Portfolio Equity Curve(s)',
                    xaxis={'title': 'Date'},
                    yaxis={'title': 'Profit and Loss $USD'},
                    height=GRAPH_HEIGHT,
                    hovermode='x unified',
                    plot_bgcolor='rgba(0, 0, 0, 0)',
                    paper_bgcolor='rgba(0, 0, 0, 0)'
                )
            }
        )
    ]

def _update_opt_table_stats(p_obj: PortfolioCalculator) -> list:
    """
    Update Table Statistics on an Optimized Portfolio PortfolioCalculator Object
    :param p_obj: A PortfolioCalculator Object
    :return: A list of dicts for the Statistics Table
    """
    return [
        dict(Statistic='Net Profit', Value=f"${p_obj.net_profit:,.2f}"),
        dict(Statistic='Max Drawdown', Value=f"${p_obj.max_drawdown:,.2f}"),
        dict(Statistic='Return to Drawdown', Value=f"{p_obj.return_to_dd:,.2f}")
    ]

"""****************** Callbacks ******************"""
@callback(
    Output('dyn-opt-radio-opts', 'children'),
    Input('optimize-button', 'n_clicks'),
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
            {'label': f'{count}. Return/DD: {top_pc.return_to_dd}, Profit: ${top_pc.net_profit}, Strategies: {len(top_pc.strat_names)}',
             'value': f'opt_{count}'})
        # Add to Optimized Strategies Dictionary
        set_opt_strats(session_id, f'opt_{count}', top_pc)
        logger.debug(
            f"{count}. Return to DD: {top_pc.return_to_dd}. Strategy Names: {top_pc.strat_names}, Option: opt_{count}")
    return RadioItems(options=opt_options, id='opt-radio-items')

@callback(
    [Output("portfolio-stat-table", "data", allow_duplicate=True), Output('calc-graphs', 'children', allow_duplicate=True)],
    Input('analysis-button', 'n_clicks'),
    State('strategy-dropdown', 'value'),
    State('analysis-opt-date-range', 'start_date'),
    State('analysis-opt-date-range', 'end_date'),
    prevent_initial_call='initial_duplicate'
)
def update_analysis_click(n_clicks: int, strats_chosen: list, start_date: str, end_date: str) -> tuple[list, list]:
    """
    Update the Statistics Table when a New Strategy Combination is chosen or the optimize button is hit
    :param n_clicks: Amount of times button is clicked
    :param strats_chosen: A list of strings of Strategies Chosen
    :param start_date: [Optional] Date to start selection of statistics. Default: ALL Dates
    :param end_date: [Optional] Date to end selection of statistics. Default: ALL Dates
    :return: A list containing dicts to update each row in the Statistics Table
    """
    portfolio_stats = get_portfolio_obj(p_obj=strats_chosen, start_date=start_date, end_date=end_date)
    return _update_opt_table_stats(p_obj=portfolio_stats), _update_graphs(p_obj=portfolio_stats)

@callback(
    [Output('strategy-dropdown', 'value'), Output("portfolio-stat-table", "data", allow_duplicate=True), Output('calc-graphs', 'children', allow_duplicate=True)],
    Input('opt-radio-items', 'value'),
    State('session-id', 'data'),
    prevent_initial_call=True
)
def sel_radio_opt(option: str, session_id: str) -> tuple[list, list, list]:
    """
    Called when a Radio Button is Selected from "Optimized Strategies"
    :param option: Name of Option
    :param session_id: Current Session ID
    :return: (A list of Strategy Names), Statistics Table
    """
    if option is not None:
        p_calc = get_opt_strats(session_id, option)
        return sorted(p_calc.strat_names), _update_opt_table_stats(p_obj=p_calc), _update_graphs(p_obj=p_calc)
    else:  # No reason to update anything on Initial loading of Optimize Radio buttons when value = None
        raise PreventUpdate