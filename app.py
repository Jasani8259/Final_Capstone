# app.py

import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import flask

# Import doctor dashboard
from dashboard_doctor import doctor_dashboard_layout, register_doctor_callbacks

# Initialize app
app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Dummy User Database (Hardcoded for now)
users = {
    "doctor1@example.com": {"password": "doctorpass", "role": "doctor", "name": "Dr. John Doe"},
    "patient1@example.com": {"password": "patientpass", "role": "patient", "name": "Alice Smith"},
    "nurse1@example.com": {"password": "nursepass", "role": "nurse", "name": "Nurse Nancy"},
    "admin1@example.com": {"password": "adminpass", "role": "admin", "name": "Admin Bob"},
    "frontdesk1@example.com": {"password": "frontdeskpass", "role": "frontdesk", "name": "Frontdesk Charlie"}
}

# App Layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='current_user', storage_type='session'),  # Session store
    html.Div(id='page-content')
])

# Login Page Layout
login_layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H2("Healthcare System Login", className="text-center my-4"),
            dbc.Input(id="login-email", placeholder="Email", type="email", className="mb-3"),
            dbc.Input(id="login-password", placeholder="Password", type="password", className="mb-3"),
            dbc.Button("Login", id="login-button", color="primary", className="w-100"),
            html.Div(id="login-alert", className="text-danger mt-3")
        ], width=4)
    ], justify="center", align="center", style={"minHeight": "100vh"})
], fluid=True)

# Placeholder Dashboards (Patient, Nurse, Admin, Frontdesk for now)
patient_dashboard_layout = html.H1("🧑‍⚕️ Patient Dashboard - Coming Soon")
nurse_dashboard_layout = html.H1("💉 Nurse Dashboard - Coming Soon")
admin_dashboard_layout = html.H1("🛡️ Admin Dashboard - Coming Soon")
frontdesk_dashboard_layout = html.H1("🧾 Frontdesk Dashboard - Coming Soon")

# Routing Logic
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
    State('current_user', 'data')
)
def display_page(pathname, current_user):
    if pathname == '/':
        return login_layout
    elif pathname == '/doctor_dashboard' and current_user and current_user['role'] == 'doctor':
        return doctor_dashboard_layout
    elif pathname == '/patient_dashboard' and current_user and current_user['role'] == 'patient':
        return patient_dashboard_layout
    elif pathname == '/nurse_dashboard' and current_user and current_user['role'] == 'nurse':
        return nurse_dashboard_layout
    elif pathname == '/admin_dashboard' and current_user and current_user['role'] == 'admin':
        return admin_dashboard_layout
    elif pathname == '/frontdesk_dashboard' and current_user and current_user['role'] == 'frontdesk':
        return frontdesk_dashboard_layout
    else:
        return html.H1("❌ Access Denied. You are not authorized to view this page.")

# Login Authentication
@app.callback(
    Output('current_user', 'data'),
    Output('url', 'pathname'),
    Output('login-alert', 'children'),
    Input('login-button', 'n_clicks'),
    State('login-email', 'value'),
    State('login-password', 'value'),
    prevent_initial_call=True
)
def login_user(n_clicks, email, password):
    user = users.get(email)
    if user and user['password'] == password:
        # Login Successful
        role = user['role']
        if role == "doctor":
            return user, '/doctor_dashboard', ""
        elif role == "patient":
            return user, '/patient_dashboard', ""
        elif role == "nurse":
            return user, '/nurse_dashboard', ""
        elif role == "admin":
            return user, '/admin_dashboard', ""
        elif role == "frontdesk":
            return user, '/frontdesk_dashboard', ""
    else:
        # Login Failed
        return dash.no_update, dash.no_update, "Invalid email or password."

# Register external dashboard callbacks
register_doctor_callbacks(app)

# Run Server
if __name__ == '__main__':
    app.run(debug=True, port=8050)
