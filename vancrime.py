from dash import Dash, dcc, html, dash_table, Input, Output, callback
import pandas as pd
import numpy as np

import plotly.express as px

import dash_bootstrap_components as dbc
from dash_bootstrap_templates import ThemeChangerAIO, template_from_url

########################################################################################
# read the data 
df = pd.read_csv('data/raw/crimedata_csv_AllNeighbourhoods_AllYears.csv')
# wrangle the data
df = df.dropna()
# get the unique number of years
years = np.sort(df['YEAR'].unique())
# remove the the last year data as it is incomplete
df = df[df['YEAR'] != years[-1]]
df = df.sample(frac=0.1, random_state=0)
# unique neighbourhoods
unique_hoods = np.sort(df['NEIGHBOURHOOD'].unique())
unique_crimetype = np.sort(df['TYPE'].unique())
unique_years = np.sort(df['YEAR'].unique())

# ui controls ##########################################################################
crime_type_dropdown = html.Div(
    [
        dbc.Label("Select Crime Type"),
        dcc.Dropdown(
        options = unique_crimetype,
        value = unique_crimetype[1:3],
        id="crime",
        multi=True)
    ],
    className="mb-1",
)

neighbourhoods_dropdown = html.Div(
    [
        dbc.Label("Select Vancouver Neighbourhood"),
        dcc.Dropdown(
        options = unique_hoods,
        id="hood",
        value = unique_hoods[1:3],
        multi=True)
    ],
    className="mb-2",
)

year_slider = html.Div(
    [
        dbc.Label("Select Years"),
        dcc.RangeSlider(
            unique_years[0],
            unique_years[-1],
            1,
            id="years",
            marks=None,
            tooltip={"placement": "bottom", "always_visible": True},
            value=[years[5], years[-4]],
            className="p-0",
            allowCross=False
        ),
    ],
    className="mb-4",
)

# stylesheet with the .dbc class
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc_css])

header = html.H4(
    "VanCrime", className="bg-primary text-white p-2 mb-2 text-center"
)

#TYPE,YEAR,MONTH,DAY,HOUR,MINUTE,HUNDRED_BLOCK,NEIGHBOURHOOD,X,Y
table = html.Div(
    dash_table.DataTable(
        id="table",
        columns=[{"name": i, "id": i, 
                  "deletable": False} for i in ["YEAR",
                                                "MONTH",
                                                "TYPE",
                                                "HUNDRED_BLOCK",
                                                "NEIGHBOURHOOD"]],
        data=df.to_dict("records"),
        page_size=10,
        editable=False,
        cell_selectable=False,
        filter_action="native",
        sort_action="native",
        style_table={"overflowX": "auto"},
        row_selectable="multi",
    ),
    className="dbc-row-selectable",
)


dropdown = html.Div(
    [
        dbc.Label("Select indicator (y-axis)"),
        dcc.Dropdown(
            ["gdpPercap", "lifeExp", "pop"],
            "pop",
            id="indicator",
            clearable=False,
        ),
    ],
    className="mb-4",
)

theme_colors = [
    "primary",
    "secondary",
    "success",
    "warning",
    "danger",
    "info",
    "light",
    "dark",
    "link",
]
# colors = html.Div(
#     [dbc.Button(f"{color}", color=f"{color}", size="sm") for color in theme_colors]
# )
# colors = html.Div(["Theme Colors:", colors], className="mt-2")


controls = dbc.Card(
    [
        year_slider,
        neighbourhoods_dropdown,
        crime_type_dropdown, 
        # dropdown, checklist, slider
    ],
    body=True,
)

tab1 = dbc.Tab([dcc.Graph(id="line-chart")], label="Line Chart")
tab2 = dbc.Tab([dcc.Graph(id="scatter-chart")], label="Scatter Chart")
tab3 = dbc.Tab([table], label="Table", className="p-4")
tabs = dbc.Card(dbc.Tabs([tab1, tab2, tab3]))

app.layout = dbc.Container(
    [
        header,
        dbc.Row(
            [
                dbc.Col(
                    [
                        controls,
                        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                        # When running this app locally, un-comment this line:
                        ThemeChangerAIO(aio_id="theme")
                    ],
                    width=4,
                ),
                dbc.Col([tabs], width=8),
            ]
        ),
    ],
    fluid=True,
    className="dbc",
)


@callback(
    Output("line-chart", "figure"),
    Output("scatter-chart", "figure"),
    Output("table", "data"),
    # Input("indicator", "value"),
    # Input("continents", "value"),
    Input("years", "value"),
    Input("crime", "value"),
    Input("hood", "value"),
    Input(ThemeChangerAIO.ids.radio("theme"), "value"),
)
def update_line_chart(
    #indicator, continent, 
    yrs,
    crime,
    hood,
    theme):
    # if continent == [] or indicator is None:
    #     return {}, {}, []

    dff = df[df["YEAR"].between(yrs[0], yrs[1])]
    dff = dff[dff["TYPE"].isin(crime)]
    dff = dff[dff["NEIGHBOURHOOD"].isin(hood)]
    data = dff.to_dict("records")

    dff_area = dff; dff_area["COUNT"] = 1
    fig = px.area(
        dff_area, x="YEAR", 
        y="COUNT", color="NEIGHBOURHOOD", line_group="HUNDRED_BLOCK",template=template_from_url(theme))

    fig_scatter = px.bar(dff_area, x="COUNT", y="TYPE", color='TYPE', orientation='h',
             hover_data=["TYPE"],
             title='Crimes by Type')
    # return fig, fig_scatter, data
    return fig, fig_scatter,data


if __name__ == "__main__":
    app.run_server(debug=True)