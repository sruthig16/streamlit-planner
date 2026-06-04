from datetime import date, datetime
from html import escape

import streamlit as st

from database import (
    init_db,
    create_plan,
    get_plans,
    get_plan,
    get_buckets,
    create_task,
    get_tasks,
    update_task_status,
    delete_task,
    add_checklist_item,
    get_checklist_items,
    update_checklist_item,
    delete_checklist_item,
    get_checklist_progress,
    update_task_details,
    rename_plan,
    delete_plan,
)


def apply_custom_css():
    st.markdown(
        """
        <style>
        .main-title {
            font-size: 34px;
            font-weight: 700;
            margin-bottom: 0px;
        }

        .subtitle {
            color: #666;
            margin-top: 0px;
            margin-bottom: 25px;
        }

        .task-card {
            border: 1px solid #e6e6e6;
            border-radius: 12px;
            padding: 12px;
            margin-bottom: 12px;
            background-color: #ffffff;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        }

        .task-title {
            font-size: 16px;
            font-weight: 700;
            margin-bottom: 6px;
        }

        .task-meta {
            font-size: 13px;
            color: #555;
            margin-bottom: 4px;
        }

        .priority-low {
            background-color: #e8f5e9;
            color: #256029;
            padding: 3px 8px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            display: inline-block;
        }

        .priority-medium {
            background-color: #fff8e1;
            color: #7a5c00;
            padding: 3px 8px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            display: inline-block;
        }

        .priority-high {
            background-color: #ffebee;
            color: #b71c1c;
            padding: 3px 8px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            display: inline-block;
        }

        .bucket-heading {
            font-size: 18px;
            font-weight: 700;
            padding-bottom: 8px;
            border-bottom: 2px solid #eeeeee;
            margin-bottom: 12px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def priority_badge(priority):
    css_class = {
        "Low": "priority-low",
        "Medium": "priority-medium",
        "High": "priority-high",
    }.get(priority, "priority-medium")

    return f"<span class='{css_class}'>{escape(priority)}</span>"


def parse_date(date_text):
    if not date_text:
        return date.today()

    try:
        return datetime.strptime(date_text, "%Y-%m-%d").date()
    except ValueError:
        return date.today()


def filter_tasks(tasks, search, bucket, priority, status):
    results = tasks

    if search:
        query = search.lower()
        results = [
            t for t in results
            if query in (t["title"] or "").lower()
            or query in (t["description"] or "").lower()
            or query in (t["assignee"] or "").lower()
            or query in (t["labels"] or "").lower()
        ]

    if bucket != "All":
        results = [t for t in results if t["bucket_name"] == bucket]

    if priority != "All":
        results = [t for t in results if t["priority"] == priority]

    if status == "Completed":
        results = [t for t in results if t["completed"]]
    elif status == "Not started":
        results = [t for t in results if not t["completed"]]

    return results


st.set_page_config(
    page_title="Planner App",
    layout="wide"
)

init_db()
apply_custom_css()

if "selected_plan_id" not in st.session_state:
    st.session_state.selected_plan_id = None


st.markdown("<div class='main-title'>Planner App</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='subtitle'>Create plans, organize tasks, and track progress.</div>",
    unsafe_allow_html=True,
)

st.sidebar.title("My Plans")

with st.sidebar.form("create_plan_form"):
    new_plan_name = st.text_input("New plan name")
    create_clicked = st.form_submit_button("Create plan")

    if create_clicked:
        if new_plan_name.strip():
            plan_id = create_plan(new_plan_name.strip())
            st.session_state.selected_plan_id = plan_id
            st.rerun()
        else:
            st.warning("Please enter a plan name.")


plans = get_plans()

if plans:
    plan_ids = [plan["id"] for plan in plans]
    plan_name_map = {
        plan["id"]: plan["name"]
        for plan in plans
    }

    current_index = 0

    if st.session_state.selected_plan_id in plan_ids:
        current_index = plan_ids.index(st.session_state.selected_plan_id)

    selected_plan_id_from_box = st.sidebar.selectbox(
        "Open a plan",
        plan_ids,
        index=current_index,
        format_func=lambda plan_id: plan_name_map[plan_id],
    )

    st.session_state.selected_plan_id = selected_plan_id_from_box
else:
    st.sidebar.info("No plans yet. Create your first plan.")


selected_plan_id = st.session_state.selected_plan_id

if selected_plan_id is None:
    st.info("Create a plan from the sidebar to get started.")
    st.stop()


current_plan = get_plan(selected_plan_id)

if current_plan is None:
    st.session_state.selected_plan_id = None
    st.rerun()


st.sidebar.divider()
st.sidebar.subheader("Manage current plan")

with st.sidebar.form("rename_plan_form"):
    renamed_plan_name = st.text_input(
        "Rename plan",
        value=current_plan["name"],
    )

    rename_clicked = st.form_submit_button("Save plan name")

    if rename_clicked:
        if renamed_plan_name.strip():
            rename_plan(
                selected_plan_id,
                renamed_plan_name.strip(),
            )
            st.rerun()
        else:
            st.warning("Plan name cannot be empty.")


with st.sidebar.form("delete_plan_form"):
    st.warning("Deleting a plan will delete its buckets, tasks, and checklist items.")
    confirm_delete = st.checkbox("Yes, delete this plan")
    delete_clicked = st.form_submit_button("Delete current plan")

    if delete_clicked:
        if confirm_delete:
            delete_plan(selected_plan_id)
            st.session_state.selected_plan_id = None
            st.rerun()
        else:
            st.warning("Please tick the checkbox first.")


buckets = get_buckets(selected_plan_id)
tasks = get_tasks(selected_plan_id)

st.markdown(
    f"<div class='main-title'>{escape(current_plan['name'])}</div>",
    unsafe_allow_html=True,
)

st.divider()

search_col, bucket_col, priority_col, status_col = st.columns([3, 2, 2, 2])

with search_col:
    search_query = st.text_input(
        "Search tasks",
        placeholder="Search by title, description, assignee, or labels...",
        label_visibility="collapsed",
    )

bucket_names_for_filter = ["All"] + [b["name"] for b in buckets]

with bucket_col:
    filter_bucket = st.selectbox("Bucket", bucket_names_for_filter)

with priority_col:
    filter_priority = st.selectbox("Priority", ["All", "Low", "Medium", "High"])

with status_col:
    filter_status = st.selectbox("Status", ["All", "Not started", "Completed"])

filtered_tasks = filter_tasks(tasks, search_query, filter_bucket, filter_priority, filter_status)

filters_active = search_query or filter_bucket != "All" or filter_priority != "All" or filter_status != "All"
if filters_active:
    st.caption(f"{len(filtered_tasks)} of {len(tasks)} task(s) shown")

st.divider()

tab1, tab2 = st.tabs(["Grid", "Board"])


with tab1:
    st.subheader("Grid View")

    if filtered_tasks:
        task_rows = []

        for task in filtered_tasks:
            completed_items, total_items = get_checklist_progress(task["id"])

            task_rows.append({
                "Task Name": task["title"],
                "Assigned to": task["assignee"] or "",
                "Due": task["due_date"] or "",
                "Bucket": task["bucket_name"],
                "Status": "Completed" if task["completed"] else "Not started",
                "Priority": task["priority"],
                "Labels": task["labels"] or "",
                "Checklist": f"{completed_items}/{total_items}",
            })

        st.dataframe(task_rows, use_container_width=True)
    else:
        if tasks:
            st.info("No tasks match your search or filters.")
        else:
            st.info("No tasks yet. Add a task from the Board view.")


with tab2:
    st.subheader("Board View")

    columns = st.columns(len(buckets))

    for index, bucket in enumerate(buckets):
        with columns[index]:
            bucket_tasks = [
                task for task in filtered_tasks
                if task["bucket_id"] == bucket["id"]
            ]

            st.markdown(
                f"<div class='bucket-heading'>{escape(bucket['name'])} ({len(bucket_tasks)})</div>",
                unsafe_allow_html=True,
            )

            with st.expander("+ Add task"):
                with st.form(f"add_task_form_{bucket['id']}"):
                    task_title = st.text_input("Task title")
                    description = st.text_area("Description")

                    add_due_date = st.checkbox("Add due date")
                    due_date = None

                    if add_due_date:
                        due_date = st.date_input("Due date")

                    priority = st.selectbox(
                        "Priority",
                        ["Low", "Medium", "High"],
                        index=1
                    )

                    assignee = st.text_input("Assignee")
                    labels = st.text_input("Labels/tags")

                    save_task = st.form_submit_button("Save task")

                    if save_task:
                        if task_title.strip():
                            create_task(
                                plan_id=selected_plan_id,
                                bucket_id=bucket["id"],
                                title=task_title.strip(),
                                description=description.strip(),
                                due_date=due_date,
                                priority=priority,
                                assignee=assignee.strip(),
                                labels=labels.strip(),
                            )
                            st.rerun()
                        else:
                            st.warning("Task title is required.")

            if bucket_tasks:
                for task in bucket_tasks:
                    completed_items, total_items = get_checklist_progress(task["id"])

                    title_text = escape(task["title"])

                    if task["completed"]:
                        title_html = f"<s>{title_text}</s>"
                    else:
                        title_html = title_text

                    card_html = f"""
                    <div class="task-card">
                        <div class="task-title">{title_html}</div>
                    """

                    if task["description"]:
                        card_html += f"<div class='task-meta'>{escape(task['description'])}</div>"

                    if task["labels"]:
                        card_html += f"<div class='task-meta'>Labels: {escape(task['labels'])}</div>"

                    if task["due_date"]:
                        card_html += f"<div class='task-meta'>Due: {escape(task['due_date'])}</div>"

                    if task["assignee"]:
                        card_html += f"<div class='task-meta'>Assigned to: {escape(task['assignee'])}</div>"

                    card_html += f"<div class='task-meta'>Checklist: {completed_items}/{total_items}</div>"
                    card_html += f"<div class='task-meta'>Priority: {priority_badge(task['priority'])}</div>"

                    if task["completed"]:
                        card_html += "<div class='task-meta'>Status: Completed</div>"

                    card_html += "</div>"

                    st.markdown(card_html, unsafe_allow_html=True)

                    with st.expander("Manage task"):
                        st.markdown("**Move / Complete / Delete**")

                        bucket_names = [item["name"] for item in buckets]
                        bucket_id_map = {
                            item["name"]: item["id"]
                            for item in buckets
                        }

                        current_bucket_index = bucket_names.index(task["bucket_name"])

                        with st.form(f"manage_task_form_{task['id']}"):
                            selected_bucket_name = st.selectbox(
                                "Move to bucket",
                                bucket_names,
                                index=current_bucket_index,
                            )

                            completed = st.checkbox(
                                "Completed",
                                value=bool(task["completed"]),
                            )

                            update_clicked = st.form_submit_button("Update task status")
                            delete_clicked = st.form_submit_button("Delete task")

                            if update_clicked:
                                selected_bucket_id = bucket_id_map[selected_bucket_name]

                                update_task_status(
                                    task_id=task["id"],
                                    bucket_id=selected_bucket_id,
                                    completed=completed,
                                )

                                st.rerun()

                            if delete_clicked:
                                delete_task(task["id"])
                                st.rerun()

                        st.divider()
                        st.markdown("**Edit task details**")

                        priority_options = ["Low", "Medium", "High"]

                        if task["priority"] in priority_options:
                            priority_index = priority_options.index(task["priority"])
                        else:
                            priority_index = 1

                        with st.form(f"edit_task_form_{task['id']}"):
                            edited_title = st.text_input(
                                "Task title",
                                value=task["title"],
                            )

                            edited_description = st.text_area(
                                "Description",
                                value=task["description"] or "",
                            )

                            keep_due_date = st.checkbox(
                                "Use due date",
                                value=bool(task["due_date"]),
                            )

                            edited_due_date = None

                            if keep_due_date:
                                edited_due_date = st.date_input(
                                    "Due date",
                                    value=parse_date(task["due_date"]),
                                )

                            edited_priority = st.selectbox(
                                "Priority",
                                priority_options,
                                index=priority_index,
                            )

                            edited_assignee = st.text_input(
                                "Assignee",
                                value=task["assignee"] or "",
                            )

                            edited_labels = st.text_input(
                                "Labels/tags",
                                value=task["labels"] or "",
                            )

                            save_edit_clicked = st.form_submit_button("Save edited task")

                            if save_edit_clicked:
                                if edited_title.strip():
                                    update_task_details(
                                        task_id=task["id"],
                                        title=edited_title.strip(),
                                        description=edited_description.strip(),
                                        due_date=edited_due_date,
                                        priority=edited_priority,
                                        assignee=edited_assignee.strip(),
                                        labels=edited_labels.strip(),
                                    )
                                    st.rerun()
                                else:
                                    st.warning("Task title is required.")

                        st.divider()
                        st.markdown("**Checklist**")

                        checklist_items = get_checklist_items(task["id"])

                        if checklist_items:
                            for item in checklist_items:
                                item_done = st.checkbox(
                                    item["text"],
                                    value=bool(item["completed"]),
                                    key=f"checklist_item_{item['id']}",
                                )

                                if item_done != bool(item["completed"]):
                                    update_checklist_item(
                                        item_id=item["id"],
                                        completed=item_done,
                                    )
                                    st.rerun()

                                if st.button(
                                    "Delete checklist item",
                                    key=f"delete_checklist_item_{item['id']}",
                                ):
                                    delete_checklist_item(item["id"])
                                    st.rerun()
                        else:
                            st.caption("No checklist items yet.")

                        with st.form(f"add_checklist_form_{task['id']}"):
                            new_checklist_text = st.text_input("New checklist item")
                            add_item_clicked = st.form_submit_button("Add checklist item")

                            if add_item_clicked:
                                if new_checklist_text.strip():
                                    add_checklist_item(
                                        task_id=task["id"],
                                        text=new_checklist_text.strip(),
                                    )
                                    st.rerun()
                                else:
                                    st.warning("Checklist item cannot be empty.")
            else:
                st.info("No tasks yet.")