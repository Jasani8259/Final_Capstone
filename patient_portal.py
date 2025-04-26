# patient_portal.py

import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import requests

# Initialize app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX], suppress_callback_exceptions=True)
server = app.server
API = "http://localhost:8000"

# ======= Layout =======
app.layout = dbc.Container([
    html.H2("🏥 Patient Health Portal", className="text-center text-primary my-4 fw-bold"),

    dbc.Tabs([
        dbc.Tab(label="📋 Health Records", tab_id="records"),
        dbc.Tab(label="💊 Medications", tab_id="meds"),
        dbc.Tab(label="🧪 Lab Results", tab_id="labs"),
        dbc.Tab(label="❤️ Risk Scores", tab_id="risks"),
        dbc.Tab(label="💉 Vaccinations", tab_id="vaccines"),
        dbc.Tab(label="📚 Education", tab_id="education"),
        dbc.Tab(label="📨 Messages", tab_id="messages"),
        dbc.Tab(label="📅 Appointments", tab_id="appointments"),
        dbc.Tab(label="📓 Symptom Journal", tab_id="journal"),
        dbc.Tab(label="🎯 Health Goals", tab_id="goals")
    ], id="tabs", active_tab="records", className="mb-3"),

    html.Div(id="tab-content")
], fluid=True)

# ======= Callbacks =======

@app.callback(Output("tab-content", "children"), Input("tabs", "active_tab"))
def render_tab(tab):
    if tab == "records":
        return get_health_records()
    elif tab == "meds":
        return get_medications()
    elif tab == "labs":
        return get_lab_results()
    elif tab == "risks":
        return get_risk_scores()
    elif tab == "vaccines":
        return get_vaccination_records()
    elif tab == "education":
        return get_educational_resources()
    elif tab == "messages":
        return get_messages_section()
    elif tab == "appointments":
        return get_appointments()
    elif tab == "journal":
        return get_symptom_journal()
    elif tab == "goals":
        return get_health_goals()
    else:
        return "Tab content not found."

# ======= Sections =======

def get_health_records():
    try:
        patients = requests.get(f"{API}/active_patients").json()
        if not patients:
            return html.Div("No patient records available.")
        patient = patients[0]  # Assume logged-in patient's first record (can be customized)
        return dbc.Card([
            dbc.CardBody([
                html.H4(f"{patient['first_name']} {patient['last_name']}", className="fw-bold"),
                html.P(f"Gender: {patient['gender']}"),
                html.P(f"Date of Birth: {patient['date_of_birth']}"),
                html.P(f"Check-in Status: {patient['check_in_status']}")
            ])
        ])
    except:
        return html.Div("Error loading patient records.")

def get_medications():
    return html.Div([
        html.H4("Current Medications"),
        html.Ul([
            html.Li("Lisinopril 10mg - Daily at 8 AM"),
            html.Li("Metformin 500mg - Twice daily with meals")
        ]),
        html.P("Please follow medication schedule strictly.")
    ])

def get_lab_results():
    try:
        labs = requests.get(f"{API}/recent_lab_reports").json()
        if not labs:
            return html.Div("No lab reports available.")
        df = pd.DataFrame(labs)
        fig = px.scatter(df, x="report_date", y="report_type", color="result",
                         title="Recent Lab Results", labels={"report_type": "Test", "report_date": "Date"})
        fig.update_traces(marker=dict(size=12), selector=dict(mode='markers'))
        return dcc.Graph(figure=fig)
    except:
        return html.Div("Error loading lab reports.")

def get_risk_scores():
    try:
        risks = requests.get(f"{API}/risk_scores").json()
        if not risks:
            return html.Div("No risk scores available.")
        df = pd.DataFrame(risks)
        fig = px.line(df, x="score_date", y=["heart_disease_risk", "diabetes_risk"],
                      title="Risk Score Trends", markers=True)
        fig.update_layout(legend_title_text="Risk Type")
        return dcc.Graph(figure=fig)
    except:
        return html.Div("Error loading risk scores.")

def get_vaccination_records():
    return html.Div([
        html.H4("Vaccination Records"),
        html.Ul([
            html.Li("Flu Vaccine - Oct 2023"),
            html.Li("COVID-19 Booster - Jan 2024")
        ]),
        html.P("Upcoming: Tetanus Booster (Due 2026)")
    ])

def get_educational_resources():
    return html.Div([
        html.H4("Educational Resources"),
        html.Ul([
            html.Li(html.A("Managing Hypertension", href="#")),
            html.Li(html.A("Diabetes Lifestyle Changes", href="#")),
            html.Li(html.A("Exercise Recommendations", href="#"))
        ])
    ])

def get_messages_section():
    return html.Div([
        html.H4("Secure Messaging"),
        dbc.Textarea(id="message-box", placeholder="Type your message here...", className="mb-2"),
        dbc.Button("Send Message", color="primary")
    ])

def get_appointments():
    try:
        appointments = requests.get(f"{API}/appointments_today").json()
        if not appointments:
            return html.Div("No upcoming appointments.")
        items = [html.Li(f"{appt['appointment_date']} - {appt['doctor_name']}") for appt in appointments]
        return html.Div([
            html.H4("Appointments Today"),
            html.Ul(items)
        ])
    except:
        return html.Div("Error loading appointments.")

def get_symptom_journal():
    return html.Div([
        html.H4("Symptom Tracker"),
        dbc.Textarea(placeholder="Describe any symptoms or concerns...", rows=5)
    ])

def get_health_goals():
    return html.Div([
        html.H4("Health Goals"),
        html.Ul([
            html.Li("Achieve 10,000 steps per day"),
            html.Li("Maintain Blood Pressure under 120/80"),
            html.Li("Control blood sugar to normal range")
        ])
    ])

# ======= Run =======
if __name__ == '__main__':
    app.run(debug=True, port=8056)
