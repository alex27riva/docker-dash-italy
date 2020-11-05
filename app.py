#!/usr/bin/python3
from datetime import date

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas

# data URL
url = 'https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-andamento-nazionale/dpc-covid19-ita-andamento' \
      '-nazionale.csv'
today = date.today()
df = pandas.read_csv(url)

plotly_js_minified = ['https://cdn.plot.ly/plotly-basic-latest.min.js']

app = dash.Dash(__name__, external_scripts=plotly_js_minified,
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=0.8, maximum-scale=1.2, minimum-scale=0.5'}])
app.title = 'Dashboard Italia'

server = app.server

# chart config
chart_config = {'displaylogo': False,
                'displayModeBar': False,
                'responsive': True
                }

# slider buttons
slider_button = list([
    dict(count=1,
         label="1m",
         step="month",
         stepmode="backward"),
    dict(count=3,
         label="3m",
         step="month",
         stepmode="backward"),
    dict(count=6,
         label="6m",
         step="month",
         stepmode="backward"),
    dict(step="all")
])

# constants
MIN_DELTA_TAMP = 964  # =MIN(Q$7:Q$119)    Q = delta_tamp
REF_TAMP = 48000  # reference value


def refresh_data():
    global today
    global df
    # read csv for url and get date
    df = pandas.read_csv(url)
    today = date.today()

    # data calculation
    df['nuovi_decessi'] = df.deceduti.diff().fillna(df.deceduti)

    # normalized cases
    df['delta_tamponi'] = df.tamponi.diff().fillna(df.tamponi)
    df['tamp_norm'] = MIN_DELTA_TAMP / df['delta_tamponi'] * df['nuovi_positivi']
    df['nuovi_casi_norm'] = df['nuovi_positivi'] * REF_TAMP / df['delta_tamponi']

    # ratio cases - tests
    df['delta_casi_testati'] = df.casi_testati.diff().fillna(df.casi_testati)  # U
    df['tamponi_meno_casi_testati'] = df['tamponi'] - df['casi_testati']  # S
    df['delta_tamponi_casi'] = df.tamponi_meno_casi_testati.diff().fillna(df.tamponi_meno_casi_testati)  # T
    df['rapp_casi_test'] = (df['nuovi_positivi'] / df['delta_casi_testati']) * 100
    df['perc_tamponi_meno_testati'] = (df['nuovi_positivi'] / df['delta_tamponi_casi']) * 100

    # averages
    df['terapia_intensiva_avg'] = df['terapia_intensiva'].rolling(7).mean()
    df['nuovi_positivi_avg'] = df['nuovi_positivi'].rolling(7).mean()
    df['nuovi_decessi_avg'] = df['nuovi_decessi'].rolling(7).mean()
    df['totale_ospedalizzati_avg'] = df['totale_ospedalizzati'].rolling(7).mean()
    df['nuovi_casi_norm_avg'] = df['nuovi_casi_norm'].rolling(7).mean()
    df['rolling_tested'] = df['rapp_casi_test'].rolling(7).mean()
    df['rolling_swabs_tested'] = df['perc_tamponi_meno_testati'].rolling(7).mean()


def serve_layout():
    refresh_data()
    return html.Div(  # main div
        dbc.Container([
            dbc.Row(
                dbc.Col(
                    dcc.Graph(
                        id='nuovi_positivi',
                        figure={
                            'data': [
                                {'x': df['data'], 'y': df['nuovi_positivi'], 'type': 'bar', 'name': 'Casi totali'},
                            ],
                            'layout': {
                                'title': 'Nuovi Casi',
                                'xaxis': dict(
                                    rangeselector=dict(buttons=slider_button),
                                    rangeslider=dict(visible=False),
                                    type='date'
                                )
                            }
                        },
                        config=chart_config

                    )

                )
            ),
            dbc.Row(
                dbc.Col(
                    dcc.Graph(
                        id='Casi-totali',
                        figure={
                            'data': [
                                {'x': df['data'], 'y': df['totale_casi'], 'type': 'bar', 'name': 'Casi totali'},
                            ],
                            'layout': {
                                'title': 'Totale Casi',
                                'xaxis': dict(
                                    rangeselector=dict(buttons=slider_button),
                                    rangeslider=dict(visible=False),
                                    type='date'
                                )
                            }
                        },
                        config=chart_config
                    )
                )

            ),
            dbc.Row(
                dbc.Col(
                    dcc.Graph(
                        id='isolamento-domiciliare',
                        figure={
                            'data': [
                                {'x': df['data'], 'y': df['isolamento_domiciliare'], 'type': 'bar',
                                 'marker': dict(color='grey')},
                            ],
                            'layout': {
                                'title': 'Isolamento domiciliare',
                                'xaxis': dict(
                                    rangeselector=dict(buttons=slider_button),
                                    rangeslider=dict(visible=False),
                                    type='date'
                                )
                            }
                        },
                        config=chart_config
                    )
                )
            ),
            dbc.Row(
                dbc.Col(
                    dcc.Graph(
                        id='Terapia-intensiva',
                        figure={
                            'data': [
                                {'x': df['data'], 'y': df['terapia_intensiva'], 'type': 'bar',
                                 'name': 'Terapia Intensiva',
                                 'marker': dict(color='RebeccaPurple')},
                                {'x': df['data'], 'y': df['terapia_intensiva_avg'], 'type': 'scatter',
                                 'line': dict(color='blue'),
                                 'name': 'Media 7 giorni'}
                            ],
                            'layout': {
                                'title': 'Terapia intensiva',
                                'xaxis': dict(
                                    rangeselector=dict(buttons=slider_button),
                                    rangeslider=dict(visible=False),
                                    type='date'
                                )
                            }
                        },
                        config=chart_config
                    )
                )

            ),

            dbc.Row(
                dbc.Col(
                    dcc.Graph(
                        id='nuovi-casi-norm',
                        figure={
                            'data': [
                                {'x': df['data'], 'y': df['nuovi_casi_norm'], 'type': 'bar', 'name': 'Nuovi casi norm.',
                                 'marker': dict(color='DarkOliveGreen')},
                                {'x': df['data'], 'y': df['nuovi_casi_norm_avg'], 'type': 'scatter',
                                 'name': 'Media 7gg'}
                            ],
                            'layout': {
                                'title': 'Nuovi casi normalizzati',
                                'xaxis': dict(
                                    rangeselector=dict(buttons=slider_button),
                                    rangeslider=dict(visible=False),
                                    type='date'
                                )
                            }
                        },
                        config=chart_config
                    )

                )
            ),

            dbc.Row(
                dbc.Col(
                    dcc.Graph(
                        id='totale-ospedalizzati',
                        figure={
                            'data': [
                                {'x': df['data'], 'y': df['totale_ospedalizzati'], 'type': 'bar',
                                 'name': 'Totale ospedalizzati',
                                 'marker': dict(color='DarkCyan')},
                                {'x': df['data'], 'y': df['totale_ospedalizzati_avg'], 'type': 'scatter',
                                 'line': dict(color='blue', dash='dot'),
                                 'name': 'Media 7 giorni'}
                            ],
                            'layout': {
                                'title': 'Terapia intensiva e Ospedalizzati',
                                'xaxis': dict(
                                    rangeselector=dict(buttons=slider_button),
                                    rangeslider=dict(visible=False),
                                    type='date'
                                )
                            }
                        },
                        config=chart_config
                    )
                )
            ),

            dbc.Row(
                dbc.Col(
                    dcc.Graph(
                        id='rapporto-positivi-tamponi',
                        figure={
                            'data': [
                                {'x': df['data'], 'y': df['nuovi_positivi'], 'type': 'scatter',
                                 'line': dict(color='orange', dash='dot'),
                                 'name': 'Nuovi casi'},
                                {'x': df['data'], 'y': df['nuovi_decessi'], 'type': 'scatter', 'yaxis': 'y2',
                                 'line': dict(color='blue', dash='dot'),
                                 'name': 'Decessi giornalieri'},
                                {'x': df['data'], 'y': df['nuovi_positivi_avg'], 'type': 'scatter',
                                 'line': dict(color='orange'),
                                 'name': 'Nuovi casi (media 7 giorni)'},
                                {'x': df['data'], 'y': df['nuovi_decessi_avg'], 'type': 'scatter', 'yaxis': 'y2',
                                 'line': dict(color='blue'),
                                 'name': 'Nuovi decessi (media 7 giorni)'}
                            ],
                            'layout': {
                                'title': 'Media 7gg: Decessi giorn. vs. Contagi giorn.',
                                'xaxis': {
                                    'type': 'date',
                                    'range': ['2020-04-22', today]
                                },
                                'yaxis': {'rangemode': 'nonnegative'},
                                'yaxis2': {
                                    'side': 'right',
                                    'overlaying': 'y',  # show both traces,
                                    'rangemode': 'nonnegative'

                                }
                            }
                        },
                        config=chart_config
                    )

                )
            ),

            dbc.Row(
                dbc.Col(
                    dcc.Graph(
                        id='rapporto-pos-tamponi',
                        figure={
                            'data': [
                                {'x': df['data'], 'y': df['rapp_casi_test'], 'type': 'scatter',
                                 'line': dict(color='orange', dash='dot'),
                                 'name': '% Casi testati'},
                                {'x': df['data'], 'y': df['perc_tamponi_meno_testati'], 'type': 'scatter',
                                 'yaxis': 'y2',
                                 'line': dict(color='blue', dash='dot'),
                                 'name': '% Tamponi totali - Casi testati'},

                                {'x': df['data'], 'y': df['rolling_tested'], 'type': 'scatter',
                                 'line': dict(color='orange'),
                                 'name': 'Media (% casi testati)'},
                                {'x': df['data'], 'y': df['rolling_swabs_tested'], 'type': 'scatter', 'yaxis': 'y2',
                                 'line': dict(color='blue'),
                                 'name': 'Media (% tamp totali - casi testati)'}

                            ],
                            'layout': {
                                'title': '(%) Nuovi Positivi / Casi Testati con tamponi',
                                'xaxis': {
                                    'type': 'date',
                                    'range': ['2020-04-22', today]
                                },
                                'yaxis': {'rangemode': 'nonnegative'},
                                'yaxis2': {
                                    'side': 'right',
                                    'overlaying': 'y',  # show both traces,
                                    'rangemode': 'nonnegative'
                                }
                            }
                        },
                        config=chart_config
                    )

                )

            ),

            dbc.Row(
                dbc.Col(
                    dcc.Graph(
                        id='nuovi-casi-vs-morti',
                        figure={
                            'data': [
                                {'x': df['data'], 'y': df['nuovi_decessi'], 'type': 'bar', 'name': 'Nuovi decessi',
                                 'yaxis': 'y1', 'marker': dict(color='orange')},
                                {'x': df['data'], 'y': df['nuovi_positivi'], 'type': 'scatter', 'yaxis': 'y2',
                                 'line': dict(color='blue'),
                                 'name': 'Nuovi casi'}
                            ],
                            'layout': {
                                'title': 'Nuovi casi vs decessi',
                                'xaxis': dict(
                                    rangeselector=dict(buttons=slider_button),
                                    rangeslider=dict(visible=True),
                                    type='date'
                                ),
                                'yaxis': {'rangemode': 'nonnegative',
                                          },
                                'yaxis2': {
                                    'side': 'right',
                                    'overlaying': 'y',  # show both traces,
                                    'rangemode': 'tozero'
                                }
                            }
                        },
                        config=chart_config
                    )

                )

            )

        ])
    )


app.layout = serve_layout

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050, debug=False)
