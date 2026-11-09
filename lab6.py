import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Gym Member Analytics",
    page_icon="G",
    layout="wide"
)

st.title("Gym Member Analytics Dashboard")
st.write("Explore and analyse gym member data.")

# Load CSV dataset
@st.cache_data
def load_data():
    df = pd.read_csv("gym_members.csv")
    df["Join_Date"] = pd.to_datetime(df["Join_Date"])
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("Filter Options")

membership_options = ["All"] + sorted(df["Membership"].dropna().unique().tolist())

membership = st.sidebar.selectbox(
    "Select Membership",
    membership_options
)

gender = st.sidebar.multiselect(
    "Select Gender",
    sorted(df["Gender"].dropna().unique().tolist()),
    default=sorted(df["Gender"].dropna().unique().tolist())
)

workout = st.sidebar.multiselect(
    "Select Workout Type",
    sorted(df["Workout_Type"].dropna().unique().tolist()),
    default=sorted(df["Workout_Type"].dropna().unique().tolist())
)

min_age = int(df["Age"].min())
max_age = int(df["Age"].max())

age_range = st.sidebar.slider(
    "Select Age Range",
    min_age,
    max_age,
    (min_age, max_age)
)

# Apply filters
filtered_df = df.copy()

if membership != "All":
    filtered_df = filtered_df[
        filtered_df["Membership"] == membership
    ]

filtered_df = filtered_df[
    (filtered_df["Gender"].isin(gender)) &
    (filtered_df["Workout_Type"].isin(workout)) &
    (filtered_df["Age"].between(age_range[0], age_range[1]))
]

# Check filtered data
if filtered_df.empty:
    st.warning("No records found. Please change the filters.")
    st.stop()

# KPI Metrics
st.header("Gym Statistics")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Members",
    len(filtered_df)
)

col2.metric(
    "Total Monthly Fees",
    f"₹{filtered_df['Monthly_Fee'].sum():,.0f}"
)

col3.metric(
    "Average Age",
    f"{filtered_df['Age'].mean():.1f}"
)

col4.metric(
    "Average Monthly Fee",
    f"₹{filtered_df['Monthly_Fee'].mean():,.0f}"
)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "Overview",
    "Analysis",
    "Visualizations",
    "Insights"
])

# TAB 1: Overview
with tab1:
    st.header("Gym Member Overview")

    st.dataframe(
        filtered_df,
        use_container_width=True
    )

    st.subheader("Membership Category Count")

    membership_count = filtered_df.groupby(
        "Membership"
    ).size().reset_index(name="Total Members")

    st.dataframe(
        membership_count,
        use_container_width=True
    )

# TAB 2: Analysis
with tab2:
    st.header("Data Analysis")

    st.subheader("Statistical Summary")

    st.dataframe(
        filtered_df[
            ["Age", "Monthly_Fee", "Attendance_Days", "Calories_Burned"]
        ].describe(),
        use_container_width=True
    )

    st.subheader("Workout Type Analysis")

    workout_count = filtered_df.groupby(
        "Workout_Type"
    ).size().reset_index(name="Total Members")

    st.dataframe(
        workout_count,
        use_container_width=True
    )

    st.subheader("Membership Fee Analysis")

    fee_analysis = filtered_df.groupby(
        "Membership"
    )["Monthly_Fee"].mean().reset_index()

    st.dataframe(
        fee_analysis,
        use_container_width=True
    )

# TAB 3: Visualizations
with tab3:
    st.header("Data Visualizations")

    # Bar Chart
    st.subheader("Membership-wise Member Count")

    membership_chart = filtered_df.groupby(
        "Membership"
    ).size().reset_index(name="Total Members")

    fig1 = px.bar(
        membership_chart,
        x="Membership",
        y="Total Members",
        color="Membership",
        title="Members in Each Membership Category",
        labels={
            "Membership": "Membership Type",
            "Total Members": "Number of Members"
        }
    )

    st.plotly_chart(fig1, use_container_width=True)

    # Line Chart
    st.subheader("Monthly Joining Trend")

    monthly_data = filtered_df.copy()
    monthly_data["Month"] = (
        monthly_data["Join_Date"].dt.to_period("M").astype(str)
    )

    monthly_count = monthly_data.groupby(
        "Month"
    ).size().reset_index(name="Total Members")

    monthly_count = monthly_count.sort_values("Month")

    fig2 = px.line(
        monthly_count,
        x="Month",
        y="Total Members",
        markers=True,
        title="Number of Members Joining Each Month",
        labels={
            "Month": "Joining Month",
            "Total Members": "Number of Members"
        }
    )

    st.plotly_chart(fig2, use_container_width=True)

    # Scatter Plot
    st.subheader("Age vs Monthly Fee")

    fig3 = px.scatter(
        filtered_df,
        x="Age",
        y="Monthly_Fee",
        color="Membership",
        size="Attendance_Days",
        hover_data=["Name", "Workout_Type"],
        title="Relationship Between Age and Monthly Fee",
        labels={
            "Age": "Member Age",
            "Monthly_Fee": "Monthly Fee (₹)"
        }
    )

    st.plotly_chart(fig3, use_container_width=True)

# TAB 4: Insights
with tab4:
    st.header("Gym Business Insights")

    popular_membership = (
        filtered_df["Membership"].mode().iloc[0]
    )

    popular_workout = (
        filtered_df["Workout_Type"].mode().iloc[0]
    )

    highest_attendance = filtered_df.loc[
        filtered_df["Attendance_Days"].idxmax()
    ]

    st.success(
        f"Most popular membership: {popular_membership}"
    )

    st.info(
        f"Most popular workout type: {popular_workout}"
    )

    st.write(
        "Member with highest attendance:",
        highest_attendance["Name"]
    )

    st.write(
        "Highest attendance days:",
        highest_attendance["Attendance_Days"]
    )

    st.write(
        "Average calories burned:",
        round(filtered_df["Calories_Burned"].mean(), 2)
    )

    st.subheader("Conclusion")

    st.write(
        "The dashboard helps analyse gym membership, "
        "monthly fees, attendance, workout preferences "
        "and member joining trends. The filters and charts "
        "support better gym management decisions."
    )