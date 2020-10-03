import os 
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.io as pio
import pandas as pd
import numpy as np
import plotly.graph_objs as go


df = pd.read_excel("https://drive.google.com/file/d/1i3pj3JGGoPOU07kxqrGXgDlsZ5fPpCB8/view?usp=sharing")

def get_rainny_days(df, value):
    df['Dummy'] = np.where(df['sknt'] > value, 1, 0)
    df['shift'] = df['Dummy'].ne(df['Dummy'].shift())
    df=df.iloc[1:,:]
    index_list = df.index[df['shift']==True]
    index_list = index_list.append(index_list-1)
    df1 =df.iloc[index_list,:]
    return(df1)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


app.layout = html.Div(
    className ="row",
    children=[
    html.H1(children='CleanBDL Visualization Template'),
    html.Div(children='''Dash: A Simple Visualization with filter features.'''),
    html.Br(),
    dash_table.DataTable(
    id='table-paging-with-graph',
    columns=[
        {"name": i, "id": i} for i in df.columns
    ],
    page_current = 0,
    page_size = 10,
    page_action = "custom",
    filter_action = "custom",
    filter_query = "",
    sort_action = "custom",
    sort_mode = "multi",
    sort_by=[],
    style_table = {
        'height': 400, 
    },
    style_data={
        'width': '150px', 'minWidth': '150px', 'maxWidth': '150px',
        'overflow': 'hidden',
        'textOverflow': 'ellipsis',
    }
    ),
    dcc.Graph(
        id='table-paging-with-graph-container',
    )
    ]
)

operators = [['ge ', '>='],
             ['le ', '<='],
             ['lt ', '<'],
             ['gt ', '>'],
             ['ne ', '!='],
             ['eq ', '='],
             ['contains '],
             ['datestartswith ']]


def split_filter_part(filter_part):
    for operator_type in operators:
        for operator in operator_type:
            if operator in filter_part:
                name_part, value_part = filter_part.split(operator, 1)
                name = name_part[name_part.find('{') + 1: name_part.rfind('}')]

                value_part = value_part.strip()
                v0 = value_part[0]
                if (v0 == value_part[-1] and v0 in ("'", '"', '`')):
                    value = value_part[1: -1].replace('\\' + v0, v0)
                else:
                    try:
                        value = float(value_part)
                    except ValueError:
                        value = value_part

                # word operators need spaces after them in the filter string,
                # but we don't want these later
                return name, operator_type[0].strip(), value

    return [None] * 3


@app.callback(
    Output('table-paging-with-graph', "data"),
    [Input('table-paging-with-graph', "page_current"),
     Input('table-paging-with-graph', "page_size"),
     Input('table-paging-with-graph', "sort_by"),
     Input('table-paging-with-graph', "filter_query")])
def update_table(page_current, page_size, sort_by, filter):
    filtering_expressions = filter.split(' && ')
    dff = df
    for filter_part in filtering_expressions:
        col_name, operator, filter_value = split_filter_part(filter_part)

        if operator in ('eq', 'ne', 'lt', 'le', 'gt', 'ge'):
            # these operators match pandas series operator method names
            dff = dff.loc[getattr(dff[col_name], operator)(filter_value)]
        elif operator == 'contains':
            dff = dff.loc[dff[col_name].str.contains(filter_value)]
        elif operator == 'datestartswith':
            # this is a simplification of the front-end filtering logic,
            # only works with complete fields in standard format
            dff = dff.loc[dff[col_name].str.startswith(filter_value)]

    if len(sort_by):
        dff = dff.sort_values(
            [col['column_id'] for col in sort_by],
            ascending=[
                col['direction'] == 'asc'
                for col in sort_by
            ],
            inplace=False
        )

    return dff.iloc[ 
        page_current*page_size: (page_current + 1)*page_size
    ].to_dict('records')


@app.callback(
    Output('table-paging-with-graph-container', "figure"),
    [Input('table-paging-with-graph', "data")])
def update_output(rows):
    df1 = pd.DataFrame(rows)
    return {

                    "data": [dict(
                    x = df1['valid'],
                    autobinx = False,
                    autobiny = True,
                    marker = dict(color = 'rgb(68, 68, 68)'),
                    name = 'valid',
                    type = 'histogram',
                    xbins = dict(
                        end = '2020-04-11 22:00:00',
                        size = 'M1',
                        start = '2015-01-01 00:00:00'
                        )
                     )],
                    "layout": 
                    dict(
                        xaxis= dict(
                        title = '',
                        type = 'date'
                        ),
                        yaxis= dict(
                        title = 'Incidents Count',
                        type = 'linear'
                        ),
                        updatemenus = [dict(
                            x = 0.1,
                            y = 1.15,
                            xref = 'paper',
                            yref = 'paper',
                            yanchor = 'top',
                            active = 1,
                            showactive = True,
                            buttons = [
                            dict(
                                args = ['xbins.size', 'D1'],
                                label = 'Day',
                                method = 'restyle',
                            ), dict(
                                args = ['xbins.size', 'M1'],
                                label = 'Month',
                                method = 'restyle',
                            ), dict(
                                args = ['xbins.size', 'M3'],
                                label = 'Quater',
                                method = 'restyle',
                            ), dict(
                                args = ['xbins.size', 'M6'],
                                label = 'Half Year',
                                method = 'restyle',
                            ), dict(
                                args = ['xbins.size', 'M12'],
                                label = 'Year',
                                method = 'restyle',
                            )]
                    )]                        
                    ),

                }

if __name__ == '__main__':
    app.run_server(debug=True)

    #df['Dummy'] = np.where(df['sknt'] > sknt1, 1, 0) #) & (df['sknt'] > 20)
    #df['shift'] = df['Dummy'].ne(df['Dummy'].shift())
    #df=df.iloc[1:,:]
    #df1 =df[df['shift']==True]
