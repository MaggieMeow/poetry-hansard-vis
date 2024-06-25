import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

viz_df = pd.read_csv('location_counts_by_year.csv', index_col=0)

type_column_name = 'type' # Change to 'type_biased' for types biased towards australia.

# Normalize the 'type' values as specified
#viz_df[type_column_name] = viz_df[type_column_name].apply(lambda x: x if x in ['continent', 'territory', 'region', 'country', 'state', 'city'] else 'others')

# Initialize Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

app.layout = html.Div([
    dcc.Dropdown(
        id='placename-dropdown',
        options=[{'label': i, 'value': i} for i in sorted(viz_df['placename'].unique())],
        multi=True,
        placeholder='Select a Placename'
    ),
    dcc.Dropdown(
        id='year-dropdown',
        options=[{'label': i, 'value': i} for i in sorted(viz_df['year'].unique())],
        multi=True,
        placeholder='Select a Year'
    ),
    dcc.Dropdown(
        id='type-dropdown',
        options=[{'label': i, 'value': i} for i in viz_df[type_column_name].dropna().unique()],
        multi=True,
        placeholder='Select a Type'
    ),
    dcc.Input(
        id='year-start-input',
        type='number',
        placeholder='Year Start',
        style={'margin': '10px'}
    ),
    dcc.Input(
        id='year-end-input',
        type='number',
        placeholder='Year End',
        style={'margin': '10px'}
    ),
    dcc.Input(
        id='min-count-input',
        type='number',
        placeholder='Min count total',
        style={'margin': '10px'}
    ),
    dcc.Input(
        id='max-count-input',
        type='number',
        placeholder='Max count total',
        style={'margin': '10px'}
    ),
    dcc.Graph(id='graph-output', style={'height': '600px'})
])

@app.callback(
    Output('year-dropdown', 'options'),
    Input('placename-dropdown', 'value')
)
def update_year_options(selected_placenames):
    if selected_placenames:
        years = viz_df[viz_df['placename'].isin(selected_placenames)]['year'].unique()
        years_sorted = sorted(years)
        return [{'label': str(year), 'value': year} for year in years_sorted]
    return []

@app.callback(
    Output('graph-output', 'figure'),
    [Input('placename-dropdown', 'value'),
     Input('year-dropdown', 'value'),
     Input('type-dropdown', 'value'),
     Input('year-start-input', 'value'),
     Input('year-end-input', 'value'),
     Input('min-count-input', 'value'),
     Input('max-count-input', 'value')]
)
def update_graph(selected_placenames, selected_years, selected_types, year_start, year_end, min_count, max_count):
    filtered_df = viz_df.copy()
    if selected_placenames:
        filtered_df = filtered_df[filtered_df['placename'].isin(selected_placenames)]
    if selected_years:
        filtered_df = filtered_df[filtered_df['year'].isin(selected_years)]
    if selected_types:
        filtered_df = filtered_df[filtered_df[type_column_name].isin(selected_types)]
    if year_start and year_end:
        filtered_df = filtered_df[(filtered_df['year'] >= year_start) & (filtered_df['year'] <= year_end)]
    if min_count is not None:
        filtered_df = filtered_df[filtered_df['count_total'] >= min_count]
    if max_count is not None:
        filtered_df = filtered_df[filtered_df['count_total'] <= max_count]
    
    # make stacked bar sorted by year
    filtered_df = filtered_df.sort_values(by=['placename','year','count_total'], ascending=[True, True, False])
    
    fig = px.bar(filtered_df, x='placename', y='count_year', color=type_column_name,
                 barmode='group', hover_data=['year', 'count_year', 'count_total'])
    fig.update_layout(
        xaxis={'categoryorder': 'total descending'},
        xaxis_tickangle=-45
    )
    
    # Customize hover text to include year prominently
    fig.update_traces(hovertemplate="<br>".join([
        "Placename: %{x}",
        "Year: %{customdata[0]}",
        "Count Year: %{y}",
        "Total Count: %{customdata[1]}"
    ]))

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)