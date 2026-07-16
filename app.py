"""
Main entry point for the Streamlit Web Application of AI Task Manager.
"""

import streamlit as st
import pandas as pd
import os
import json
import sys
import importlib
from datetime import datetime

# Force reload module to prevent Streamlit caching old class definitions
import services.task_manager
importlib.reload(services.task_manager)
from services.task_manager import TaskManager

from models.task import Task
from pydantic import ValidationError
from utils.logger import get_logger

# Initialize logger
logger = get_logger("web_app")

# Page configurations
st.set_page_config(
    page_title="AI Task Manager",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize TaskManager in session state
if "manager" not in st.session_state or not hasattr(st.session_state.manager, "filter_tasks"):
    st.session_state.manager = TaskManager()
manager = st.session_state.manager

# Initialize session state for navigation
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

# Initialize session state for theme
if "theme" not in st.session_state:
    st.session_state.theme = "Sleek Dark"

# Theme Mode Colors config
if st.session_state.theme == "Sleek Dark":
    bg = "#030014"
    bg_subtle = "#08071a"
    card = "rgba(255, 255, 255, 0.03)"
    card_hover = "rgba(255, 255, 255, 0.06)"
    border = "rgba(255, 255, 255, 0.08)"
    border_focus = "#8f56ef"
    text = "#fafafa"
    text_muted = "#8e90a6"
    text_dim = "#5c5d70"
    accent_gradient = "linear-gradient(135deg, #8f56ef, #4f20ec)"
    green = "#22c55e"
    green_muted = "rgba(34, 197, 94, 0.1)"
    red = "#ef4444"
    red_muted = "rgba(239, 68, 68, 0.1)"
    amber = "#f59e0b"
    amber_muted = "rgba(245, 158, 11, 0.1)"
else:
    # Classic Light Mode Theme
    bg = "#f9fafd"
    bg_subtle = "#f0f2f8"
    card = "#ffffff"
    card_hover = "#f3f4f6"
    border = "#e5e7eb"
    border_focus = "#4f20ec"
    text = "#1f2937"
    text_muted = "#4b5563"
    text_dim = "#9ca3af"
    accent_gradient = "linear-gradient(135deg, #4f20ec, #8f56ef)"
    green = "#16a34a"
    green_muted = "rgba(22, 163, 74, 0.1)"
    red = "#dc2626"
    red_muted = "rgba(220, 38, 38, 0.1)"
    amber = "#d97706"
    amber_muted = "rgba(217, 119, 6, 0.1)"

shadow = "none"
radius = "12px"

# Inject custom SaaS CSS block
css = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

:root {{
    --bg: {bg};
    --bg-subtle: {bg_subtle};
    --card: {card};
    --card-hover: {card_hover};
    --border: {border};
    --border-focus: {border_focus};
    --text: {text};
    --text-muted: {text_muted};
    --text-dim: {text_dim};
    --accent-gradient: {accent_gradient};
    --green: {green};
    --green-muted: {green_muted};
    --red: {red};
    --red-muted: {red_muted};
    --amber: {amber};
    --amber-muted: {amber_muted};
    --radius: {radius};
}}

/* Hide Streamlit top bar decoration and footer */
footer, [data-testid="stDecoration"] {{
    display: none !important;
}}

header[data-testid="stHeader"] {{
    background-color: transparent !important;
}}

/* Ensure the sidebar toggle button is always colored high-contrast and very visible */
header[data-testid="stHeader"] button {{
    background-color: rgba(143, 86, 239, 0.2) !important;
    border: 1px solid rgba(143, 86, 239, 0.4) !important;
    color: var(--text) !important;
    border-radius: 50% !important;
    padding: 5px !important;
}}

/* Global app background */
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], .main, .block-container, section[data-testid="stMain"] {{
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
}}

.block-container {{
    padding: 2.5rem 3rem 4rem !important;
    max-width: 1400px !important;
}}

/* Sidebar Custom Styling */
[data-testid="stSidebar"] {{
    background-color: var(--bg-subtle) !important;
    border-right: 1px solid var(--border) !important;
    backdrop-filter: blur(20px);
}}

/* Metric Cards Custom Layout */
.metric-card-saas {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.25rem 1.4rem;
    backdrop-filter: blur(12px);
    box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.2);
    margin-bottom: 1rem;
}}
.metric-label-saas {{
    font-size: 0.72rem;
    color: var(--text-muted);
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}}
.metric-value-saas {{
    font-size: 2.2rem;
    font-weight: 800;
    color: var(--text);
    letter-spacing: -0.04em;
    margin-top: 0.2rem;
}}

/* Custom badge styles */
.badge {{
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}}
.badge-prio-high {{ color: var(--red); background: var(--red-muted); border: 1px solid rgba(239, 68, 68, 0.2); }}
.badge-prio-medium {{ color: var(--amber); background: var(--amber-muted); border: 1px solid rgba(245, 158, 11, 0.2); }}
.badge-prio-low {{ color: var(--green); background: var(--green-muted); border: 1px solid rgba(34, 197, 94, 0.2); }}
.badge-status-completed {{ color: var(--green); background: var(--green-muted); border: 1px solid rgba(34, 197, 94, 0.2); }}
.badge-status-pending {{ color: #8f56ef; background: rgba(143, 86, 239, 0.1); border: 1px solid rgba(143, 86, 239, 0.2); }}

/* Custom task list card styling */
.premium-card {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.5rem;
    backdrop-filter: blur(12px);
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    margin-bottom: 1.25rem;
    transition: border-color 0.2s, background-color 0.2s, transform 0.2s;
}}
.premium-card:hover {{
    border-color: rgba(143, 86, 239, 0.4);
    background: var(--card-hover);
    transform: translateY(-1px);
}}

/* Custom Buttons styling */
.stButton > button {{
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    transition: all 0.2s !important;
    text-align: left !important;
    justify-content: flex-start !important;
    padding: 0.5rem 1rem !important;
}}
.stButton > button:hover {{
    border-color: #8f56ef !important;
    background: rgba(143, 86, 239, 0.1) !important;
    color: #fafafa !important;
}}

/* Primary / Form Submit Buttons */
div[data-testid="stFormSubmitButton"] button, button[type="primary"] {{
    background: var(--accent-gradient) !important;
    border: none !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 14px 0 rgba(143, 86, 239, 0.4) !important;
    text-align: center !important;
    justify-content: center !important;
}}
div[data-testid="stFormSubmitButton"] button:hover, button[type="primary"]:hover {{
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px 0 rgba(143, 86, 239, 0.6) !important;
}}

/* Set horizontal block gap */
[data-testid="stHorizontalBlock"] {{
    gap: 1.25rem !important;
}}

/* Explicitly style input fields, textareas, and selectboxes to match the theme colors */
div[data-baseweb="input"] input, div[data-baseweb="textarea"] textarea {{
    background-color: var(--bg-subtle) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
}}

div[data-baseweb="input"] input:focus, div[data-baseweb="textarea"] textarea:focus {{
    border-color: var(--border-focus) !important;
    box-shadow: 0 0 0 1px var(--border-focus) !important;
}}

/* Ensure placeholder text is readable */
div[data-baseweb="input"] input::placeholder, div[data-baseweb="textarea"] textarea::placeholder {{
    color: var(--text-muted) !important;
    opacity: 0.7;
}}

/* Selectbox custom styles */
div[data-baseweb="select"] > div {{
    background-color: var(--bg-subtle) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
}}
</style>
  """
st.markdown(css, unsafe_allow_html=True)

# Helper function for rendering KPI metric card
def render_metric_card(label: str, value: str):
    st.markdown(f"""
    <div class="metric-card-saas">
        <div class="metric-label-saas">{label}</div>
        <div class="metric-value-saas">{value}</div>
    </div>
    """, unsafe_allow_html=True)

# Navigation Callback
def set_page(page_name: str):
    st.session_state.page = page_name

# ----------------- SIDEBAR NAVIGATION -----------------
with st.sidebar:
    st.markdown("""
    <div style="padding-top: 1rem; padding-bottom: 1.5rem; border-bottom: 1px solid var(--border); margin-bottom: 1.5rem;">
        <span style="font-size: 1.5rem; font-weight: 800; letter-spacing: -0.04em;">🤖 AI Task Manager</span>
        <div style="font-size: 0.72rem; color: var(--text-muted); margin-top: 0.2rem;">SaaS Operational Core</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Render Navigation via st.session_state callback
    st.button("🏠 Dashboard", type="primary" if st.session_state.page == "Dashboard" else "secondary", on_click=set_page, args=("Dashboard",), use_container_width=True)
    st.button("📋 Tasks", type="primary" if st.session_state.page == "Tasks" else "secondary", on_click=set_page, args=("Tasks",), use_container_width=True)
    st.button("➕ Add Task", type="primary" if st.session_state.page == "Add Task" else "secondary", on_click=set_page, args=("Add Task",), use_container_width=True)
    st.button("📊 Analytics (Coming Soon)", type="primary" if st.session_state.page == "Analytics" else "secondary", on_click=set_page, args=("Analytics",), use_container_width=True)
    st.button("✨ AI Assistant (Coming Soon)", type="primary" if st.session_state.page == "AI Assistant" else "secondary", on_click=set_page, args=("AI Assistant",), use_container_width=True)
    st.button("⚙️ Settings", type="primary" if st.session_state.page == "Settings" else "secondary", on_click=set_page, args=("Settings",), use_container_width=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Theme Selection dropdown
    theme_selection = st.selectbox("Theme Preference", ["Sleek Dark", "Classic Light"], index=0 if st.session_state.theme == "Sleek Dark" else 1)
    if theme_selection != st.session_state.theme:
        st.session_state.theme = theme_selection
        st.rerun()
        
    # Read modifications timestamp
    last_updated_str = "Never"
    if os.path.exists(manager.file_path):
        mtime = os.path.getmtime(manager.file_path)
        last_updated_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
        
    st.markdown(f"""
    <div style="border-top: 1px solid var(--border); padding-top: 1rem; margin-top: 2rem; font-size: 0.72rem; color: var(--text-muted); text-align: center;">
        Platform: TKXEL Core Framework<br>
        <span style="font-size: 0.65rem; color: var(--text-dim);">Last sync: {last_updated_str}</span>
    </div>
    """, unsafe_allow_html=True)

# Fetch current task statistics
stats = manager.show_statistics()

# Display success notifications from session state
if "success_msg" in st.session_state and st.session_state.success_msg:
    st.success(st.session_state.success_msg)
    st.session_state.success_msg = None

# ----------------- PAGE ROUTING -----------------

# ================= PAGE: DASHBOARD =================
if st.session_state.page == "Dashboard":
    # 1. Welcome Section
    st.markdown("""
    <div style="padding-bottom: 1.5rem;">
        <span style="font-size: 2.2rem; font-weight: 800; letter-spacing: -0.04em;">Welcome back 👋</span>
        <div style="font-size: 0.95rem; color: var(--text-muted); margin-top: 0.15rem;">
            Let's orchestrate and prioritize your tasks with precision.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 2. Statistics
    kpi_c1, kpi_c2, kpi_c3, kpi_c4 = st.columns(4)
    with kpi_c1:
        render_metric_card("Total Tasks", str(stats["total"]))
    with kpi_c2:
        render_metric_card("Pending", str(stats["pending"]))
    with kpi_c3:
        render_metric_card("Completed", str(stats["completed"]))
    with kpi_c4:
        # Calculate today's created tasks count
        today_date = datetime.now().date()
        todays_created_count = sum(1 for t in manager.iter_tasks() if t.created_at.date() == today_date)
        render_metric_card("Created Today", str(todays_created_count))
        
    # 3. Progress bar
    st.markdown("### 📈 Today's Progress")
    st.progress(stats["percentage_completed"] / 100.0)
    st.write(f"Today's Progress: **{stats['percentage_completed']}%**")
    
    st.write("")  # space
    
    # Layout Grid
    dash_col1, dash_col2 = st.columns([5, 5])
    
    with dash_col1:
        # 4. Recent Tasks
        st.markdown("### ⏱️ Recent Tasks")
        all_tasks = manager.view_tasks()
        recent_tasks = all_tasks[-3:] if all_tasks else []
        
        if not recent_tasks:
            st.info("No logs in task list queue. Add tasks to see them.")
        else:
            for t in reversed(recent_tasks):
                prio_badge_cls = f"badge-prio-{t.priority.lower()}"
                status_badge_cls = "badge-status-completed" if t.completed else "badge-status-pending"
                status_text = "Completed" if t.completed else "Pending"
                overdue_badge = '<span class="badge" style="background: rgba(239, 68, 68, 0.15); color: var(--red); border: 1px solid rgba(239, 68, 68, 0.3); margin-left: 5px;">⏳ Overdue</span>' if not t.completed else ''
                st.markdown(f"""
                <div class="premium-card">
                    <div style="display: flex; align-items: center; justify-content: space-between;">
                        <span style="font-weight: 700; font-size: 1.05rem;">{t.title}</span>
                        <div>
                            <span class="badge {prio_badge_cls}">{t.priority}</span>
                            <span class="badge {status_badge_cls}" style="margin-left: 5px;">{status_text}</span>
                            {overdue_badge}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
    with dash_col2:
        # 5. AI Suggestions placeholder
        st.markdown("### 💡 AI Engine Suggestions")
        st.markdown("""
        <div class="premium-card">
            <div style="font-weight: 700; color: #8f56ef; margin-bottom: 0.4rem;">💡 Today's Recommendation</div>
            <div style="font-size: 0.88rem; color: var(--text-muted); line-height: 1.4;">
                Complete High priority tasks first to optimize system queue throughput.
            </div>
            <hr style="margin: 0.8rem 0; border: 0; border-top: 1px solid var(--border);">
            <div style="font-weight: 700; color: #8f56ef; margin-bottom: 0.4rem;">📈 Productivity Tips</div>
            <div style="font-size: 0.88rem; color: var(--text-muted); line-height: 1.4;">
                Queue backlog is stable. Keep completing tasks to maintain index response health.
            </div>
        </div>
        """, unsafe_allow_html=True)

# ================= PAGE: TASKS =================
elif st.session_state.page == "Tasks":
    st.markdown("""
    <div style="padding-bottom: 1.5rem;">
        <span style="font-size: 2.2rem; font-weight: 800; letter-spacing: -0.04em;">📋 Task Backlog Registry</span>
        <div style="font-size: 0.85rem; color: var(--text-muted);">View, complete, filter and query tasks.</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Search and Filter criteria
    f_col1, f_col2, f_col3, f_col4 = st.columns([4, 2, 2, 2])
    with f_col1:
        search_query = st.text_input("Search tasks...", placeholder="Search by title keywords or details...")
    with f_col2:
        status_filter = st.selectbox("Status", ["All", "Pending", "Completed"])
    with f_col3:
        priority_filter = st.selectbox("Priority Level", ["All", "High", "Medium", "Low"])
    with f_col4:
        sort_option = st.selectbox("Sort Order", ["Newest", "Oldest", "High Priority", "Low Priority"])
        
    # Map to backend sort strings
    sort_mapping = {
        "Newest": "Newest First",
        "Oldest": "Oldest First",
        "High Priority": "High Priority First",
        "Low Priority": "Low Priority First"
    }
    sort_criterion = sort_mapping.get(sort_option, "Newest First")
        
    # Delegate query logic to backend search
    if search_query:
        filtered_tasks = manager.search_tasks(search_query)
    else:
        filtered_tasks = manager.view_tasks()
        
    # Delegate filter logic to backend filter
    filter_ids = {t.id for t in manager.filter_tasks(status=status_filter, priority=priority_filter)}
    filtered_tasks = [t for t in filtered_tasks if t.id in filter_ids]
    
    # Delegate sort logic to backend sorter
    filtered_tasks = manager.sort_tasks(filtered_tasks, sort_criterion)
        
    st.write("")  # space
    
    if not filtered_tasks:
        st.markdown("""
        <div style="text-align: center; padding: 4rem 2rem; border: 1px dashed var(--border); border-radius: var(--radius); background: var(--card);">
            <span style="font-size: 3rem;">🔍</span>
            <h3 style="margin-top: 1rem; font-weight: 700; color: var(--text);">No tasks found.</h3>
            <p style="font-size: 0.88rem; color: var(--text-muted); margin-bottom: 0;">Try adjusting your search queries or priority level filters.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Display task cards
        for t in filtered_tasks:
            prio_badge_cls = f"badge-prio-{t.priority.lower()}"
            status_badge_cls = "badge-status-completed" if t.completed else "badge-status-pending"
            status_text = "Completed" if t.completed else "Pending"
            
            t_col1, t_col2 = st.columns([8, 2])
            with t_col1:
                desc_html = t.description.replace("\n", "<br>") if t.description else "<span style='font-style: italic; color: var(--text-dim);'>No description provided.</span>"
                overdue_badge = '<span class="badge" style="background: rgba(239, 68, 68, 0.15); color: var(--red); border: 1px solid rgba(239, 68, 68, 0.3); margin-left: 5px;">⏳ Overdue</span>' if not t.completed else ''
                st.markdown(f"""
                <div class="premium-card">
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.5rem;">
                        <span style="font-size: 1.15rem; font-weight: 700; color: var(--text);">{t.title}</span>
                        <div>
                            <span class="badge {prio_badge_cls}">{t.priority}</span>
                            <span class="badge {status_badge_cls}" style="margin-left: 5px;">{status_text}</span>
                            {overdue_badge}
                        </div>
                    </div>
                    <div style="font-size: 0.88rem; color: var(--text-muted); line-height: 1.4; margin-bottom: 0.6rem;">
                        {desc_html}
                    </div>
                    <div style="font-size: 0.72rem; color: var(--text-dim);">
                        Task ID: #{t.id} | Created: {t.created_at.strftime('%Y-%m-%d %H:%M')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with t_col2:
                st.write("") # spacing alignment
                if not t.completed:
                    if st.button("✓ Complete", key=f"comp_{t.id}", use_container_width=True):
                        with st.spinner("Completing task..."):
                            manager.complete_task(t.id)
                        st.toast(f"Task #{t.id} completed successfully!", icon="✅")
                        st.session_state.success_msg = f"Task #{t.id} marked as completed successfully!"
                        st.rerun()
                else:
                    st.button("✓ Done", key=f"done_{t.id}", disabled=True, use_container_width=True)
                    
                if st.button("🗑 Delete", key=f"del_{t.id}", use_container_width=True):
                    with st.spinner("Deleting task..."):
                        manager.delete_task(t.id)
                    st.toast(f"Task #{t.id} deleted successfully!", icon="🗑️")
                    st.session_state.success_msg = f"Task #{t.id} deleted successfully!"
                    st.rerun()

# ================= PAGE: ADD TASK =================
elif st.session_state.page == "Add Task":
    st.markdown("""
    <div style="padding-bottom: 1.5rem;">
        <span style="font-size: 2.2rem; font-weight: 800; letter-spacing: -0.04em;">➕ Create Task Record</span>
        <div style="font-size: 0.85rem; color: var(--text-muted);">Insert a validated task entry into the serialization queue.</div>
    </div>
    """, unsafe_allow_html=True)
    
    form_c1, form_c2 = st.columns([7, 3])
    
    with form_c1:
        # Relocated creation form
        with st.form("create_task_form", clear_on_submit=True):
            title = st.text_input("Task Title (minimum 3 characters)", placeholder="Enter title...")
            description = st.text_area("Task Description (optional)", placeholder="Enter details...")
            priority = st.selectbox("Task Priority Level", ["Low", "Medium", "High"], index=1)
            
            submitted = st.form_submit_button("Add Task To Registry", use_container_width=True)
            if submitted:
                try:
                    with st.spinner("Saving task to registry..."):
                        task = manager.add_task(title, description, priority)
                    st.toast("Task successfully created!", icon="➕")
                    st.session_state.success_msg = f"Task #{task.id} created successfully!"
                    st.rerun()
                except ValidationError as ve:
                    for err in ve.errors():
                        field = " -> ".join(str(l) for l in err['loc'])
                        st.error(f"Validation Error ({field}): {err['msg']}")
                except Exception as e:
                    st.error(f"Failed to create task: {e}")
                        
    with form_c2:
        st.markdown("### 🏷️ Rules & Constraints")
        st.info("""
        - **Title Validation:** Must be at least 3 characters.
        - **Priority Enums:** Constrained strictly to `Literal["Low", "Medium", "High"]`.
        - **Atomic Save:** Writes to `data/tasks.json` instantaneously on successful submit actions.
        """)

# ================= PAGES: COMING SOON / PLACEHOLDERS =================
elif st.session_state.page in ["Analytics", "AI Assistant"]:
    title_text = "📊 Analytics" if st.session_state.page == "Analytics" else "✨ AI Assistant"
    desc_text = (
        "Analytics & Predictive queue metrics are coming soon in Sprint 3."
        if st.session_state.page == "Analytics"
        else "AI Agentic planning, LangChain tools and OpenRouter routing are coming soon."
    )
    
    st.markdown(f"""
    <div style="padding-bottom: 1.5rem;">
        <span style="font-size: 2.2rem; font-weight: 800; letter-spacing: -0.04em;">🛠️ Feature Node</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="premium-card" style="text-align: center; padding: 4rem 2rem;">
        <span style="font-size: 3rem;">⚡</span>
        <h2 style="font-weight: 800; letter-spacing: -0.03em; margin-top: 1rem;">{title_text}</h2>
        <p style="color: var(--text-muted); font-size: 0.95rem; max-width: 500px; margin: 0.5rem auto 1.5rem;">
            {desc_text}
        </p>
        <span class="badge" style="background: rgba(143, 86, 239, 0.1); color: #8f56ef; padding: 6px 16px; border: 1px solid rgba(143, 86, 239, 0.2);">
            Coming Soon
        </span>
    </div>
    """, unsafe_allow_html=True)

# ================= PAGE: SETTINGS =================
elif st.session_state.page == "Settings":
    st.markdown("""
    <div style="padding-bottom: 1.5rem;">
        <span style="font-size: 2.2rem; font-weight: 800; letter-spacing: -0.04em;">⚙️ Database & Settings</span>
        <div style="font-size: 0.85rem; color: var(--text-muted);">Manage backups, queue database, and export options.</div>
    </div>
    """, unsafe_allow_html=True)
    
    # 1. Export JSON
    st.markdown("### 📥 Database Backups")
    tasks_list = [t.model_dump(mode="json") for t in manager.view_tasks()]
    tasks_json_data = json.dumps(tasks_list, indent=4)
    
    st.download_button(
        label="Export Tasks Database (JSON)",
        data=tasks_json_data,
        file_name="tasks_backup.json",
        mime="application/json",
        use_container_width=True
    )
    
    st.write("")  # space
    
    # 2. Clear Tasks (Danger Zone)
    st.markdown("### 🚨 Danger Zone")
    with st.expander("Wipe Task Database", expanded=True):
        st.write("Wiping the task repository database is permanent and cannot be undone.")
        if st.button("Wipe Task Database", use_container_width=True, type="secondary"):
            with st.spinner("Wiping task database..."):
                manager.tasks = []
                manager.save_tasks()
            st.toast("Wiped task database successfully.", icon="🚨")
            st.session_state.success_msg = "Wiped task database successfully."
            st.rerun()
