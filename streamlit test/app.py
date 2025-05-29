import streamlit as st
import pandas as pd

# --- Helper Functions ---

def get_grade_point(grade):
    """Converts a letter grade to its corresponding GPA point value."""
    grade_map = {
        "A+": 4.0, "A": 4.0, "A-": 3.7,
        "B+": 3.3, "B": 3.0, "B-": 2.7,
        "C+": 2.3, "C": 2.0, "C-": 1.7,
        "D+": 1.3, "D": 1.0, "D-": 0.7,
        "F": 0.0,
        "Pass": None, # Pass/Fail courses don't affect GPA
        "Fail": 0.0   # Failing a Pass/Fail course might affect GPA depending on institution
    }
    return grade_map.get(grade, 0.0) # Default to 0.0 for unknown grades or F

def calculate_gpa(credits_list, grade_points_list):
    """Calculates GPA from lists of credits and corresponding grade points."""
    total_grade_points = sum(c * gp for c, gp in zip(credits_list, grade_points_list) if gp is not None)
    total_credits = sum(c for c, gp in zip(credits_list, grade_points_list) if gp is not None)

    if total_credits == 0:
        return 0.0
    return total_grade_points / total_credits

def calculate_cumulative_gpa(current_gpa, current_credits, new_gpa, new_credits):
    """Calculates the new cumulative GPA after adding new semester's performance."""
    if current_credits < 0 or new_credits < 0:
        st.error("Credits cannot be negative.")
        return None

    current_total_grade_points = current_gpa * current_credits
    new_total_grade_points = new_gpa * new_credits

    combined_total_credits = current_credits + new_credits
    combined_total_grade_points = current_total_grade_points + new_total_grade_points

    if combined_total_credits == 0:
        return 0.0
    return combined_total_grade_points / combined_total_credits

# --- Streamlit App Configuration ---
st.set_page_config(layout="centered", page_title="GPA Calculator")

st.title("GPA Calculator")

st.markdown("""
### How to Use
1. **Enter your current total credits and overall GPA** (before this semester).
2. **Enter the number of credits and expected GPA for the new semester** using the input fields and slider.
3. The calculator will show your new overall GPA and a chart to visualize how different semester GPAs affect your cumulative GPA.
4. For detailed semester performance, use the 'Current Semester Performance' tab to input each class's credits and GPA.

**Tip:** You can find your current total credits and GPA on your transcript or student portal.
""")

# --- Tabs for different functionalities ---
tab1, tab2 = st.tabs(["What If Scenario", "Current Semester Performance"])

with tab1:
    st.header("What If Scenario")
    st.markdown("Plan your future GPA by seeing what you need to achieve in your next semester.")

    # Input for current academic standing
    st.subheader("Your Current Academic Standing")
    current_gpa = st.number_input(
        "Current Cumulative GPA (e.g., 3.5)",
        min_value=0.0,
        max_value=4.0,
        value=3.0,
        step=0.01,
        help="Your GPA before the upcoming semester."
    )
    current_credits = st.number_input(
        "Current Total Credits (e.g., 60)",
        min_value=0,
        value=60,
        step=1,
        help="Total credits earned so far."
    )

    st.subheader("Your Desired Future")
    desired_gpa = st.number_input(
        "Desired Cumulative GPA (e.g., 3.7)",
        min_value=0.0,
        max_value=4.0,
        value=3.5,
        help="The overall GPA you want to achieve."
    )
    next_semester_credits = st.number_input(
        "Next Semester Credits (e.g., 15)",
        min_value=0,
        value=15,
        step=1,
        help="Number of credits you plan to take next semester."
    )

    st.markdown("---")
    scenario_type = st.radio(
        "Do you already know some of your grades for this semester?",
        ("I haven't gotten any grades yet", "I know some of my grades")
    )

    known_credits = 0
    known_grade_points = 0
    remaining_credits = next_semester_credits
    if scenario_type == "I know some of my grades" and next_semester_credits > 0:
        num_known_classes = st.number_input(
            "How many classes do you already have grades for?",
            min_value=1,
            max_value=next_semester_credits,
            value=1,
            step=1
        )
        known_credits_list = []
        known_gpa_list = []
        for i in range(int(num_known_classes)):
            st.markdown(f"**Class {i+1} (with known grade)**")
            col1, col2 = st.columns(2)
            with col1:
                k_credits = st.number_input(
                    f"Credits for Class {i+1}",
                    min_value=0.0,
                    value=3.0,
                    step=0.5,
                    key=f"known_credits_{i}"
                )
            with col2:
                k_gpa = st.number_input(
                    f"GPA for Class {i+1}",
                    min_value=0.0,
                    max_value=4.0,
                    value=3.0,
                    step=0.01,
                    key=f"known_gpa_{i}"
                )
            known_credits_list.append(k_credits)
            known_gpa_list.append(k_gpa)
        known_credits = sum(known_credits_list)
        known_grade_points = sum(c * g for c, g in zip(known_credits_list, known_gpa_list))
        remaining_credits = next_semester_credits - known_credits
        if remaining_credits < 0:
            st.error("Known credits exceed total next semester credits.")

    if st.button("Calculate Required Next Semester GPA"):
        if current_credits + next_semester_credits == 0:
            st.error("Cannot calculate if total credits are zero. Please enter valid credit values.")
        elif next_semester_credits == 0:
            st.warning("You need to take credits next semester to change your GPA.")
        elif scenario_type == "I know some of my grades" and remaining_credits < 0:
            st.error("Known credits exceed total next semester credits. Please check your inputs.")
        else:
            total_credits_after_next = current_credits + next_semester_credits
            desired_total_grade_points = desired_gpa * total_credits_after_next
            current_total_grade_points = current_gpa * current_credits
            if scenario_type == "I know some of my grades":
                # Subtract known grade points from what's needed
                grade_points_needed_remaining = desired_total_grade_points - current_total_grade_points - known_grade_points
                if remaining_credits > 0:
                    required_gpa_remaining = grade_points_needed_remaining / remaining_credits
                else:
                    required_gpa_remaining = 0.0
            else:
                # Original logic
                grade_points_needed_next_semester = desired_total_grade_points - current_total_grade_points
                if next_semester_credits > 0:
                    required_gpa_remaining = grade_points_needed_next_semester / next_semester_credits
                else:
                    required_gpa_remaining = 0.0

            st.markdown("---")
            st.subheader("Results for What If Scenario")
            if required_gpa_remaining > 4.0:
                st.error(f"To reach a {desired_gpa:.2f} GPA, you would need to achieve a GPA of **{required_gpa_remaining:.2f}** in your remaining {remaining_credits if scenario_type == 'I know some of my grades' else next_semester_credits} credits. This is likely unattainable as it exceeds a perfect 4.0 GPA. Consider adjusting your desired GPA or taking more credits.")
            elif required_gpa_remaining < 0.0:
                st.info(f"To reach a {desired_gpa:.2f} GPA, you would need to achieve a GPA of **{required_gpa_remaining:.2f}** in your remaining {remaining_credits if scenario_type == 'I know some of my grades' else next_semester_credits} credits. This means your desired GPA is lower than what you'd get even with a 0.0 in the remaining classes, or you're already above your desired GPA.")
            else:
                st.success(f"To achieve an overall GPA of **{desired_gpa:.2f}**, you need to earn a GPA of **{required_gpa_remaining:.2f}** in your remaining **{remaining_credits if scenario_type == 'I know some of my grades' else next_semester_credits}** credits.")
                st.info(f"Your total credits after this semester would be: **{total_credits_after_next}**")

with tab2:
    st.header("Current Semester Performance")
    st.markdown("Enter your classes for the current semester to calculate your semester GPA and see its impact on your overall GPA.")

    st.subheader("Your Current Overall Academic Standing")
    current_overall_gpa = st.number_input(
        "Current Overall GPA (before this semester)",
        min_value=0.0,
        max_value=4.0,
        value=3.0,
        step=0.01,
        key="current_overall_gpa_perf", # Unique key for this input
        help="Your cumulative GPA before the classes you are about to enter."
    )
    current_overall_credits = st.number_input(
        "Current Overall Credits (before this semester)",
        min_value=0,
        value=60,
        step=1,
        key="current_overall_credits_perf", # Unique key for this input
        help="Total credits earned before the classes you are about to enter."
    )

    st.subheader("Current Semester Classes")
    num_classes = st.number_input(
        "Number of Classes This Semester",
        min_value=1,
        value=4,
        step=1,
        help="How many classes are you taking this semester?"
    )

    semester_credits_list = []
    semester_gpa_list = []
    valid_entries = True

    for i in range(int(num_classes)):
        st.markdown(f"**Class {i+1}**")
        col1, col2 = st.columns(2)
        with col1:
            credits = st.number_input(
                f"Credits for Class {i+1}",
                min_value=0.0,
                value=3.0,
                step=0.5,
                key=f"credits_{i}"
            )
        with col2:
            gpa = st.number_input(
                f"GPA for Class {i+1}",
                min_value=0.0,
                max_value=4.0,
                value=3.0,
                step=0.01,
                key=f"gpa_{i}"
            )
        if credits < 0:
            st.error(f"Class {i+1}: Credits must be a non-negative number.")
            valid_entries = False
        semester_credits_list.append(credits)
        semester_gpa_list.append(gpa)

    if st.button("Calculate Semester & Overall GPA"):
        if not valid_entries or sum(semester_credits_list) == 0:
            st.warning("Please enter valid credits and GPA for all classes.")
        else:
            semester_total_credits = sum(semester_credits_list)
            semester_total_grade_points = sum(c * g for c, g in zip(semester_credits_list, semester_gpa_list))

            semester_gpa = 0.0
            if semester_total_credits > 0:
                semester_gpa = semester_total_grade_points / semester_total_credits

            updated_overall_gpa = calculate_cumulative_gpa(
                current_overall_gpa,
                current_overall_credits,
                semester_gpa,
                semester_total_credits
            )
            updated_total_credits = current_overall_credits + semester_total_credits

            st.markdown("---")
            st.subheader("Results for Current Semester")
            st.success(f"Your Semester GPA: **{semester_gpa:.2f}**")
            st.info(f"Total credits for this semester: **{semester_total_credits}**")
            if updated_overall_gpa is not None:
                st.success(f"Your New Cumulative Overall GPA: **{updated_overall_gpa:.2f}**")
                st.info(f"Your New Total Cumulative Credits: **{updated_total_credits}**")

st.markdown("---")
st.caption("Note: GPA calculations may vary slightly based on your institution's specific grading scale and rounding rules.")

# Add the MP4 video at the bottom of the page
# st.image("trump-draws.gif")
