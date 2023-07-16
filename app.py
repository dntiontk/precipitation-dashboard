#!/usr/bin/env python3

from dash import Dash, html, dcc, Output, Input, State
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from os import path
import datetime
import time

# copy of cleaned data originally sourced from https://opendata.citywindsor.ca/
DATA_SRC = "https://raw.githubusercontent.com/dntiontk/windsor-opendata/main/precipitation/windsor-precipitation.csv"

df = pd.read_csv(DATA_SRC)
df["DateTime"] = pd.DatetimeIndex(df["DateTime"])

app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

server = app.server

jumbotron = html.Div(
    id="jumbotron",
    children=[
        dbc.Container(
            [
                html.H1(
                    "Windsor Precipitation Dashboard", className="display-3 text-center"
                ),
                html.P(
                    [
                        """ This project contains a dashboard focused on visualizing precipitation data in Windsor, Ontario. The dashboard provides insights and analysis based on the data collected from the City of Windsor's OpenData Catalogue. It is licensed by the Open Government License – The Corporation of the City of Windsor.
                        For more information, please see us """,
                        html.A(
                            "here.",
                            href="https://github.com/dntiontk/precipitation-dashboard",
                        ),
                    ]
                ),
                html.Hr(),
            ],
            fluid=True,
            className="py-3",
        ),
    ],
    className="bg-dark",
)


def select_all_button(id):
    return dbc.Button(
        id=id,
        size="sm",
        style={"margin-bottom": "10px"},
        children=["Select/Deselect All"],
    )


gauge_list = df["Gauge"].unique()
gauge_select = select_all_button("gauge-select")
gauge_checklist = dcc.Checklist(
    id="gauge-checklist",
    options=gauge_list,
    value=[],
    inputStyle={"margin-right": "20px"},
)

year_list = df["DateTime"].dt.year.unique()
first = year_list[0]
last = year_list[len(year_list) - 1]
year_slider = dcc.RangeSlider(
    id="year-slider",
    min=first,
    max=last,
    value=[first, last],
    allowCross=False,
    step=1,
    marks={str(i): str(i) for i in range(first, last + 1)},
)

filter_cards = dbc.CardGroup(
    id="filter-cards",
    children=[
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5("Select gauges", className="card-title"),
                    gauge_select,
                    gauge_checklist,
                ]
            )
        ),
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5(
                        "Select years",
                        className="card-title",
                        style={"margin-bottom": "20px"},
                    ),
                    year_slider,
                ]
            )
        ),
        dbc.Card(),
        dbc.Card(),
    ],
)

filter_accordion = html.Div(
    id="filter-accordion",
    children=[
        dbc.Accordion(
            [
                dbc.AccordionItem(
                    [filter_cards],
                    title="Filters",
                )
            ],
            start_collapsed=True,
        )
    ],
)

total_rainfall_card = dbc.Card(
    children=[
        dbc.CardBody(
            children=[
                dcc.Graph(id="total-rainfall-graph"),
            ],
        )
    ],
)

gauge_distribution_card = dbc.Card(
    children=[dbc.CardBody(children=[dcc.Graph(id="gauge-distribution-graph")])],
)

box_plot_accumulation_card = dbc.Card(
    children=[dbc.CardBody(children=[dcc.Graph(id="box-plot-accumulation")])],
)

top_row_cards = dbc.Row(
    [
        dbc.Col(gauge_distribution_card, width=5),
        dbc.Col(box_plot_accumulation_card, width=7),
    ]
)

app.layout = html.Div(
    children=[
        jumbotron,
        filter_accordion,
        html.Div(children=[top_row_cards]),
        total_rainfall_card,
    ],
)


@app.callback(
    Output("total-rainfall-graph", "figure"),
    [Input("gauge-checklist", "value"), Input("year-slider", "value")],
)
def total_rainfall_graph_update(gauges, years):
    first = years[0]
    last = years[len(years) - 1]
    filtered_df = df[
        (df["Gauge"].isin(gauges))
        & (df["DateTime"].dt.year >= first)
        & (df["DateTime"].dt.year <= last)
    ]
    fig = px.line(
        filtered_df,
        x="DateTime",
        y="Rainfall Total",
        color="Gauge",
        color_discrete_sequence=px.colors.qualitative.Dark24,
        template="plotly_dark",
    )
    return fig


@app.callback(
    Output("box-plot-accumulation", "figure"),
    [Input("gauge-checklist", "value"), Input("year-slider", "value")],
)
def box_accumulation_update(gauges, years):
    first = years[0]
    last = years[len(years) - 1]
    filtered_df = df[
        (df["Gauge"].isin(gauges))
        & (df["DateTime"].dt.year >= first)
        & (df["DateTime"].dt.year <= last)
    ]
    fig = px.histogram(
        filtered_df,
        x="DateTime",
        y="Daily Accumulation",
        color="Gauge",
        color_discrete_sequence=px.colors.qualitative.Dark24,
        template="plotly_dark",
    )
    return fig


@app.callback(
    Output("gauge-distribution-graph", "figure"),
    [Input("gauge-checklist", "value"), Input("year-slider", "value")],
)
def gauge_distribution_graph_update(gauges, years):
    first = years[0]
    last = years[len(years) - 1]
    filtered_df = df[
        (df["Gauge"].isin(gauges))
        & (df["DateTime"].dt.year >= first)
        & (df["DateTime"].dt.year <= last)
    ]
    rainfall = filtered_df.groupby("Gauge")["Rainfall Total"].sum()
    contribution = (rainfall / rainfall.sum()) * 100
    gauge_frame = contribution.to_frame().reset_index()
    fig = px.pie(
        gauge_frame,
        names="Gauge",
        values="Rainfall Total",
        title="Rainfall distribution ({}-{})".format(first, last),
        color_discrete_sequence=px.colors.qualitative.Dark24,
        template="plotly_dark",
    )
    return fig


@app.callback(
    Output("gauge-checklist", "value"),
    [Input("gauge-select", "n_clicks")],
    [State("gauge-checklist", "value")],
)
def on_gauge_click(n, value):
    if n is None:
        return gauge_list
    else:
        if value:
            return []
        else:
            return gauge_list


if __name__ == "__main__":
    app.run(debug=True)
