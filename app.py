import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# ---- PAGE SETTINGS ----
st.set_page_config(page_title="Competency Mapping", layout="wide")
st.title("📘 Competency Objective Mapping Tool")
st.markdown("Explore how each course aligns with 15 competency objectives using filters and a heatmap.")

# ---- LOAD CSV ----
@st.cache_data
def load_data():
    return pd.read_csv("courses.csv")

df = load_data()

# ---- FILTERS ----
st.sidebar.header("🔍 Filter Courses")
search = st.sidebar.text_input("Search by Course or Name")
year = st.sidebar.selectbox("Year", ["All"] + sorted(df["Year"].unique().tolist()))
semester = st.sidebar.selectbox("Semester", ["All"] + sorted(df["Semester"].unique().tolist()))
if st.sidebar.button("Clear Filters"):
    st.rerun()

# ---- FILTER LOGIC ----
filtered = df.copy()
if search:
    filtered = filtered[filtered["Course"].str.contains(search, case=False) |
                        filtered["Course Name"].str.contains(search, case=False)]

if year != "All":
    filtered = filtered[filtered["Year"] == year]

if semester != "All":
    filtered = filtered[filtered["Semester"] == semester]

# ---- DISPLAY TABLE ----
st.subheader("📋 Course Objective Percentages Table")

# Extract objective labels
objective_cols = [str(i) for i in range(1, 16)]
columns_order = ["Course", "Course Name", "Year", "Semester"] + objective_cols
display_df = filtered[columns_order]
st.dataframe(display_df, use_container_width=True)

# ---- COURSE HEATMAP SELECTION ----
st.subheader("📊 View Course Heatmap")

selected_course = st.selectbox("Select a course to view its competency heatmap:", options=filtered["Course"] + " - " + filtered["Course Name"])

if selected_course:
    course_code = selected_course.split(" - ")[0]
    course_row = df[df["Course"] == course_code]
    if not course_row.empty:
        course_name = course_row.iloc[0]["Course Name"]
        st.markdown(f"### 🔎 {course_code} — {course_name}")

        # Extract values and reshape
        data = course_row[objective_cols].iloc[0].values.astype(float)
        obj_labels = [f"Obj {i}" for i in range(1, 16)]

        # 3x5 matrix reshape
        matrix_data = np.reshape(data, (3, 5))
        label_matrix = np.reshape(obj_labels, (3, 5))

        fig, ax = plt.subplots(figsize=(8, 5))

        # Create diverging red-blue heatmap
        sns.heatmap(
            matrix_data,
            annot=True,
            fmt=".1f",
            cmap="RdBu_r",
            linewidths=0.5,
            linecolor='black',
            square=True,
            cbar_kws={'label': '% Objective Met'},
            xticklabels=[f"Obj {i}" for i in range(1, 6)],
            yticklabels=[f"Row {i}" for i in range(1, 4)]
        )

        ax.set_title("Course Competency Heatmap", fontsize=14)
        st.pyplot(fig)
