import time
import dash
import dash_bootstrap_components as dbc
import numpy as np
import plotly.graph_objs as go
from dash import Input, Output, State, dcc, html, dash_table
from config import *
from utils import get_table_type
from shareholding_display_class import ShareholdingDisplay

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

controls = dbc.Card(
    [
        html.Div(
            [
                dbc.Label('Stock Code', style=dict(marginRight=10)),
                dcc.Input(
                    id='stock-code',
                    type='number',
                    min=1,
                    step=1,
                    value=5,
                ),
            ]
        ),
        html.Div(
            [
                dbc.Label('Date Range', style=dict(marginRight=10)),
                dcc.DatePickerRange(
                    id='date-range',
                    min_date_allowed=(pd.Timestamp.now() -
                                      pd.Timedelta(days=365)).date(),
                    max_date_allowed=(pd.Timestamp.now() -
                                      pd.Timedelta(days=1)).date(),
                    start_date=(pd.Timestamp.now() -
                                pd.Timedelta(days=4)).date(),
                    end_date=(pd.Timestamp.now() -
                              pd.Timedelta(days=1)).date(),
                    display_format='D-M-Y'
                ),
            ]
        ),
        html.Div(
            [
                dbc.Label('Transaction Finder Only: Threshold % of Total Number of Shares (0-100)',
                          style=dict(marginRight=10)),
                dcc.Input(
                    id='threshold-percentage',
                    type='number',
                    min=0,
                    max=100,
                    step=0.01,
                    value=2,
                ),
            ]
        ),
    ],
    body=True,
)

app.layout = dbc.Container(
    [
        dcc.Store(id='store'),
        html.H1('HKEX CCASS Shareholding Dashboard'),
        html.Hr(),
        controls,
        html.Hr(),
        dbc.Button(
            'Generate',
            color='primary',
            id='generate-button',
            className='mb-3',
        ),
        html.Hr(),
        dbc.Tabs(
            [
                dbc.Tab(label='Trend Plot', tab_id='trend-tab'),
                dbc.Tab(label='Transaction Finder', tab_id='finder-tab'),
            ],
            id='tabs',
            active_tab='trend-tab',
        ),
        html.Div(id='tab-content', className='p-4'),
    ]
)


@app.callback(
    Output('store', 'data'),
    Input('generate-button', 'n_clicks'),
    State('stock-code', 'value'),
    State('date-range', 'start_date'),
    State('date-range', 'end_date'),
    State('threshold-percentage', 'value')
)
def generate_tab_data(n_clicks, stock_code, start_date, end_date, threshold_percentage):
    sd = ShareholdingDisplay(
        start_date=pd.Timestamp(start_date),
        end_date=pd.Timestamp(end_date),
        stock_code=stock_code,
        threshold_percentage=threshold_percentage
    )
    trend_tab_data = sd.generate_trend_tab_data()
    finder_tab_data = sd.generate_finder_tab_data()

    return {
        'trend_tab_data': trend_tab_data,
        'finder_tab_data': finder_tab_data
    }


@app.callback(
    Output('tab-content', 'children'),
    [Input('tabs', 'active_tab'), Input('store', 'data')],
)
def render_tab_content(active_tab, store):
    if store is not None:
        if active_tab == 'trend-tab':
            # Trend Plot Tab
            trend_fig = go.Figure(store['trend_tab_data']['trend_fig'])
            trend_data = pd.DataFrame.from_dict(
                store['trend_tab_data']['trend_data_dict'])

            trend_tab_content = [
                html.Div(
                    dcc.Graph(figure=trend_fig, id='trend-fig')
                ),
                html.Div(
                    dash_table.DataTable(
                        columns=[
                            {'name': i, 'id': i, 'type': get_table_type(trend_data[i])} for i in trend_data.columns
                        ],
                        data=trend_data.to_dict('records'),
                        filter_action='native'
                    )
                )
            ]
            return trend_tab_content

        elif active_tab == 'finder-tab':
            # Transaction Finder Tab
            potential_transactions = pd.DataFrame.from_dict(
                store['finder_tab_data']['potential_transactions_dict'])

            finder_tab_content = html.Div(
                dash_table.DataTable(
                    columns=[
                        {'name': i, 'id': i, 'type': get_table_type(potential_transactions[i])} for i in potential_transactions.columns
                    ],
                    data=potential_transactions.to_dict('records'),
                    filter_action='native'
                )
            )
            return finder_tab_content
    else:
        return 'Data not available. Please check stock code.'


if __name__ == '__main__':
    app.run_server(host=DASH_HOST, debug=DASH_DEBUG_MODE, port=DASH_PORT)
