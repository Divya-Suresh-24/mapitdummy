import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches

# ---- PAGE SETTINGS ----
st.set_page_config(page_title="Competency Mapping", layout="wide")
st.title("📘 Competency Objective Mapping Tool")
st.markdown("Explore how each course aligns with 15 competency objectives using filters and a heatmap.")

# Objective Descriptions
objective_descriptions = {
    1: "Communicate effectively with clients and co-workers",
    2: "Handle patients safely and effectively",
    3: "Manage common medical cases ...",
    4: "Seek out and utilize new information ...",
    5: "Demonstrate mastery of principles ...",
    6: "Attend to animal welfare ...",
    7: "Diagnose common diseases ...",
    8: "Create appropriate treatment plans ...",
    9: "Function as ethical, respectful professionals",
    10: "Perform anesthesia and manage pain effectively",
    11: "Utilize health promotion strategies ...",
    12: "Manage emergency and intensive care cases",
    13: "Manage financial and other business functions ...",
    14: "Plan and perform common surgical procedures ...",
    15: "Manage records effectively ..."
}

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

        # Extract and reshape
        data = course_row[objective_cols].iloc[0].values.astype(float)
        matrix = np.reshape(data, (3, 5))
        objective_numbers = np.reshape(np.arange(1, 16), (3, 5))

        fig, ax = plt.subplots(figsize=(12, 6))
        cmap = sns.light_palette("seagreen", as_cmap=True)
        heatmap = ax.imshow(matrix, cmap=cmap)

        # Annotations
        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[1]):
                obj = objective_numbers[i, j]
                val = matrix[i, j]
                ax.text(j, i, f"{obj}", va='center', ha='center', fontsize=12, fontweight='bold', color='black')
                ax.text(j, i + 0.3, f"{val:.2f}", va='top', ha='center', fontsize=8, color='black')

        # Hide ticks and labels
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title("Course Competency Objective Mapping", fontsize=14)

        # Legend
        legend_patches = []
        for i in range(1, 16):
            color = cmap(data[i - 1] / 100)
            patch = mpatches.Patch(color=color, label=f"{i}. {objective_descriptions[i]}")
            legend_patches.append(patch)

        ax.legend(handles=legend_patches, bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0., fontsize=8)
        st.pyplot(fig)
