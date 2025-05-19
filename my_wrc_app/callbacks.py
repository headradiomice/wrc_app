import dash
from dash.dependencies import Input, Output, State
from dash import html
from my_wrc_app.layouts import make_search_layout, make_time_entry_layout
from my_wrc_app.db_utils import get_races, get_runners, update_runner_time
import dash_bootstrap_components as dbc

def register_callbacks(app):

    @app.callback(
        Output("content", "children"),
        [
            Input("search-link", "n_clicks"),
            Input("add-data-link", "n_clicks"),
            Input("upcoming-tasks-link", "n_clicks"),
            Input("visualisations-link", "n_clicks"),
            Input("add-time-link", "n_clicks"),  # New time entry nav button
        ]
    )
    def render_content(search_clicks, add_data_clicks, upcoming_tasks_clicks, visualizations_clicks, add_time_clicks):
        ctx = dash.callback_context
        if not ctx.triggered:
            return html.Div("Welcome to the dashboard!")
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if button_id == "search-link":
            return make_search_layout()
        elif button_id == "add-data-link":
            return html.Div("This is the Add Data tab content.")
        elif button_id == "upcoming-tasks-link":
            return html.Div("This is the Upcoming Tasks tab content.")
        elif button_id == "visualisations-link":
            return html.Div("Coming soon!")
        elif button_id == "add-time-link":
            races = get_races()
            runners = get_runners()
            return make_time_entry_layout(races, runners)

        return html.Div("Welcome to the dashboard!")

    @app.callback(
    Output("submit-feedback", "children"),
    Input("submit-time-button", "n_clicks"),
    State("race-dropdown", "value"),
    State("runner-dropdown", "value"),
    State("time-input", "value"),
    prevent_initial_call=True
)
    def submit_time(n_clicks, race_key, runner_id, time_str):
        if not race_key or not runner_id or not time_str:
            return dbc.Alert("Please select a race, runner, and enter a valid time.", color="warning")

        import re
        if not re.match(r'^\d{1,2}:\d{2}:\d{2}$', time_str):
            return dbc.Alert("Invalid time format. Use HH:MM:SS.", color="danger")

        try:
        # Fetch race list and make a dict: key -> name
            race_map = {r['key']: r['race'] for r in get_races()}  
            race_name = race_map.get(race_key, race_key)  # fallback to key

            update_runner_time(runner_id, race_key, time_str)

            return dbc.Alert(f"Time {time_str} saved for runner ID {runner_id} in race '{race_name}'.", color="success")

        except Exception as e:
            return dbc.Alert(f"Error saving time: {str(e)}", color="danger")

    @app.callback(
        Output("search-results-table", "data"),
        Input("search-button", "n_clicks"),
        State("search-input", "value"),
        prevent_initial_call=True
    )
    def update_search_results(n_clicks, search_value):
        if not search_value:
            return []
        results = search_calibrations(search_value)
        for row in results:
            date = row.get("DOB")
            if date and not isinstance(date, str):
                row["DOB"] = date.strftime("%Y-%m-%d")
        return results
