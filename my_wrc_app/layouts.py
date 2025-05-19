from dash import html, dash_table, dcc
import dash_bootstrap_components as dbc

def make_search_layout():
    return html.Div(
        [
            html.H2("Search Runners"),
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


def base_layout():
    return dbc.Container(
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
                    "padding": "5px 0",
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
                                dbc.Button("Visualisations", id="visualisations-link", n_clicks=0, className="btn-custom"),
                                dbc.Button("Add Time", id="add-time-link", n_clicks=0, className="btn-custom"),
                            ],
                            vertical=True,
                            pills=True,
                            style={"paddingTop": "20px"}
                        ),
                        width=2,
                        style={"backgroundColor": "black", "color": "yellow"}
                    ),
                    dbc.Col(
                        html.Div(id="content"),  # This div is KEY for callbacks to update content!
                        width=10,
                        style={"padding": "20px"}
                    )
                ]
            )
        ],
        style={"backgroundColor": "black", "color": "yellow", "height": "100vh"}
    )

def make_time_entry_layout(races, runners):
    race_options = [{'label': r['race'], 'value': r['key']} for r in races]
    runner_options = [{'label': r['name'], 'value': r['id']} for r in runners]

    return dbc.Container([
        dbc.Row([
            dbc.Label("Select Race"),
            dcc.Dropdown(id="race-dropdown", options=race_options, placeholder="Select a race")
        ], className="mb-3"),
        dbc.Row([
            dbc.Label("Select Runner"),
            dcc.Dropdown(id="runner-dropdown", options=runner_options, placeholder="Select a runner")
        ], className="mb-3"),
        dbc.Row([
            dbc.Label("Enter Time (e.g., 00:25:30)"),
            dbc.Input(id="time-input", type="text", placeholder="HH:MM:SS"),
        ], className="mb-3"),
        dbc.Button("Submit Time", id="submit-time-button", color="primary"),
        html.Div(id="submit-feedback", className="mt-3")
    ])
