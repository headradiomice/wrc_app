import dash
from dash import callback_context  
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from my_wrc_app.auth import auth
from my_wrc_app.layouts import base_layout
from my_wrc_app.callbacks import register_callbacks

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

auth(app)  # set up BasicAuth (see auth.py example below)

app.layout = base_layout()

register_callbacks(app)

if __name__ == "__main__":
    app.run_server(debug=True)


server = app.server
