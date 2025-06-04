import streamlit as st
st.set_page_config(page_title="Competency Mapping", layout="wide")  # Must be first Streamlit command

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import numpy as np
import io

# Constants
objective_cols = [str(i) for i in range(1, 16)]
objective_descriptions = {
    1: "Communicate effectively with clients and co-workers",
    2: "Handle patients safely and effectively",
    3: "Manage common medical cases, clinical procedures, referrals",
    4: "Seek and apply research to practice",
    5: "Master disease mechanisms and history",
    6: "Ensure animal welfare in all practice areas",
    7: "Diagnose diseases in animals using appropriate tools",
    8: "Create appropriate treatment plans",
    9: "Function as ethical, respectful professionals",
    10: "Perform anesthesia and manage pain effectively",
    11: "Use health promotion and food safety strategies",
    12: "Manage emergency and intensive care cases",
    13: "Handle financial/business functions for success",
    14: "Plan and perform surgical procedures",
    15: "Manage records with legal/professional standards"
}

# Load Data
@st.cache_data
def load_data():
    df = pd.read_csv("courses.csv")
    df.columns = df.columns.str.strip()  # Clean column names
    df["VM Term"] = df["VM Term"].astype(str).str.strip()
    df["Course Type"] = df["Course Type"].astype(str).str.strip()
    return df

df = load_data()

# Title
st.title("📘 Competency Objective Mapping Tool")
st.markdown("Explore how each course aligns with 15 competency objectives using filters and heatmaps.")

# Theme Toggle
theme = st.radio("Choose Theme", ["Light", "Dark"], horizontal=True)
cmap = sns.light_palette("seagreen", as_cmap=True) if theme == "Light" else sns.dark_palette("purple", reverse=True, as_cmap=True)

# Filters
vm_terms = sorted(df["VM Term"].dropna().unique())
course_types = sorted(df["Course Type"].dropna().unique())

selected_term = st.selectbox("Filter by VM Term", options=["All"] + vm_terms)
selected_type = st.selectbox("Filter by Course Type", options=["All"] + course_types)

filtered_df = df.copy()
if selected_term != "All":
    filtered_df = filtered_df[filtered_df["VM Term"] == selected_term]
if selected_type != "All":
    filtered_df = filtered_df[filtered_df["Course Type"] == selected_type]

# Display Filtered Table
st.markdown("## 📋 Filtered Course List")
display_df = filtered_df.copy()
display_df["Course Info"] = display_df["Course"] + " - " + display_df["Course Name"]
display_df = display_df[["Course Info", "VM Term", "Course Type"] + objective_cols]
display_df.columns = ["Course", "VM Term", "Course Type"] + [f"Obj {i}" for i in range(1, 16)]
st.dataframe(display_df, use_container_width=True)

# Course Selector
course_options = [f"{row['Course']} - {row['Course Name']}" for _, row in filtered_df.iterrows()]
selected_courses = st.multiselect("Select Course(s)", options=course_options, default=course_options[:1])

# Render Heatmaps
for course in selected_courses:
    course_code = course.split(" - ")[0]
    row = df[df["Course"] == course_code]
    if row.empty:
        continue

    st.markdown(f"### 🔍 {course}")
    data = row[objective_cols].iloc[0].values.astype(float)
    matrix = np.reshape(data, (3, 5))
    obj_numbers = np.reshape(np.arange(1, 16), (3, 5))

    fig, ax = plt.subplots(figsize=(7, 5))
    im = ax.imshow(matrix, cmap=cmap, vmin=0, vmax=100)

    # Annotate cells
    for i in range(3):
        for j in range(5):
            obj = obj_numbers[i, j]
            val = matrix[i, j]
            ax.text(j, i, f"{obj}", va='center', ha='center', fontsize=11, fontweight='bold')
            ax.text(j, i + 0.25, f"{val:.1f}", va='top', ha='center', fontsize=8)

    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("Course Competency Objective Mapping", fontsize=13)

    # Legend
    legend_patches = [
        mpatches.Patch(color=cmap(data[i] / 100), label=f"{i+1}. {objective_descriptions[i+1]}")
        for i in range(15)
    ]
    ax.legend(handles=legend_patches, bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0., fontsize=7)

    st.pyplot(fig)

    # Download
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    st.download_button(
        label="📥 Download PNG",
        data=buf.getvalue(),
        file_name=f"{course_code}_heatmap.png",
        mime="image/png"
    )
    plt.close(fig)
