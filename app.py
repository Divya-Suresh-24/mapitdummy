import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# ----- PAGE CONFIG -----
st.set_page_config(page_title="Competency Mapping", layout="wide")

# ----- DATA LOADING -----
@st.cache_data
def load_data():
    df = pd.read_csv("courses.csv")
    return df

df = load_data()

# ----- UI HEADER -----
st.title("📘 Competency Objective Mapping Tool")
st.markdown("Explore how each course aligns with 15 competency objectives using filters and heatmaps.")

# ----- FILTERS -----
st.sidebar.header("🔍 Filter Courses")
search_query = st.sidebar.text_input("Search by Course or Name")
year_options = sorted(df["Year"].unique().tolist())
semester_options = sorted(df["Semester"].unique().tolist())

year = st.sidebar.selectbox("Year", options=["All"] + year_options)
semester = st.sidebar.selectbox("Semester", options=["All"] + semester_options)

# Clear button
if st.sidebar.button("Clear Filters"):
    st.experimental_rerun()

# ----- FILTER LOGIC -----
filtered_df = df.copy()

if search_query:
    filtered_df = filtered_df[
        filtered_df["Course"].str.contains(search_query, case=False) |
        filtered_df["Course Name"].str.contains(search_query, case=False)
    ]

if year != "All":
    filtered_df = filtered_df[filtered_df["Year"] == year]

if semester != "All":
    filtered_df = filtered_df[filtered_df["Semester"] == semester]

# ----- DISPLAY TABLE -----
st.subheader("📋 Filtered Course List")

for _, row in filtered_df.iterrows():
    course_id = row['Course']
    course_name = row['Course Name']
    year = row['Year']
    sem = row['Semester']
    link = f"[{course_id} - {course_name}](?course={course_id})"
    st.markdown(f"**{link}** — Year {year}, Semester {sem}")

# ----- HEATMAP SECTION -----
query_params = st.experimental_get_query_params()
if "course" in query_params:
    course_id = query_params["course"][0]
    course_row = df[df["Course"] == course_id]

    if course_row.empty:
        st.error("Course not found.")
    else:
        course_name = course_row.iloc[0]["Course Name"]
        st.header(f"📊 Competency Heatmap — {course_id}: {course_name}")

        # Extract objective columns (columns 5 onward)
        objective_data = course_row.iloc[0, 4:]
        obj_labels = [f"Objective {i}" for i in range(1, 16)]

        # Plot heatmap
        fig, ax = plt.subplots(figsize=(12, 1.5))
        sns.heatmap(
            [objective_data.values],
            annot=True,
            cmap="YlGnBu",
            xticklabels=obj_labels,
            yticklabels=["% Met"],
            cbar=True,
            fmt=".1f"
        )
        plt.xticks(rotation=45, ha='right')
        st.pyplot(fig)
