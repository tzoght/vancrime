from dash import Dash, html, Input, Output, dcc
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import altair as alt
import geopandas as gpd
from dash import Dash, dcc, html, Input, Output


alt.data_transformers.disable_max_rows()


def get_time(military_hour):
    if military_hour >= 20 or military_hour < 6:
        return "night"
    else:
        return "day"


# read the data
geo_json_url = "https://raw.githubusercontent.com/tzoght/vancrime/main/data/geo/van_nb.geojson"
processed_data = pd.read_csv("https://raw.githubusercontent.com/tzoght/vancrime/main/data/raw/crimedata_csv_AllNeighbourhoods_AllYears.csv")
processed_data.reset_index(drop=True, inplace=True)
processed_data["TIME"] = processed_data["HOUR"].apply(lambda x: get_time(x))
# wrangle the data
processed_data = processed_data.dropna()
# get the unique number of years
years = np.sort(processed_data["YEAR"].unique())
# remove the the last year data as it is incomplete
processed_data = processed_data[processed_data["YEAR"] != years[-1]]
processed_data = processed_data.sample(frac=0.25, random_state=0)

# selection elements
unique_hoods = np.sort(processed_data["NEIGHBOURHOOD"].unique())
unique_crimetype = np.sort(processed_data["TYPE"].unique())
unique_years = np.sort(processed_data["YEAR"].unique())

# theme
theme = dbc.themes.BOOTSTRAP;

# App server
app = Dash(
    __name__,
    title="Vancouver Crime Dashboard",
    external_stylesheets=[theme],
)
server = app.server

"""Options"""
# Options for neighbourhood
opt_dropdown_neighbourhood = [
    {"label": neighbourhood, "value": neighbourhood} for neighbourhood in unique_hoods
]

# Options for time
opt_dropdown_time = [
    {"label": "Day", "value": "Day"},
    {"label": "Night", "value": "Night"},
    {"label": "Day and Night", "value": "Day and Night"},
]

"""Cards"""
# The number of crimes card
card1 = dbc.Card(
    [
        # Summary statistics
        html.H4(
            "Total Number of Crimes", className="card-title", style={"marginLeft": 20}
        ),
        html.Div(
            id="summary", style={"color": "teal", "fontSize": 26, "marginLeft": 120}
        ),
    ],
    style={"width": "20rem", "marginLeft": 20},
    body=True,
    color="light",
    className="mb-2",
)

# Filters and control cards
card2 = dbc.Card(
    [
        html.H6("Years", className="text-dark"),
        html.Div(
            [
                dcc.RangeSlider(
                    unique_years[0],
                    unique_years[-1],
                    1,
                    id="years_slider",
                    marks=None,
                    tooltip={"placement": "bottom", "always_visible": True},
                    value=[years[5], years[-4]],
                    className="p-0",
                    allowCross=False,
                ),
            ],
        ),
        html.Br(),
        # Dropdown for neighbourhood
        html.H6("Neighbourhood", className="text-dark"),
        dcc.Dropdown(
            id="neighbourhood_input",
            value=["Kitsilano"],
            options=opt_dropdown_neighbourhood,
            className="dropdown",
            multi=True,
        ),
        html.Br(),
        html.H6("Time Of Day", className="text-dark"),
        dcc.Dropdown(
            id="time_input",
            value="Day and Night",
            options=opt_dropdown_time,
            className="dropdown",
        ),
    ],
    style={"width": "20rem", "marginLeft": 20},
    body=True,
    color="light",
    className="mb-2",
)

# information
card3 = dbc.Card(
    [
        html.H5("Information", className="text-dark"),
        html.P(
            [
                "This dashboard is based on the crime data released by the ",
                dcc.Link(
                    "Vancouver Police Department",
                    href="https://geodash.vpd.ca/opendata/",
                    target="_blank",
                ),
                ".",
            ]
        ),
        html.P(
            [
                """
                To get started, please select the timeframe (from and to year from the slider), the neighbourhood(s) and the time of the day (day, night or both) 
                from the filter panel above. The bar chart shows the number of crimes for the selected neighbourhood(s) and year(s). 
                The line graph shows the number of crimes for the selected neighbourhood(s) and time of the day. 
                The map shows the number of crimes for the selected year(s) time of day and neighbourhood(s). 
                The summary card shows the total number of crimes for the selected year(s), time of day and neighbourhood(s).,
                """,
            ]
        ),
    ],
    style={"width": "20rem", "marginLeft": 20},
    body=True,
    color="light",
    className="mb-2",
)

"""Layouts"""
# Filter layout
filter_panel = [
    dbc.Row(
        [
            html.H3("Vancouver Crime Dashboard", style={"marginLeft": 20}),
        ]
    ),
    html.Br(),
    card1,
    html.Br(),
    html.H4("Filters", style={"marginLeft": 20}),
    card2,
    html.Br(),
    card3,
]

# Plots layout
plot_body = [
    dbc.Row(
        [
            dbc.Col(
                [
                    html.Iframe(
                        id="bar_plot",
                        className="bar_plot",
                        style={
                            "border-width": "0",
                            "width": "100%",
                            "height": "300px",
                        },
                    )
                ],
            ),
        ]
    ),
    html.Br(),
    dbc.Row(
        [
            dbc.Col(
                [
                    html.Iframe(
                        id="map_plot",
                        className="map_plot",
                        style={
                            "border-width": "0",
                            "width": "100%",
                            "height": "300px",
                        },
                    )
                ],
            ),
        ]
    ),
    html.Br(),
    dbc.Row(
        [
            dbc.Col(
                [
                    html.Iframe(
                        id="line_plot",
                        className="line_plot",
                        style={
                            "border-width": "0",
                            "width": "100%",
                            "height": "400px",
                        },
                    )
                ]
            )
        ]
    ),
]

# Page layout
page_layout = html.Div(
    className="page_layout",
    children=[
        dbc.Row([html.Br()]),
        dbc.Row(
            [
                dbc.Col(filter_panel, className="panel", width=3),
                dbc.Col(plot_body, className="body"),
            ]
        ),
    ],
)

# Overall layout
app.layout = html.Div(id="main", className="app", children=page_layout)

################################ Filtger ##################################
def getSelectedData( year, time, neighbourhood, df = processed_data):
    result = df
    if (year is not None):
      result = result[result["YEAR"].between(year[0], year[1])]  
    if (time is not None): 
        if time == "Day":
            result = result[result["TIME"] == "day"]
        elif time == "Night":
            result = result[result["TIME"] == "night"]
    if (neighbourhood is not None):
        result = result[result["NEIGHBOURHOOD"].isin(neighbourhood)]
    return result


################################ Map plot ################################
@app.callback(
    Output("map_plot", "srcDoc"),
    Input("years_slider", "value"),
    Input("time_input", "value"),
)
def plot_map_all(year, time):
    geoj = alt.Data(url=geo_json_url, format=alt.DataFormat(property="features", type="json"))
    df = getSelectedData(year, time, None)  
    df = df[df["HUNDRED_BLOCK"] != "OFFSET TO PROTECT PRIVACY"]
    df = df.groupby("NEIGHBOURHOOD").size().reset_index(name="Crimes")
    base = (
        alt.Chart(geoj).mark_geoshape(fill=None).project(type="identity", reflectY=True)
    )
    pts = (
        base
        + alt.Chart(df, title="Number of Crimes per Neighbourhood")
        .transform_lookup(
            default="0",
            as_="geo",
            lookup="NEIGHBOURHOOD",
            from_=alt.LookupData(data=geoj, key="properties.name"),
        )
        .mark_geoshape()
        .encode(
            alt.Color(
                "Crimes",
                scale=alt.Scale(scheme="greenblue"),
                legend=alt.Legend(orient="right", title="Crimes"),
            ),
            alt.Shape(field="geo", type="geojson"),
            tooltip=["Crimes", "NEIGHBOURHOOD:N"],
        )
    ).project(type="identity", reflectY=True)
    map = (
        (base + pts)
        .configure_title(fontSize=20)
        .configure_legend(
            titleFontSize=16,
            labelFontSize=14,
        )
        .properties(width=870, height=200)
    )
    return map.to_html()


@app.callback(
    Output("line_plot", "srcDoc"),
    Input("time_input", "value"),
    Input("neighbourhood_input", "value"),
)
def lineplot(time, neighbourhood):
    data = getSelectedData(None, time, neighbourhood)
    line_plot = (
        alt.Chart(
            data,
            title=f"Crimes {unique_years[0]} - {unique_years[-1]} in Vancouver Neighbourhoods",
        )
        .mark_line()
        .encode(
            x=alt.X("YEAR:O", title="Year"),
            y=alt.Y("count(HOUR)", title="Number of Crimes"),
            color=alt.Color("TIME", scale=alt.Scale(scheme="greenblue"), title="Time"),
        )
        .configure_axis(labelFontSize=14, titleFontSize=16)
        .configure_legend(
            titleFontSize=16,
            labelFontSize=14,
        )
        .configure_title(fontSize=20)
        .properties(width=870, height=270)
    )

    return line_plot.to_html()


@app.callback(
    Output("bar_plot", "srcDoc"),
    Input("neighbourhood_input", "value"),
    Input("years_slider", "value"),
    Input("time_input", "value"),
    # Input("year_radio", "value"),
)
def barchart(neighbourhood, year,time):
    data = getSelectedData(year, time, neighbourhood)
    data = pd.DataFrame(
        data=data[["TYPE"]].value_counts(), columns=["Counts"]
    ).reset_index(level=["TYPE"])

    barchart = (
        alt.Chart(data, title="Top 5 Crime Types")
        .transform_window(
            rank="rank(Counts)", sort=[alt.SortField("Counts", order="descending")]
        )
        .transform_filter((alt.datum.rank <= 5))
        .mark_bar()
        .encode(
            y=alt.Y(
                "TYPE", sort="-x", axis=alt.Axis(labels=False), title="Type of Crime"
            ),
            x=alt.Y("Counts", title="Number of Crimes"),
            # color=alt.Color(
            #     "TYPE", scale=alt.Scale(scheme="lightgreyteal"), title="Type",
            #     legend=alt.Legend(orient="bottom", columns=3)
            # ),
            tooltip=alt.Tooltip(["TYPE", "Counts"]),
        )
    )
    text = barchart.mark_text(
        align="left",
        baseline="middle",
        size=14,
        dx=3,  # shift text slightly to the right
    ).encode(
        text=alt.Text("TYPE")  # display counts values with no decimal places
    )
    resulting_chart = (
        (barchart + text)
        .configure_axis(labelFontSize=14, titleFontSize=16)
        .configure_legend(
            titleFontSize=14,
            labelFontSize=12,
        )
        .configure_title(fontSize=20)
        .properties(width=870, height=200)
    )

    return resulting_chart.to_html()


@app.callback(
    Output("summary", "children"),
    Input("neighbourhood_input", "value"),
    Input("years_slider", "value"),
    Input("time_input", "value"),
)
def summary(neighbourhood, year, time):
    data = processed_data.copy()
    data = data[data["YEAR"].between(year[0], year[1])]
    data = data[data.NEIGHBOURHOOD.isin(neighbourhood)]
    if time == "Day":
        data = data[data["TIME"] == "day"]

    elif time == "Night":
        data = data[data["TIME"] == "night"]    
    return len(data)


if __name__ == "__main__":
    app.run_server(debug=True)
