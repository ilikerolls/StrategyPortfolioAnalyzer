from dash import html, dcc, Input, dash_table, Output, callback

from src.conf_setup import logger
from src.data.analyzers.portfolio_calc import PortfolioCalculator
from src.data.types.data_trades import DataTrades

data_trades = DataTrades()
# Start Dash Tab
tab_label = 'Portfolio Calculator'

def get_strat_list() -> list:
    return data_trades.strats_to_list()


def display_tab_content() -> list:
    return [
        html.H3(children=tab_label, style={"textAlign": "center"}, ),
        html.Div(children=[
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
            style={'margin-left': '80%'}
        ),
            html.Div(children=[
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
                        'margin-left': '80%',
                        'width': '20%'
                    }
                )
            ]
        )
    ]


@callback(
    Output('container-opt-button', 'children'),
    Input('optimize-button-val', 'n_clicks'),
    prevent_initial_call=True
)
def update_opt_button(value):
    top_performers = data_trades.optimize_portfolio()
    logger.debug("Top Strategy Performers:")
    for count, top_pc in enumerate(top_performers, 1):
        logger.debug(f"{count}. Return to DD: {top_pc.return_to_dd}. Strategy Names: {top_pc.strat_names}")
    return html.Div(f'The input value: {value}')

@callback(
    Output("portfolio-stat-table", "data"),
    Input("strategy-dropdown", "value")
)
def update_table_stats(strats_chosen):
    portfolio_stats: PortfolioCalculator = data_trades.get_portfolio_calc_stats(strat_names=strats_chosen)

    stat_table =[
        dict(Statistic='Net Profit', Value=f"${portfolio_stats.net_profit:,.2f}"),
        dict(Statistic='Max Drawdown', Value=f"${portfolio_stats.max_drawdown:,.2f}"),
        dict(Statistic='Return to Drawdown', Value=f"{portfolio_stats.return_to_dd:,.2f}")
    ]
    logger.debug(f"Strategy Dropdown: values chosen: {strats_chosen}\nTable: {stat_table}")
    return stat_table