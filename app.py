#!/usr/bin/env python3

from dash import Dash, html, dcc, Output, Input
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from os import path
import datetime

# copy of cleaned data originally sourced from https://opendata.citywindsor.ca/
DATA_SRC = "https://raw.githubusercontent.com/dntiontk/windsor-opendata/main/precipitation/windsor-precipitation.csv"
TEMPLATE = "plotly_dark"

df = pd.read_csv(DATA_SRC)

df["DateTime"] = pd.DatetimeIndex(df["DateTime"])

first, last = df["DateTime"].dt.year.min(), df["DateTime"].dt.year.max()
unique_years = df["DateTime"].dt.year.unique()
gauges = df["Gauge"].unique()

app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

server = app.server

app.layout = html.Div(
    [
        html.H1(children="Windsor Precipitation Dashboard ({}-{})".format(first, last)),
        html.P(
            "This dashboard provides precipitation data for the City of Windsor, Ontario. The data used for these contains information licensed under the Open Government License - The Corporation of the City of Windsor"
        ),
        html.Div("Gauge contribution to annual rainfall distribution"),
        dcc.Graph(id="gauge-contribution-pie"),
        # dcc.Dropdown(
        #    id="year-selector", options=unique_years, value=last, clearable=False, tem
        # ),
        dcc.RangeSlider(
            first,
            last,
            value=[first, last],
            id="year-slider",
            allowCross=False,
            step=1,
            marks={i: "{}".format(i) for i in range(first, last + 1)},
        ),
        html.Div("Annual cumulative rainfall composition by gauge over time"),
        dcc.Graph(id="cumulative-rainfall-stacked"),
        dcc.Dropdown(
            id="collector-style",
            options=["Rainfall Total", "Daily Accumulation"],
            value="Rainfall Total",
        ),
    ],
)


@app.callback(
    Output("gauge-contribution-pie", "figure"),
    Input("year-slider", "value"),
)
def update_pie_graph(value):
    start = value[0]
    end = value[len(value) - 1]
    filtered_df = df[
        (df["DateTime"].dt.year >= start) & (df["DateTime"].dt.year <= end)
    ]

    annual_rainfall = filtered_df.groupby("Gauge")["Rainfall Total"].sum()
    gauge_contribution = (annual_rainfall / annual_rainfall.sum()) * 100
    gauge_frame = gauge_contribution.to_frame().reset_index()

    fig = px.pie(
        gauge_frame,
        names="Gauge",
        values="Rainfall Total",
        title="Annual rainfall distribution ({}-{})".format(start, end),
        template=TEMPLATE,
    )
    return fig


@app.callback(
    Output("cumulative-rainfall-stacked", "figure"),
    Input("year-slider", "value"),
)
def update_stacked_chart(value):
    start = value[0]
    end = value[len(value) - 1]
    filtered_df = df[
        (df["DateTime"].dt.year >= start) & (df["DateTime"].dt.year <= end)
    ]

    fig = px.area(
        filtered_df,
        x="DateTime",
        y="Rainfall Total",
        color="Gauge",
    )
    return fig
    # [
    #    html.P("Precipitation per gauge"),
    #    dcc.Graph(
    #        id="total",
    #        figure=px.line(
    #            df,
    #            x="DateTime",
    #            y="Rainfall Total",
    #            labels={"Rainfall Total": "mm/hr"},
    #            color="Gauge",
    #            title="Rainfall Total",
    #        ),
    #    ),
    #    html.Hr(),
    #    dcc.Graph(
    #        id="daily",
    #        figure=px.line(
    #            df,
    #            x="DateTime",
    #            y="Daily Accumulation",
    #            labels={"Daily Accumulation": "mm/hr"},
    #            color="Gauge",
    #            title="Daily Accumulation",
    #        ),
    #    ),
    # ]


if __name__ == "__main__":
    app.run(debug=True)
