import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# PAGE CONFIG

st.set_page_config(
    page_title="UIDAI Biometric Insights Dashboard",
    layout="wide"
)

st.title("📊 UIDAI Biometric Insights Dashboard")
st.caption("Interactive analysis of state,age and time-based biometric trends")

# LOAD DATA

@st.cache_data
def load_data():


    files = [
        "biometric1.csv",
        "biometric2.csv",
        "biometric3.csv",
        "biometric4.csv"
    ]
    df_list = []
    for file in files:
        temp_df = pd.read_csv(file, encoding="latin1")
        #clean column names
        temp_df.columns = temp_df.columns.str.strip().str.lower()

        #Fix date
        temp_df["date"] = pd.to_datetime(temp_df["date"],dayfirst = True, format = "mixed", errors = "coerce" )
        df_list.append(temp_df)

        #combine all files after loop
        df = pd.concat(df_list,ignore_index = True)

    return df

df = load_data()

# SIDEBAR FILTERS

st.sidebar.header("State Comparison Filters")
states= sorted(df["state"].dropna().unique())
selected_states = st.sidebar.multiselect("Select States to compare", states , default = states[:2])
if not selected_states:
    st.warning("Please select at least one state")
    st.stop()
df_filtered = df[df["state"].isin(selected_states)]

states = sorted(df["state"].dropna().unique())

min_date = df_filtered["date"].min()
max_date = df_filtered["date"].max()

date_range = st.sidebar.date_input("Select Date range" , [min_date, max_date])
df_filtered = df_filtered[
    (df_filtered["date"] >= pd.to_datetime(date_range[0])) &
    (df_filtered["date"] <= pd.to_datetime(date_range[1]))]

# KPIs

total_5_17 = df_filtered["bio_age_5_17"].sum()
total_17_ = df_filtered["bio_age_17_"].sum()
total_attempts = total_5_17 + total_17_

col1, col2, col3 = st.columns(3)

col1.metric("Total Biometric Attempts", int(total_attempts))
col2.metric("Age 5_17 Attempts", int(total_5_17))
col3.metric("Age 17+ Attempts", int(total_17_))

st.divider()
st.divider()
df["total_attempts"] = df["bio_age_5_17"] + df["bio_age_17_"]
top3_states = (
    df.groupby("state")["total_attempts"]
    .sum()
    .sort_values(ascending=False)
    .head(3)
    .reset_index()
)

st.subheader("🏆 Top 3 States by Total Biometric Attempts")

c1, c2, c3 = st.columns(3)

c1.metric(
    f"🥇 {top3_states.iloc[0]['state']}",
    f"{int(top3_states.iloc[0]['total_attempts']):,}"
)

c2.metric(
    f"🥈 {top3_states.iloc[1]['state']}",
    f"{int(top3_states.iloc[1]['total_attempts']):,}"
)

c3.metric(
    f"🥉 {top3_states.iloc[2]['state']}",
    f"{int(top3_states.iloc[2]['total_attempts']):,}"
)

st.caption(
    "Top 3 states account for a disproportionately high share of biometric authentication activity."
)

df["month"] = df["date"].dt.to_period("M")

monthly_totals = (
    df.groupby("month")[["bio_age_5_17", "bio_age_17_"]]
    .sum()
)

monthly_totals["total"] = (
    monthly_totals["bio_age_5_17"] + monthly_totals["bio_age_17_"]
)

avg_monthly = monthly_totals["total"].mean()

st.metric(
    "📅 Average Monthly Biometrics",
    f"{int(avg_monthly):,}"
)

peak_months = (
    monthly_totals
    .sort_values("total", ascending=False)
    .head(3)
)

st.subheader("🔥 Peak Biometric Activity Months")
st.table(
    peak_months.reset_index()
    .rename(columns={"month": "Month", "total": "Total Biometrics"})
)
# STATE-WISE BIOMETRIC ATTEMPTS

st.subheader("State-wise Biometric Attempts")

state_group = (
    df.groupby("state")[["bio_age_5_17", "bio_age_17_"]]
    .sum()
    .sort_values(by="bio_age_17_", ascending=False)
)

fig1, ax1 = plt.subplots(figsize=(12, 8))
state_group.sort_values(
    by="bio_age_17_"
).plot(
    kind="barh",
    ax=ax1
)

ax1.set_xlabel("Number of Attempts")
ax1.set_ylabel("State")
ax1.set_title("State-wise Biometric Attempts")

st.pyplot(fig1)

age_cols = [c for c in df.columns if c.startswith("bio_age")]

state_summary = (
    df_filtered
    .groupby("state")[age_cols]
    .sum()
    .reset_index()
)
#State-Wise Biometric Enrollment

st.subheader("State-wise Biometric Enrollment")
st.dataframe(state_summary)
state_summary["total_biometrics"] = state_summary[age_cols].sum(axis=1)

st.subheader("Total Biometrics by State")
st.bar_chart(
    state_summary.set_index("state")["total_biometrics"]
)

if "district" in df.columns:

    top5_districts = (
        df.groupby("standard_district")[["bio_age_5_17", "bio_age_17_"]]
        .sum()
    )

    top5_districts["total"] = (
        top5_districts["bio_age_5_17"] + top5_districts["bio_age_17_"]
    )

    top5_districts = (
        top5_districts
        .sort_values("total", ascending=False)
        .head(5)
        .reset_index()
    )

    st.markdown("## 🗺️ Top 5 Districts by Biometric Activity")
    st.bar_chart(
        top5_districts.set_index("standard_district")["total"]
    )


# -----------------------
# AGE-WISE DISTRIBUTION (PIE)
# -----------------------
st.subheader("Age-wise Biometric Distribution")

fig2, ax2 = plt.subplots()
ax2.pie(
    [total_5_17, total_17_],
    labels=["Age 5_17", "Age 17+"],
    autopct="%1.1f%%",
    startangle=90
)
ax2.set_title("Biometric Attempts by Age Group")

st.pyplot(fig2)

# -----------------------
# BIOMETRIC ATTEMPTS OVER TIME
# -----------------------
st.subheader("Biometric Attempts Over Time")

time_series = (
    df.groupby("date")[["bio_age_5_17", "bio_age_17_"]]
    .sum()
)

fig3, ax3 = plt.subplots(figsize=(12, 8))
time_series.plot(ax=ax3)
ax3.set_ylabel("Attempts")
ax3.set_xlabel("Date")
ax3.set_title("Biometric Attempts Over Time")

st.pyplot(fig3)

#----------------------
#MONTHLY TRENDS
#----------------------

st.markdown("## 📈 Monthly Biometric Trend")
st.divider()

fig, ax = plt.subplots(figsize=(12, 6))
monthly_totals["total"].plot(ax=ax)

ax.set_xlabel("Month")
ax.set_ylabel("Total Biometrics")
ax.set_title("Monthly Biometric Attempts Trend")

st.pyplot(fig)

# -----------------------
# INSIGHTS SECTION
# -----------------------
st.subheader("## 🧠 Key Insights")
st.metric("Total Records", len(df))

age_cols = [c for c in df.columns if c.startswith("bio_age")]

st.write("### Age-wise Biometric Distribution")
st.bar_chart(df[age_cols].sum())


st.line_chart(
    df.groupby("date")[age_cols].sum()
)


top_state = state_summary.sort_values(
    "total_biometrics", ascending=False
).iloc[0]["state"]
st.info(
    f"📌 Insight: {top3_states.iloc[0]['state']}, "
    f"{top3_states.iloc[1]['state']}, and "
    f"{top3_states.iloc[2]['state']} dominate biometric attempts nationally."
)

st.success(
    f"Insight: {top_state} leads in biometric enrollment among the selected states."
)

st.caption("This comparison higlights inter-state difference in iometric enrollment patterns.")