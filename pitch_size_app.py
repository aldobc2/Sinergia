import dash
from dash import dcc, html, callback_context
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State

app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div([  # Sidebar
        html.H2("Parametros", style={'text-align': 'center'}),
        html.Div([
            html.Div(id='total-area', style={'margin-top': '20px', 'margin-bottom': '20px', 'font-weight': 'bold'}),
            html.Div(id='display-density', style={'margin-top': '20px', 'font-weight': 'bold'}),
            html.Br(),
            html.Label("N jugadores Equipo A:"),
            dcc.Input(id='players-team-a', type='number', value=5, min=1, max=11, step=1, style={'width': '100%'}),  # Initial value set to 5
            html.Label("N jugadores Equipo B:"),
            dcc.Input(id='players-team-b', type='number', value=5, min=1, max=11, step=1, style={'width': '100%'}),  # Initial value set to 5
            html.Label("Largo (m):"),
            dcc.Input(id='input-length', type='number', value=40, min=5, style={'width': '100%'}),
            html.Label("Ancho (m):"),
            dcc.Input(id='input-width', type='number', value=30, min=5, style={'width': '100%'}),
            html.Br(),
            
            html.Div(id='energy-bars', children=[
                dcc.Graph(id='total-distance-bar', config={'staticPlot': True}, style={'height': '60px'}),
                dcc.Graph(id='high-speed-running-bar', config={'staticPlot': True}, style={'height': '60px'}),
                dcc.Graph(id='sprint-distance-bar', config={'staticPlot': True}, style={'height': '60px'}),
                dcc.Graph(id='accelerations-decelerations-bar', config={'staticPlot': True}, style={'height': '60px'}),
            ]),
        ], style={'padding': '20px'}),
    ], style={
        'background-color': '#f8f9fa',
        'padding': '10px 20px',
        'width': '300px',
        'position': 'fixed',
        'height': '100%',
        'overflow': 'auto'
    }),
    html.Div([  # Content
        dcc.Graph(id='pitch-visualization')
    ], style={'margin-left': '340px'}),
])

@app.callback(
    [Output('total-area', 'children'),
     Output('input-length', 'value'),
     Output('input-width', 'value'),
     Output('display-density', 'children'),  # Updated to display calculated density
     Output('total-distance-bar', 'figure'),
     Output('high-speed-running-bar', 'figure'),
     Output('sprint-distance-bar', 'figure'),
     Output('accelerations-decelerations-bar', 'figure')],
    [Input('players-team-a', 'value'),
     Input('players-team-b', 'value'),
     Input('input-length', 'value'),
     Input('input-width', 'value')],
    [State('input-length', 'value'), State('input-width', 'value')]
)
def update_interactive_elements(team_a, team_b, length_input, width_input, length_state, width_state):
    ctx = callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
    total_players = (team_a or 0) + (team_b or 0)

    # Constrain input values to be within specified minimums and maximums
    length = max(min(length_input, 105), 5)
    width = max(min(width_input, 68), 5)
    total_area = length * width
    density = total_area / total_players if total_players > 0 else 0

    # Calculate energy levels based on updated density
    levels = calculate_energy_levels(density)
    total_distance_fig = create_energy_bar(levels[0], 5, "Distancia total")
    high_speed_running_fig = create_energy_bar(levels[1], 5, "Alta velocidad")
    sprint_distance_fig = create_energy_bar(levels[2], 5, "Sprints")
    accelerations_decelerations_fig = create_energy_bar(levels[3], 5, "Acc y Dec")

    return (f"Area Total: {round(total_area)} m²",
            length, width,
            f"Densidad por jugador: {round(density)} m²",
            total_distance_fig, high_speed_running_fig, sprint_distance_fig, accelerations_decelerations_fig)

def calculate_energy_levels(density):
    if density > 300:
        return 5, 5, 5, 2
    elif 250 < density <= 300:
        return 5, 4, 4, 3
    elif 200 < density <= 250:
        return 4, 4, 3, 3
    elif 150 < density <= 200:
        return 4, 3, 2, 4
    elif 100 < density <= 150:
        return 3, 2, 1, 5
    elif 50 < density <= 100:
        return 2, 1, 0, 5
    else:
        return 1, 0, 0, 4


def create_energy_bar(level, max_level, title):
    fig = go.Figure(go.Bar(
        x=[level],
        y=[title],
        orientation='h',
        marker_color='orange',
        text=[f"{title}"],
        width=2
    ))

    fig.update_layout(
        xaxis=dict(range=[0, 5], showticklabels=True),
        yaxis=dict(showticklabels=False),
        margin=dict(l=10, r=10, t=30, b=10),
        height=60
    )

    return fig

@app.callback(
    Output('pitch-visualization', 'figure'),
    [Input('input-length', 'value'), Input('input-width', 'value')]
)
def update_visualization(length, width):
    if length is None or width is None or (length == 0 and width == 0):
        length, width = 50, 30  # Default dimensions
        
    fig = go.Figure()

    # Draw the full pitch background
    fig.add_shape(type="rect", x0=0, y0=0, x1=105, y1=68, line=dict(color="Black"), fillcolor="DarkGreen")

    # Halfway line
    fig.add_shape(type="line", x0=52.5, y0=0, x1=52.5, y1=68, line=dict(color="White"))

    # Center circle
    fig.add_shape(type="circle", xref="x", yref="y", x0=47.5, y0=31, x1=57.5, y1=37, line_color="White")

    # Penalty areas (adjusted to 40.3m wide)
    # Left penalty area
    fig.add_shape(type="rect", x0=0, y0=(68-40.3)/2, x1=16.5, y1=(68+40.3)/2, line=dict(color="White"))
    # Right penalty area
    fig.add_shape(type="rect", x0=105-16.5, y0=(68-40.3)/2, x1=105, y1=(68+40.3)/2, line=dict(color="White"))

    # Left goal area (no change)
    fig.add_shape(type="rect", x0=0, y0=30.34, x1=5.5, y1=37.66, line=dict(color="White"))
    # Right goal area (no change)
    fig.add_shape(type="rect", x0=105-5.5, y0=30.34, x1=105, y1=37.66, line=dict(color="White"))

    # Drawing the exercise area with correct orientation
    fig.add_shape(type="rect", 
                  x0=52.5 - (length / 2), y0=34 - (width / 2), 
                  x1=52.5 + (length / 2), y1=34 + (width / 2), 
                  line=dict(color="Black"), fillcolor="Blue", opacity=0.5)

    # Annotation for the exercise area dimensions
    fig.add_annotation(x=52.5, y=34 + (width / 2) + 1, text=f"Length: {length}m", showarrow=False, font=dict(color="White", size=14), bgcolor="Black")
    fig.add_annotation(x=52.5 - (length / 2) - 1, y=34, text=f"Width: {width}m", showarrow=False, font=dict(color="White", size=14), bgcolor="Black", textangle=-90)

    # Update the layout of the figure
    fig.update_layout(width=800, height=520, title="Dimensiones y Densidad", 
                      xaxis_showgrid=False, yaxis_showgrid=False,
                      xaxis_range=[0, 105], yaxis_range=[0, 68], 
                      xaxis_showticklabels=False, yaxis_showticklabels=False)

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
