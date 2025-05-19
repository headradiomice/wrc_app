import re

import dash
import dash_bootstrap_components as dbc
from dash import html
from dash.dependencies import Input, Output, State

from my_wrc_app.db_utils import (
    calculate_age,
    get_race_date,
    get_races,
    get_runner_info,
    get_runners,
    get_world_record,
    time_str_to_seconds,
    update_runner_value,
)
from my_wrc_app.layouts import make_search_layout, make_time_entry_layout


def register_callbacks(app):
    # -------------------------------------------------------------- #
    #  NAVIGATION – load the corresponding layout
    # -------------------------------------------------------------- #
    @app.callback(
        Output("content", "children"),
        [
            Input("search-link", "n_clicks"),
            Input("add-data-link", "n_clicks"),
            Input("upcoming-tasks-link", "n_clicks"),
            Input("visualisations-link", "n_clicks"),
            Input("add-time-link", "n_clicks"),
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

        if button_id == "add-data-link":
            return html.Div("This is the Add Data tab content.")

        if button_id == "upcoming-tasks-link":
            return html.Div("This is the Upcoming Tasks tab content.")

        if button_id == "visualisations-link":
            return html.Div("Coming soon!")

        if button_id == "add-time-link":
            races = get_races()
            runners = get_runners()
            return make_time_entry_layout(races, runners)

        return html.Div("Welcome to the dashboard!")

    # -------------------------------------------------------------- #
#  SUBMIT TIME
# -------------------------------------------------------------- #
    @app.callback(
        Output("submit-feedback", "children"),
        Input("submit-time-button", "n_clicks"),
        State("race-dropdown", "value"),   # e.g. '5k_1'
        State("runner-dropdown", "value"), # runner *name* (str)
        State("time-input", "value"),      # 'HH:MM:SS'  or  'MM:SS'
        prevent_initial_call=True,
    )
    def submit_time(_, race_key, runner_name, time_str):
        # ---- clean inputs ---------------------------------------- #
        if race_key:
            race_key = race_key.strip()        # removes stray \n

        if not (race_key and runner_name and time_str):
            return dbc.Alert(
                "Please select a race, a runner, and enter a time.", color="warning"
            )

        if not re.fullmatch(r"^\d{1,2}:\d{2}(:\d{2})?$", time_str.strip()):
            return dbc.Alert("Time must be MM:SS or HH:MM:SS.", color="danger")

        try:
            # ------------------------------------------------------ #
            #  1. Save RAW TIME
            # ------------------------------------------------------ #
            update_runner_value(runner_name, race_key, time_str.strip())

            # ------------------------------------------------------ #
            #  2. Meta data
            # ------------------------------------------------------ #
            runner_info = get_runner_info(runner_name)
            race_date   = get_race_date(race_key)

            print("DEBUG-runner_name:", repr(runner_name))
            print("DEBUG runner_info:", runner_info)
            print("DEBUG-race_key:", repr(race_key), "race_date:", race_date)


            if not runner_info or not race_date:
                return dbc.Alert("Missing runner or race meta data.", color="danger")

            age = calculate_age(runner_info["dob"], race_date)
            if age is None:
                return dbc.Alert(f"DOB or race date missing / unparsable.", color="danger")
            sex = runner_info["sex"]

            # ------------------------------------------------------ #
            #  3. Points (optional)
            # ------------------------------------------------------ #
            points = None
            base_distance = race_key.split("_")[0].lower()

            if base_distance == "5k":
                wr_sec = get_world_record(sex, age, distance="5k")
                if wr_sec is not None:
                    athlete_sec = time_str_to_seconds(time_str)
                    points = (wr_sec / athlete_sec) * 1000           # higher = better
                    update_runner_value(
                        runner_name, f"{race_key}_points", round(points, 6)
                    )

            # ------------------------------------------------------ #
            #  4. User message
            # ------------------------------------------------------ #
            races_map = {r["key"]: r["race"] for r in get_races()}
            nice_race_name = races_map.get(race_key, race_key)

            msg = (
                f"Saved {time_str} for runner {runner_name} "
                f"in race '{nice_race_name}'."
            )
            if points is not None:
                msg += f" Points: {points:.3f}"

            return dbc.Alert(msg, color="success")

        except Exception as ex:
            return dbc.Alert(f"Error: {ex}", color="danger")
