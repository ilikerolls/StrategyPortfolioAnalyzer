import uuid
from dash import html, dcc, Dash, callback, Input, Output
import dash_bootstrap_components as dbc

from src.UI.tabs import portfolio_tab
from src.UI.tabs import live_portfolio_tab
from src.conf_setup import logger, APP_NAME

# suppress_callback_exceptions=True is necessary for multi file dash apps
app = Dash(name=__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP], title=APP_NAME)

def create_layout() -> html.Div:
    return html.Div([
        dcc.Store(id='session-id', storage_type='memory'),
        html.Title(APP_NAME),
        html.H1(children='Strategy Portfolio Optimizer', style={'textAlign': 'center'}),
        dcc.Tabs(children=[
            dcc.Tab(children=live_portfolio_tab.load_page(), label=live_portfolio_tab.TAB_LABEL),
            dcc.Tab(children=portfolio_tab.load_page(), label=portfolio_tab.TAB_LABEL)
        ])
    ])

# Create new layout On Page Load via this method
app.layout = create_layout


def start_dashboard():
    logger.info("Dashboard: Starting")
    app.run(host='127.0.0.1', port=5050, debug=False)
    logger.info("Dashboard: Ended")

@callback(
    Output('session-id', 'data'),
    Input('session-id', 'data'),
)
def generate_session_id(data):
    """
    Generate a Session ID until browser refreshes or closes. Set storage_type='session' if we want to wait until browser
    completely closes
    :param data: The session ID stored in data of 'session-id'
    :return: A unique Session ID
    """
    #return str(uuid.uuid4()) if data is None else data
    return 'default' if data is None else data