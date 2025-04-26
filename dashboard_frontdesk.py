# dashboard_frontdesk.py (Professional Frontend)

import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import requests
import plotly.express as px

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX], suppress_callback_exceptions=True)
server = app.server
API = "http://localhost:8000"

# ===== Sidebar =====
sidebar = html.Div(
    [
        html.Div(
            [
                html.Img(src="/assets/hospital_logo.png", style={"width": "80%", "marginBottom": "20px"}),
                html.H4("Health Center", className="text-primary text-center mb-4")
            ],
            className="text-center"
        ),
        dbc.Nav(
            [
                dbc.NavLink("🏥 Dashboard", href="/", active="exact"),
                dbc.NavLink("🧑‍⚕️ Patient Profiles", href="/patient_record", active="exact"),
                dbc.NavLink("📋 Visit Records", href="/visits", active="exact"),
                dbc.NavLink("💊 Medications", href="/medications", active="exact"),
                dbc.NavLink("📈 Reports", href="/reports", active="exact"),
                dbc.NavLink("⚙️ Settings", href="/settings", active="exact")
            ],
            vertical=True,
            pills=True,
            className="flex-column"
        )
    ],
    style={
        "backgroundColor": "#f8f9fa",
        "height": "100vh",
        "padding": "20px",
        "borderRight": "1px solid #dee2e6",
        "position": "fixed",
        "width": "16%"
    }
)

# ===== Header =====
header = dbc.Navbar(
    dbc.Container([
        dbc.Row([
            dbc.Col(html.H2("Health Center Dashboard", className="text-white"), width="auto"),
            dbc.Col(
                dbc.Button("Logout", href="/", color="danger", className="ms-auto"),
                width="auto"
            )
        ], align="center", className="g-0")
    ]),
    color="primary",
    dark=True,
    className="mb-4",
    style={"marginLeft": "16%"}
)

# ===== Main Dashboard Layout =====
def get_dashboard_layout():
    return html.Div([
        html.H3("Today's Overview", className="mb-4 fw-bold"),

        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H6("Active Patients", className="text-muted"),
                    html.H2(id="active-patient-count", className="text-primary fw-bold"),
                    html.P("+5% from last month", className="text-muted")
                ])
            ], className="shadow-sm p-3 bg-light"), width=4),

            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H6("Appointments Today", className="text-muted"),
                    html.H2(id="appointment-count", className="text-danger fw-bold"),
                    html.P(id="appointment-remaining", className="text-muted")
                ])
            ], className="shadow-sm p-3 bg-light"), width=4),

            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H6("Health Trends (Last 6 Months)", className="text-muted"),
                    dcc.Graph(id="health-trend-chart", style={"height": "250px"})
                ])
            ], className="shadow-sm p-3 bg-light"), width=4)
        ], className="mb-4"),

        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H6("Patient Demographics", className="text-muted"),
                    dcc.Graph(id="age-group-pie", style={"height": "300px"})
                ])
            ], className="shadow-sm p-3 bg-light"), width=6),

            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H6("Recent Lab Reports", className="text-muted"),
                    dcc.Interval(id="refresh-interval", interval=10*1000, n_intervals=0),
                    html.Div(id="recent-activity-wrapper")
                ])
            ], className="shadow-sm p-3 bg-light"), width=6)
        ], className="mb-4"),
    ], style={"marginLeft": "16%", "padding": "30px"})

# Placeholder Pages
def get_placeholder_layout(title):
    return html.Div([
        html.H3(title, className="mt-4 mb-3"),
        html.P("This page is under development. Please check back soon.")
    ], style={"marginLeft": "16%", "padding": "30px"})

# ===== App Layout =====
app.layout = html.Div([
    dcc.Location(id="url"),
    sidebar,
    header,
    html.Div(id="page-content")
])

# ===== Routing =====
@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def display_page(pathname):
    if pathname == "/":
        return get_dashboard_layout()
    elif pathname == "/patients":
        return get_placeholder_layout("Patient Profiles")
    elif pathname == "/visits":
        return get_placeholder_layout("Visit Records")
    elif pathname == "/medications":
        return get_placeholder_layout("Medications")
    elif pathname == "/risk":
        return get_placeholder_layout("Risk Assessment")
    elif pathname == "/resources":
        return get_placeholder_layout("Resources")
    elif pathname == "/reports":
        return get_placeholder_layout("Reports")
    elif pathname == "/settings":
        return get_placeholder_layout("Settings")
    return get_placeholder_layout("Page Not Found")

# ===== API-Driven Callbacks =====
@app.callback(Output("active-patient-count", "children"), Input("refresh-interval", "n_intervals"))
def update_patient_count(_):
    try:
        data = requests.get(f"{API}/active_patients").json()
        return f"{len(data):,}"
    except:
        return "0"

@app.callback(
    Output("appointment-count", "children"),
    Output("appointment-remaining", "children"),
    Input("refresh-interval", "n_intervals")
)
def update_appointments(_):
    try:
        data = requests.get(f"{API}/appointments_today").json()
        remaining = max(0, 30 - len(data))
        return str(len(data)), f"{remaining} remaining"
    except:
        return "0", "--"

@app.callback(Output("age-group-pie", "figure"), Input("refresh-interval", "n_intervals"))
def update_age_group_chart(_):
    try:
        data = requests.get(f"{API}/age_demographics").json()
        df = pd.DataFrame(data)
        fig = px.pie(df, names='age_group', values='count', title='Age Group Distribution', hole=0.3)
        fig.update_traces(textinfo='percent+label', pull=[0.05]*len(df), hoverinfo='label+percent+value')
        fig.update_layout(clickmode='event+select')
        return fig
    except:
        return px.pie(title="No data available")

@app.callback(Output("health-trend-chart", "figure"), Input("refresh-interval", "n_intervals"))
def update_trend_chart(_):
    try:
        data = requests.get(f"{API}/monthly_risk_trends").json()
        df = pd.DataFrame(data)
        df['month'] = pd.to_datetime(df['month']).dt.strftime('%b')
        fig = px.bar(df, x='month', y='avg_heart_risk', title='Avg Heart Risk (Monthly)', labels={'avg_heart_risk': 'Avg Heart Risk'}, color='avg_heart_risk')
        fig.update_traces(marker_line_width=0, hovertemplate='Month: %{x}<br>Avg Risk: %{y:.2f}')
        fig.update_layout(clickmode='event+select')
        return fig
    except:
        return px.bar(title="No data available")

@app.callback(Output("recent-activity-wrapper", "children"), Input("refresh-interval", "n_intervals"))
def update_activity_list(_):
    try:
        data = requests.get(f"{API}/recent_lab_reports").json()
        items = [html.Li([html.Strong(f"{r['first_name']} {r['last_name']}"), f" - {r['report_type']} on {r['report_date']}"]) for r in data[:5]]
        return html.Ul(items, className="list-unstyled")
    except:
        return html.Div("No recent activity available")

# ===== Run App =====
if __name__ == "__main__":
    app.run(debug=True, port=8050)
