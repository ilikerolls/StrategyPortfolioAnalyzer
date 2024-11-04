from dash import Dash, html, dcc
import dash_bootstrap_components as dbc

from src.UI.tabs import Portfolio_Optimizer
from src.UI.tabs import tab2
from src.conf_setup import logger

# suppress_callback_exceptions=True is necessary for multi file dash apps
app = Dash(name=__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])


def create_layout() -> list:
    return [
        html.H1(children=f'Strategy Portfolio Optimizer', style={'textAlign': 'center'}),
        dcc.Tabs(children=[
            dcc.Tab(children=Portfolio_Optimizer.display_tab_content(), label=Portfolio_Optimizer.tab_label),
            dcc.Tab(children=tab2.display_tab_content(), label=tab2.tab_label),
        ])
    ]


# Create new layout On Page Load via this method
app.layout = create_layout


def start_dashboard():
    logger.info("Dashboard: Starting")
    app.run(host='127.0.0.1', port=5050, debug=False)
    logger.info("Dashboard: Ended")

# if __name__ == '__main__':
#    start_dashboard()
