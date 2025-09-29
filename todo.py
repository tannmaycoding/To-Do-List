import streamlit as st
import pandas as pd
import datetime
import os


# --- Helper Function for Data Persistence ---
def initialize_tasks_file():
    """Initializes the tasks.csv file if it doesn't exist."""
    if not os.path.exists("tasks.csv"):
        df = pd.DataFrame(columns=["Date", "Time", "Task", "Status"])
        df.to_csv("tasks.csv", index=False)


initialize_tasks_file()

st.title("To-Do List")


# --- Function to Handle Deletion ---
def delete_task(index_to_delete):
    """Deletes a task by its original DataFrame index."""
    try:
        df = pd.read_csv("tasks.csv")

        # Use drop(index) to remove the row
        # Since the index passed is the original pandas index, this works reliably.
        df_updated = df.drop(index_to_delete).reset_index(drop=True)

        # Save the modified DataFrame
        df_updated.to_csv("tasks.csv", index=False)

        st.toast("Task deleted successfully! 🗑️")
        st.rerun()

    except Exception as e:
        st.error(f"An error occurred during deletion: {e}")


# --- Dialog Function (for Modification) ---
@st.dialog("Modify Task")
def modify_task(task_index, current_task, current_status):
    """
    Dialog to modify the status of a specific task.
    """
    st.markdown(f"**Task:** {current_task}")
    st.markdown(f"**Current Status:** {current_status}")

    new_status = st.radio(
        "Select New Status",
        ["Not Started", "In Progress", "Done"],
        index=["Not Started", "In Progress", "Done"].index(current_status),
        key=f"status_radio_{task_index}"
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Update Status"):
            try:
                df = pd.read_csv("tasks.csv")
                df.at[task_index, 'Status'] = new_status
                df.to_csv("tasks.csv", index=False)

                st.toast("Task status updated successfully! 🎉")
                st.rerun()

            except Exception as e:
                st.error(f"An error occurred: {e}")

    with col2:
        if st.button("Cancel"):
            st.rerun()

        # --- Main App Logic ---


add_task, tasks = st.tabs(["Add Tasks", "See Tasks"])

# 1. Add Task Tab
with add_task:
    st.markdown("## Add Task")
    task = st.text_input("What's the task?")
    status = st.radio("What's the progress?", ["Not Started", "In Progress", "Done"])

    if st.button("Submit"):
        if task:
            df = pd.read_csv("tasks.csv")
            df2 = pd.DataFrame([{
                "Date": datetime.datetime.now().strftime("%d/%m/%Y"),
                "Time": datetime.datetime.now().strftime("%H:%M"),
                "Task": task,
                "Status": status
            }])
            df3 = pd.concat([df, df2], ignore_index=True)
            df3.to_csv("tasks.csv", index=False)
            st.toast("Task added successfully! ✅")
            st.rerun()
        else:
            st.error("Please enter a task before submitting.")

# 2. See Tasks Tab
with tasks:
    try:
        # Read all tasks and create a column for the original index
        all_tasks_df = pd.read_csv("tasks.csv")
        all_tasks_df['Original_Index'] = all_tasks_df.index

        # Reverse for display (newest first)
        df_display = all_tasks_df[::-1]

        if not df_display.empty:
            for i, row in df_display.iterrows():
                # We use the 'Original_Index' to correctly reference the row in the CSV
                original_index = row['Original_Index']

                # --- Task Card Display ---
                with st.container():
                    st.markdown(
                        f"""
                        <div style="
                            border:1px solid #ddd;
                            border-radius:12px;
                            padding:15px;
                            margin-bottom:12px;
                            background-color:#f9f9f9;
                            box-shadow:2px 2px 6px rgba(0,0,0,0.1);
                        ">
                            <h4 style="margin:0;color:#333;">{row['Task']}</h4>
                            <p style="margin:6px 0;color:#333;">
                            <b>Entered On:</b> {row['Date']} on {row["Time"]}<br>
                            <b>Status:</b> {row['Status']}
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    # --- Action Buttons ---
                    col_mod, col_del, _ = st.columns([1, 1, 4])  # Create columns for buttons

                    with col_mod:
                        # Modify Button
                        if st.button("Modify Status", key=f"btn_mod_{i}"):
                            modify_task(
                                task_index=original_index,
                                current_task=row['Task'],
                                current_status=row['Status']
                            )

                    with col_del:
                        # Delete Popover for Confirmation
                        with st.popover("Delete Task", use_container_width=True):
                            st.warning("Are you sure you want to delete this task?")
                            st.caption(f"**Task:** *{row['Task']}*")
                            if st.button("Confirm Delete", key=f"btn_del_conf_{i}", type="primary"):
                                delete_task(original_index)
                                # The delete_task function will handle the rerun

        else:
            st.info("No tasks added yet! Go to the 'Add Tasks' tab to start.")

    except pd.errors.EmptyDataError:
        st.info("No tasks added yet! Go to the 'Add Tasks' tab to start.")
    except FileNotFoundError:
        st.error("The tasks file was not found. Please try adding a task.")