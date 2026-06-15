import streamlit as st
import json
from advisor import (
    search_courses,
    check_prerequisites,
    filter_courses,
    get_course_by_id,
    workload_check,
    get_track_courses,
)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Husky Advisor",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_kb():
    with open("knowledge_base.json") as f:
        return json.load(f)

kb = load_kb()
courses = kb["courses"]
tracks = kb["concentration_tracks"]
grad_req = kb["graduation_requirements"]
tuition = kb["tuition_info"]
workload_thresholds = kb["workload_warning_thresholds"]

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

h1, h2, h3 { font-family: 'Space Grotesk', sans-serif; }

.main { background: #0f1117; }

.course-card {
    background: #1a1d27;
    border: 1px solid #2a2d3e;
    border-left: 4px solid #c8102e;
    border-radius: 8px;
    padding: 16px 20px;
    margin-bottom: 12px;
    transition: border-color 0.2s;
}
.course-card:hover { border-left-color: #ff4b6e; }

.course-id {
    font-family: 'Space Grotesk', monospace;
    font-size: 0.75rem;
    font-weight: 700;
    color: #c8102e;
    letter-spacing: 1px;
    text-transform: uppercase;
}
.course-name {
    font-size: 1.05rem;
    font-weight: 600;
    color: #f0f2f8;
    margin: 4px 0;
}
.course-meta {
    font-size: 0.8rem;
    color: #8b8fa8;
    margin-top: 6px;
}
.tag {
    display: inline-block;
    background: #252838;
    border: 1px solid #3a3d52;
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 0.72rem;
    color: #a0a4be;
    margin: 2px 3px 2px 0;
}
.tag-red {
    background: #2a1520;
    border-color: #c8102e;
    color: #ff6b89;
}
.tag-green {
    background: #0d2018;
    border-color: #1a7a45;
    color: #4ade80;
}
.tag-yellow {
    background: #1f1a0a;
    border-color: #7a6010;
    color: #fbbf24;
}
.diff-dot {
    display: inline-block;
    width: 9px; height: 9px;
    border-radius: 50%;
    margin-right: 2px;
}
.prereq-ok { color: #4ade80; font-weight: 600; }
.prereq-missing { color: #ff6b89; font-weight: 600; }
.stat-box {
    background: #1a1d27;
    border: 1px solid #2a2d3e;
    border-radius: 8px;
    padding: 16px;
    text-align: center;
}
.stat-num {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    color: #c8102e;
}
.stat-label { font-size: 0.8rem; color: #8b8fa8; margin-top: 4px; }
.section-header {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.4rem;
    font-weight: 700;
    color: #f0f2f8;
    border-bottom: 2px solid #c8102e;
    padding-bottom: 8px;
    margin-bottom: 20px;
}
.warning-box {
    background: #2a1520;
    border: 1px solid #c8102e;
    border-radius: 8px;
    padding: 12px 16px;
    color: #ff6b89;
    margin: 8px 0;
}
.success-box {
    background: #0d2018;
    border: 1px solid #1a7a45;
    border-radius: 8px;
    padding: 12px 16px;
    color: #4ade80;
    margin: 8px 0;
}
.info-box {
    background: #101828;
    border: 1px solid #1a4a7a;
    border-radius: 8px;
    padding: 12px 16px;
    color: #7ab8f5;
    margin: 8px 0;
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🐾 Husky Advisor")
    st.markdown("*Northeastern CS · Seattle GEENG*")
    st.divider()

    page = st.radio(
        "Navigate",
        ["🔍 Course Search", "✅ Prerequisite Checker", "🎯 Track Planner", "⚖️ Workload Calculator", "📋 Graduation Tracker"],
        label_visibility="collapsed",
    )

    st.divider()
    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-num">{len(courses)}</div>
        <div class="stat-label">courses in catalog</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(f"""
    <div class="stat-box" style="margin-top:8px">
        <div class="stat-num">${tuition['cost_per_course']:,}</div>
        <div class="stat-label">per course</div>
    </div>
    """, unsafe_allow_html=True)


# ── Helper: render course card ────────────────────────────────────────────────
DIFF_COLORS = {1: "#4ade80", 2: "#86efac", 3: "#fbbf24", 4: "#f87171", 5: "#c8102e"}
DIFF_LABELS = {1: "Very Easy", 2: "Easy", 3: "Medium", 4: "Hard", 5: "Very Hard"}

def difficulty_dots(level):
    dots = ""
    for i in range(1, 6):
        color = DIFF_COLORS[level] if i <= level else "#2a2d3e"
        dots += f'<span class="diff-dot" style="background:{color}"></span>'
    return dots

def render_course_card(c, show_prereq_status=None, completed=None):
    prereq_html = ""
    if show_prereq_status is not None:
        missing = [p for p in c["prerequisites"] if p not in (completed or [])]
        if not missing:
            prereq_html = '<span class="prereq-ok">✓ Prerequisites met</span>'
        else:
            prereq_html = f'<span class="prereq-missing">✗ Missing: {", ".join(missing)}</span>'

    prereqs_display = ", ".join(c["prerequisites"]) if c["prerequisites"] else "None"
    tracks_display = " ".join([f'<span class="tag">{t}</span>' for t in c["tracks"]])
    career_display = " ".join([f'<span class="tag">{t}</span>' for t in c["career_tags"][:3]])

    st.markdown(f"""
    <div class="course-card">
        <div class="course-id">{c['id']}</div>
        <div class="course-name">{c['name']}</div>
        <div class="course-meta">
            {difficulty_dots(c['difficulty'])} {DIFF_LABELS[c['difficulty']]} &nbsp;·&nbsp;
            {c['credits']} credits &nbsp;·&nbsp;
            ~{c['workload_hrs_per_week']}h/wk &nbsp;·&nbsp;
            ⭐ {c['student_rating']} &nbsp;·&nbsp;
            {c['delivery_mode']}
        </div>
        <div style="margin-top:8px; font-size:0.85rem; color:#c0c4d8">{c['description']}</div>
        <div style="margin-top:10px">
            {tracks_display}
            {career_display}
        </div>
        <div style="margin-top:8px; font-size:0.8rem; color:#8b8fa8">
            Prerequisites: <span style="color:#c0c4d8">{prereqs_display}</span>
            &nbsp;·&nbsp; {c['professor']}
            &nbsp;·&nbsp; Offered: {", ".join(c['semesters_offered'])}
        </div>
        {"<div style='margin-top:8px'>" + prereq_html + "</div>" if prereq_html else ""}
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — Course Search
# ══════════════════════════════════════════════════════════════════════════════
if page == "🔍 Course Search":
    st.markdown('<div class="section-header">Course Search</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
    with col1:
        query = st.text_input("Search by name, description, or professor", placeholder="e.g. machine learning, Pavlu, NLP...")
    with col2:
        track_filter = st.selectbox("Track", ["All Tracks"] + sorted(set(t for c in courses for t in c["tracks"])))
    with col3:
        diff_filter = st.selectbox("Difficulty", ["Any", "1 – Very Easy", "2 – Easy", "3 – Medium", "4 – Hard", "5 – Very Hard"])
    with col4:
        semester_filter = st.selectbox("Semester", ["Any", "Fall", "Spring", "Summer"])

    diff_val = int(diff_filter[0]) if diff_filter != "Any" else None
    track_val = None if track_filter == "All Tracks" else track_filter
    sem_val = None if semester_filter == "Any" else semester_filter

    results = filter_courses(courses, query=query, track=track_val, difficulty=diff_val, semester=sem_val)

    st.markdown(f"<div style='color:#8b8fa8; font-size:0.85rem; margin-bottom:16px'>{len(results)} course{'s' if len(results) != 1 else ''} found</div>", unsafe_allow_html=True)

    if results:
        for c in results:
            render_course_card(c)
    else:
        st.markdown('<div class="info-box">No courses match your filters. Try broadening your search.</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — Prerequisite Checker
# ══════════════════════════════════════════════════════════════════════════════
elif page == "✅ Prerequisite Checker":
    st.markdown('<div class="section-header">Prerequisite Checker</div>', unsafe_allow_html=True)
    st.markdown("Enter the courses you've completed, then check if you're eligible for any course.")

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("**Courses you've completed**")
        all_ids = [c["id"] for c in courses]
        completed = st.multiselect(
            "Select completed courses",
            options=all_ids,
            format_func=lambda x: f"{x} – {get_course_by_id(courses, x)['name']}",
            label_visibility="collapsed",
        )

    with col2:
        st.markdown("**Course to check**")
        target = st.selectbox(
            "Select target course",
            options=all_ids,
            format_func=lambda x: f"{x} – {get_course_by_id(courses, x)['name']}",
            label_visibility="collapsed",
        )

    if target:
        result = check_prerequisites(courses, target, completed)
        course = get_course_by_id(courses, target)

        st.divider()
        if result["eligible"]:
            st.markdown(f'<div class="success-box">✓ You are eligible to enroll in <strong>{target}: {course["name"]}</strong></div>', unsafe_allow_html=True)
        else:
            missing_names = [f"{p} ({get_course_by_id(courses, p)['name'] if get_course_by_id(courses, p) else p})" for p in result["missing"]]
            st.markdown(f'<div class="warning-box">✗ Missing prerequisites: <strong>{", ".join(missing_names)}</strong></div>', unsafe_allow_html=True)

        render_course_card(course, show_prereq_status=True, completed=completed)

    st.divider()
    st.markdown("**Eligibility overview for all courses**")

    eligible_courses = [c for c in courses if check_prerequisites(courses, c["id"], completed)["eligible"]]
    ineligible_courses = [c for c in courses if not check_prerequisites(courses, c["id"], completed)["eligible"]]

    tab_elig, tab_inelig = st.tabs([f"✅ Eligible ({len(eligible_courses)})", f"🔒 Not yet eligible ({len(ineligible_courses)})"])
    with tab_elig:
        for c in eligible_courses:
            render_course_card(c, show_prereq_status=True, completed=completed)
    with tab_inelig:
        for c in ineligible_courses:
            render_course_card(c, show_prereq_status=True, completed=completed)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — Track Planner
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🎯 Track Planner":
    st.markdown('<div class="section-header">Track Planner</div>', unsafe_allow_html=True)

    selected_track = st.selectbox("Choose a concentration track", list(tracks.keys()))

    track_course_ids = tracks[selected_track]
    track_course_list = [get_course_by_id(courses, cid) for cid in track_course_ids if get_course_by_id(courses, cid)]

    col1, col2, col3 = st.columns(3)
    avg_diff = sum(c["difficulty"] for c in track_course_list) / len(track_course_list)
    avg_rating = sum(c["student_rating"] for c in track_course_list) / len(track_course_list)
    total_credits = sum(c["credits"] for c in track_course_list)

    with col1:
        st.markdown(f'<div class="stat-box"><div class="stat-num">{len(track_course_list)}</div><div class="stat-label">courses in track</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="stat-box"><div class="stat-num">{avg_diff:.1f}/5</div><div class="stat-label">avg difficulty</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="stat-box"><div class="stat-num">⭐ {avg_rating:.1f}</div><div class="stat-label">avg student rating</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    for c in track_course_list:
        render_course_card(c)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — Workload Calculator
# ══════════════════════════════════════════════════════════════════════════════
elif page == "⚖️ Workload Calculator":
    st.markdown('<div class="section-header">Workload Calculator</div>', unsafe_allow_html=True)
    st.markdown("Select the courses you're planning to take this semester to estimate your weekly workload.")

    all_ids = [c["id"] for c in courses]
    selected = st.multiselect(
        "Add courses to your semester plan",
        options=all_ids,
        format_func=lambda x: f"{x} – {get_course_by_id(courses, x)['name']}",
    )

    if selected:
        selected_courses = [get_course_by_id(courses, cid) for cid in selected]
        total_hours = sum(c["workload_hrs_per_week"] for c in selected_courses)
        total_credits_sem = sum(c["credits"] for c in selected_courses)
        total_cost = sum(c["tuition_cost"] for c in selected_courses)

        safe = workload_thresholds["safe_weekly_hours"]
        caution = workload_thresholds["caution_weekly_hours"]
        danger = workload_thresholds["danger_weekly_hours"]

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div class="stat-box"><div class="stat-num">{total_hours}h</div><div class="stat-label">estimated hrs/week</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="stat-box"><div class="stat-num">{total_credits_sem}</div><div class="stat-label">total credits</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="stat-box"><div class="stat-num">${total_cost:,}</div><div class="stat-label">semester tuition</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if total_hours <= safe:
            st.markdown(f'<div class="success-box">✓ Manageable workload ({total_hours}h/week). You have room to breathe.</div>', unsafe_allow_html=True)
        elif total_hours <= caution:
            st.markdown(f'<div class="info-box">⚠ Moderate workload ({total_hours}h/week). Doable but will keep you busy.</div>', unsafe_allow_html=True)
        elif total_hours <= danger:
            st.markdown(f'<div class="warning-box">⚠ Heavy workload ({total_hours}h/week). Consider dropping one course.</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="warning-box">🚨 Overloaded ({total_hours}h/week). Strongly recommend reducing your course load.</div>', unsafe_allow_html=True)

        st.markdown("**Selected courses:**")
        for c in selected_courses:
            render_course_card(c)
    else:
        st.markdown('<div class="info-box">Select courses above to see your estimated workload and tuition cost.</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — Graduation Tracker
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📋 Graduation Tracker":
    st.markdown('<div class="section-header">Graduation Tracker</div>', unsafe_allow_html=True)

    req = grad_req
    all_ids = [c["id"] for c in courses]

    completed = st.multiselect(
        "Courses you've completed",
        options=all_ids,
        format_func=lambda x: f"{x} – {get_course_by_id(courses, x)['name']}",
    )

    completed_courses = [get_course_by_id(courses, cid) for cid in completed]
    completed_credits = sum(c["credits"] for c in completed_courses)
    remaining_credits = max(0, req["total_credits"] - completed_credits)
    remaining_courses = max(0, req["total_courses"] - len(completed))
    completed_cost = sum(c["tuition_cost"] for c in completed_courses)
    remaining_cost = remaining_courses * tuition["cost_per_course"]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="stat-box"><div class="stat-num">{len(completed)}/{req["total_courses"]}</div><div class="stat-label">courses done</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="stat-box"><div class="stat-num">{completed_credits}/{req["total_credits"]}</div><div class="stat-label">credits earned</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="stat-box"><div class="stat-num">{remaining_courses}</div><div class="stat-label">courses remaining</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="stat-box"><div class="stat-num">${remaining_cost:,}</div><div class="stat-label">tuition remaining</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Progress bar
    progress = min(1.0, len(completed) / req["total_courses"])
    st.progress(progress, text=f"{int(progress * 100)}% complete toward graduation")

    # Required course check
    for req_course_id in req["required_courses"]:
        req_course = get_course_by_id(courses, req_course_id)
        if req_course_id in completed:
            st.markdown(f'<div class="success-box">✓ Required course completed: <strong>{req_course_id} – {req_course["name"]}</strong></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="warning-box">⚠ Required course not yet completed: <strong>{req_course_id} – {req_course["name"]}</strong></div>', unsafe_allow_html=True)

    if remaining_courses == 0 and req_course_id in completed:
        st.balloons()
        st.markdown('<div class="success-box" style="font-size:1.1rem; text-align:center">🎓 <strong>All requirements met! You are ready to graduate.</strong></div>', unsafe_allow_html=True)