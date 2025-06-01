import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# ---- Load Data ----
@st.cache_data
def load_data():
    df = pd.read_csv("c/Users/divyas/Documents/MapIT/website/courses.csv")
    return df

df = load_data()

# ---- Sidebar Filters ----
st.set_page_config(page_title="Course Competency Map", layout="wide")
st.title("📘 Course Competency Mapping Tool")

st.markdown("Use the filters below to explore which courses meet which competency objectives.")

search_query = st.text_input("🔍 Search Course")
year_filter = st.selectbox("📅 Select Year", options=["All"] + sorted(df["Year"].unique().tolist()))
semester_filter = st.selectbox("📚 Select Semester", options=["All"] + sorted(df["Semester"].unique().tolist()))
if st.button("Clear Filters"):
    st.experimental_rerun()

# ---- Filter Logic ----
filtered_df = df.copy()
if search_query:
    filtered_df = filtered_df[filtered_df["Course"].str.contains(search_query, case=False)]

if year_filter != "All":
    filtered_df = filtered_df[filtered_df["Year"] == year_filter]

if semester_filter != "All":
    filtered_df = filtered_df[filtered_df["Semester"] == semester_filter]

# ---- Main Table ----
st.subheader("📋 Courses Table")
st.write("Click a course name below to see its heatmap of competency objectives.")

for _, row in filtered_df.iterrows():
    course_link = f"[{row['Course']}](?course={row['Course']})"
    st.markdown(f"**{course_link}** — Year: {row['Year']}, Semester: {row['Semester']}")

# ---- Detail Page via URL Parameter ----
query_params = st.experimental_get_query_params()
if "course" in query_params:
    course_name = query_params["course"][0]
    st.header(f"🔎 Competency Heatmap for {course_name}")
    course_row = df[df["Course"] == course_name]
    if course_row.empty:
        st.error("Course not found.")
    else:
        data = course_row.iloc[0, 3:]  # only the objective columns
        fig, ax = plt.subplots(figsize=(10, 1))
        sns.heatmap([data], cmap="YlGnBu", cbar=True, annot=True, fmt=".2f", xticklabels=data.index, yticklabels=["% Met"])
        plt.xticks(rotation=45, ha='right')
        st.pyplot(fig)
