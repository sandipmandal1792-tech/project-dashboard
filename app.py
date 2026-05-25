
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date
import os

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Enterprise PMO Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# FILES
# =========================================================

PROJECT_FILE = "project_name.txt"
EXCEL_FILE = "project_tracker.xlsx"

# =========================================================
# CSS
# =========================================================

st.markdown("""
<style>

.stApp {
    background: linear-gradient(
        135deg,
        #061428,
        #0b1f3a,
        #10284d
    );
    color: white;
}

header {
    background: transparent !important;
}

.block-container {
    padding-top: 1rem !important;
}

section[data-testid="stSidebar"] {

    background: linear-gradient(
        180deg,
        #0b1220,
        #111c33
    );

    border-right: 1px solid #2563eb;
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

.main-title {

    font-size: 52px;

    font-weight: 800;

    color: white;
}

.sub-title {

    font-size: 18px;

    color: #bfdbfe;

    margin-bottom: 25px;
}

label,
p,
span {
    color: white !important;
}

input,
textarea {

    background-color: white !important;

    color: black !important;

    -webkit-text-fill-color: black !important;

    border-radius: 12px !important;

    border: 1px solid #94a3b8 !important;

    box-shadow: none !important;
}

.stSelectbox div[data-baseweb="select"] {

    background-color: white !important;

    border-radius: 12px !important;

    border: 1px solid #94a3b8 !important;
}

.stSelectbox * {

    color: black !important;

    -webkit-text-fill-color: black !important;
}

[data-baseweb="select"] input {

    color: black !important;

    -webkit-text-fill-color: black !important;
}

.stDateInput input {

    background-color: white !important;

    color: black !important;

    -webkit-text-fill-color: black !important;
}

.stButton > button {

    background: linear-gradient(
        90deg,
        #2563eb,
        #3b82f6
    ) !important;

    color: white !important;

    border: none !important;

    border-radius: 12px !important;

    height: 45px !important;

    font-weight: 700 !important;

    box-shadow: 0px 4px 15px rgba(37,99,235,0.4);
}

.stButton button * {

    color: white !important;

    -webkit-text-fill-color: white !important;
}

.phase-card {

    background: rgba(15,23,42,0.85);

    border: 1px solid #2563eb;

    border-radius: 20px;

    padding: 20px;

    margin-bottom: 30px;
}

.phase-title {

    font-size: 30px;

    font-weight: 700;

    color: white;
}

.form-box {

    background-color: rgba(15,23,42,0.92);

    border: 1px solid #2563eb;

    border-radius: 18px;

    padding: 20px;

    margin-top: 20px;

    margin-bottom: 20px;
}

[data-testid="stDataFrame"] {

    border-radius: 14px;

    overflow: hidden;

    border: 1px solid #2563eb;
}

[data-testid="stDataFrame"] * {

    color: black !important;
}

footer {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# LOAD PROJECT NAME
# =========================================================

if os.path.exists(PROJECT_FILE):

    with open(PROJECT_FILE, "r") as f:

        project_name = f.read()

else:

    project_name = "Enterprise PMO Dashboard"

# =========================================================
# LOAD DATA
# =========================================================

if "phase_data" not in st.session_state:

    st.session_state.phase_data = {}

    if os.path.exists(EXCEL_FILE):

        all_sheets = pd.read_excel(
            EXCEL_FILE,
            sheet_name=None
        )

        for sheet, df in all_sheets.items():

            if "Task_ID" not in df.columns:

                df.insert(
                    0,
                    "Task_ID",
                    range(1, len(df) + 1)
                )

            st.session_state.phase_data[sheet] = df

    else:

        sample_df = pd.DataFrame([

            {
                "Task_ID": 1,
                "Task": "Requirement Gathering",
                "Status": "In Progress",
                "Priority": "High",
                "Assignee": "Rahul",
                "Planned Start Date": "2026-01-01",
                "Planned End Date": "2026-01-15",
                "Actual End Date": "",
                "Progress": 50
            }

        ])

        st.session_state.phase_data[
            "Requirement Analysis"
        ] = sample_df

# =========================================================
# SAVE FUNCTION
# =========================================================

def save_excel():

    with pd.ExcelWriter(
        EXCEL_FILE,
        engine="openpyxl"
    ) as writer:

        for phase_name, df in st.session_state.phase_data.items():

            df.to_excel(
                writer,
                sheet_name=phase_name[:31],
                index=False
            )

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("⚙️ Project Setup")

new_project_name = st.sidebar.text_input(
    "Project Name",
    value=project_name
)

if st.sidebar.button("Save Project Name"):

    with open(PROJECT_FILE, "w") as f:

        f.write(new_project_name)

    project_name = new_project_name

phase_names = list(
    st.session_state.phase_data.keys()
)

selected_phase = st.sidebar.selectbox(
    "Select Phase",
    ["All Phases"] + phase_names
)

st.sidebar.markdown("---")

# =========================================================
# CREATE PHASE
# =========================================================

st.sidebar.subheader("➕ Create New Phase")

new_phase_name = st.sidebar.text_input(
    "Phase Name"
)

if st.sidebar.button("Create Phase"):

    if new_phase_name.strip() != "":

        if new_phase_name not in st.session_state.phase_data:

            st.session_state.phase_data[
                new_phase_name
            ] = pd.DataFrame(columns=[

                "Task_ID",
                "Task",
                "Status",
                "Priority",
                "Assignee",
                "Planned Start Date",
                "Planned End Date",
                "Actual End Date",
                "Progress"

            ])

            save_excel()

            st.rerun()

# =========================================================
# HEADER
# =========================================================

st.markdown(f"""
<div class="main-title">
📊 {project_name}
</div>

<div class="sub-title">
Enterprise PMO Dashboard
</div>
""", unsafe_allow_html=True)

# =========================================================
# LOOP PHASES
# =========================================================

for phase_name in list(
    st.session_state.phase_data.keys()
):

    if (
        selected_phase != "All Phases"
        and phase_name != selected_phase
    ):
        continue

    phase_df = st.session_state.phase_data[
        phase_name
    ]

    st.markdown(
        '<div class="phase-card">',
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns([8,1,1])

    with c1:

        st.markdown(f"""
        <div class="phase-title">
        🚀 {phase_name}
        </div>
        """, unsafe_allow_html=True)

    edit_key = f"edit_{phase_name}"

    if edit_key not in st.session_state:

        st.session_state[edit_key] = False

    with c2:

        if st.button(
            "✏️",
            key=f"edit_btn_{phase_name}"
        ):

            st.session_state[edit_key] = not st.session_state[
                edit_key
            ]

    with c3:

        if st.button(
            "🗑",
            key=f"delete_phase_{phase_name}"
        ):

            del st.session_state.phase_data[
                phase_name
            ]

            save_excel()

            st.rerun()

    # =====================================================
    # TABLE
    # =====================================================

    show_df = phase_df.copy()

    if "Task_ID" in show_df.columns:

        show_df = show_df.drop(
            columns=["Task_ID"]
        )

    show_df.insert(
        0,
        "S.No",
        range(1, len(show_df) + 1)
    )

    st.dataframe(
        show_df,
        use_container_width=True,
        height=250
    )

    # =====================================================
    # EDIT PANEL
    # =====================================================

    if st.session_state[edit_key]:

        st.markdown(
            '<div class="form-box">',
            unsafe_allow_html=True
        )

        st.markdown(
            "## ✏️ Add / Edit Task"
        )

        task_options = ["New Task"]

        if len(phase_df) > 0:

            task_options += list(
                phase_df["Task"].fillna("")
            )

        selected_task = st.selectbox(
            "Select Task",
            task_options,
            key=f"task_select_{phase_name}"
        )

        selected_task_id = None

        selected_row = {}

        if (
            selected_task != "New Task"
            and selected_task in list(
                phase_df["Task"]
            )
        ):

            selected_row = phase_df[
                phase_df["Task"] == selected_task
            ].iloc[0]

            selected_task_id = selected_row[
                "Task_ID"
            ]

        task_name = st.text_input(
            "Task Name",
            value=selected_row.get(
                "Task",
                ""
            )
        )

        x1, x2, x3 = st.columns(3)

        with x1:

            status = st.selectbox(
                "Status",
                [
                    "Pending",
                    "In Progress",
                    "Done",
                    "Blocked"
                ],
                index=[
                    "Pending",
                    "In Progress",
                    "Done",
                    "Blocked"
                ].index(
                    selected_row.get(
                        "Status",
                        "Pending"
                    )
                )
            )

        with x2:

            priority = st.selectbox(
                "Priority",
                [
                    "High",
                    "Medium",
                    "Low"
                ],
                index=[
                    "High",
                    "Medium",
                    "Low"
                ].index(
                    selected_row.get(
                        "Priority",
                        "Medium"
                    )
                )
            )

        with x3:

            assignee = st.text_input(
                "Assignee",
                value=selected_row.get(
                    "Assignee",
                    ""
                )
            )

        y1, y2 = st.columns(2)

        with y1:

            planned_start = st.date_input(
                "Planned Start Date",
                value=pd.to_datetime(
                    selected_row.get(
                        "Planned Start Date",
                        str(date.today())
                    )
                )
            )

        with y2:

            planned_end = st.date_input(
                "Planned End Date",
                value=pd.to_datetime(
                    selected_row.get(
                        "Planned End Date",
                        str(date.today())
                    )
                )
            )

        has_actual = st.checkbox(
            "Has Actual End Date?",
            value=(
                str(
                    selected_row.get(
                        "Actual End Date",
                        ""
                    )
                ).strip() != ""
            )
        )

        actual_end = ""

        if has_actual:

            actual_end = st.date_input(
                "Actual End Date",
                value=pd.to_datetime(
                    selected_row.get(
                        "Actual End Date",
                        str(date.today())
                    )
                )
            )

        position_options = ["Default (Last)"]

        for i in range(
            1,
            len(phase_df) + 2
        ):
            position_options.append(str(i))

        task_position = st.selectbox(
            "Task Position",
            position_options
        )

        progress = st.slider(
            "Progress",
            0,
            100,
            int(
                selected_row.get(
                    "Progress",
                    0
                )
            )
        )

        # =================================================
        # BUTTONS
        # =================================================

        b1, b2 = st.columns(2)

        with b1:

            if st.button(
                "💾 Save Changes",
                key=f"save_{phase_name}"
            ):

                if len(phase_df) == 0:

                    next_task_id = 1

                else:

                    next_task_id = int(
                        phase_df["Task_ID"].max()
                    ) + 1

                new_row = {

                    "Task_ID": (
                        selected_task_id
                        if selected_task != "New Task"
                        else next_task_id
                    ),

                    "Task": task_name,

                    "Status": status,

                    "Priority": priority,

                    "Assignee": assignee,

                    "Planned Start Date": str(planned_start),

                    "Planned End Date": str(planned_end),

                    "Actual End Date": (
                        str(actual_end)
                        if has_actual
                        else ""
                    ),

                    "Progress": progress
                }

                # =========================================
                # EDIT EXISTING
                # =========================================

                if (
                    selected_task != "New Task"
                    and selected_task_id is not None
                ):

                    idx = phase_df[
                        phase_df["Task_ID"] == selected_task_id
                    ].index[0]

                    phase_df = phase_df.drop(idx)

                    phase_df = phase_df.reset_index(
                        drop=True
                    )

                    if task_position == "Default (Last)":

                        insert_pos = len(phase_df)

                    else:

                        insert_pos = int(
                            task_position
                        ) - 1

                    top = phase_df.iloc[:insert_pos]

                    bottom = phase_df.iloc[insert_pos:]

                    phase_df = pd.concat(
                        [
                            top,
                            pd.DataFrame([new_row]),
                            bottom
                        ],
                        ignore_index=True
                    )

                # =========================================
                # ADD NEW
                # =========================================

                else:

                    if task_position == "Default (Last)":

                        phase_df = pd.concat(
                            [
                                phase_df,
                                pd.DataFrame([new_row])
                            ],
                            ignore_index=True
                        )

                    else:

                        insert_pos = int(
                            task_position
                        ) - 1

                        top = phase_df.iloc[:insert_pos]

                        bottom = phase_df.iloc[insert_pos:]

                        phase_df = pd.concat(
                            [
                                top,
                                pd.DataFrame([new_row]),
                                bottom
                            ],
                            ignore_index=True
                        )

                st.session_state.phase_data[
                    phase_name
                ] = phase_df

                save_excel()

                st.session_state[
                    edit_key
                ] = False

                st.rerun()

        with b2:

            if st.button(
                "🗑 Delete Task",
                key=f"delete_task_{phase_name}"
            ):

                if selected_task_id is not None:

                    phase_df = phase_df[
                        phase_df["Task_ID"] != selected_task_id
                    ]

                    st.session_state.phase_data[
                        phase_name
                    ] = phase_df

                    save_excel()

                    st.session_state[
                        edit_key
                    ] = False

                    st.rerun()

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )

    # =====================================================
    # TIMELINE
    # =====================================================

    st.markdown("### 📅 Timeline")

    try:

        if len(phase_df) > 0:

            fig = go.Figure()

            task_names = []
            y_positions = []

            total_tasks = len(phase_df)

            for i, (_, row) in enumerate(
                phase_df.iterrows()
            ):

                task_name = row["Task"]

                y_base = total_tasks - i

                task_names.append(task_name)

                y_positions.append(y_base)

                planned_start = pd.to_datetime(
                    row["Planned Start Date"]
                )

                planned_end = pd.to_datetime(
                    row["Planned End Date"]
                )

                fig.add_trace(

                    go.Scatter(

                        x=[
                            planned_start,
                            planned_end
                        ],

                        y=[
                            y_base + 0.04,
                            y_base + 0.04
                        ],

                        mode="lines",

                        line=dict(
                            color="#facc15",
                            width=12
                        ),

                        name="Planned",

                        showlegend=(i == 0)
                    )
                )

                actual_end = str(
                    row["Actual End Date"]
                ).strip()

                if actual_end != "":

                    actual_end = pd.to_datetime(
                        actual_end
                    )

                    fig.add_trace(

                        go.Scatter(

                            x=[
                                planned_start,
                                actual_end
                            ],

                            y=[
                                y_base - 0.04,
                                y_base - 0.04
                            ],

                            mode="lines",

                            line=dict(
                                color="#ef4444",
                                width=12
                            ),

                            name="Actual",

                            showlegend=(i == 0)
                        )
                    )

            fig.update_layout(

                height=max(
                    350,
                    total_tasks * 65
                ),

                paper_bgcolor="#0f172a",

                plot_bgcolor="#0f172a",

                font=dict(
                    color="white",
                    size=14
                ),

                margin=dict(
                    l=20,
                    r=20,
                    t=20,
                    b=20
                ),

                legend=dict(

                    orientation="h",

                    yanchor="bottom",

                    y=1.02,

                    xanchor="right",

                    x=1
                ),

                xaxis=dict(

                    showgrid=True,

                    gridcolor="rgba(255,255,255,0.08)"
                ),

                yaxis=dict(

                    tickmode="array",

                    tickvals=y_positions,

                    ticktext=task_names,

                    showgrid=False
                )
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    except:

        st.warning(
            "Please enter valid dates."
        )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    "Enterprise PMO Dashboard"
)

