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
