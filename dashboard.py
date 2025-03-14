import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pyecharts.charts import Bar3D, Pie, Sunburst
from pyecharts import options as opts
from pyecharts.globals import ThemeType
from streamlit_echarts import st_pyecharts
import threading
import time

# CSV File Path
CSV_FILE_PATH = "/Users/sanjojoy/Documents/Study/S2/Modern Data Arch/GP/Group Project_resources/Completed/kafka_data.csv"

# State Abbreviation Mapping
state_abbrev = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
    'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA',
    'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
    'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
    'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS', 'Missouri': 'MO',
    'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ',
    'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH',
    'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
    'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT',
    'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY'
}

# Global variable to store the data
data_lock = threading.Lock()
global_df = pd.DataFrame()

    # Data Loading
def load_data():
    """
    Loads and cleans data from kafka_data.csv while ensuring proper data types.Also loads test_results.csv for model predictions.
    """
    global global_df, df_results  # ✅ Ensure df_results is global

    try:
        df = pd.read_csv(CSV_FILE_PATH)
    except FileNotFoundError:
        st.warning("⚠️ No existing data found. Creating a new DataFrame.")
        df = pd.DataFrame(columns=[
            "timestamp", "user_id", "age", "gender", "height", "interests",
            "looking_for", "children", "education_level", "occupation",
            "swiping_history", "frequency_of_usage", "state"
        ])

    # ✅ Load Test Results (Predictions)
    TEST_RESULTS_FILE_PATH = "/Users/sanjojoy/Documents/Study/S2/Modern Data Arch/GP/Group Project_resources/Completed/test_results.csv"

    # Initialize an empty DataFrame to prevent errors
    df_results = pd.DataFrame()

    try:
        df_results = pd.read_csv(TEST_RESULTS_FILE_PATH)
        st.success("✅ Predictions loaded successfully from test_results.csv")
    except FileNotFoundError:
        st.warning("⚠️ No predictions found. Run `test_xgboost_model.py` to generate `test_results.csv`.")

    # ✅ Ensure df_results is not empty before summing values
    if not df_results.empty:
        total_predicted_swipes = df_results["predicted_swipes"].sum()
        high_engagement_count = df_results["predicted_engagement"].sum()
    else:
        total_predicted_swipes = 0
        high_engagement_count = 0

    # Convert data types
    df["age"] = pd.to_numeric(df["age"], errors="coerce")
    df["swiping_history"] = pd.to_numeric(df["swiping_history"], errors="coerce")
    df["height"] = pd.to_numeric(df["height"], errors="coerce")
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    # Display Predicted Metrics
    if not df_results.empty:
        st.markdown("## 📊 Predicted User Engagement")
        
        total_predicted_swipes = df_results["predicted_swipes"].sum()
        high_engagement_count = df_results["predicted_engagement"].sum()
        
        col1, col2 = st.columns(2)
        col1.metric("Total Predicted Swipes", int(total_predicted_swipes))
        col2.metric("Users Predicted as Highly Engaged", int(high_engagement_count))

    # Fill missing values
    df.fillna(0, inplace=True)

    with data_lock:
        global_df = df

# Background thread to load data every 10 seconds
def data_loader():
    while True:
        load_data()
        time.sleep(10)

# Start the background thread
threading.Thread(target=data_loader, daemon=True).start()

# Wait for the data to be loaded
time.sleep(1)

# Sidebar filters
st.sidebar.header("Filters")
if not global_df.empty:
    gender_filter = st.sidebar.multiselect("Gender", options=global_df["gender"].unique(), default=global_df["gender"].unique())
    age_range = st.sidebar.slider("Age Range", int(global_df["age"].min()), int(global_df["age"].max()), (int(global_df["age"].min()), int(global_df["age"].max())))
    occupation_filter = st.sidebar.selectbox("Occupation", options=["All"] + global_df["occupation"].unique().tolist())
    state_filter = st.sidebar.selectbox("State", options=["All"] + global_df["state"].unique().tolist())
    education_filter = st.sidebar.multiselect("Education Level", options=global_df["education_level"].unique(), default=global_df["education_level"].unique())
    theme = st.sidebar.radio("Theme", ["Light", "Dark"], index=0)

    # Apply filters
    with data_lock:
        filtered_df = global_df[global_df["gender"].isin(gender_filter)]
        filtered_df = filtered_df[(filtered_df["age"] >= age_range[0]) & (filtered_df["age"] <= age_range[1])]
        if occupation_filter != "All":
            filtered_df = filtered_df[filtered_df["occupation"] == occupation_filter]
        if state_filter != "All":
            filtered_df = filtered_df[filtered_df["state"] == state_filter]
        filtered_df = filtered_df[filtered_df["education_level"].isin(education_filter)]

    # Convert state names to abbreviations
    filtered_df["state"] = filtered_df["state"].map(state_abbrev)

    # Debug: Display filtered data
    st.write("Filtered Data", filtered_df)

    # Basic metrics
    total_users = len(filtered_df)
    total_swipes = filtered_df["swiping_history"].sum()
    daily_users = len(filtered_df[filtered_df["frequency_of_usage"] == "Daily"])

    # Display metrics
    st.title(" Dating App Engagement Dashboard")
    st.markdown("### Key Metrics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Users", total_users)
    col2.metric("Total Swipes", total_swipes)
    col3.metric("Daily Users", daily_users)

    # Theme settings
    chart_theme = ThemeType.LIGHT if theme == "Light" else ThemeType.DARK
    plotly_template = "plotly_white" if theme == "Light" else "plotly_dark"

    # 3D Scatter Chart
    scatter_fig = go.Figure(
        data=[
            go.Scatter3d(
                x=filtered_df["age"],
                y=filtered_df["swiping_history"],
                z=filtered_df["height"],
                mode="markers",
                marker=dict(
                    size=8,
                    color=filtered_df["age"],
                    colorscale=[(0, "white"), (1, "red")],
                    cmin=filtered_df["age"].min(),
                    cmax=filtered_df["age"].max(),
                    opacity=0.9
                )
            )
        ]
    )
    scatter_fig.update_layout(
        title="🟢 3D User Engagement Scatter Plot (Plotly)",
        template=plotly_template,
        height=875,  # Increased height by 25%
        scene=dict(
            xaxis_title="Age",
            yaxis_title="Swipes",
            zaxis_title="Height",
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            zaxis=dict(title_font=dict(size=14), tickfont=dict(size=12))
        ),
        title_font=dict(size=20)
    )
    st.plotly_chart(scatter_fig)

    # Choropleth Map
    def generate_geo_chart(df):
        """
        Generates a heatmap showing user distribution across US states.
        """
        if df.empty or "state" not in df.columns:
            return go.Figure()

        state_counts = df["state"].value_counts().reset_index()
        state_counts.columns = ["state", "count"]

        fig = px.choropleth(
            state_counts,
            locations="state",
            locationmode="USA-states",
            color="count",
            scope="usa",
            title="🌎 User Distribution by State",
            color_continuous_scale="Viridis",
            template=plotly_template,
            height=875,  # Increased height by 25%
            labels={"count": "User Count"}
        )
        fig.update_layout(
            title_font=dict(size=20),
            geo=dict(bgcolor='rgba(0,0,0,0)'),
            coloraxis_colorbar=dict(title="User Count", title_font=dict(size=14), tickfont=dict(size=12))
        )
        return fig

    geo_chart_fig = generate_geo_chart(filtered_df)
    st.plotly_chart(geo_chart_fig)

    # Line Chart
    df_sorted = filtered_df.sort_values(by="timestamp")
    line_chart_fig = px.line(
        df_sorted,
        x="timestamp",
        y="swiping_history",
        title="📈 Swipes Over Time",
        template=plotly_template,
        height=875,  # Increased height by 25%
        labels={"timestamp": "Timestamp", "swiping_history": "Swipes"}
    )
    line_chart_fig.update_layout(
        title_font=dict(size=20),
        xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
        yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12))
    )
    st.plotly_chart(line_chart_fig)

    # Bar Chart - Count of Predicted Low vs. High Engagement Users
    engagement_counts = df_results["predicted_engagement"].value_counts().reset_index()
    engagement_counts.columns = ["Engagement Level", "Count"]
    engagement_counts["Engagement Level"] = engagement_counts["Engagement Level"].map({0: "Low", 1: "High"})

    bar_chart_fig = px.bar(
        engagement_counts,
        x="Engagement Level",
        y="Count",
        title="🔍 Predicted User Engagement Levels",
        labels={"Count": "User Count"},
        color="Engagement Level",
        template="plotly_white"
    )

    st.plotly_chart(bar_chart_fig)

    # Bar Chart for Total Swipes Over Time
    bar_chart_fig = px.bar(
        df_sorted,
        x="timestamp",
        y="swiping_history",
        title="📊 Total Swipes Over Time",
        template=plotly_template,
        height=875,  # Increased height by 25%
        labels={"timestamp": "Timestamp", "swiping_history": "Swipes"}
    )
    bar_chart_fig.update_layout(
        title_font=dict(size=20),
        xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
        yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12))
    )
    st.plotly_chart(bar_chart_fig)

    # Line Chart - Predicted vs. Actual Swipes Over Time
    if "timestamp" in df_results.columns:
        df_results["timestamp"] = pd.to_datetime(df_results["timestamp"])
        df_sorted = df_results.sort_values(by="timestamp")
        
        line_chart_fig = px.line(
            df_sorted,
            x="timestamp",
            y=["swiping_history", "predicted_swipes"],
            title="📈 Actual vs. Predicted Swipes Over Time",
            labels={"timestamp": "Time", "value": "Swipes"},
            template="plotly_white"
        )
        
        st.plotly_chart(line_chart_fig)

    # Bar Chart for Occupation
    def generate_pyecharts_occupation_bar(df):
        occupation_data = (
            df.groupby("occupation")["swiping_history"]
            .sum()
            .reset_index()
            .sort_values(by="swiping_history", ascending=False)
        )
        x_data = occupation_data["occupation"].astype(str).tolist()
        y_data = occupation_data["swiping_history"].tolist()

        bar_chart = Bar3D(init_opts=opts.InitOpts(theme=chart_theme, renderer="svg"))
        bar_chart.add(
            series_name="Total Swipes",
            data=[[i, 0, y_data[i]] for i in range(len(x_data))],
            xaxis3d_opts=opts.Axis3DOpts(type_="category", data=x_data),
            yaxis3d_opts=opts.Axis3DOpts(type_="category", data=["Swipes"]),
            zaxis3d_opts=opts.Axis3DOpts(type_="value"),
        )
        bar_chart.set_global_opts(
            title_opts=opts.TitleOpts(
                title="💼 3D Swipes by Occupation",
                subtitle="Bar Chart",
                title_textstyle_opts=opts.TextStyleOpts(font_size=18, color="#333"),
                subtitle_textstyle_opts=opts.TextStyleOpts(font_size=14, color="#666")
            ),
            toolbox_opts=opts.ToolboxOpts(),
            visualmap_opts=opts.VisualMapOpts(max_=max(y_data)),
        )
        return bar_chart

    bar_chart = generate_pyecharts_occupation_bar(filtered_df)
    st_pyecharts(bar_chart, key="bar_chart")

    # Pie Chart for Education Levels
    def generate_pyecharts_education_pie(df):
        edu_counts = df["education_level"].value_counts()
        data_pairs = [list(z) for z in zip(edu_counts.index.tolist(), edu_counts.values.tolist())]

        # Debug: Display education counts
        st.write("Education Counts", edu_counts)

        if not data_pairs:
            st.warning("No data available for the selected filters.")
            return None

        pie_chart = Pie(init_opts=opts.InitOpts(theme=chart_theme, renderer="svg"))
        pie_chart.add("Users", data_pairs)
        pie_chart.set_global_opts(
            title_opts=opts.TitleOpts(
                title="🥧 Education Pie",
                subtitle="Pie Chart",
                title_textstyle_opts=opts.TextStyleOpts(font_size=18, color="#333"),
                subtitle_textstyle_opts=opts.TextStyleOpts(font_size=14, color="#666")
            )
        )
        return pie_chart
    
    # Scatter Plot - Age vs. Predicted Swipes
    scatter_fig = px.scatter(
        df_results,
        x="age",
        y="predicted_swipes",
        color="predicted_engagement",
        title="🎯 Age vs. Predicted Swipes",
        labels={"age": "User Age", "predicted_swipes": "Predicted Swipes"},
        template="plotly_white"
    )

    st.plotly_chart(scatter_fig)

    pie_chart = generate_pyecharts_education_pie(filtered_df)
    if pie_chart:
        st_pyecharts(pie_chart, key="pie_chart")

    # Sunburst Chart for 'Looking For'
    def generate_pyecharts_sunburst(df):
        data = [{"name": k, "value": v} for k, v in df["looking_for"].value_counts().items()]

        # Debug: Display looking for counts
        st.write("Looking For Counts", df["looking_for"].value_counts())

        if not data:
            st.warning("No data available for the selected filters.")
            return None

        sunburst_chart = Sunburst(init_opts=opts.InitOpts(theme=chart_theme, renderer="svg"))
        sunburst_chart.add("Looking For", data)
        sunburst_chart.set_global_opts(
            title_opts=opts.TitleOpts(
                title="💑 Relationship Preferences",
                subtitle="Sunburst Chart",
                title_textstyle_opts=opts.TextStyleOpts(font_size=18, color="#333"),
                subtitle_textstyle_opts=opts.TextStyleOpts(font_size=14, color="#666")
            )
        )
        return sunburst_chart

    sunburst_chart = generate_pyecharts_sunburst(filtered_df)
    if sunburst_chart:
        st_pyecharts(sunburst_chart, key="sunburst_chart")

    # Download Data Button
    def convert_df(df):
        return df.to_csv(index=False).encode('utf-8')

    csv = convert_df(filtered_df)
    st.download_button(
        label="📥 Download Filtered Data",
        data=csv,
        file_name='filtered_data.csv',
        mime='text/csv',
    )

    # Download Predicted Data
    def convert_df(df):
        return df.to_csv(index=False).encode('utf-8')

    if not df_results.empty:
        csv = convert_df(df_results)
        st.download_button(
            label="📥 Download Prediction Data",
            data=csv,
            file_name="test_results.csv",
            mime="text/csv",
        )

    # Refresh Button
    if st.button("🔄 Refresh Data"):
        load_data()
        st.experimental_rerun()
else:
    st.warning("Data is not loaded yet. Please wait a moment.")