# nurse_portal.py

import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import requests

# Initialize app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX], suppress_callback_exceptions=True)
server = app.server
API = "http://localhost:8000"

# ======= Layout =======

# Sidebar
sidebar = html.Div([
    html.Div([
        html.Img(src="/assets/hospital_logo.png", style={"width": "80%", "marginBottom": "20px"}),
        html.H4("Nurse Portal", className="text-primary text-center mb-4")
    ], className="text-center"),

    dbc.Nav([
        dbc.NavLink("🏥 Dashboard", href="/", active="exact"),
        dbc.NavLink("📋 Patients", href="/patients", active="exact"),
        dbc.NavLink("🧪 Lab Reports", href="/labs", active="exact"),
        dbc.NavLink("❤️ Vitals", href="/vitals", active="exact"),
        dbc.NavLink("⚙️ Settings", href="/settings", active="exact"),
    ], vertical=True, pills=True)
], style={
    "backgroundColor": "#f8f9fa",
    "height": "100vh",
    "padding": "20px",
    "position": "fixed",
    "width": "16%",
    "borderRight": "1px solid #dee2e6"
})

# Header
header = dbc.Navbar(
    dbc.Container([
        dbc.Row([
            dbc.Col(html.H2("Health Center Nurse Portal", className="text-white"), width="auto"),
            dbc.Col(dbc.Button("Logout", href="/", color="danger", className="ms-auto"), width="auto")
        ], align="center", className="g-0")
    ]),
    color="primary",
    dark=True,
    className="mb-4",
    style={"marginLeft": "16%"}
)

# Main layout
app.layout = html.Div([
    dcc.Location(id="url"),
    sidebar,
    header,
    html.Div(id="page-content", style={"marginLeft": "16%", "padding": "30px"})
])

# ======= Pages =======

def dashboard_page():
    return html.Div([
        html.H3("Today's Overview", className="mb-4 fw-bold"),

        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H6("Active Patients"),
                    html.H2(id="active-patient-count", className="text-primary fw-bold")
                ])
            ], className="shadow-sm p-3 bg-light"), width=6),

            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H6("New Lab Reports (Last 7 days)"),
                    html.H2(id="lab-report-count", className="text-danger fw-bold")
                ])
            ], className="shadow-sm p-3 bg-light"), width=6)
        ])
    ])

def patients_page():
    try:
        data = requests.get(f"{API}/active_patients").json()
        if not data:
            return html.Div("No active patients found.")
        table = dbc.Table.from_dataframe(pd.DataFrame(data)[['first_name', 'last_name', 'gender', 'date_of_birth']], striped=True, bordered=True, hover=True)
        return html.Div([
            html.H4("Checked-in Patients"),
            table
        ])
    except:
        return html.Div("Error loading patient data.")

def labs_page():
    return html.Div([
        html.H4("Recent Lab Reports", className="mb-4 fw-bold"),
        dcc.Interval(id="refresh-labs", interval=10*1000, n_intervals=0),
        html.Div(id="lab-reports-list"),
        html.Hr(),
        html.H4("Add New Lab Report"),
        dbc.Form([
            dbc.Row([
                dbc.Col(dbc.Input(id="patient-id", placeholder="Patient ID", type="number"), width=4),
                dbc.Col(dbc.Input(id="report-type", placeholder="Report Type (e.g., Blood Test)", type="text"), width=4),
                dbc.Col(dbc.Input(id="report-result", placeholder="Result (Normal/Abnormal)", type="text"), width=4)
            ], className="mb-3"),
            dbc.Button("Submit Lab Report", id="submit-lab-btn", color="success"),
            html.Div(id="submit-status", className="mt-3")
        ])
    ])

def vitals_page():
    try:
        data = requests.get(f"{API}/risk_scores").json()
        if not data:
            return html.Div("No vitals data found.")
        df = pd.DataFrame(data)
        fig = px.line(df, x="score_date", y=["heart_disease_risk", "diabetes_risk"], markers=True, title="Vitals Risk Score Trends")
        return dcc.Graph(figure=fig)
    except:
        return html.Div("Error loading vitals data.")

def settings_page():
    return html.Div([
        html.H4("Settings"),
        html.P("Profile updates, notification settings coming soon...")
    ])

# ======= Routing =======

@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def display_page(pathname):
    if pathname == "/":
        return dashboard_page()
    elif pathname == "/patients":
        return patients_page()
    elif pathname == "/labs":
        return labs_page()
    elif pathname == "/vitals":
        return vitals_page()
    elif pathname == "/settings":
        return settings_page()
    return html.H1("404 - Page not found")

# ======= Live Updating Cards =======

@app.callback(Output("active-patient-count", "children"), Input("refresh-labs", "n_intervals"))
def update_active_patients(_):
    try:
        data = requests.get(f"{API}/active_patients").json()
        return str(len(data))
    except:
        return "0"

@app.callback(Output("lab-report-count", "children"), Input("refresh-labs", "n_intervals"))
def update_lab_reports(_):
    try:
        data = requests.get(f"{API}/recent_lab_reports").json()
        return str(len(data))
    except:
        return "0"

@app.callback(Output("lab-reports-list", "children"), Input("refresh-labs", "n_intervals"))
def refresh_lab_list(_):
    try:
        data = requests.get(f"{API}/recent_lab_reports").json()
        items = [html.Li(f"{r['report_type']} - {r['result']} ({r['report_date']})") for r in data[:10]]
        return html.Ul(items)
    except:
        return html.Div("No recent lab reports available.")

# ======= Submitting New Lab Report =======

@app.callback(
    Output("submit-status", "children"),
    Input("submit-lab-btn", "n_clicks"),
    State("patient-id", "value"),
    State("report-type", "value"),
    State("report-result", "value"),
    prevent_initial_call=True
)
def submit_lab_report(n_clicks, patient_id, report_type, report_result):
    try:
        payload = {
            "patient_id": patient_id,
            "report_type": report_type,
            "report_date": pd.Timestamp.now().isoformat(),
            "result": report_result
        }
        # 🚨 NOTE: You need to create /save_lab_report in FastAPI backend for real saving
        response = requests.post(f"{API}/save_lab_report", json=payload)
        if response.status_code == 200:
            return dbc.Alert("✅ Lab Report Saved Successfully!", color="success")
        else:
            return dbc.Alert("❌ Failed to save Lab Report.", color="danger")
    except Exception as e:
        return dbc.Alert(f"❌ Error: {str(e)}", color="danger")

# ======= Run =======
if __name__ == "__main__":
    app.run(debug=True, port=8052)
