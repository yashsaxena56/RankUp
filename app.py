mport streamlit as st
import html
from datetime import date
from supabase import create_client, Client

# =========================================================
# PAGE CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="RankUp | JEE Prep Portal",
    page_icon="🚀",
    layout="wide"
)

# =========================================================
# SESSION STATE
# =========================================================
defaults = {
    "theme_mode": "Dark",
    "access_token": None,
    "refresh_token": None,
    "user": None,
    "answers": {},
    "quiz_submitted": False,
    "study_hours": 6.0,
    "flash_message": None,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# SUPABASE CONNECTION
# =========================================================
def get_supabase_client() -> Client:
    return create_client(
        st.secrets["SUPABASE_URL"].strip(),
        st.secrets["SUPABASE_KEY"].strip()
    )


try:
    supabase = get_supabase_client()
except Exception as e:
    st.error("Supabase connection could not be initialized.")
    st.caption(str(e))
    st.stop()


# =========================================================
# RESTORE AUTH SESSION
# =========================================================
if st.session_state.access_token and st.session_state.refresh_token:
    try:
        supabase.auth.set_session(
            st.session_state.access_token,
            st.session_state.refresh_token
        )

        response = supabase.auth.get_user()
        st.session_state.user = response.user

        current_session = supabase.auth.get_session()

        if current_session:
            st.session_state.access_token = current_session.access_token
            st.session_state.refresh_token = current_session.refresh_token

    except Exception:
        st.session_state.access_token = None
        st.session_state.refresh_token = None
        st.session_state.user = None


# =========================================================
# THEME
# =========================================================
theme = st.session_state.theme_mode

if theme == "Dark":
    page_bg = "#090d1b"
    panel_bg = "#171f3b"
    sidebar_bg = "#10162a"
    text_color = "#eef1ff"
    muted_color = "#98a7cf"
    border_color = "#29365c"
    metric_bg = "linear-gradient(145deg,#171f3b,#11182d)"
else:
    page_bg = "#f4f6fc"
    panel_bg = "#ffffff"
    sidebar_bg = "#e9edfa"
    text_color = "#17213d"
    muted_color = "#5c6885"
    border_color = "#d8def0"
    metric_bg = "linear-gradient(145deg,#ffffff,#f7f8ff)"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
}}

.stApp {{
    background: {page_bg};
    color: {text_color};
}}

section[data-testid="stSidebar"] {{
    background: {sidebar_bg};
    border-right: 1px solid {border_color};
}}

section[data-testid="stSidebar"] * {{
    color: {text_color} !important;
}}

h1, h2, h3 {{
    color: {text_color} !important;
}}

p, label, span {{
    color: {muted_color};
}}

div[data-testid="stMetric"] {{
    background: {metric_bg};
    border: 1px solid {border_color};
    padding: 16px;
    border-radius: 16px;
}}

div[data-testid="stMetric"] label {{
    color: {muted_color} !important;
}}

div[data-testid="stMetric"] [data-testid="stMetricValue"] {{
    color: {text_color} !important;
}}

div.stButton > button {{
    border-radius: 10px;
    border: 1px solid #6859e8;
    background: linear-gradient(100deg,#6557e8,#3d78e8);
    color: white;
    font-weight: 700;
}}

div.stButton > button:hover {{
    border-color: #a99fff;
    color: white;
}}

.card {{
    background: {panel_bg};
    border: 1px solid {border_color};
    border-radius: 16px;
    padding: 18px 20px;
    margin-bottom: 12px;
}}

.muted {{
    color: {muted_color};
    font-size: 0.9rem;
}}

.pill {{
    display: inline-block;
    background: #25214d;
    color: #b9b0ff;
    border: 1px solid #5145a8;
    padding: 4px 10px;
    border-radius: 30px;
    font-size: 12px;
}}

.big-number {{
    font-size: 28px;
    font-weight: 800;
    color: {text_color};
}}

hr {{
    border-color: {border_color};
}}

[data-testid="stSelectbox"] label,
[data-testid="stNumberInput"] label,
[data-testid="stTextInput"] label {{
    color: {text_color} !important;
}}
</style>
""", unsafe_allow_html=True)


# =========================================================
# AUTHENTICATION SCREEN
# =========================================================
if not st.session_state.user:

    st.markdown("<br>", unsafe_allow_html=True)
    left, center, right = st.columns([1, 1.4, 1])

    with center:
        st.markdown(
            "<h1 style='text-align:center'>🚀 RankUp</h1>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<p style='text-align:center'>YOUR JEE PREPARATION COMPANION</p>",
            unsafe_allow_html=True
        )
        st.markdown("---")

        login_tab, signup_tab = st.tabs(["Login", "Create Account"])

        with login_tab:
            st.subheader("Welcome back!")

            with st.form("login_form"):
                login_email = st.text_input(
                    "Email address",
                    placeholder="you@example.com"
                )
                login_password = st.text_input(
                    "Password",
                    type="password"
                )
                login_submit = st.form_submit_button(
                    "Login to RankUp",
                    use_container_width=True
                )

            if login_submit:
                if not login_email.strip() or not login_password:
                    st.warning("Please enter your email and password.")
                else:
                    try:
                        response = supabase.auth.sign_in_with_password({
                            "email": login_email.strip(),
                            "password": login_password
                        })

                        if response.session:
                            st.session_state.access_token = response.session.access_token
                            st.session_state.refresh_token = response.session.refresh_token
                            st.session_state.user = response.user
                            st.success("Login successful!")
                            st.rerun()
                        else:
                            st.error("Login session could not be created.")

                    except Exception as e:
                        st.error("Login failed.")
                        st.caption(str(e))

        with signup_tab:
            st.subheader("Create your student account")

            with st.form("signup_form"):
                full_name = st.text_input(
                    "Full name",
                    placeholder="Your name"
                )
                signup_email = st.text_input(
                    "Email address",
                    placeholder="you@example.com"
                )
                signup_password = st.text_input(
                    "Create password",
                    type="password"
                )
                confirm_password = st.text_input(
                    "Confirm password",
                    type="password"
                )

                signup_submit = st.form_submit_button(
                    "Create RankUp Account",
                    use_container_width=True
                )

            if signup_submit:
                if not full_name.strip() or not signup_email.strip():
                    st.warning("Please fill in your name and email.")
                elif len(signup_password) < 6:
                    st.warning("Password must contain at least 6 characters.")
                elif signup_password != confirm_password:
                    st.warning("Passwords do not match.")
                else:
                    try:
                        response = supabase.auth.sign_up({
                            "email": signup_email.strip(),
                            "password": signup_password,
                            "options": {
                                "data": {
                                    "full_name": full_name.strip()
                                }
                            }
                        })

                        if response.user and response.session:
                            st.session_state.access_token = response.session.access_token
                            st.session_state.refresh_token = response.session.refresh_token
                            st.session_state.user = response.user
                            st.success("Account created successfully!")
                            st.rerun()

                        elif response.user:
                            st.success(
                                "Account created. Please log in to continue."
                            )
                        else:
                            st.error("Account could not be created.")

                    except Exception as e:
                        st.error("Signup failed.")
                        st.caption(str(e))

        st.markdown("---")
        st.caption("RankUp · Built for JEE aspirants")

    st.stop()


# =========================================================
# LOGGED-IN USER AND PROFILE
# =========================================================
user = st.session_state.user
user_id = str(user.id)
user_metadata = user.user_metadata or {}

try:
    profile_response = (
        supabase.table("profiles")
        .select("*")
        .eq("id", user_id)
        .execute()
    )

    if not profile_response.data:
        st.error("Your student profile was not found.")
        st.info(
            "Please check the profile creation trigger in Supabase."
        )
        st.stop()

    profile = profile_response.data[0]

except Exception as e:
    st.error("Could not load your student profile.")
    st.caption(str(e))
    st.stop()

student_name = (
    profile.get("full_name")
    or user_metadata.get("full_name")
    or user.email
)


# =========================================================
# DATABASE FUNCTIONS
# =========================================================
def load_tasks():
    response = (
        supabase.table("study_tasks")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=False)
        .execute()
    )
    return response.data or []


def save_task_status(task_id, widget_key, sync_key):
    new_status = (
        "Completed"
        if st.session_state.get(widget_key, False)
        else "Pending"
    )

    try:
        result = (
            supabase.table("study_tasks")
            .update({"status": new_status})
            .eq("id", task_id)
            .eq("user_id", user_id)
            .select("id")
            .execute()
        )

        if not result.data:
            raise Exception("Task update was not confirmed.")

        st.session_state[sync_key] = new_status
        st.session_state["task_error"] = None

    except Exception as e:
        st.session_state[sync_key] = None
        st.session_state["task_error"] = str(e)


def get_task_checkbox_keys(task, section):
    task_id = str(task["id"])
    db_status = task.get("status", "Pending")

    widget_key = f"{section}_task_{task_id}"
    sync_key = f"{section}_sync_{task_id}"

    if (
        widget_key not in st.session_state
        or st.session_state.get(sync_key) != db_status
    ):
        st.session_state[widget_key] = db_status == "Completed"
        st.session_state[sync_key] = db_status

    return widget_key, sync_key


def send_friend_request(receiver_id):
    existing_outgoing = (
        supabase.table("friend_requests")
        .select("id,status")
        .eq("sender_id", user_id)
        .eq("receiver_id", receiver_id)
        .execute()
    )

    existing_incoming = (
        supabase.table("friend_requests")
        .select("id,status")
        .eq("sender_id", receiver_id)
        .eq("receiver_id", user_id)
        .execute()
    )

    if existing_outgoing.data or existing_incoming.data:
        return False, "A request or friendship already exists."

    supabase.table("friend_requests").insert({
        "sender_id": user_id,
        "receiver_id": receiver_id,
        "status": "pending"
    }).execute()

    return True, "Friend request sent successfully!"


def get_pending_requests():
    response = supabase.rpc(
        "get_pending_friend_requests"
    ).execute()
    return response.data or []


def get_friends():
    response = supabase.rpc("get_my_friends").execute()
    return response.data or []


def respond_to_friend_request(request_id, status):
    response = (
        supabase.table("friend_requests")
        .update({"status": status})
        .eq("id", request_id)
        .eq("receiver_id", user_id)
        .eq("status", "pending")
        .select("id")
        .execute()
    )
    return bool(response.data)


# =========================================================
# LOAD TASKS
# =========================================================
try:
    tasks = load_tasks()
except Exception as e:
    st.error("Could not load study tasks.")
    st.caption(str(e))
    st.stop()

completed_count = sum(
    1 for task in tasks if task.get("status") == "Completed"
)
pending_count = len(tasks) - completed_count

pending_hours = sum(
    float(task.get("estimated_hours") or 0)
    for task in tasks
    if task.get("status") != "Completed"
)

completion_ratio = (
    completed_count / len(tasks) if tasks else 0
)

if st.session_state.get("flash_message"):
    st.success(st.session_state.pop("flash_message"))

if st.session_state.get("task_error"):
    st.error("Task update failed: " + st.session_state["task_error"])


# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.markdown("## 🚀 RankUp")
    st.caption("YOUR JEE PREPARATION COMPANION")
    st.markdown("---")

    page = st.radio(
        "NAVIGATION",
        [
            "Overview",
            "Smart Scheduler",
            "PYQ Vault",
            "Quiz Arena",
            "Friends Zone",
            "Profile"
        ]
    )

    st.markdown("---")

    # Profile picture and student details
    avatar_url = profile.get("avatar_url")

    safe_name = html.escape(str(student_name or "RankUp Student"))
    safe_email = html.escape(str(user.email or ""))

    if avatar_url:
        safe_avatar_url = html.escape(str(avatar_url), quote=True)
        avatar_html = (
            f'<img src="{safe_avatar_url}" '
            'style="width:54px;height:54px;min-width:54px;'
            'border-radius:50%;object-fit:cover;'
            'border:2px solid #6859e8;display:block;">'
        )
    else:
        initials = "".join(
            part[0] for part in str(student_name or "RankUp").split()[:2]
        ).upper() or "RU"
        avatar_html = (
            '<div style="width:54px;height:54px;min-width:54px;'
            'border-radius:50%;display:flex;align-items:center;'
            'justify-content:center;background:#29245d;color:white;'
            'font-size:19px;font-weight:800;'
            'border:2px solid #6859e8;">'
            f'{html.escape(initials)}</div>'
        )

    # Keep HTML on a single line so Markdown cannot mistake it for a code block.
    profile_card_html = (
        '<div style="display:flex;align-items:center;gap:12px;'
        'padding:8px 2px 12px 2px;">'
        f'{avatar_html}'
        '<div style="min-width:0;overflow:hidden;">'
        f'<div style="font-size:14px;font-weight:700;color:{text_color};'
        'white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">'
        f'{safe_name}</div>'
        f'<div style="font-size:11px;color:{muted_color};'
        'white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">'
        f'{safe_email}</div></div></div>'
    )

    st.markdown(profile_card_html, unsafe_allow_html=True)

    st.progress(
        completion_ratio,
        text=f"Task completion · {completed_count}/{len(tasks)}"
    )

    if st.button("Logout", use_container_width=True):
        try:
            supabase.auth.sign_out()
        except Exception:
            pass

        st.session_state.access_token = None
        st.session_state.refresh_token = None
        st.session_state.user = None
        st.rerun()

# =========================================================
# HEADER
# =========================================================
header_left, header_right = st.columns([0.78, 0.22])

with header_left:
    st.markdown(
        f"<div class='muted'>{date.today().strftime('%A, %d %B %Y').upper()}</div>",
        unsafe_allow_html=True
    )
    st.title("Let's make today count. ✨")
    st.markdown(
        "<span class='pill'>JEE MAIN + ADVANCED</span> "
        "&nbsp; "
        "<span class='pill'>YOUR PERSONAL STUDY SPACE</span>",
        unsafe_allow_html=True
    )

with header_right:
    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

    selected_theme = st.selectbox(
        "Appearance",
        ["Dark", "Light"],
        index=0 if st.session_state.theme_mode == "Dark" else 1
    )

    if selected_theme != st.session_state.theme_mode:
        st.session_state.theme_mode = selected_theme
        st.rerun()


# =========================================================
# OVERVIEW
# =========================================================
if page == "Overview":

    st.markdown("### Your preparation at a glance")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Study tasks", len(tasks))
    c2.metric("Completed tasks", completed_count)
    c3.metric("Pending hours", f"{pending_hours:.1f} hrs")
    c4.metric("Task completion", f"{completion_ratio * 100:.0f}%")

    left, right = st.columns([1.45, 1])

    with left:
        st.markdown(
            """
            <div class='card'>
                <h3>📚 Your study tasks</h3>
                <p class='muted'>Your personal tasks saved in the cloud.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        if not tasks:
            st.info(
                "No study tasks yet. Open Smart Scheduler to add your first chapter."
            )

        for task in tasks:
            cols = st.columns([0.12, 0.68, 0.20])

            widget_key, sync_key = get_task_checkbox_keys(
                task, "overview"
            )

            cols[0].checkbox(
                " ",
                key=widget_key,
                on_change=save_task_status,
                args=(task["id"], widget_key, sync_key)
            )

            cols[1].markdown(f"**{task['title']}**")
            cols[1].caption(
                f"{task.get('subject') or 'General'} · "
                f"{task.get('priority') or 'Medium'} priority"
            )

            cols[2].markdown(
                f"**{float(task.get('estimated_hours') or 0):g} hrs**"
            )

        st.progress(
            completion_ratio,
            text=f"{completed_count} of {len(tasks)} tasks completed"
        )

    with right:
        st.markdown(
            f"""
            <div class='card'>
                <h3>🎯 Your task progress</h3>
                <p class='muted'>Based on your saved study tasks</p>
                <div class='big-number'>{completion_ratio * 100:.0f}%</div>
                <p class='muted'>
                    {completed_count} completed · {pending_count} pending
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <div class='card'>
                <h3>⚡ Quick action</h3>
                <p class='muted'>Jump into a focused practice session.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button("Start a 10-question quiz", use_container_width=True):
            st.info("Open Quiz Arena from the sidebar to begin.")


# =========================================================
# SMART SCHEDULER
# =========================================================
elif page == "Smart Scheduler":

    st.markdown("### 🧠 Self-Healing Scheduler")

    st.write(
        "Apna available time aur pending chapters add karo. "
        "RankUp estimated study plan calculate karega."
    )

    a, b = st.columns(2)

    with a:
        available = st.number_input(
            "Daily available study hours",
            min_value=1.0,
            max_value=16.0,
            value=float(st.session_state.study_hours),
            step=0.5
        )

        target_days = st.number_input(
            "Target days to clear backlog",
            min_value=1,
            max_value=90,
            value=7
        )

    with b:
        st.markdown(
            """
            <div class='card'>
                <h3>How it works</h3>
                <p class='muted'>
                    Pending hours are divided across your target days.
                    This is a planning estimate, not an automatic calendar sync.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.session_state.study_hours = available

    st.markdown("#### Add your backlog")

    with st.form("backlog_form", clear_on_submit=True):
        chapter = st.text_input(
            "Chapter / topic",
            placeholder="e.g. Laws of Motion"
        )

        subject = st.selectbox(
            "Subject",
            ["Physics", "Chemistry", "Mathematics", "Other"]
        )

        hours = st.number_input(
            "Estimated hours",
            min_value=0.5,
            max_value=100.0,
            value=2.0,
            step=0.5
        )

        priority = st.selectbox(
            "Priority",
            ["Low", "Medium", "High"],
            index=1
        )

        add = st.form_submit_button("＋ Add chapter")

        if add:
            if not chapter.strip():
                st.warning("Please enter a chapter or topic.")
            else:
                try:
                    result = supabase.table("study_tasks").insert({
                        "user_id": user_id,
                        "title": chapter.strip(),
                        "subject": subject,
                        "estimated_hours": float(hours),
                        "priority": priority,
                        "status": "Pending"
                    }).execute()

                    if result.data:
                        st.session_state["flash_message"] = (
                            f"Added successfully: {chapter.strip()}"
                        )
                        st.rerun()
                    else:
                        st.error("Task could not be saved.")

                except Exception as e:
                    st.error("Could not add task to Supabase.")
                    st.caption(str(e))

    pending = sum(
        float(task.get("estimated_hours") or 0)
        for task in tasks
        if task.get("status") != "Completed"
    )

    daily = pending / target_days

    st.markdown("---")
    x, y, z = st.columns(3)
    x.metric("Pending backlog", f"{pending:.1f} hrs")
    y.metric("Target duration", f"{target_days} days")
    z.metric("Suggested daily load", f"{daily:.1f} hrs/day")

    if daily > available:
        st.warning(
            f"Backlog needs {daily:.1f} hrs/day, above your "
            f"available {available:.1f} hrs. Increase target days or reduce backlog."
        )
    else:
        st.success("Your backlog fits within your available daily study time.")

    st.markdown("#### Your current task list")

    if not tasks:
        st.info("No tasks added yet.")

    for task in tasks:
        cc = st.columns([0.08, 0.54, 0.14, 0.14, 0.10])

        widget_key, sync_key = get_task_checkbox_keys(
            task, "scheduler"
        )

        cc[0].checkbox(
            " ",
            key=widget_key,
            on_change=save_task_status,
            args=(task["id"], widget_key, sync_key)
        )

        cc[1].write(task["title"])
        cc[1].caption(
            f"{task.get('subject') or 'General'} · "
            f"{task.get('priority') or 'Medium'} priority"
        )

        cc[2].write(
            f"{float(task.get('estimated_hours') or 0):g} h"
        )
        cc[3].write(task.get("status", "Pending"))

        if cc[4].button("✕", key=f"remove_{task['id']}"):
            try:
                result = (
                    supabase.table("study_tasks")
                    .delete()
                    .eq("id", task["id"])
                    .eq("user_id", user_id)
                    .select("id")
                    .execute()
                )

                if result.data:
                    st.session_state["flash_message"] = "Task deleted successfully."
                    st.rerun()
                else:
                    st.error("Task could not be deleted.")

            except Exception as e:
                st.error("Could not delete task.")
                st.caption(str(e))


# =========================================================
# PYQ VAULT
# =========================================================
elif page == "PYQ Vault":

    st.markdown("### 📖 Interactive PYQ Vault")
    st.write("Subject aur topic select karke practice set explore karo.")

    subject = st.selectbox(
        "Choose subject",
        ["Physics", "Chemistry", "Mathematics"]
    )

    topics = {
        "Physics": [
            "Units & Dimensions",
            "Kinematics",
            "Laws of Motion"
        ],
        "Chemistry": [
            "Atomic Structure",
            "Chemical Bonding",
            "Mole Concept"
        ],
        "Mathematics": [
            "Quadratic Equations",
            "Limits",
            "Straight Lines"
        ]
    }

    topic = st.selectbox("Choose chapter", topics[subject])

    st.markdown(
        "<div class='card'>"
        "<span class='pill'>PRACTICE SET</span>"
        f"<h3>{subject} · {topic}</h3>"
        "<p class='muted'>A focused practice area for chapter-wise JEE preparation.</p>"
        "<p>Question bank integration is the next phase. Try the sample quiz in Quiz Arena.</p>"
        "</div>",
        unsafe_allow_html=True
    )

    if st.button("Open sample quiz"):
        st.info("Select Quiz Arena in the sidebar to attempt the sample questions.")


# =========================================================
# QUIZ ARENA
# =========================================================
elif page == "Quiz Arena":

    st.markdown("### ⚔️ Quiz Arena")
    st.write("Sample practice quiz · 5 questions · Instant evaluation")

    questions = [
        (
            "Physics",
            "The dimensional formula of force is:",
            ["MLT⁻²", "ML²T⁻²", "MLT⁻¹", "M⁰LT⁻²"],
            0
        ),
        (
            "Chemistry",
            "The maximum number of electrons in the 2nd shell is:",
            ["2", "8", "18", "32"],
            1
        ),
        (
            "Mathematics",
            "The roots of x² − 5x + 6 = 0 are:",
            ["1, 6", "−2, −3", "2, 3", "−1, −6"],
            2
        ),
        (
            "Physics",
            "The SI unit of work is:",
            ["Newton", "Watt", "Joule", "Pascal"],
            2
        ),
        (
            "Chemistry",
            "Atomic number is equal to the number of:",
            ["Neutrons", "Protons", "Nucleons", "Shells"],
            1
        ),
    ]

    with st.form("quiz_form"):
        for i, (sub, question, options, correct) in enumerate(questions):
            st.markdown(f"**Q{i+1}. [{sub}] {question}**")

            selected = st.radio(
                "Select one",
                options,
                key=f"q_{i}",
                index=None,
                label_visibility="collapsed"
            )

            st.session_state.answers[i] = selected

        submit = st.form_submit_button("Submit answers")

    if submit:
        st.session_state.quiz_submitted = True

        st.session_state.quiz_score = sum(
            1
            for i, (_, _, options, correct) in enumerate(questions)
            if st.session_state.answers.get(i) == options[correct]
        )

    if st.session_state.quiz_submitted:
        score = st.session_state.get("quiz_score", 0)

        st.success(f"You scored {score}/5 · Accuracy: {score * 20}%")

        for i, (sub, question, options, correct) in enumerate(questions):
            chosen = st.session_state.answers.get(i)

            if chosen == options[correct]:
                st.markdown(f"✅ Q{i+1}: Correct")
            else:
                st.markdown(
                    f"❌ Q{i+1}: Correct answer — **{options[correct]}**"
                )

        if st.button("Try again"):
            st.session_state.answers = {}
            st.session_state.quiz_submitted = False

            for i in range(len(questions)):
                key = f"q_{i}"
                if key in st.session_state:
                    del st.session_state[key]

            st.rerun()


# =========================================================
# FRIENDS ZONE
# =========================================================
elif page == "Friends Zone":

    st.markdown("### 🏆 Friends Zone")
    st.write(
        "Connect with other RankUp students using their unique Friend Code."
    )

    st.markdown("#### Add a friend")

    with st.form("friend_search_form"):
        friend_code_input = st.text_input(
            "Enter Friend Code",
            placeholder="e.g. A1B2C3D4"
        ).strip().upper()

        search_friend = st.form_submit_button("Search student")

    if search_friend:
        if not friend_code_input:
            st.warning("Please enter a Friend Code.")
        else:
            try:
                result = supabase.rpc(
                    "search_student_by_code",
                    {"p_friend_code": friend_code_input}
                ).execute()

                matches = result.data or []

                if not matches:
                    st.warning("No student found with this Friend Code.")
                else:
                    found = matches[0]

                    st.session_state["found_friend"] = found

            except Exception as e:
                st.error("Could not search for this student.")
                st.caption(str(e))

    found = st.session_state.get("found_friend")

    if found:
        st.markdown("---")
        st.markdown("#### Student found")

        st.markdown(f"**{found.get('full_name') or 'RankUp Student'}**")
        st.caption(
            f"{found.get('target_exam') or 'JEE'} · "
            f"Friend Code: {found.get('friend_code')}"
        )

        if found.get("study_goal"):
            st.write(f"Goal: {found['study_goal']}")

        if st.button("＋ Send Friend Request", key="send_friend_request"):
            try:
                ok, message = send_friend_request(found["id"])

                if ok:
                    st.success(message)
                else:
                    st.info(message)

            except Exception as e:
                st.error("Could not send friend request.")
                st.caption(str(e))

    st.markdown("---")
    st.markdown("#### Incoming friend requests")

    try:
        incoming_requests = get_pending_requests()

        if not incoming_requests:
            st.info("You don't have any pending friend requests.")

        for request in incoming_requests:
            with st.container(border=True):
                st.markdown(
                    f"**{request.get('full_name') or 'RankUp Student'}**"
                )
                st.caption(
                    f"{request.get('target_exam') or 'JEE'} · "
                    f"Code: {request.get('friend_code')}"
                )

                accept_col, reject_col = st.columns(2)

                if accept_col.button(
                    "Accept",
                    key=f"accept_{request['request_id']}"
                ):
                    if respond_to_friend_request(
                        request["request_id"], "accepted"
                    ):
                        st.session_state["flash_message"] = (
                            "Friend request accepted!"
                        )
                        st.rerun()
                    else:
                        st.error("Request could not be accepted.")

                if reject_col.button(
                    "Reject",
                    key=f"reject_{request['request_id']}"
                ):
                    if respond_to_friend_request(
                        request["request_id"], "rejected"
                    ):
                        st.session_state["flash_message"] = (
                            "Friend request rejected."
                        )
                        st.rerun()
                    else:
                        st.error("Request could not be rejected.")

    except Exception as e:
        st.error("Could not load incoming requests.")
        st.caption(str(e))

    st.markdown("---")
    st.markdown("#### My friends")

    try:
        friends = get_friends()

        if not friends:
            st.info(
                "No friends connected yet. Search using a Friend Code "
                "to connect with another student."
            )

        for friend in friends:
            with st.container(border=True):
                st.markdown(
                    f"**{friend.get('full_name') or 'RankUp Student'}**"
                )
                st.caption(
                    f"{friend.get('target_exam') or 'JEE'} · "
                    f"Friend Code: {friend.get('friend_code')}"
                )

                if friend.get("study_goal"):
                    st.write(f"Goal: {friend['study_goal']}")

    except Exception as e:
        st.error("Could not load your friends.")
        st.caption(str(e))


# =========================================================
# PROFILE
# =========================================================
elif page == "Profile":

    st.markdown("### 👤 My Profile")
    st.write("Manage your personal details and JEE preparation goals.")

    current_name = profile.get("full_name") or student_name
    current_mobile = profile.get("mobile_number") or ""
    current_goal = profile.get("study_goal") or ""
    current_exam = profile.get("target_exam") or "JEE"
    current_avatar = profile.get("avatar_url")
    current_code = profile.get("friend_code") or "Not assigned"

    left, right = st.columns([1, 1.5])

    with left:
        st.markdown("#### Profile photo")

        if current_avatar:
            st.image(current_avatar, width=180)
        else:
            st.markdown("### 📷")
            st.caption("No profile photo uploaded yet.")

        uploaded_photo = st.file_uploader(
            "Choose profile photo",
            type=["png", "jpg", "jpeg"],
            key="profile_photo"
        )

        if uploaded_photo:
            st.image(uploaded_photo, width=180)

            if st.button("Upload profile photo"):
                try:
                    extension = uploaded_photo.name.rsplit(".", 1)[-1].lower()
                    file_path = f"{user_id}/avatar.{extension}"

                    upload_result = supabase.storage.from_(
                        "rankup-avatars"
                    ).upload(
                        file_path,
                        uploaded_photo.getvalue(),
                        {
                            "content-type": uploaded_photo.type,
                            "upsert": "true"
                        }
                    )

                    public_url = supabase.storage.from_(
                        "rankup-avatars"
                    ).get_public_url(file_path)

                    supabase.table("profiles").update({
                        "avatar_url": public_url
                    }).eq("id", user_id).execute()

                    st.session_state["flash_message"] = (
                        "Profile photo updated successfully!"
                    )
                    st.rerun()

                except Exception as e:
                    st.error("Photo upload failed.")
                    st.caption(str(e))

    with right:
        st.markdown("#### Personal information")

        with st.form("profile_update_form"):
            updated_name = st.text_input(
                "Full name",
                value=current_name
            )

            st.text_input(
                "Email address",
                value=user.email or "",
                disabled=True
            )

            updated_mobile = st.text_input(
                "Mobile number",
                value=current_mobile,
                placeholder="Enter your mobile number"
            )

            updated_exam = st.selectbox(
                "Target exam",
                ["JEE Main", "JEE Advanced", "JEE Main + Advanced"],
                index=(
                    ["JEE Main", "JEE Advanced", "JEE Main + Advanced"].index(
                        current_exam
                    )
                    if current_exam in [
                        "JEE Main",
                        "JEE Advanced",
                        "JEE Main + Advanced"
                    ]
                    else 2
                )
            )

            updated_goal = st.text_area(
                "Your study goal",
                value=current_goal,
                placeholder="e.g. Target IIT Delhi CSE in JEE Advanced 2027"
            )

            save_profile = st.form_submit_button(
                "Save Profile",
                use_container_width=True
            )

        if save_profile:
            if not updated_name.strip():
                st.warning("Name cannot be empty.")
            else:
                try:
                    supabase.table("profiles").update({
                        "full_name": updated_name.strip(),
                        "mobile_number": updated_mobile.strip() or None,
                        "target_exam": updated_exam,
                        "study_goal": updated_goal.strip() or None
                    }).eq("id", user_id).execute()

                    st.session_state["flash_message"] = (
                        "Your profile has been updated!"
                    )
                    st.rerun()

                except Exception as e:
                    st.error("Could not update your profile.")
                    st.caption(str(e))

    st.markdown("---")
    st.markdown("#### Your RankUp Friend Code")

    st.write(
        "Share this code with another RankUp student so they can send you a friend request."
    )

    st.code(current_code)

    st.caption(
        "Your mobile number is not displayed in the Friends Zone."
    )


# =========================================================
# FOOTER
# =========================================================
st.markdown("---")
st.caption(
    "RankUp · Prototype v0.5 | Personal tasks, student profiles and friends."
)
