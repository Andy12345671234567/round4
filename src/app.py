import dash_bootstrap_components as dbc
import plotly.express as px
import dash_html_components as html
from dash import dcc
from dash import Dash, dcc, html, Input, Output
import pandas as pd
import numpy as np

df = pd.read_csv(
    'https://raw.githubusercontent.com/Andy12345671234567/round4/main/final.csv')

#Data cleaning
#Adjusted the dates of sale to be mm-yy
df["month"] = pd.to_datetime(df["month"])
df["month"] = df["month"].dt.strftime('%Y')
df.columns = df.columns.str.replace('month', 'year')

df['floor_area_sqm'].apply(np.ceil)
df['floor_area_sqm'] = df['floor_area_sqm'].astype('int')
df.dtypes

#Getting the lease out
#Assumption is to forgo the number of months
df['remaining_lease'] = df['remaining_lease'].str[:2]
df['remaining_lease'] = df['remaining_lease'].astype('int')

#Getting what I need
df_median = df[['year', 'town', 'flat_type', 'street_name',
                'floor_area_sqm', 'flat_model', 'remaining_lease', 'resale_price']]

df_flat = df[["year", "town", "street_name", "flat_type", "storey_range",
              "floor_area_sqm", "flat_model", "remaining_lease", "resale_price"]]

# Choice to choose: Year / Town /Street Name / Storey_range  / Flat Model
# Sliders for remaining_lease and floor_area_sqm
# Target variable: flat_type
year_choices = df_flat['year'].unique()
town_choices = df_flat['town'].unique()
street_choices = df_flat['street_name'].unique()
storey_choices = df_flat['storey_range'].unique()
flat_model_choices = df_flat['flat_model'].unique()
flat_type_choices = df_flat['flat_type'].unique()


# Adding card

app = Dash(__name__, external_stylesheets=[dbc.themes.COSMO])
server = app.server

#Have all the components in the layout


left_side = dbc.Card([
    dbc.CardBody([
        html.H4('Make your Choice'),
        dcc.Dropdown(id='year_choice', options=year_choices, value=year_choices[0],
                     clearable=False, style={'width': '300px', 'height': '40px'}),
        dcc.Dropdown(id='town_choice', options=[], style={
                     'width': '300px', 'height': '40px'}),
        dcc.Dropdown(id='street_choice', options=[], style={
                     'width': '300px', 'height': '40px'})

    ])
], style={'width': '20%', 'display': 'inline-block', 'vertical-align': 'top', 'background-color': '#f9f9f9'})

right_side = dbc.Card([
    dbc.CardBody([
        html.H4('Analysis on HDB Transactions from 2017 to 2023(Q1)',
                style={'color': 'Black'}),
        dcc.Graph(id='graph', figure={}),
        dcc.Graph(id='graph_median', figure={})

    ])
], style={'width': '80%', 'display': 'inline-block'})


app.layout = html.Div([
    dbc.Row([
        left_side,
        right_side
    ]), html.Hr(style={'margin-top': '0', 'margin-bottom': '0', 'border-top': '1px solid #ddd'})


], style={'background-color': '#fff'})


@app.callback(
    Output('town_choice', 'options'),
    Input('year_choice', 'value')

)
def set_options(chosen_year):
    df_flat_year = df_flat[df_flat['year'] == str(chosen_year)]
    town_choices = df_flat_year['town'].unique()

    return town_choices


@app.callback(

    Output('street_choice', 'options'),
    Input('year_choice', 'value'),
    Input('town_choice', 'value'),

)
def street_options(chosen_year, chosen_town):

    df_flat_year = df_flat[df_flat['year'] == str(chosen_year)]
    df_flat_town = df_flat_year[df_flat_year['town'] == str(chosen_town)]
    street_choices = df_flat_town['street_name'].unique()

    return street_choices


@app.callback(
    Output('graph', 'figure'),
    Input('year_choice', 'value'),
    Input('town_choice', 'value'),
    Input('street_choice', 'value')


)
def graph_count(chosen_year, chosen_town, chosen_street):
    df_flat_year = df_flat[df_flat['year'] == str(chosen_year)]
    df_flat_town = df_flat_year[df_flat_year['town'] == str(chosen_town)]
    df_flat_street = df_flat_town[df_flat_town['street_name'] == str(
        chosen_street)]

    dfcount = df_flat_street.groupby('flat_type').count()
    fig = px.bar(dfcount, x=dfcount.index, y='year', labels={
                 'df_median.index': 'Flat Type', 'year': 'Count'}, title='Number of Flat - Types Sold', template='ggplot2')

    return fig


@app.callback(
    Output('graph_median', 'figure'),
    Input('year_choice', 'value'),
    Input('town_choice', 'value'),
    Input('street_choice', 'value')


)
def graph_median(chosen_year, chosen_town, chosen_street):
    df_flat_year = df_flat[df_flat['year'] == str(chosen_year)]
    df_flat_town = df_flat_year[df_flat_year['town'] == str(chosen_town)]
    df_flat_street = df_flat_town[df_flat_town['street_name'] == str(
        chosen_street)]

    df_median = df_flat_street.groupby("flat_type")['resale_price'].median()
    fig_median = px.bar(df_median, x=df_median.index, y='resale_price', labels={
                        'df_median.index': 'Flat Type', 'resale_price': 'Median Price'}, title='Median Prices for Flat - Types', template='ggplot2')

    return fig_median


if __name__ == '__main__':
    app.run_server(debug=True)



