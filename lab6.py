
import streamlit as st
import pandas as pd
import plotly.express as px

# Page Configuration
st.set_page_config(
    page_title="Gym Member Analytics",
    layout="wide"
)

st.title("Gym Member Analytics Dashboard")
st.write("Explore and analyse gym member data.")

# Load CSV Dataset
@st.cache_data
def load_data():
    df = pd.read_csv(r"E:\PY LAB 6\gym_members.csv")
    df["Join_Date"] = pd.to_datetime(df["Join_Date"])
    return df

df = load_data()

# Sidebar Filters
st.sidebar.header("Filter Options")

membership = st.sidebar.selectbox(
    "Select Membership",
    ["All"] + sorted(df["Membership"].unique().tolist())
)

gender = st.sidebar.multiselect(
    "Select Gender",
    df["Gender"].unique(),
    default=df["Gender"].unique().tolist()
)

workout = st.sidebar.multiselect(
    "Select Workout Type",
    df["Workout_Type"].unique(),
    default=df["Workout_Type"].unique().tolist()
)

age = st.sidebar.slider(
    "Select Age Range",
    int(df["Age"].min()),
    int(df["Age"].max()),
    (int(df["Age"].min()), int(df["Age"].max()))
)

# Apply Filters
filtered_df = df[
    (df["Gender"].isin(gender)) &
    (df["Workout_Type"].isin(workout)) &
    (df["Age"].between(age[0], age[1]))
]

if membership != "All":
    filtered_df = filtered_df[
        filtered_df["Membership"] == membership
    ]

# Dashboard Metrics
st.header("Dashboard Overview")

col1, col2, col3, col4 = st.columns(4)

total_members = len(filtered_df)
total_fees = filtered_df["Monthly_Fee"].sum()

average_age = (
    round(filtered_df["Age"].mean(), 2)
    if not filtered_df.empty else 0
)

average_fee = (
    round(filtered_df["Monthly_Fee"].mean(), 2)
    if not filtered_df.empty else 0
)

col1.metric("Total Members", total_members)
col2.metric("Total Monthly Fees", f"₹{total_fees:,.0f}")
col3.metric("Average Age", average_age)
col4.metric("Average Monthly Fee", f"₹{average_fee:,.2f}")

# Category-wise Counts
st.subheader("Membership Category Counts")

if not filtered_df.empty:
    category_data = filtered_df.groupby("Membership").size()
    st.bar_chart(category_data)
else:
    st.info("No records found.")

# Create Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "Overview",
    "Analysis",
    "Visualizations",
    "Insights"
])

# TAB 1 - Overview
with tab1:

    st.header("Dataset Overview")

    st.dataframe(filtered_df, use_container_width=True)

    with st.expander("Dataset Information"):
        st.write("Total Records:", len(filtered_df))
        st.write("Total Columns:", len(filtered_df.columns))
        st.write("Column Names:", list(filtered_df.columns))
        st.write("Missing Values:")
        st.write(filtered_df.isnull().sum())

# TAB 2 - Analysis
with tab2:

    st.header("Data Analysis")

    if not filtered_df.empty:

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Members by Gender")
            gender_data = filtered_df.groupby("Gender").size()
            st.bar_chart(gender_data)

        with col2:
            st.subheader("Members by Workout Type")
            workout_data = filtered_df.groupby("Workout_Type").size()
            st.bar_chart(workout_data)

        st.subheader("Membership Analysis")

        analysis = filtered_df.groupby("Membership").agg(
            Total_Members=("Member_ID", "count"),
            Average_Fee=("Monthly_Fee", "mean"),
            Average_Attendance=("Attendance_Days", "mean")
        ).reset_index()

        st.dataframe(analysis, use_container_width=True)

        st.subheader("Numerical Data Summary")

        st.write(filtered_df[
            ["Age", "Monthly_Fee", "Attendance_Days", "Calories_Burned"]
        ].describe())

    else:
        st.info("No data available for analysis.")

# TAB 3 - Visualizations
with tab3:

    st.header("Data Visualizations")

    if not filtered_df.empty:

        # Bar Chart
        st.subheader("1. Bar Chart - Members by Membership")

        bar_data = filtered_df.groupby("Membership").size().reset_index(
            name="Total Members"
        )

        fig1 = px.bar(
            bar_data,
            x="Membership",
            y="Total Members",
            color="Membership",
            title="Number of Members in Each Membership"
        )

        st.plotly_chart(fig1, use_container_width=True)

        st.write(
            "Interpretation: This graph compares the number of members "
            "in different membership categories."
        )

        # Line Chart
        st.subheader("2. Line Chart - Monthly Joining Trend")

        line_data = filtered_df.copy()

        line_data["Join_Month"] = (
            line_data["Join_Date"].dt.to_period("M").astype(str)
        )

        line_data = line_data.groupby("Join_Month").size().reset_index(
            name="Total Members"
        )

        fig2 = px.line(
            line_data,
            x="Join_Month",
            y="Total Members",
            markers=True,
            title="Monthly Gym Member Joining Trend"
        )

        st.plotly_chart(fig2, use_container_width=True)

        st.write(
            "Interpretation: This graph shows the number of members "
            "joining the gym in each month."
        )

        # Scatter Plot
        st.subheader("3. Scatter Plot - Age vs Monthly Fee")

        fig3 = px.scatter(
            filtered_df,
            x="Age",
            y="Monthly_Fee",
            color="Membership",
            size="Attendance_Days",
            hover_name="Name",
            title="Relationship Between Age and Monthly Fee"
        )

        st.plotly_chart(fig3, use_container_width=True)

        st.write(
            "Interpretation: This graph compares member age and "
            "monthly fees. The point size represents attendance days."
        )

    else:
        st.info("No data available for visualizations.")

# TAB 4 - Insights
with tab4:

    st.header("Important Insights")

    if not filtered_df.empty:

        popular_membership = filtered_df["Membership"].mode()[0]
        popular_workout = filtered_df["Workout_Type"].mode()[0]

        highest_attendance = filtered_df.loc[
            filtered_df["Attendance_Days"].idxmax()
        ]

        st.write("Most Popular Membership:", popular_membership)
        st.write("Most Popular Workout:", popular_workout)
        st.write("Average Member Age:", average_age)
        st.write("Total Monthly Fees: ₹", total_fees)

        st.write(
            "Member with Highest Attendance:",
            highest_attendance["Name"]
        )

        st.write(
            "Highest Attendance Days:",
            highest_attendance["Attendance_Days"]
        )

    else:
        st.info("No insights available.")

# Footer
st.sidebar.write("--------------------")
st.sidebar.caption("Gym Member Analytics Project")

st.write("--------------------")
st.caption("Developed using Python, Pandas, Plotly and Streamlit.")
