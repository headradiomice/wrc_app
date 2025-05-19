import dash
from dash.dependencies import Input, Output, State
from wrc_app.layouts import make_search_layout
from wrc_app.search_function import search_calibrations
from dash import html

def register_callbacks(app):
    @app.callback(
        Output("content", "children"),
        [
            Input("search-link", "n_clicks"),
            Input("add-data-link", "n_clicks"),
            Input("upcoming-tasks-link", "n_clicks"),
            Input("visualisations-link", "n_clicks"),
        ]
    )
    def render_content(search_clicks, add_data_clicks, upcoming_tasks_clicks, visualizations_clicks):
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
            return html.Div("coming soon!")
        return html.Div("Welcome to the dashboard!")

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
