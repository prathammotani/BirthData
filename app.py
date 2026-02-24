import streamlit as st
import pandas as pd
import plotly.express as px

# STEP 2 — Page Config
st.set_page_config(layout="wide")
st.title("Provisional Natality Data Dashboard")
st.subheader("Birth Analysis by State and Gender")

# STEP 3 — Load Data
try:
    df = pd.read_csv("Provisional_Natality_2025_CDC.csv")
except FileNotFoundError:
    st.error("Dataset file not found in repository.")
    st.stop()
except Exception as e:
    st.error(f"Error loading dataset: {e}")
    st.stop()

# Normalize column names
df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
)

# Logical field mapping
required_fields = {
    "state_of_residence": None,
    "month": None,
    "sex_of_infant": None,
    "births": None
}

for col in df.columns:
    if "state" in col and "residence" in col:
        required_fields["state_of_residence"] = col
    elif col == "month" or "month" in col:
        required_fields["month"] = col
    elif "sex" in col:
        required_fields["sex_of_infant"] = col
    elif "birth" in col:
        required_fields["births"] = col

missing_fields = [k for k, v in required_fields.items() if v is None]

if missing_fields:
    st.error(f"Missing required logical fields: {missing_fields}")
    st.write("Available columns:")
    st.write(df.columns)
    st.stop()

# Rename columns to standardized names
df = df.rename(columns={
    required_fields["state_of_residence"]: "state_of_residence",
    required_fields["month"]: "month",
    required_fields["sex_of_infant"]: "sex_of_infant",
    required_fields["births"]: "births"
})

# Convert births to numeric
df["births"] = pd.to_numeric(df["births"], errors="coerce")
df = df.dropna(subset=["births"])

# STEP 4 — Sidebar Filters
st.sidebar.header("Filters")

months = sorted(df["month"].dropna().unique())
states = sorted(df["state_of_residence"].dropna().unique())
genders = sorted(df["sex_of_infant"].dropna().unique())

month_options = ["All"] + list(months)
state_options = ["All"] + list(states)
gender_options = ["All"] + list(genders)

selected_months = st.sidebar.multiselect(
    "Select Month(s)",
    options=month_options,
    default=["All"]
)

selected_states = st.sidebar.multiselect(
    "Select State(s)",
    options=state_options,
    default=["All"]
)

selected_genders = st.sidebar.multiselect(
    "Select Gender(s)",
    options=gender_options,
    default=["All"]
)

# STEP 5 — Filtering Logic
filtered_df = df.copy()

if "All" not in selected_months:
    filtered_df = filtered_df[filtered_df["month"].isin(selected_months)]

if "All" not in selected_states:
    filtered_df = filtered_df[filtered_df["state_of_residence"].isin(selected_states)]

if "All" not in selected_genders:
    filtered_df = filtered_df[filtered_df["sex_of_infant"].isin(selected_genders)]

if filtered_df.empty:
    st.warning("No data available for selected filters.")
    st.stop()

# STEP 6 — Aggregation
aggregated_df = (
    filtered_df
    .groupby(["state_of_residence", "sex_of_infant"], as_index=False)["births"]
    .sum()
)

aggregated_df = aggregated_df.sort_values("state_of_residence")

# STEP 7 — Plot
fig = px.bar(
    aggregated_df,
    x="state_of_residence",
    y="births",
    color="sex_of_infant",
    title="Total Births by State and Gender"
)

fig.update_layout(
    plot_bgcolor="white",
    legend_title_text="Gender",
    xaxis_title="State of Residence",
    yaxis_title="Total Births",
    xaxis_tickangle=-45
)

st.plotly_chart(fig, use_container_width=True)

# STEP 8 — Show Filtered Table
st.dataframe(aggregated_df.reset_index(drop=True))
