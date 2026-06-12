import traceback
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date
import os
import shutil 
import gspread
from google.oauth2.service_account import Credentials


PROJECT_FILE = "project_name.txt"
EXCEL_FILE = "project_tracker.xlsx"
BACKUP_FILE = "backup.xlsx"
GOOGLE_SHEET_NAME = "PMO Dashboard Data" 

def create_backup():

    if os.path.exists(EXCEL_FILE):

        shutil.copy2(
            EXCEL_FILE,
            BACKUP_FILE
        )
def restore_backup():

    if os.path.exists(BACKUP_FILE):

        shutil.copy2(
            BACKUP_FILE,
            EXCEL_FILE
        )

        if "phase_data" in st.session_state:
            del st.session_state.phase_data

        st.session_state.confirm_restore = False
        st.session_state.restore_success = True

        st.rerun()

def connect_google_sheet():

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scopes
    )

    client = gspread.authorize(creds)

    return client.open(
        GOOGLE_SHEET_NAME
    )

def backup_to_google_sheet():

    sheet = connect_google_sheet()

    # Delete all existing worksheets

    existing_sheets = sheet.worksheets()

    for ws in existing_sheets[1:]:

        sheet.del_worksheet(ws)
    first_sheet = sheet.get_worksheet(0)

    first_sheet.clear()
    first_sheet.update_title("TEMP_BACKUP")

    # Create fresh worksheets

    for phase_name, df in st.session_state.phase_data.items():

        try:
            old_ws = sheet.worksheet(phase_name[:100])
            sheet.del_worksheet(old_ws)
        except:
            pass

        ws = sheet.add_worksheet(
            title=phase_name[:100],
            rows=max(len(df) + 10, 100),
            cols=max(len(df.columns) + 5, 20)
        )

        safe_df = df.copy()

        safe_df = safe_df.fillna("")

        safe_df = safe_df.astype(str)

        data = [safe_df.columns.tolist()] + safe_df.values.tolist()

        ws.update(data)
# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Enterprise PMO Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)
# =====================================================
# ADMIN SECURITY
# =====================================================

ADMIN_PASSWORD = st.secrets.get(
    "ADMIN_PASSWORD",
    "admin123"
)

if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "show_login" not in st.session_state:
    st.session_state.show_login = False
if "confirm_restore" not in st.session_state:
    st.session_state.confirm_restore = False
if "restore_success" not in st.session_state:
    st.session_state.restore_success = False
with st.sidebar:

    st.markdown("---")

    if not st.session_state.is_admin:

        if not st.session_state.show_login:

            if st.button(
                "🔐 Login",
                use_container_width=True
            ):
                st.session_state.show_login = True
                st.rerun()

        else:

            admin_pass = st.text_input(
                "Password",
                type="password"
            )

            if st.button(
                "Login",
                use_container_width=True
            ):

                if admin_pass == ADMIN_PASSWORD:

                    st.session_state.is_admin = True
                    st.session_state.show_login = False

                    st.rerun()

                else:

                    st.error("Wrong Password")

    else:

        st.markdown("""
        <div style="
        text-align:center;
        padding:8px 0;
        margin-bottom:10px;
        ">
        <div style="font-size:28px;">👤</div>
        <div style="color:white;font-weight:600;">
        Administrator
        </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(
            "🚪 Logout",
            use_container_width=True
        ):

            st.session_state.is_admin = False
            st.session_state.show_login = False
            

            st.rerun()
        st.markdown("---")

        if st.button(
            "📦 Create Backup",
            use_container_width=True
        ):

            try:

                create_backup()

                backup_to_google_sheet()

                st.success(
                    "Backup Saved to Local & Google Sheet"
                )

            except Exception as e:

                st.error(str(e))
                st.code(traceback.format_exc())



        if st.button(
            "♻ Restore Backup",
            use_container_width=True
        ):

            st.session_state.confirm_restore = True
        if st.session_state.confirm_restore:

            st.warning(
                "This will replace current data with backup data."
            )

            c1, c2 = st.columns(2)

            with c1:

                if st.button(
                    "✅ Yes Restore",
                    use_container_width=True
                ):

                    restore_backup()

            with c2:

                if st.button(
                    "❌ Cancel",
                    use_container_width=True
                ):

                    st.session_state.confirm_restore = False
                    
                    st.rerun()

        if st.session_state.restore_success:

            st.success(
                "Restore Successful"
            )

            st.session_state.restore_success = False

    st.markdown("---")

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

            if "Task_Type" not in df.columns:

                df["Task_Type"] = "Main Task"

            if "Parent_Task" not in df.columns:

                df["Parent_Task"] = ""

            if "Task_ID" not in df.columns:

                df.insert(
                    0,
                    "Task_ID",
                    range(1, len(df) + 1)
                )

            st.session_state.phase_data[sheet] = df

    else:

        st.session_state.phase_data = {}

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
    value=project_name, 
    disabled=not st.session_state.is_admin
)

if st.session_state.is_admin:

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
if st.session_state.is_admin:

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

                        "Task_Type",

                        "Parent_Task",

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

# =====================================================
# GLOBAL SUMMARY ROW
# =====================================================

st.markdown("""
<div style="
    color:#93c5fd;
    font-size:18px;
    font-weight:700;
    margin-bottom:8px;
">
📌 Select Phase
</div>
""", unsafe_allow_html=True)

phase_list = list(
    st.session_state.phase_data.keys()
)

summary_phase = None

if len(phase_list) > 0:

    drop_col1, drop_col2 = st.columns([2,5])

with drop_col1:

    summary_phase = st.selectbox(
        "",
        phase_list,
        key="summary_dropdown"
    )

if summary_phase is not None:

    summary_df = st.session_state.phase_data[
        summary_phase
    ]

    if "Task_Type" not in summary_df.columns:

        summary_df["Task_Type"] = "Main Task"

    main_summary_df = summary_df[
        summary_df["Task_Type"]
        == "Main Task"
    ]

    total_tasks = len(main_summary_df)

    completed_tasks = len(
        main_summary_df[
            main_summary_df["Status"]
            == "Done"
        ]
    )

    avg_progress = 0

    if total_tasks > 0:

        avg_progress = int(
            main_summary_df["Progress"]
            .astype(int)
            .mean()
        )

    weeks_elapsed = 0

    try:

        all_start_dates = pd.to_datetime(
            summary_df["Planned Start Date"],
            errors="coerce"
        ).dropna()

        if len(all_start_dates) > 0:

            earliest_date = all_start_dates.min()

            total_days = (
                pd.Timestamp.today()
                - earliest_date
            ).days

            weeks_elapsed = (
                total_days // 7
            ) + 1

    except:
        pass

    sum1, sum2, sum3 = st.columns(3)

    with sum1:

        st.metric(
            "Phase Progress",
            f"{avg_progress}%"
        )

    with sum2:

        st.metric(
            "Weeks Elapsed",
            f"{weeks_elapsed}"
        )

    with sum3:

        st.metric(
            "Completed Tasks",
            f"{completed_tasks}/{total_tasks}"
        )

    st.markdown("<br>", unsafe_allow_html=True)

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

    # ==========================================
    # FIX OLD PHASE DATA
    # ==========================================

    if "Task_Type" not in phase_df.columns:

        phase_df["Task_Type"] = "Main Task"

    if "Parent_Task" not in phase_df.columns:

        phase_df["Parent_Task"] = ""

    st.session_state.phase_data[
        phase_name
    ] = phase_df

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

         if st.session_state.is_admin:

            if st.button(
                "✏️",
                key=f"edit_btn_{phase_name}"
            ):

                st.session_state[edit_key] = not st.session_state[
                    edit_key
                ]

    with c3:

        if st.session_state.is_admin:

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
    # TABLE VIEW
    # =====================================================

    header_cols = st.columns(
        [1, 5, 2, 2, 2, 2, 2, 2, 1.5]
    )

    headers = [
        "S.No",
        "Task",
        "Status",
        "Priority",
        "Assignee",
        "Start",
        "End",
        "Actual End",
        "Progress"
    ]

    for col, head in zip(header_cols, headers):

        with col:

            st.markdown(
                f"""
                <div style="
                background:#172554;
                color:white;
                padding:12px;
                border-radius:8px;
                font-weight:bold;
                text-align:center;
                min-height:50px;
                display:flex;
                align-items:center;
                justify-content:center;
                ">
                {head}
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown(
        "<div style='height:10px'></div>",
        unsafe_allow_html=True
    )

    main_tasks = phase_df[
        phase_df["Task_Type"] == "Main Task"
    ]

    main_serial = 1

    for _, main_row in main_tasks.iterrows():

        # ==========================================
        # AUTO MAIN TASK PROGRESS
        # ==========================================

        sub_df_calc = phase_df[
            phase_df["Parent_Task"]
            == main_row["Task"]
        ]

        if len(sub_df_calc) > 0:

            try:

                avg_sub_progress = int(
                    sub_df_calc["Progress"]
                    .astype(int)
                    .mean()
                )

                phase_df.loc[
                    phase_df["Task"]
                    == main_row["Task"],
                    "Progress"
                ] = avg_sub_progress
                # ==========================================
                # AUTO MAIN TASK STATUS
                # ==========================================

                all_subtasks_done = (
                    sub_df_calc["Status"]
                    .astype(str)
                    .str.strip()
                    .eq("Done")
                    .all()
                )

                if all_subtasks_done:

                    main_status = "Done"

                else:

                    main_status = "Pending"

                phase_df.loc[
                    phase_df["Task"]
                    == main_row["Task"],
                    "Status"
                ] = main_status

                main_row["Status"] = main_status

                main_row["Progress"] = avg_sub_progress

                st.session_state.phase_data[
                    phase_name
                ] = phase_df
                # ==========================================
                # AUTO MAIN TASK ACTUAL END DATE
                # ==========================================

                try:

                    sub_actual_dates = pd.to_datetime(
                        sub_df_calc["Actual End Date"],
                        errors="coerce"
                    ).dropna()

                    if len(sub_actual_dates) > 0:

                        max_actual_date = (
                            sub_actual_dates.max()
                        )

                        phase_df.loc[
                            phase_df["Task"]
                            == main_row["Task"],
                            "Actual End Date"
                        ] = str(max_actual_date.date())

                        main_row[
                            "Actual End Date"
                        ] = str(max_actual_date.date())

                except:
                    pass

            except:
                pass

        task_id = main_row["Task_ID"]

        subtasks = phase_df[
            phase_df["Parent_Task"]
            == main_row["Task"]
        ]

        has_subtasks = len(subtasks) > 0

        expand_key = f"expand_{phase_name}_{task_id}"

        if expand_key not in st.session_state:

            st.session_state[expand_key] = False

        row_cols = st.columns(
            [1, 5, 2, 2, 2, 2, 2, 2, 1.5]
        )

        # ============================================
        # S.NO
        # ============================================

        with row_cols[0]:

            st.markdown(
                f"""
                <div style="
                padding-top:10px;
                color:white;
                text-align:center;
                font-size:16px;
                ">
                {main_serial}
                </div>
                """,
                unsafe_allow_html=True
            )

        # ============================================
        # TASK
        # ============================================

        with row_cols[1]:

            if has_subtasks:

                arrow = (
                    "▼"
                    if st.session_state[expand_key]
                    else "▶"
                )

                if st.button(
                    f"{arrow} {main_row['Task']}",
                    key=f"expand_btn_{phase_name}_{task_id}",
                    use_container_width=True
                ):

                    st.session_state[
                        expand_key
                    ] = not st.session_state[
                        expand_key
                    ]

                    st.rerun()

            else:

                st.markdown(
                    f"""
                    <div style="
                    padding-top:10px;
                    color:white;
                    ">
                    {main_row['Task']}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        # ============================================
        # STATUS
        # ============================================

        with row_cols[2]:

            st.markdown(
                f"""
                <div style="
                padding-top:10px;
                color:white;
                text-align:center;
                ">
                {main_row['Status']}
                </div>
                """,
                unsafe_allow_html=True
            )

        # ============================================
        # PRIORITY
        # ============================================

        with row_cols[3]:

            st.markdown(
                f"""
                <div style="
                padding-top:10px;
                color:white;
                text-align:center;
                ">
                {main_row['Priority']}
                </div>
                """,
                unsafe_allow_html=True
            )

        # ============================================
        # ASSIGNEE
        # ============================================

        with row_cols[4]:

            st.markdown(
                f"""
                <div style="
                padding-top:10px;
                color:white;
                text-align:center;
                ">
                {'' if pd.isna(main_row['Assignee']) else main_row['Assignee']}
                </div>
                """,
                unsafe_allow_html=True
            )

        # ============================================
        # START
        # ============================================

        with row_cols[5]:

            st.markdown(
                f"""
                <div style="
                padding-top:10px;
                color:white;
                text-align:center;
                ">
                {pd.to_datetime(main_row['Planned Start Date']).strftime('%Y-%m-%d')}
                </div>
                """,
                unsafe_allow_html=True
            )

        # ============================================
        # END
        # ============================================

        with row_cols[6]:

            st.markdown(
                f"""
                <div style="
                padding-top:10px;
                color:white;
                text-align:center;
                ">
                {pd.to_datetime(main_row['Planned End Date']).strftime('%Y-%m-%d')}
                </div>
                """,
                unsafe_allow_html=True
            )

        with row_cols[7]:

            st.markdown(
                f"""
                <div style="
                padding-top:10px;
                color:white;
                text-align:center;
                ">
                {'' if pd.isna(main_row['Actual End Date']) else pd.to_datetime(main_row['Actual End Date']).strftime('%Y-%m-%d')} 
                </div>
                """,
                unsafe_allow_html=True
            )

        # ============================================
        # PROGRESS
        # ============================================

        with row_cols[8]:

            st.markdown(
                f"""
                <div style="
                padding-top:10px;
                color:white;
                text-align:center;
                ">
                {main_row['Progress']}%
                </div>
                """,
                unsafe_allow_html=True
            )

        # ============================================
        # SUBTASKS
        # ============================================

        if (
            has_subtasks
            and st.session_state[expand_key]
        ):

            for _, sub_row in subtasks.iterrows():

                sub_cols = st.columns(
                    [1, 5, 2, 2, 2, 2, 2, 2, 1.5]
                )

                # BLANK S.NO

                with sub_cols[0]:

                    st.markdown(" ")

                # TASK

                with sub_cols[1]:

                    st.markdown(
                        f"""
                        <div style="
                        padding-top:10px;
                        padding-left:40px;
                        color:#bfdbfe;
                        ">
                        └── {sub_row['Task']}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                # STATUS

                with sub_cols[2]:

                    st.markdown(
                        f"""
                        <div style="
                        padding-top:10px;
                        color:#bfdbfe;
                        text-align:center;
                        ">
                        {sub_row['Status']}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                # PRIORITY

                with sub_cols[3]:

                    st.markdown(
                        f"""
                        <div style="
                        padding-top:10px;
                        color:#bfdbfe;
                        text-align:center;
                        ">
                        {sub_row['Priority']}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                # ASSIGNEE

                with sub_cols[4]:

                    st.markdown(
                        f"""
                        <div style="
                        padding-top:10px;
                        color:#bfdbfe;
                        text-align:center;
                        ">
                        {'' if pd.isna(sub_row['Assignee']) else sub_row['Assignee']}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                # START

                with sub_cols[5]:

                    st.markdown(
                        f"""
                        <div style="
                        padding-top:10px;
                        color:#bfdbfe;
                        text-align:center;
                        ">
                        {pd.to_datetime(sub_row['Planned Start Date']).strftime('%Y-%m-%d')}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                # END

                with sub_cols[6]:

                    st.markdown(
                        f"""
                        <div style="
                        padding-top:10px;
                        color:#bfdbfe;
                        text-align:center;
                        ">
                        {pd.to_datetime(sub_row['Planned End Date']).strftime('%Y-%m-%d')}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                # PROGRESS

                with sub_cols[7]:

                    st.markdown(
                        f"""
                        <div style="
                        padding-top:10px;
                        color:#bfdbfe;
                        text-align:center;
                        ">
                            {'' if pd.isna(sub_row.get('Actual End Date', '')) else pd.to_datetime(sub_row.get('Actual End Date', '')).strftime('%Y-%m-%d')}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                with sub_cols[8]:

                    st.markdown(
                        f"""
                        <div style="
                        padding-top:10px;
                        color:#bfdbfe;
                        text-align:center;
                        ">
                        {sub_row['Progress']}%
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

        st.markdown("---")

        main_serial += 1
    # =====================================================
    # EDIT PANEL
    # =====================================================

    if (
        st.session_state.is_admin
        and st.session_state[edit_key]
    ):

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

        # =================================================
        # TASK TYPE
        # =================================================

        task_type = st.selectbox(
            "Task Type",
            [
                "Main Task",
                "Sub Task"
            ],
            index=[
                "Main Task",
                "Sub Task"
            ].index(
                selected_row.get(
                    "Task_Type",
                    "Main Task"
                )
            ),
            key=f"task_type_{phase_name}_{selected_task}"
        )

        parent_task = ""

        if task_type == "Sub Task":

            main_task_list = list(

                phase_df[
                    phase_df["Task_Type"]
                    == "Main Task"
                ]["Task"]

            )

            if len(main_task_list) > 0:

                parent_task = st.selectbox(
                        "Parent Main Task",
                        main_task_list,
                        index=(
                            main_task_list.index(
                                selected_row.get(
                                    "Parent_Task",
                                    main_task_list[0]
                                )
                            )
                            if selected_row.get(
                                "Parent_Task",
                                ""
                            ) in main_task_list
                            else 0
                        )
                    )

            else:

                st.warning(
                    "Create a Main Task first."
                )
        if selected_task == "New Task":

            selected_row = {
                "Task": "",
                "Task_Type": "Main Task",
                "Status": "Pending",
                "Priority": "Medium",
                "Assignee": "",
                "Progress": 0
            }    
    
    
   
        # =================================================
        # TASK DETAILS
        # =================================================

        task_name = st.text_input(
        "Task Name",
        value=selected_row.get(
            "Task",
            ""
        ),
        key=f"task_name_{phase_name}_{selected_task}"
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
                ),
                key=f"status_{phase_name}_{selected_task}"
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
                ),
                key=f"priority_{phase_name}_{selected_task}"
            )

        with x3:

            assignee = st.text_input(
                "Assignee",
                value=selected_row.get(
                    "Assignee",
                    ""
                ),
                key=f"assignee_{phase_name}_{selected_task}"
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
                ),
                    key=f"planned_start_{phase_name}_{selected_task}"
            )

        with y2:

            planned_end = st.date_input(
                "Planned End Date",
                value=pd.to_datetime(
                    selected_row.get(
                        "Planned End Date",
                        str(date.today())
                    )
                ),
                key=f"planned_end_{phase_name}_{selected_task}"
            )

        
            # =====================================================
            # ACTUAL END DATE
            # =====================================================

        actual_end = ""

        if task_type == "Sub Task":

            existing_actual = str(
                selected_row.get(
                    "Actual End Date",
                    ""
                )
            ).strip()

            has_actual = st.checkbox(
                "Has Actual End Date?",
                value=(
                    existing_actual not in [
                        "",
                        "nan",
                        "NaT",
                        "None"
                    ]
                )
            )

            if has_actual:

                parsed_date = pd.to_datetime(
                    existing_actual,
                    errors="coerce"
                )

                actual_end = st.date_input(
                    "Actual End Date",
                    value=(
                        parsed_date.date()
                        if pd.notna(parsed_date)
                        else date.today()
                    ),
                    key=f"actual_end_{phase_name}_{selected_task}"
                )

        else:

            st.info(
                "Main Task Actual End Date is auto calculated from subtasks"
            )
                
        # =================================================
        # POSITION
        # =================================================

        position_options = ["Default (Last)"]

        for i in range(
            1,
            len(phase_df) + 2
        ):
            position_options.append(str(i))

        task_position = st.selectbox(
            "Task Position",
            position_options,
            key=f"task_position_{phase_name}"
        )
        

        # ==========================================
        # PROGRESS
        # ==========================================

        progress = int(
            selected_row.get("Progress", 0)
        )

        if task_type == "Sub Task":

            progress = st.slider(
                "Progress",
                0,
                100,
                int(selected_row.get("Progress", 0)),
            
            )

        else:

            st.info(
                "Main Task Progress is auto calculated from subtasks"
            )
        # =================================================
        # BUTTONS
        # =================================================
        if st.session_state.is_admin:
        
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

                            "Task_Type": task_type,

                            "Parent_Task": parent_task,

                            "Task": task_name,

                            "Status": status,

                            "Priority": priority,

                            "Assignee": assignee,

                            "Planned Start Date": str(planned_start),

                            "Planned End Date": str(planned_end),

                            "Actual End Date": (
                                str(actual_end)
                                if actual_end != ""
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

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )
    # =====================================================
    # TIMELINE
    # =====================================================

    st.markdown("### 📅 Timeline")

    try:

        timeline_df = phase_df[
            phase_df["Task_Type"]
            == "Main Task"
        ]

        if len(timeline_df) > 0:

            fig = go.Figure()

            task_names = []
            y_positions = []

            total_tasks = len(timeline_df)

            # =================================================
            # GLOBAL DATE COLLECTION
            # =================================================

            global_dates = []

            for _, row in timeline_df.iterrows():

                try:

                    task_name = row["Task"]

                    main_start = pd.to_datetime(
                        row["Planned Start Date"]
                    )

                    main_end = pd.to_datetime(
                        row["Planned End Date"]
                    )

                    global_dates.append(main_start)
                    global_dates.append(main_end)

                    subtasks_df = phase_df[

                        (
                            phase_df["Task_Type"]
                            == "Sub Task"
                        )

                        &

                        (
                            phase_df["Parent_Task"]
                            == task_name
                        )
                    ]

                    if len(subtasks_df) > 0:

                        for _, sub_row in subtasks_df.iterrows():

                            # START

                            try:

                                global_dates.append(
                                    pd.to_datetime(
                                        sub_row[
                                            "Planned Start Date"
                                        ]
                                    )
                                )

                            except:
                                pass

                            # END

                            try:

                                global_dates.append(
                                    pd.to_datetime(
                                        sub_row[
                                            "Planned End Date"
                                        ]
                                    )
                                )

                            except:
                                pass

                            # ACTUAL

                            sub_actual = str(
                                sub_row.get(
                                    "Actual End Date",
                                    ""
                                )
                            ).strip()

                            if (
                                sub_actual != ""
                                and sub_actual.lower() != "nan"
                            ):

                                try:

                                    global_dates.append(
                                        pd.to_datetime(
                                            sub_actual
                                        )
                                    )

                                except:
                                    pass

                except:
                    pass

            # =================================================
            # SMART DATE SCALE
            # =================================================

            min_date = min(global_dates)

            max_date = max(global_dates)

            total_days = max(
                1,
                (max_date - min_date).days
            )

            tick_gap = max(
                1,
                total_days // 7
            )

            tick_dates = pd.date_range(
                start=min_date,
                end=max_date,
                freq=f"{tick_gap}D"
            )

            # =================================================
            # TASK LOOP
            # =================================================

            for i, (_, row) in enumerate(
                timeline_df.iterrows()
            ):

                task_name = row["Task"]

                y_base = total_tasks - i

                task_names.append(task_name)

                y_positions.append(y_base)

                # =================================================
                # MAIN TASK DATES
                # =================================================

                main_start = pd.to_datetime(
                    row["Planned Start Date"]
                )

                main_end = pd.to_datetime(
                    row["Planned End Date"]
                )

                # =================================================
                # SUBTASKS
                # =================================================

                subtasks_df = phase_df[

                    (
                        phase_df["Task_Type"]
                        == "Sub Task"
                    )

                    &

                    (
                        phase_df["Parent_Task"]
                        == task_name
                    )
                ]

                # =================================================
                # DATE COLLECTION
                # =================================================

                all_start_dates = [main_start]

                all_end_dates = [main_end]

                actual_dates = []

                # MAIN ACTUAL

                main_actual = str(
                    row.get(
                        "Actual End Date",
                        ""
                    )
                ).strip()

                if (
                    main_actual != ""
                    and main_actual.lower() != "nan"
                ):

                    try:

                        actual_dates.append(
                            pd.to_datetime(
                                main_actual
                            )
                        )

                    except:
                        pass

                # =================================================
                # SUBTASK DATE COLLECTION
                # =================================================

                if len(subtasks_df) > 0:

                    for _, sub_row in subtasks_df.iterrows():

                        # START

                        try:

                            sub_start = pd.to_datetime(
                                sub_row[
                                    "Planned Start Date"
                                ]
                            )

                            all_start_dates.append(
                                sub_start
                            )

                        except:
                            pass

                        # END

                        try:

                            sub_end = pd.to_datetime(
                                sub_row[
                                    "Planned End Date"
                                ]
                            )

                            all_end_dates.append(
                                sub_end
                            )

                        except:
                            pass

                        # ACTUAL

                        sub_actual = str(
                            sub_row.get(
                                "Actual End Date",
                                ""
                            )
                        ).strip()

                        if (
                            sub_actual != ""
                            and sub_actual.lower() != "nan"
                        ):

                            try:

                                actual_dates.append(
                                    pd.to_datetime(
                                        sub_actual
                                    )
                                )

                            except:
                                pass

                # =================================================
                # FINAL CALCULATED DATES
                # =================================================

                planned_start = min(
                    all_start_dates
                )

                planned_end = max(
                    all_end_dates
                )

                # PREVENT ZERO DAY LINE

                if planned_end <= planned_start:

                    planned_end = (
                        planned_start
                        + pd.Timedelta(days=1)
                    )

                # =================================================
                # PLANNED LINE
                # =================================================

                fig.add_trace(

                    go.Scatter(

                        x=[
                            planned_start,
                            planned_end
                        ],

                        y=[
                            y_base - 0.01,
                            y_base - 0.01
                        ],

                        mode="lines",

                        line=dict(
                            color="#facc15",
                            width=10
                        ),

                        name="Planned",

                        showlegend=(i == 0),

                        hovertemplate=
                        (
                            f"<b>{task_name}</b><br>"
                            f"Planned:<br>"
                            f"{planned_start.date()}"
                            f" → "
                            f"{planned_end.date()}"
                            "<extra></extra>"
                        )
                    )
                )

                # =================================================
                # ACTUAL LINE
                # =================================================

                if len(actual_dates) > 0:

                    actual_end = max(
                        actual_dates
                    )

                    if actual_end <= planned_start:

                        actual_end = (
                            planned_start
                            + pd.Timedelta(days=1)
                        )

                    fig.add_trace(

                        go.Scatter(

                            x=[
                                planned_start,
                                actual_end
                            ],

                            y=[
                                y_base - 0.033,
                                y_base - 0.033
                            ],

                            mode="lines",

                            line=dict(
                                color="#ff4d4f",
                                width=10
                            ),

                            name="Actual",

                            showlegend=(i == 0),

                            hovertemplate=
                            (
                                f"<b>{task_name}</b><br>"
                                f"Actual:<br>"
                                f"{planned_start.date()}"
                                f" → "
                                f"{actual_end.date()}"
                                "<extra></extra>"
                            )
                        )
                    )

            # =================================================
            # LAYOUT
            # =================================================

            fig.update_layout(

                height=max(
                    260,
                    total_tasks * 90
                ),

                paper_bgcolor="#0f172a",

                plot_bgcolor="#0b1220",

                font=dict(
                    color="white",
                    size=13
                ),

                margin=dict(
                    l=45,
                    r=20,
                    t=20,
                    b=20
                ),

                legend=dict(

                    orientation="h",

                    yanchor="top",

                    y=1.12,

                    xanchor="right",

                    x=0.98,

                    bgcolor="rgba(0,0,0,0)",

                    font=dict(
                        size=13,
                        color="#f8fafc"
                    )
                ),

                xaxis=dict(

                    showgrid=True,

                    gridcolor=
                    "rgba(255,255,255,0.08)",

                    tickvals=tick_dates,

                    tickformat="%b %d",

                    zeroline=False,

                    color="#ffffff",

                    tickfont=dict(
                        color="#ffffff",
                        size=12
                    )
                ),

                yaxis=dict(

                    tickmode="array",

                    tickvals=y_positions,

                    ticktext=task_names,

                    showgrid=False,

                    automargin=True,

                    tickfont=dict(
                        color="#ffffff",
                        size=13
                    ),

                    color="#ffffff",

                    range=[
                        0.7,
                        total_tasks + 0.3
                    ],

                    fixedrange=True
                )
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={
                    "displayModeBar": False
                }
            )

    except Exception as e:

        st.warning(
            f"Timeline Error: {e}"
        )
    # =========================================================
    # FOOTER
    # =========================================================

    st.markdown("---")

    st.caption(
        "Enterprise PMO Dashboard"
    )

