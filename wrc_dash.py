import dash
from dash import dcc, html, dash_table, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import dash_auth
import plotly.express as px
import plotly.graph_objs as go
#from calibration_pie_chart import generate_pie_chart
from search_function import search_calibrations
# Server address is http://127.0.0.1:8050/
# Authentication setup
VALID_USERNAME_PASSWORD_PAIRS = {
    'admin': 'admin'
}

# code just for the search function
def make_search_layout():
    return html.Div(
        [
            html.H2("Search"),
            dbc.Input(id="search-input", placeholder="Runner name", debounce=True),
            dbc.Button("Search", id="search-button", n_clicks=0, className="mt-2", color="primary"),
            html.Hr(),
            dash_table.DataTable(
                id="search-results-table",
                columns=[
                    {"name": "Runner", "id": "name"},
                    {"name": "DOB", "id": "dob"},
                    {"name": "M/F", "id": "sex"},
                ],
                data=[],
                page_size=10,
                style_table={"overflowX": "auto"},
                style_cell={
                    "textAlign": "left",
                    "backgroundColor": "#333",
                    "color": "white",
                    "border": "1px solid #444",
                },
                style_header={
                    "backgroundColor": "#222",
                    "color": "white",
                    "fontWeight": "bold",
                },
                style_data_conditional=[
                    {
                        "if": {"row_index": "odd"},
                        "backgroundColor": "#2a2a2a",
                    }
                ],
            ),
        ],
        style={"color": "white"},
    )



# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

auth = dash_auth.BasicAuth(app, VALID_USERNAME_PASSWORD_PAIRS)

# Define the app layout
app.layout = dbc.Container(
    fluid=True,
    children=[
        dbc.Row(
            dbc.Col(
                html.Img(src='/assets/wrc_logo.png', height="75px"),
                width="auto",
            ),
            justify="start",
            align="center",
            style={
                "backgroundColor": "black",
                "padding": "5px 0",  # Minimal padding to keep the border thin
                "borderBottom": "2px solid black"
            }
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Nav(
                        [
                            dbc.Button("Search", id="search-link", n_clicks=0, className="btn-custom"),
                            dbc.Button("Add Data", id="add-data-link", n_clicks=0, className="btn-custom"),
                            dbc.Button("Upcoming Tasks", id="upcoming-tasks-link", n_clicks=0, className="btn-custom"),
                            dbc.Button("Visualisations", id="visualisations-link", n_clicks=0, className="btn-custom"),  # New button
                        ],
                        vertical=True,
                        pills=True,
                        style={"paddingTop": "20px"}
                    ),
                    width=2,
                    style={"backgroundColor": "black", "color": "yellow"}
                ),
                dbc.Col(
                    html.Div(id="content"),
                    width=10,
                    style={"padding": "20px"}
                )
            ]
        )
    ],
    style={"backgroundColor": "black", "color": "yellow", "height": "100vh"}
)

# Custom CSS for button styling
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            .btn-custom {
                background-color: #333;
                color: yellow;
                margin-bottom: 10px;
                width: 100%;
                transition: background-color 0.3s, transform 0.3s, box-shadow 0.3s;
                border: none;
                border-radius: 5px;
                font-family: 'Roboto', sans-serif;
                box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.3);
            }
            .btn-custom:hover {
                background-color: #555;
                transform: scale(1.05);
                box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.5);
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

# Define callback to update tab content
@app.callback(
    dash.dependencies.Output("content", "children"),
    [dash.dependencies.Input("search-link", "n_clicks"),
     dash.dependencies.Input("add-data-link", "n_clicks"),
     dash.dependencies.Input("upcoming-tasks-link", "n_clicks"),
     dash.dependencies.Input("visualisations-link", "n_clicks")]  # New button input
)
def render_content(search_clicks, add_data_clicks, upcoming_tasks_clicks, visualizations_clicks):
    ctx = dash.callback_context

    if not ctx.triggered:
        return html.Div("Welcome to the dashboard!")
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == "search-link":
        return make_search_layout()
    elif button_id == "add-data-link":
        return html.Div("This is the Add Data tab content.")
    elif button_id == "upcoming-tasks-link":
        return html.Div("This is the Upcoming Tasks tab content.")
    elif button_id == "visualisations-link":
        return html.Div("coming soon!")
        # Example visualization with Plotly Graph Object
        # fig = generate_pie_chart()
        # return html.Div([
        #     html.H2("Visualisations"),
        #     dcc.Graph(
        #         figure=fig,
        #         style={"height": "400px", "width": "400px"}
        #         )  # Embedding a Plotly graph
        # ])

    return html.Div("Welcome to the dashboard!")

@app.callback(
    Output("search-results-table", "data"),
    Input("search-button", "n_clicks"),
    State("search-input", "value"),
    prevent_initial_call=True,
)
def update_search_results(n_clicks, search_value):
    if not search_value:
        return []

    results = search_calibrations(search_value)  # Calls your DB search function

    # Format date if it's not already a string
    for row in results:
        date = row.get("DOB")
        if date and not isinstance(date, str):
            row["DOB"] = date.strftime("%Y-%m-%d")

    return results


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)

server = app.server