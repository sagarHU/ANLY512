###############################################################
##  Name: Sagar Panwar                                       ##
##  Course Name: ANLY 512                                    ##
##  Summer 2024                                              ##
##  Final Project                                            ##
###############################################################


import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import json

df = pd.read_csv("Health_Dataset.csv")

# Dash App Initialization
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


app.layout = html.Div([
    html.H1("Health and Activity Dashboard"),

    # Input fields
    dbc.Row([
        dbc.Col([
            dcc.Input(id='age-input', type='number', placeholder='Enter Age', min=0, max=120),
        ], width=3),
        dbc.Col([
            dcc.Dropdown(id='gender-input', options=[{'label': i, 'value': i} for i in df['gender'].unique()],
                         placeholder='Select Gender'),
        ], width=3),
        dbc.Col([
            dcc.Input(id='height-input', type='number', placeholder='Enter Height (cm)', min=0, max=300),
        ], width=3),
        dbc.Col([
            dcc.Input(id='weight-input', type='number', placeholder='Enter Weight (kg)', min=0, max=500),
        ], width=3),
    ], className='mb-4'),

    # Visualizations
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='steps-calories-scatter')
        ], width=6),
        dbc.Col([
            dcc.Graph(id='heart-rate-histogram')
        ], width=6),
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='activity-pie-chart')
        ], width=4),
        dbc.Col([
            dcc.Graph(id='distance-boxplot')
        ], width=4),
        dbc.Col([
            dcc.Graph(id='heart-rate-comparison')
        ], width=4),
    ]),

    # Button to generate static HTML
    html.Button('Generate Static HTML', id='generate-html-button', n_clicks=0),
    html.Div(id='download-link', style={'display': 'none'})
])


@app.callback(
    [Output('steps-calories-scatter', 'figure'),
     Output('heart-rate-histogram', 'figure'),
     Output('activity-pie-chart', 'figure'),
     Output('distance-boxplot', 'figure'),
     Output('heart-rate-comparison', 'figure')],
    [Input('age-input', 'value'),
     Input('gender-input', 'value'),
     Input('height-input', 'value'),
     Input('weight-input', 'value')]
)
def update_graphs(age, gender, height, weight):
    # Filter the dataframe based on user inputs
    filtered_df = df
    if age:
        filtered_df = filtered_df[filtered_df['age'] == age]
    if gender:
        filtered_df = filtered_df[filtered_df['gender'] == gender]
    if height:
        filtered_df = filtered_df[filtered_df['height'] == height]
    if weight:
        filtered_df = filtered_df[filtered_df['weight'] == weight]

    # 1. Steps vs Calories Scatter Plot
    scatter_fig = px.scatter(filtered_df, x='steps', y='calories', color='activity',
                             title='Steps vs Calories Burned')

    # 2. Heart Rate Histogram
    hist_fig = px.histogram(filtered_df, x='hear_rate', title='Distribution of Heart Rates')

    # 3. Activity Pie Chart
    pie_fig = px.pie(filtered_df, names='activity', title='Activity Distribution')

    # 4. Distance Boxplot by Activity
    box_fig = px.box(filtered_df, x='activity', y='distance', title='Distance by Activity Type')

    # 5. Heart Rate Comparison (Resting vs Normal)
    heart_comp_fig = go.Figure()
    heart_comp_fig.add_trace(go.Box(y=filtered_df['resting_heart'], name='Resting Heart Rate'))
    heart_comp_fig.add_trace(go.Box(y=filtered_df['norm_heart'], name='Normal Heart Rate'))
    heart_comp_fig.update_layout(title='Resting vs Normal Heart Rate Comparison')

    return scatter_fig, hist_fig, pie_fig, box_fig, heart_comp_fig


# Callback to generate static HTML
@app.callback(
    Output('download-link', 'children'),
    Input('generate-html-button', 'n_clicks'),
    [State('age-input', 'value'),
     State('gender-input', 'value'),
     State('height-input', 'value'),
     State('weight-input', 'value')],
    prevent_initial_call=True
)
def generate_static_html(n_clicks, age, gender, height, weight):
    if n_clicks > 0:
        # Generate figures
        scatter_fig, hist_fig, pie_fig, box_fig, heart_comp_fig = update_graphs(age, gender, height, weight)

        # Create HTML content
        html_content = f"""
        <html>
        <head>
            <title>Health and Activity Dashboard</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        </head>
        <body>
            <h1>Health and Activity Dashboard</h1>
            <div>
                <label>Age: <input type="number" value="{age or ''}" min="0" max="120"></label>
                <label>Gender: <input type="text" value="{gender or ''}"></label>
                <label>Height (cm): <input type="number" value="{height or ''}" min="0" max="300"></label>
                <label>Weight (kg): <input type="number" value="{weight or ''}" min="0" max="500"></label>
            </div>
            <div id="steps-calories-scatter"></div>
            <div id="heart-rate-histogram"></div>
            <div id="activity-pie-chart"></div>
            <div id="distance-boxplot"></div>
            <div id="heart-rate-comparison"></div>
            <script>
                var scatter_data = {json.dumps(scatter_fig.to_dict())};
                var hist_data = {json.dumps(hist_fig.to_dict())};
                var pie_data = {json.dumps(pie_fig.to_dict())};
                var box_data = {json.dumps(box_fig.to_dict())};
                var heart_comp_data = {json.dumps(heart_comp_fig.to_dict())};

                Plotly.newPlot('steps-calories-scatter', scatter_data.data, scatter_data.layout);
                Plotly.newPlot('heart-rate-histogram', hist_data.data, hist_data.layout);
                Plotly.newPlot('activity-pie-chart', pie_data.data, pie_data.layout);
                Plotly.newPlot('distance-boxplot', box_data.data, box_data.layout);
                Plotly.newPlot('heart-rate-comparison', heart_comp_data.data, heart_comp_data.layout);
            </script>
        </body>
        </html>
        """

        # Save HTML content to a file
        with open('dashboard.html', 'w') as f:
            f.write(html_content)

        return html.A('Download Static HTML', href='/dashboard.html', download='dashboard.html')


if __name__ == '__main__':
    app.run_server(debug=True)