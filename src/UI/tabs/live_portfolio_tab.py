from dash import dcc, html, Input, Output, State, callback

from src.conf_setup.live_settings import LiveSettings
from src.data.types.data_trades import DataTrades
from src.utils import get_cur_date

TAB_LABEL = 'Live Portfolio'
HEADER = html.H3(children=TAB_LABEL, style={"textAlign": "center"}, )
PERSISTENCE_TYPE = 'session'
MARGIN_LEFT = '75%'
ST_DATE_PICKER = 'live-date-picker-'
STRAT_STOP_NUM = 'strat-stop-num-'

data_trades = DataTrades()

LIVE_SETTINGS = LiveSettings()


def get_strat_list(all_opts: bool) -> list:
    """
    :param all_opts: True = get ALL available Strategies in Database, False = Only Previous Selected Strategies
    :return: A List of Live Strategy Names
    """
    if all_opts or LIVE_SETTINGS.live_strategies is None:
        return sorted(data_trades.strats_to_list())
    return sorted(LIVE_SETTINGS.live_strategies)

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
    return [HEADER, get_live_strat_dropdown()]


"""****************** Callbacks ******************"""


@callback(
    Input('live-save-button', 'n_clicks'),
    State('dyn-live-strat-list', 'children')
)
def save_settings(n_clicks: int, children: list):
    tmp_date_settings: dict = {}
    cur_date = get_cur_date()
    for child in children:
        if isinstance(child, dict):
            if child['type'] == 'DatePickerSingle': # Live Start Date
                strat_name = child['props']['id'].replace(ST_DATE_PICKER, '')
                live_start_date = child['props']['date']
                tmp_date_settings.setdefault(strat_name, {})['LIVE_DATE'] = live_start_date if live_start_date is not None else cur_date
            elif child['type'] == 'Input': # Stop Number of when we take this much losses we should shut strategy down
                strat_name = child['props']['id'].replace(STRAT_STOP_NUM, '')
                stop_loss = child['props']['value']
                tmp_date_settings.setdefault(strat_name, {})['STOP_LOSS'] = stop_loss
                print(f"number: {strat_name}, cutoff_num: {stop_loss}")
    LIVE_SETTINGS.save_settings(tmp_date_settings)


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
        # Use Databases STOP_LOSS setting 1st, but if there is none. Then use the Max DD. upto the current Live Date
        stop_loss = LIVE_SETTINGS.get_strat_sl(name=strategy) or data_trades.get_strat_stats(strat_name=strategy).get_daily_max_dd(end_date=live_date)
        strat_start_dates.extend(
            (
                f'{strategy} Live Date: ',
                dcc.DatePickerSingle(id=f'{ST_DATE_PICKER}{strategy}', date=live_date, clearable=True),
                ' Stop Loss: ',
                dcc.Input(id=f'{STRAT_STOP_NUM}{strategy}', value=stop_loss, type='number', placeholder="PnL Cut Off / Max DD.", max=0.0)
            )
        )
    return strat_start_dates