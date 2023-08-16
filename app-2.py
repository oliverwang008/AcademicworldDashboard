# Import packages
from dash import Dash, html, dash_table, dcc, callback, Output, Input, State
import plotly.express as px
from mysql_utils import mysql_utils
from neo4j_utils import neo4j_utils
from mongo_utils import mongo_utils

# Initialize the app - incorporate css
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)

# Database access
sqlhost='127.0.0.1'
sqluser='root'
sqlpassword='test_root'
sqldatabase='academicworld'
neo4juri='bolt://localhost:7687'
neo4juser='neo4j'
neo4jpassword='test_root'
neo4jdatabase='academicworld'
mongodb_uri = 'mongodb://localhost:27017'
mongodb_database_name = 'academicworld'

# Create a mongo_utils instance with the MongoDB URI and database name
mongo = mongo_utils(mongodb_uri, mongodb_database_name)

# Execute the aggregation query and get the result list
result = mongo.execute_query()

# Prepare the data for Widget
graph_data = []
for item in result:
    graph_data.append(item)


# App layout
app.layout = html.Div([
    html.Div(className='row', children='Explore Academic World by Keyword',
             style={'textAlign': 'center', 'color': 'black', 'fontSize': 30}),
    # Widget for the searchbox, search button and add to watchlist button
    html.Div(className='row', children=[
            dcc.Input(id='keyword-input', value='', type='text', placeholder='input keyword here'),
            html.Button(id='submit-button', type='submit', children='Search',
                        style={'margin-left': '20px'}),
            html.Button(id='add-button', type='submit', children='Add to Watchlist',
                        style={'margin-left': '20px'})
            ], style={'textAlign': 'center', 'margin-top': '20px'}),
    # Widget for Top Universities by Faculty Number on this Keyword
    html.Div(className='row', children=[
        html.Div(className='six columns', children=[
            html.Div(className='row', children='Top Universities by Faculty Number on This Keyword',
             style={'textAlign': 'center', 'color': 'black', 'fontSize': 18}),
            dcc.Graph(id='top-uni', figure={})
        ], style={'margin-left': '20px', 'margin-top': '30px'}),
        # Widget for displaying NEO4J query result on Top 10 Faculty by KRC on this keyword
        html.Div(className='six columns', children=[
            html.Div(className='row', children='Top Faculty by Relevant Citation (KRC) on This Keyword',
             style={'textAlign': 'center', 'color': 'black', 'fontSize': 18}),
            dcc.Graph(id='top-prof', figure={})
        ], style={'margin-left': '20px', 'margin-top': '30px'})
    ]),
    html.Div(className='row', children=[
        #Widget for the top 10 relevant keywords appearing in the same publications with the inputted keyword
        html.Div(className='six columns', children=[
            html.Div(className='row', children='Top 10 Relevant Keywords',
             style={'textAlign': 'center', 'color': 'black', 'fontSize': 18}),
            html.Div(className='row',
                     children='the top keywords that appear in the same publications with the inputted keyword',
                     style={'margin-top': '30px', 'textAlign': 'left', 'color': 'blue', 'fontSize': 15}),
            html.Div(className='row', children=[
                html.Div(className='six columns', children=[
                    dcc.Dropdown(id='related-keyword-dropdown', options=[], value='', placeholder='Select...')
                ]),
                html.Div(className='six columns', children=[
                    html.Button(id='related-add-button', type='submit', children='Add to Watchlist',
                                style={'margin-left': '20px'})
                ])
            ],
            style={'margin-top': '30px'}),
            dcc.Graph(id='related-keyword', figure={})
        ], style={'margin-left': '20px', 'margin-top': '30px'}),
        # Widget for displaying MongoDB query result displaying the top 10 keywords of all time
        html.Div(className='six columns', children=[
            html.Div(className='row', children='Top 10 Keywords of All Time',
             style={'textAlign': 'center', 'color': 'black', 'fontSize': 18}),
            html.Div(className='row',
                     children='the top 10 keywords that appear in all publications through all the years',
                     style={'margin-top': '30px', 'textAlign': 'left', 'color': 'blue', 'fontSize': 15}),
            html.Div(className='row', children=[
                html.Div(className='six columns', children=[
                    dcc.Dropdown(id='top-keyword-dropdown', options=[item['_id'] for item in graph_data], value='', placeholder='Select...')
                ]),
                html.Div(className='six columns', children=[
                    html.Button(id='top-add-button', type='submit', children='Add to Watchlist',
                                style={'margin-left': '20px'})
                ])
            ], style={'margin-top': '30px'}),
            html.Div(id='graph-container', children=[
                dcc.Graph(
                    id='bar-chart',
                    figure={
                        'data': [
                            {'x': [item['_id'] for item in graph_data], 'y': [item['count'] for item in graph_data], 'type': 'bar'}
                        ],
                        'layout': {
                            'xaxis': {'title': 'keyword'},
                            'yaxis': {'title': 'Count'}
                        }
                    }
                )
            ]) if graph_data else html.Div('No data available.', style={'textAlign': 'center'})
        ], style={'margin-left': '20px', 'margin-top': '30px'})
    ]),
    html.Div(className='row', children=[
        # Widget for the keyword watchlist table and dropdown list
        html.Div(className='six columns', children=[
            html.Div(className='row', children='Keyword Watchlist (Maximum 5)',
             style={'textAlign': 'center', 'color': 'black', 'fontSize': 18}),
            html.Div(className='row', children='only keywords that exist in the publication database can be added into watchlist',
             style={'margin-top': '30px', 'textAlign': 'left', 'color': 'blue', 'fontSize': 15}),
            html.Div(className='row', children=[
                html.Div(className='six columns', children=[
                    dcc.Dropdown(id='keyword-dropdown', options=[], value='', placeholder='Select...')
                ]),
                html.Div(className='six columns', children=[
                    html.Button(id='remove-button', type='submit', children='Remove',
                                style={'margin-left': '20px'})
                ])
            ],
            style={'margin-top': '30px'}),
            dash_table.DataTable(id='fav-keyword', data=[], page_size=10,
                                 style_table={'overflowX': 'auto', 'margin-top': '20px'})
        ], style={'margin-left': '20px', 'margin-top': '30px'}),
        # Widget for the watchlist comparison keyword diagram
        html.Div(className='six columns', children=[
            html.Div(className='row', children='Compare Keywords in Watchlist',
             style={'textAlign': 'center', 'color': 'black', 'fontSize': 18}),
            dcc.Graph(id='fav-trend', figure={})
        ], style={'margin-left': '20px', 'margin-top': '30px'})

    ])

])

#Callback function for "Search" button
@callback(
    [Output(component_id='top-prof', component_property='figure'),
     Output(component_id='top-uni', component_property='figure'),
     Output(component_id='related-keyword-dropdown', component_property='options'),
     Output(component_id='related-keyword', component_property='figure')],
    [Input(component_id='submit-button', component_property='n_clicks')],
    [State(component_id='keyword-input', component_property='value')]
)
def update_output(clicks, input_value):
    sql = mysql_utils(host=sqlhost, user=sqluser, password=sqlpassword, database=sqldatabase)
    neo4j = neo4j_utils(uri=neo4juri, user=neo4juser, password=neo4jpassword, database=neo4jdatabase)
    if clicks is not None:
        df_uni = sql.get_top_university_by_keyword(input_value)
        df_prof = neo4j.get_top_professor_by_keyword(input_value)
        df_rel_keyword = sql.get_related_keyword(input_value)
        dropdown_rel_keyword = sql.get_related_keyword_dropdown(input_value)
    else:
        df_uni = sql.get_top_university_by_keyword('')
        df_prof = neo4j.get_top_professor_by_keyword('')
        df_rel_keyword = sql.get_related_keyword('')
        dropdown_rel_keyword = sql.get_related_keyword_dropdown('')

    fig_uni = px.histogram(df_uni, y='university', x='faculty')
    fig_uni.update_layout(yaxis=dict(autorange='reversed'),
                          xaxis={'title': 'no. of interested faculty'})
    fig_uni.update_layout(yaxis={'title': 'university'})

    fig_rel_keyword = px.pie(df_rel_keyword, values='no. of shared publications', names='keyword')
    sql.cnx.close()

    fig_prof = px.scatter(df_prof, x='publication count', y='citation count', size='KRC', color='name',
                          hover_name='name', hover_data=['university'], log_x=True, size_max=60)
    neo4j.driver.close()

    return fig_prof, fig_uni, dropdown_rel_keyword, fig_rel_keyword

# Callback function for "Add to Watchlist" button on inputted keyword in the searchbox
@callback(
    [Output(component_id='keyword-dropdown', component_property='options', allow_duplicate=True),
     Output(component_id='fav-keyword', component_property='data', allow_duplicate=True),
     Output(component_id='fav-trend', component_property='figure', allow_duplicate=True)],
    [Input(component_id='add-button', component_property='n_clicks')],
    [State(component_id='keyword-input', component_property='value')], config_prevent_initial_callbacks=True
)
def add_keyword(clicks, input_value):
    sql = mysql_utils(host=sqlhost, user=sqluser, password=sqlpassword, database=sqldatabase)
    if clicks is not None:
        df_keyword = sql.add_fav_keyword(input_value)
    else:
        df_keyword = sql.show_fav_keyword()

    dropdown = sql.get_fav_keyword_dropdown()
    table = df_keyword.to_dict('records')
    df_trend = sql.get_fav_keyword_trend()
    fig = px.line(df_trend, x='year', y='count', color='keyword')
    fig.update_layout(yaxis={'title': 'no. of publications'})
    sql.cnx.close()

    return dropdown, table, fig

# Callback function for "Add to Watchlist" button on relevant keyword widget
@callback(
    [Output(component_id='keyword-dropdown', component_property='options', allow_duplicate=True),
     Output(component_id='fav-keyword', component_property='data', allow_duplicate=True),
     Output(component_id='fav-trend', component_property='figure', allow_duplicate=True)],
    [Input(component_id='related-add-button', component_property='n_clicks')],
    [State(component_id='related-keyword-dropdown', component_property='value')], config_prevent_initial_callbacks=True
)
def add_related_keyword(clicks, input_value):
    sql = mysql_utils(host=sqlhost, user=sqluser, password=sqlpassword, database=sqldatabase)
    if clicks is not None:
        df_keyword = sql.add_fav_keyword(input_value)
    else:
        df_keyword = sql.show_fav_keyword()

    dropdown = sql.get_fav_keyword_dropdown()
    table = df_keyword.to_dict('records')
    df_trend = sql.get_fav_keyword_trend()
    fig = px.line(df_trend, x='year', y='count', color='keyword')
    fig.update_layout(yaxis={'title': 'no. of publications'})
    sql.cnx.close()

    return dropdown, table, fig

# Callback function for "Add to Watchlist" button on top keyword widget
@callback(
    [Output(component_id='keyword-dropdown', component_property='options', allow_duplicate=True),
     Output(component_id='fav-keyword', component_property='data', allow_duplicate=True),
     Output(component_id='fav-trend', component_property='figure', allow_duplicate=True)],
    [Input(component_id='top-add-button', component_property='n_clicks')],
    [State(component_id='top-keyword-dropdown', component_property='value')], config_prevent_initial_callbacks=True
)
def add_top_keyword(clicks, input_value):
    sql = mysql_utils(host=sqlhost, user=sqluser, password=sqlpassword, database=sqldatabase)
    if clicks is not None:
        df_keyword = sql.add_fav_keyword(input_value)
    else:
        df_keyword = sql.show_fav_keyword()

    dropdown = sql.get_fav_keyword_dropdown()
    table = df_keyword.to_dict('records')
    df_trend = sql.get_fav_keyword_trend()
    fig = px.line(df_trend, x='year', y='count', color='keyword')
    fig.update_layout(yaxis={'title': 'no. of publications'})
    sql.cnx.close()

    return dropdown, table, fig

# Callback function for "Remove" button on the keyword watchlist table
@callback(
    [Output(component_id='keyword-dropdown', component_property='options'),
     Output(component_id='fav-keyword', component_property='data'),
     Output(component_id='fav-trend', component_property='figure')],
    [Input(component_id='remove-button', component_property='n_clicks')],
    [State(component_id='keyword-dropdown', component_property='value')]
)
def remove_keyword(clicks, input_value):
    sql = mysql_utils(host=sqlhost, user=sqluser, password=sqlpassword, database=sqldatabase)
    if clicks is not None:
        df_keyword = sql.remove_fav_keyword(input_value)
    else:
        df_keyword = sql.show_fav_keyword()

    dropdown = sql.get_fav_keyword_dropdown()
    table = df_keyword.to_dict('records')
    df_trend = sql.get_fav_keyword_trend()
    fig = px.line(df_trend, x='year', y='count', color='keyword')
    fig.update_layout(yaxis={'title': 'no. of publications'})
    sql.cnx.close()

    return dropdown, table, fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
