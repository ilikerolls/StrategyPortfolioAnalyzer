from dash import html, dcc, Input, callback

from src.data.types.data_trades import DataTrades

label = 'Portfolio Calculator'

def get_strat_list() -> list:
    dt = DataTrades()
    return dt.strats_to_list()

def display_tab_content():
    return html.Div([
        html.H3(label),
        html.Br(),
        html.Div("Choose Strategies:"),
        dcc.Dropdown(
            id="strategy-dropdown",
            value=get_strat_list(),
            options=get_strat_list(),
            multi=True,
        ),
    ])

@callback(
Input("strategy-dropdown", "value")
)
def update_stats():
    pass