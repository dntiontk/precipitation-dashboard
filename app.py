#!/usr/bin/env python3

from dash import Dash, html, dcc, Output, Input
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from os import path

# copy of cleaned data originally sourced from https://opendata.citywindsor.ca/
data_source="https://raw.githubusercontent.com/dntiontk/windsor-opendata/main/precipitation/windsor-precipitation.csv"

def get_first_and_last_year(df):
    df["DateTime"] = pd.DatetimeIndex(df["DateTime"])
    return df["DateTime"].dt.year.min(), df["DateTime"].dt.year.max()


df = pd.read_csv(data_source)
options = df["Gauge"].unique()
first, last = get_first_and_last_year(df)
theme = "plotly_dark"

app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

server = app.server

app.layout = html.Div(
    [
        html.H4("Windsor precipitation ({}-{})".format(first, last)),
        html.Div(
            [
                html.P("Precipitation per gauge"),
                dcc.Graph(
                    id="total",
                    figure=px.line(
                        df,
                        x="DateTime",
                        y="Rainfall Total",
                        labels={"Rainfall Total": "mm/hr"},
                        color="Gauge",
                        template=theme,
                        title="Rainfall Total",
                    ),
                ),
                html.Hr(),
                dcc.Graph(
                    id="daily",
                    figure=px.line(
                        df,
                        x="DateTime",
                        y="Daily Accumulation",
                        labels={"Daily Accumulation": "mm/hr"},
                        color="Gauge",
                        template=theme,
                        title="Daily Accumulation",
                    ),
                ),
            ]
        ),
    ],
)


if __name__ == "__main__":
    app.run(debug=True)
