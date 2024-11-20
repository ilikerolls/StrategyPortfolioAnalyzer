from dash import dcc, html, Input, Output, State, callback, MATCH
from dash.exceptions import PreventUpdate

from src.UI.utils import create_equity_graph
from src.conf_setup.live_settings import LiveSettings
from src.data.types.data_trades import DataTrades
from src.utils import get_cur_date

TAB_LABEL = 'Live Portfolio'
HEADER = html.H3(children=TAB_LABEL, style={"textAlign": "center"}, )
PERSISTENCE_TYPE = 'session'
MARGIN_LEFT = '75%'
ID_ST_DATE_PICKER = 'live-date-picker'
ID_STRAT_STOP_LOSS = 'strat-stop-loss'
# Graph Settings
LIVE_GRAPHS_ID = 'live-graphs'
LIVE_EQUITY_GRAPH_ID = 'live-equity-graph'
GRAPH_HEIGHT = 750
UPDATE_GRAPH_SECS = 180

data_trades = DataTrades()

LIVE_SETTINGS = LiveSettings()


def get_graphs() -> html.Div: return html.Div(id=LIVE_GRAPHS_ID)

def get_graph_updates() -> html.Div:
    """
    At every so many seconds(interval) update the Live Equity Graph
    :return: A Div containing an update Interval for update_live_graph() callback
    """
    return html.Div(id='Live-Graph-Updates', children=[dcc.Interval(
        id='graph-update',
        interval=UPDATE_GRAPH_SECS*1000, # is in milliseconds
        n_intervals=0
    )])

def get_strat_list(all_opts: bool) -> list:
    """
    :param all_opts: True = get ALL available Strategies in Database, False = Only Previous Selected Strategies
    :return: A List of Live Strategy Names
    """
    if all_opts or LIVE_SETTINGS.live_strategies is None:
        return sorted(data_trades.strats_to_list())
    return sorted(LIVE_SETTINGS.live_strategies)

def get_strat_sl(strat_name: str, live_date: str = None) -> float:
    """
    Use Databases STOP_LOSS setting 1st, but if there is none. Then use the Max DD. upto the current Live Date
    :param strat_name: Name of Strategy
    :param live_date: String representing the Live Date
    :return: A float representing the Max DrawDown of the Strategy
    """
    return LIVE_SETTINGS.get_strat_sl(name=strat_name) or data_trades.get_strat_stats(strat_name=strat_name).get_daily_max_dd(end_date=live_date)

def get_live_strat_dropdown() -> html.Div:
    """:return: Return Strategy Drop Down Menu and Optimize Portfolio button"""
    return html.Div(children=[
        html.Div(children=[
            "Choose Strategies:",
            dcc.Dropdown(
                id="live-strategy-dropdown",
                value=get_strat_list(False),
                options=get_strat_list(True),
                multi=True,
                clearable=True,
            )]
        ),
        html.Div(children=[
            html.Button('Save Strategy Settings', id='live-save-button', n_clicks=0),
        ],
            style={'margin-left': MARGIN_LEFT}
        ),
        html.Div(id='dyn-live-strat-list')
    ])


def load_page() -> list:
    """Returns PortfolioTab's layout"""
    return [HEADER, get_live_strat_dropdown(), get_graphs(), get_graph_updates()]


"""****************** Callbacks ******************"""


@callback(
    Output(LIVE_GRAPHS_ID, 'children', allow_duplicate=True),
    Input('live-save-button', 'n_clicks'),
    State('dyn-live-strat-list', 'children'),
    prevent_initial_call=True
)
def save_settings(n_clicks: int, children: list):
    """
    Save Live Settings on Page and Update Live Graphs
    :param n_clicks: [Not Used] Amount of times button has been clicked
    :param children: Children/Settings List from dyn-live-strat-list
    :return: Live Equity Graph
    """
    if children is not None: # Only save settings if there are settings to save
        tmp_date_settings: dict = {}
        cur_date = get_cur_date()
        for child in children:
            if isinstance(child, dict):
                if child['type'] == 'DatePickerSingle': # Live Start Date
                    strat_name = child['props']['id']['index']
                    live_start_date = child['props']['date']
                    tmp_date_settings.setdefault(strat_name, {})['LIVE_DATE'] = live_start_date if live_start_date is not None else cur_date
                elif child['type'] == 'Input': # Stop Loss number
                    strat_name = child['props']['id']['index']
                    stop_loss = child['props']['value']
                    tmp_date_settings.setdefault(strat_name, {})['STOP_LOSS'] = stop_loss
        LIVE_SETTINGS.save_settings(tmp_date_settings)
    if len(LIVE_SETTINGS.live_strategies) > 0:
        # Create Live Equity graph
        strat_name_dt = LIVE_SETTINGS.get_strat_name_date()
        p_calc = data_trades.get_live_portfolio_stats(strat_name_dt=strat_name_dt)
        return create_equity_graph(p_obj=p_calc, id_name=LIVE_EQUITY_GRAPH_ID, height=GRAPH_HEIGHT)
    raise PreventUpdate

@callback(
Output(LIVE_GRAPHS_ID, 'children', allow_duplicate=True),
    Input('graph-update', 'n_intervals'),
    prevent_initial_call='initial_duplicate'
)
def update_live_graph(n_intervals: int):
    """
    Update the Live Graph if there is 1 more Live Strategies Setup
    :param n_intervals: [PlaceHolder] Amount of times update Interval for graph has been called
    """
    if len(LIVE_SETTINGS.live_strategies) > 0:
        # Create Live Equity graph
        strat_name_dt = LIVE_SETTINGS.get_strat_name_date()
        p_calc = data_trades.get_live_portfolio_stats(strat_name_dt=strat_name_dt)
        return create_equity_graph(p_obj=p_calc, id_name=LIVE_EQUITY_GRAPH_ID, height=GRAPH_HEIGHT)
    raise PreventUpdate


@callback(
    Output('dyn-live-strat-list', 'children'),
    Input('live-strategy-dropdown', 'value'),
)
def add_sel_strats_dates(values: list) -> list:
    """
    Adds the Selected Strategies from live-strategy-dropdown, so we can set Start Dates for them
    :param values: The value of selected strategies from dropdown
    :return: List of Live enabled Strategies with DatePicker for Live Starting Date
    """
    strat_start_dates: list = []
    cur_date = get_cur_date()
    for strategy in values:
        live_date = LIVE_SETTINGS.get_strat_date(name=strategy) or cur_date
        stop_loss = get_strat_sl(strat_name=strategy, live_date=live_date)
        strat_start_dates.extend(
            (
                f'{strategy} Live Date: ',
                dcc.DatePickerSingle(id={
                    'type': ID_ST_DATE_PICKER,
                    'index': strategy
                }, date=live_date, clearable=True),
                ' Stop Loss: ',
                dcc.Input(id={
                    'type': ID_STRAT_STOP_LOSS,
                    'index': strategy
                }, value=stop_loss, type='number', placeholder="Stop Loss / Max DD.", max=0.0)
            )
        )
    return strat_start_dates

@callback(
    Output({'type': ID_STRAT_STOP_LOSS, 'index': MATCH}, 'value'),
    Input({'type': ID_ST_DATE_PICKER, 'index': MATCH}, 'date'),
    State({'type': ID_ST_DATE_PICKER, 'index': MATCH}, 'id')
)
def update_sl_input(live_date: str, input_id: dict):
    """
    Update Stop Loss for Strategy Input when we change the Live Date
    :param live_date: String of the new Live Starting Date
    :param input_id: A dictionary of the id with type and index. index = strategy name
    """
    return get_strat_sl(strat_name=input_id['index'], live_date=live_date)
