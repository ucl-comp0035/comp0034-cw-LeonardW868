import pandas as pd
import plotly.graph_objects as go
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import sqlite3

# Data loading from SQLite database
def load_data():
    conn = sqlite3.connect('unemployment.db')
    
    # Load gender data
    gender_data = pd.read_sql_query("""
        SELECT year, male, female 
        FROM gender_unemployment 
        ORDER BY year
    """, conn)
    
    # Load regional data
    regional_data = pd.read_sql_query("""
        SELECT tp.PeriodName, r.RegionName, ur.Rate
        FROM UnemploymentRateByRegion ur
        JOIN TimePeriod tp ON ur.PeriodID = tp.PeriodID
        JOIN Region r ON ur.RegionID = r.RegionID
        ORDER BY tp.PeriodID, r.RegionID
    """, conn)
    
    # Load London specific data
    london_data = pd.read_sql_query("""
        SELECT tp.PeriodName, ur.Rate
        FROM UnemploymentRateByRegion ur
        JOIN TimePeriod tp ON ur.PeriodID = tp.PeriodID
        JOIN Region r ON ur.RegionID = r.RegionID
        WHERE r.RegionName = 'LDN'
        ORDER BY tp.PeriodID
    """, conn)
    
    conn.close()
    return gender_data, regional_data, london_data

# Load the data
gender_data, regional_data, london_data = load_data()

# Initialize the Dash app
app = Dash(
    __name__,
    external_stylesheets=[
        'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css',
        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css'
    ],
    suppress_callback_exceptions=True
)

# Create home page layout
home_layout = html.Div([
    html.Div([
        html.H1('Unemployment Insight Hub'),
        html.Div([
            dcc.Link(
                'Go to Dashboard',
                href='/dashboard',
                className='dashboard-button'
            )
        ], style={
            'display': 'flex',
            'justifyContent': 'center',
            'marginTop': '50px'
        })
    ], className='container')
])

dashboard_layout = html.Div([
    html.Div([
        html.H1('Unemployment Insight Hub'),
        html.Div([
            html.Button('Gender Analysis',
                     id='nav-gender',
                     className='nav-link'),
            html.Button('Regional Trends',
                     id='nav-regional',
                     className='nav-link'),
            html.Button('London Focus',
                     id='nav-london',
                     className='nav-link'),
            html.Button('Trend Comparison',
                     id='nav-trend',
                     className='nav-link'),
            dcc.Link([html.I(className='fas fa-home'), ' Back to Home'],
                    href='/',
                    className='back-button')
        ], className='nav-menu',
           style={'position': 'sticky', 'top': '0', 'zIndex': '1000'}),
        html.Div([
            html.H2([html.I(className='fas fa-venus-mars'),
                    ' Gender-Based Unemployment Trends']),
            dcc.Loading(
                dcc.Graph(id='gender-unemployment-chart')
            )
        ], className='dashboard-section',
           id='gender-section'),
        html.Div([
            html.H2([html.I(className='fas fa-map-marked-alt'),
                    ' Regional Unemployment Comparison']),
            dcc.Loading(
                dcc.Graph(id='regional-unemployment-chart')
            )
        ], className='dashboard-section',
           id='regional-section'),
        html.Div([
            html.H2([html.I(className='fas fa-city'),
                    ' London Unemployment Trend']),
            dcc.Loading(
                dcc.Graph(id='london-unemployment-chart')
            )
        ], className='dashboard-section',
           id='london-section'),
        html.Div([
            html.H2([html.I(className='fas fa-chart-line'),
                    ' Trend Comparison']),
            dcc.Loading(
                dcc.Graph(id='trend-comparison-chart')
            ),
            dcc.Dropdown(
                id='trend-metric',
                options=[
                    {'label': 'Gender Gap', 'value': 'gender_gap'},
                    {'label': 'Regional Variance', 'value': 'regional_var'},
                    {'label': 'London vs National', 'value': 'london_national'}
                ],
                value='gender_gap',
                style={'width': '50%', 'margin': '20px auto'}
            )
        ], className='dashboard-section',
           id='trend-section')
    ], className='container')
])

# Main layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# Callback to update page content
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    """
    Route to appropriate page based on URL pathname.
    
    Args:
        pathname (str): Current URL pathname
    
    Returns:
        dash component: Appropriate layout for the current page
    """
    if pathname == '/dashboard':
        return dashboard_layout
    return home_layout

# Separate callbacks for each chart
@app.callback(
    Output('gender-unemployment-chart', 'figure'),
    [Input('url', 'pathname')]
)
def update_gender_chart(pathname):
    """
    Update the gender unemployment chart.
    
    Args:
        pathname (str): Current URL pathname
    
    Returns:
        dict: Plotly figure object
    """
    if pathname != '/dashboard':
        return {}
    conn = sqlite3.connect('unemployment.db')
    fresh_gender_data = pd.read_sql_query("""
        SELECT year, male, female
        FROM gender_unemployment
        ORDER BY year""", conn)
    conn.close()
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=fresh_gender_data['year'],
        y=fresh_gender_data['male'],
        name='Male',
        line={'color': '#3498db'}
    ))
    fig.add_trace(go.Scatter(
        x=fresh_gender_data['year'],
        y=fresh_gender_data['female'],
        name='Female',
        line={'color': '#e74c3c'}
    ))
    fig.update_layout(
        title='Gender-Based Unemployment Trends',
        xaxis_title='Year',
        yaxis_title='Unemployment Rate (%)',
        template='plotly_white'
    )
    return fig

@app.callback(
    Output('regional-unemployment-chart', 'figure'),
    [Input('url', 'pathname')]
)
def update_regional_chart(pathname):
    """
    Update the regional unemployment comparison chart.
    
    Args:
        pathname (str): Current URL pathname
    
    Returns:
        dict: Plotly figure object
    """
    if pathname != '/dashboard':
        return {}
    conn = sqlite3.connect('unemployment.db')
    fresh_regional_data = pd.read_sql_query("""
        SELECT tp.PeriodName, r.RegionName, ur.Rate
        FROM UnemploymentRateByRegion ur
        JOIN TimePeriod tp ON ur.PeriodID = tp.PeriodID
        JOIN Region r ON ur.RegionID = r.RegionID
        ORDER BY tp.PeriodID, r.RegionID""", conn)
    conn.close()
    fig = go.Figure()
    for region in fresh_regional_data['RegionName'].unique():
        region_df = fresh_regional_data[fresh_regional_data['RegionName'] == region]
        fig.add_trace(go.Bar(
            x=region_df['PeriodName'],
            y=region_df['Rate'],
            name=region
        ))
    fig.update_layout(
        title='Regional Unemployment Comparison',
        xaxis_title='Time Period',
        yaxis_title='Unemployment Rate (%)',
        template='plotly_white',
        barmode='group'
    )
    return fig

@app.callback(
    Output('london-unemployment-chart', 'figure'),
    [Input('url', 'pathname')]
)
def update_london_chart(pathname):
    """
    Update the London unemployment trend chart.
    
    Args:
        pathname (str): Current URL pathname
    
    Returns:
        dict: Plotly figure object
    """
    if pathname != '/dashboard':
        return {}
    conn = sqlite3.connect('unemployment.db')
    fresh_london_data = pd.read_sql_query("""
        SELECT tp.PeriodName, ur.Rate
        FROM UnemploymentRateByRegion ur
        JOIN TimePeriod tp ON ur.PeriodID = tp.PeriodID
        JOIN Region r ON ur.RegionID = r.RegionID
        WHERE r.RegionName = 'LDN'
        ORDER BY tp.PeriodID""", conn)
    conn.close()
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=fresh_london_data['PeriodName'],
        y=fresh_london_data['Rate'],
        name='London',
        line={'color': '#2ecc71'}
    ))
    fig.update_layout(
        title='London Unemployment Trend',
        xaxis_title='Time Period',
        yaxis_title='Unemployment Rate (%)',
        template='plotly_white'
    )
    return fig

@app.callback(
    Output('trend-comparison-chart', 'figure'),
    [Input('url', 'pathname'),
     Input('trend-metric', 'value')]
)
def update_trend_comparison(pathname, metric):
    """
    Update the trend comparison chart based on selected metric.
    
    Args:
        pathname (str): Current URL pathname
        metric (str): Selected comparison metric
    
    Returns:
        dict: Plotly figure object
    """
    if pathname != '/dashboard':
        return {}
    conn = sqlite3.connect('unemployment.db')
    fig = go.Figure()
    if metric == 'gender_gap':
        fresh_gender_data = pd.read_sql_query("""
            SELECT year, male, female
            FROM gender_unemployment
            ORDER BY year""", conn)
        gender_gap = fresh_gender_data['male'] - fresh_gender_data['female']
        fig.add_trace(go.Scatter(
            x=fresh_gender_data['year'],
            y=gender_gap,
            name='Gender Gap',
            line={'color': '#8e44ad'}
        ))
        title = 'Gender Gap in Unemployment Rates'
        yaxis_title = 'Gap (Male - Female) %'
    elif metric == 'regional_var':
        fresh_regional_data = pd.read_sql_query("""
            SELECT tp.PeriodName, ur.Rate
            FROM UnemploymentRateByRegion ur
            JOIN TimePeriod tp ON ur.PeriodID = tp.PeriodID
            JOIN Region r ON ur.RegionID = r.RegionID
            ORDER BY tp.PeriodID""", conn)
        regional_stats = fresh_regional_data.groupby('PeriodName')['Rate'].agg(['mean', 'std'])
        fig.add_trace(go.Scatter(
            x=regional_stats.index,
            y=regional_stats['std'],
            name='Regional Variance',
            line={'color': '#2ecc71'}
        ))
        title = 'Regional Unemployment Rate Variance'
        yaxis_title = 'Standard Deviation'
    else:  # london_national
        national_data = pd.read_sql_query("""
            SELECT tp.PeriodName, AVG(ur.Rate) as NationalAvg
            FROM UnemploymentRateByRegion ur
            JOIN TimePeriod tp ON ur.PeriodID = tp.PeriodID
            GROUP BY tp.PeriodID, tp.PeriodName
            ORDER BY tp.PeriodID""", conn)
        fresh_london_data = pd.read_sql_query("""
            SELECT tp.PeriodName, ur.Rate
            FROM UnemploymentRateByRegion ur
            JOIN TimePeriod tp ON ur.PeriodID = tp.PeriodID
            JOIN Region r ON ur.RegionID = r.RegionID
            WHERE r.RegionName = 'LDN'
            ORDER BY tp.PeriodID""", conn)
        london_vs_national = pd.merge(
            fresh_london_data,
            national_data,
            on='PeriodName'
        )
        difference = london_vs_national['Rate'] - london_vs_national['NationalAvg']
        fig.add_trace(go.Scatter(
            x=london_vs_national['PeriodName'],
            y=difference,
            name='London vs National',
            line={'color': '#e67e22'}
        ))
        title = 'London Unemployment Rate vs National Average'
        yaxis_title = 'Difference from National Average (%)'
    conn.close()
    fig.update_layout(
        title=title,
        xaxis_title='Time Period',
        yaxis_title=yaxis_title,
        template='plotly_white',
        hovermode='x unified'
    )
    return fig

# Add this clientside callback at the end of your file
app.clientside_callback(
    """
    function(n_clicks) {
        if (n_clicks) {
            const section = document.getElementById('gender-section');
            if (section) {
                section.scrollIntoView({behavior: 'smooth', block: 'start'});
            }
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output('gender-section', 'style'),
    Input('nav-gender', 'n_clicks'),
)

app.clientside_callback(
    """
    function(n_clicks) {
        if (n_clicks) {
            const section = document.getElementById('regional-section');
            if (section) {
                section.scrollIntoView({behavior: 'smooth', block: 'start'});
            }
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output('regional-section', 'style'),
    Input('nav-regional', 'n_clicks'),
)

app.clientside_callback(
    """
    function(n_clicks) {
        if (n_clicks) {
            const section = document.getElementById('london-section');
            if (section) {
                section.scrollIntoView({behavior: 'smooth', block: 'start'});
            }
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output('london-section', 'style'),
    Input('nav-london', 'n_clicks'),
)

app.clientside_callback(
    """
    function(n_clicks) {
        if (n_clicks) {
            const section = document.getElementById('trend-section');
            if (section) {
                section.scrollIntoView({behavior: 'smooth', block: 'start'});
            }
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output('trend-section', 'style'),
    Input('nav-trend', 'n_clicks'),
)

# Update the app styling
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Unemployment Insight Hub</title>
        {%favicon%}
        {%css%}
        <style>
            html {
                scroll-behavior: smooth;
                scroll-padding-top: 100px;
            }
            body {
                margin: 0;
                padding: 0;
                background: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)),
                            url('https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?ixlib=rb-1.2.1&auto=format&fit=crop&w=1950&q=80');
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
            }
            .container {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 15px;
                padding: 20px;
                margin: 20px auto;
            }
            .nav-menu {
                background: #2c3e50;
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 30px;
                display: flex;
                justify-content: space-around;
                align-items: center;
            }
            .nav-link {
                color: white !important;
                text-decoration: none;
                padding: 8px 15px;
                margin: 0 10px;
                border-radius: 5px;
                transition: background 0.3s;
                cursor: pointer;
            }
            .nav-link:hover {
                background: #34495e;
            }
            .back-button {
                color: white !important;
                background: #c0392b;
                padding: 8px 15px;
                border-radius: 5px;
                text-decoration: none;
                transition: background 0.3s;
            }
            .back-button:hover {
                background: #e74c3c;
            }
            .dashboard-section {
                margin-bottom: 40px;
            }
            .dashboard-button {
                background: #2c3e50;
                color: white !important;
                padding: 15px 30px;
                border-radius: 8px;
                text-decoration: none;
                font-size: 20px;
                transition: background 0.3s;
                text-align: center;
            }
            .dashboard-button:hover {
                background: #34495e;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

if __name__ == '__main__':
    app.run_server(debug=True)