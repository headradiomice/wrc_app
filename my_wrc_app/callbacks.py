import dash
from dash.dependencies import Input, Output, State
from dash import html
import dash_bootstrap_components as dbc
from my_wrc_app.layouts import make_search_layout, make_time_entry_layout
from my_wrc_app.db_utils import (
    get_races,
    get_runners,
    update_runner_time,
    get_runner_info,
    get_race_date,
    get_world_record,
    time_str_to_seconds,
    calculate_age,
)
import re


def register_callbacks(app):

    @app.callback(
        Output("content", "children"),
        [
            Input("search-link", "n_clicks"),
            Input("add-data-link", "n_clicks"),
            Input("upcoming-tasks-link", "n_clicks"),
            Input("visualisations-link", "n_clicks"),
            Input("add-time-link", "n_clicks"),  # New time entry nav button
        ],
    )
    def render_content(
        search_clicks,
        add_data_clicks,
        upcoming_tasks_clicks,
        visualizations_clicks,
        add_time_clicks,
    ):
        ctx = dash.callback_context
        if not ctx.triggered:
            return html.Div("Welcome to the dashboard!")
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

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
    prevent_initial_call=True,
)
    def submit_time(n_clicks, race_key, runner_id, time_str):
        if not race_key or not runner_id or not time_str:
            return dbc.Alert(
                "Please select a race, runner, and enter a valid time.", color="warning"
            )

        import re
        if not re.match(r"^\d{1,2}:\d{2}:\d{2}$", time_str):
            return dbc.Alert("Invalid time format. Use HH:MM:SS.", color="danger")

        try:
            # 1. Save raw time into runner_info.<race_key> column
            update_runner_time(runner_id, race_key, time_str)

            # 2. Fetch runner info & race date
            runner_info = get_runner_info(runner_id)
            race_date = get_race_date(race_key)
            if not runner_info or not race_date:
                return dbc.Alert(
                    "Could not fetch runner info or race date.", color="danger"
                )

            # 3. Calculate runner age on race day
            age = calculate_age(runner_info["dob"], race_date)
            sex = runner_info["sex"]

            points = None

            # 4. Extract base distance for world record lookup: e.g. '5k' from '5k_1'
            base_distance = race_key.split("_")[0].lower()

            # 5. Calculate points only if distance recognized, e.g., '5k'
            if base_distance == "5k":
                # Fetch world record in seconds for this age and sex
                wr_seconds = get_world_record(sex, age, distance="5k")
                if wr_seconds is None:
                    return dbc.Alert(
                        f"No world record found for age {age} and sex {sex}",
                        color="warning",
                    )

                # Convert runner's time to seconds
                runner_seconds = time_str_to_seconds(time_str)

                # Calculate points (ratio)
                points = runner_seconds / wr_seconds

                # Update runner_info.<race_key>_points column
                points_col = f"{race_key}_points"
                update_runner_time(runner_id, points_col, str(points))

            # 6. Prepare race display name for user-friendly message
            race_map = {r["key"]: r["race"] for r in get_races()}
            race_name = race_map.get(race_key, race_key)

            msg = f"Time {time_str} saved for runner ID {runner_id} in race '{race_name}'."
            if points is not None:
                msg += f" Points calculated: {points:.3f}"

            return dbc.Alert(msg, color="success")

        except Exception as e:
            return dbc.Alert(f"Error saving time or calculating points: {str(e)}", color="danger")
    
    @app.callback(
        Output("search-results-table", "data"),
        Input("search-button", "n_clicks"),
        State("search-input", "value"),
        prevent_initial_call=True,
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


