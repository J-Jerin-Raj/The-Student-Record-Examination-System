"""
Acadence - Student Academic & Examination Assistant
Streamlit Web Interface.
Runs with: streamlit run streamlit_app.py
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

import database as db
from models import Task, Exam, Assessment
from services.academic_planner import AcademicPlannerService
from services.exam_manager import ExamManagerService
from services.performance_analyzer import PerformanceAnalyzerService
from services.rescue_mode import AcademicRescueService
from services.priority_engine import PriorityEngine
from services.dsa_lab import DSALabService

# Page configuration
st.set_page_config(
    page_title="Acadence - Academic & Exam Assistant",
    page_icon="A",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize Database
db.init_db()

# Services initialization
if "planner" not in st.session_state:
    st.session_state.planner = AcademicPlannerService()
if "exam_mgr" not in st.session_state:
    st.session_state.exam_mgr = ExamManagerService()

planner = st.session_state.planner
exam_mgr = st.session_state.exam_mgr

# Sidebar Navigation
st.sidebar.title("Acadence")
st.sidebar.caption("Student Academic & Examination Assistant")

nav_choice = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Smart Academic Planner",
        "Examination Management",
        "Academic Performance",
        "Academic Rescue Mode",
        "DSA Performance Lab",
    ],
)

# Undo Button in Sidebar (CO1: LIFO Stack)
st.sidebar.markdown("---")
undo_desc = planner.peek_undo()
if undo_desc:
    if st.sidebar.button(f"Undo: {undo_desc[:30]}..."):
        ok, msg = planner.undo_last_action()
        if ok:
            st.sidebar.success(msg)
            st.rerun()
        else:
            st.sidebar.error(msg)
else:
    st.sidebar.caption("Undo Stack is empty.")

# Quick Admin Options
st.sidebar.markdown("---")
col_res1, col_res2 = st.sidebar.columns(2)
with col_res1:
    if st.button("Reset Demo", use_container_width=True):
        db.clear_all_data()
        db.seed_demo_data()
        planner.refresh_linked_list()
        st.success("Demo data reset!")
        st.rerun()
with col_res2:
    if st.button("Clear All", use_container_width=True):
        db.clear_all_data()
        planner.refresh_linked_list()
        st.warning("All data cleared!")
        st.rerun()


# ================= VIEW 1: DASHBOARD =================
if nav_choice == "Dashboard":
    st.title("Academic Dashboard")

    threshold = float(db.get_setting("warning_threshold", "60.0"))

    # Next Exam Countdown Banner
    countdown = exam_mgr.get_next_exam_countdown()
    if countdown:
        exam = countdown["exam"]
        st.info(
            f"**Upcoming Examination:** {exam['subject']} scheduled on **{countdown['target_datetime']}** "
            f"({exam['venue']}). Countdown: **{countdown['days']} days, {countdown['hours']} hours, {countdown['minutes']} minutes**."
        )

    # Schedule Clash Warning
    conflicts = exam_mgr.detect_conflicts()
    if conflicts:
        for c in conflicts:
            st.error(f"**Critical Clash:** {c['slot1']} overlaps with {c['slot2']} on {c['date']}!")

    # 4 Key Metrics
    metrics = planner.get_task_metrics()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Pending Tasks", metrics["pending"])
    c2.metric("In Progress", metrics["in_progress"])
    c3.metric("Completed", metrics["completed"])
    c4.metric("Overdue Tasks", metrics["overdue"], delta_color="inverse")

    st.markdown("---")

    # Main Dashboard Columns
    col_left, col_right = st.columns([1.2, 1.0])

    with col_left:
        st.subheader("What Should I Do Next?")
        st.caption("Deterministic rule-based study priority recommendations")

        perf = PerformanceAnalyzerService.get_subject_summaries(threshold)
        subject_avgs = {s: d["average_percentage"] for s, d in perf["subjects"].items()}
        all_tasks = db.get_all_tasks()
        ranked = PriorityEngine.rank_tasks(all_tasks, subject_avgs, threshold, include_completed=False)

        if not ranked:
            st.success("No urgent pending tasks. You are all caught up!")
        else:
            for item in ranked[:3]:
                t = item["task"]
                with st.container():
                    st.markdown(f"**{t.title}** (`{t.subject}`)")
                    st.caption(f"Priority: {t.priority} | Est: {t.estimated_effort}h | Deadline: {t.deadline}")
                    st.write(f"*Why prioritized:* {item['breakdown'].rationale}")
                    if st.button("Mark Completed", key=f"dash_done_{t.id}"):
                        planner.toggle_status(t.id, "Completed")
                        st.rerun()
                    st.markdown("---")

    with col_right:
        st.subheader("Academic Rescue Status")
        rescue = AcademicRescueService.analyze_rescue_state(threshold)
        st.metric("Crisis Index", f"{rescue['crisis_index']}/100", rescue["status_level"])
        st.write(f"**Action Statement:** {rescue['action_statement']}")

        st.subheader("Performance Overview")
        st.metric("Overall Average", f"{perf['overall_average']}%", perf["overall_grade"])
        vuln = [s for s, d in perf["subjects"].items() if d["status"] in ("Critical", "Vulnerable")]
        if vuln:
            st.warning(f"Subjects below {threshold}% threshold: {', '.join(vuln)}")
        else:
            st.success("All subjects currently meet or exceed threshold.")


# ================= VIEW 2: PLANNER =================
elif nav_choice == "Smart Academic Planner":
    st.title("Smart Academic Planner")

    tasks = db.get_all_tasks()

    tab1, tab2, tab3 = st.tabs(["Task Registry", "Daily Study Scheduler", "Add New Task"])

    with tab1:
        st.subheader("Current Academic Tasks")
        if not tasks:
            st.info("No tasks recorded.")
        else:
            task_data = []
            for t in tasks:
                task_data.append({
                    "ID": t.id,
                    "Title": t.title,
                    "Subject": t.subject,
                    "Priority": t.priority,
                    "Deadline": t.deadline,
                    "Effort (h)": t.estimated_effort,
                    "Status": t.status,
                })
            st.dataframe(pd.DataFrame(task_data), use_container_width=True)

            # Quick status toggles
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                sel_task_id = st.selectbox("Select Task to Update", [t.id for t in tasks], format_func=lambda x: f"Task #{x}: {[t.title for t in tasks if t.id == x][0]}")
            with col_t2:
                sel_status = st.selectbox("New Status", ["Pending", "In Progress", "Completed"])

            if st.button("Update Task Status"):
                ok, msg = planner.toggle_status(sel_task_id, sel_status)
                st.success(msg)
                st.rerun()

    with tab2:
        st.subheader("Suggested Daily Study Plan")
        study_hrs = st.slider("Available Study Hours Today", 1.0, 10.0, 3.5, 0.5)

        threshold = float(db.get_setting("warning_threshold", "60.0"))
        perf = PerformanceAnalyzerService.get_subject_summaries(threshold)
        subject_avgs = {s: d["average_percentage"] for s, d in perf["subjects"].items()}

        sched = planner.get_suggested_daily_schedule(study_hrs, subject_avgs, threshold)
        st.write(f"**Planned:** {sched['allocated_hours']} hours across {sched['selected_count']} tasks.")

        for item in sched["tasks"]:
            t = item["task"]
            st.markdown(f"- **{t['title']}** ({t['subject']}) &bull; `{t['estimated_effort']}h` &bull; *Rationale:* {item['rationale']}")

    with tab3:
        st.subheader("Add Academic Task")
        with st.form("form_add_task"):
            title = st.text_input("Task Title", placeholder="e.g. Implement Merge Sort Algorithm")
            subject = st.text_input("Subject", placeholder="e.g. Data Structures & Algorithms")
            c1, c2 = st.columns(2)
            with c1:
                ttype = st.selectbox("Task Type", ["Assignment", "Project", "Lab Work", "Exam Prep"])
                priority = st.selectbox("Priority Level", ["Critical", "High", "Medium", "Low"], index=2)
            with c2:
                deadline = st.date_input("Deadline Date", value=datetime.now() + timedelta(days=3))
                effort = st.number_input("Estimated Effort (Hours)", min_value=0.5, max_value=40.0, value=2.5, step=0.5)
            notes = st.text_area("Notes / Deliverables")
            submitted = st.form_submit_button("Save Task")

            if submitted:
                if not title or not subject:
                    st.error("Title and Subject are required.")
                else:
                    new_t = Task(
                        title=title,
                        subject=subject,
                        task_type=ttype,
                        priority=priority,
                        deadline=deadline.strftime("%Y-%m-%d 23:59"),
                        estimated_effort=effort,
                        notes=notes,
                    )
                    ok, msg, tid = planner.add_task(new_t)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)


# ================= VIEW 3: EXAMINATIONS =================
elif nav_choice == "Examination Management":
    st.title("Examination Management")

    exams = db.get_all_exams()

    tab1, tab2, tab3 = st.tabs(["Exam Schedule", "FIFO Academic Request Queue", "Schedule New Exam"])

    with tab1:
        st.subheader("Scheduled Examinations")

        # Conflict check
        conflicts = exam_mgr.detect_conflicts()
        if conflicts:
            for c in conflicts:
                st.error(f"Schedule Conflict Detected: {c['slot1']} overlaps with {c['slot2']} on {c['date']}!")

        if not exams:
            st.info("No examinations scheduled.")
        else:
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                sort_choice = st.selectbox("Sort Examinations By", ["date", "subject", "priority", "revision"])
            with col_s2:
                algo_choice = st.selectbox("Sorting Algorithm (CO3)", ["merge", "insertion", "bubble"])

            sorted_exams = exam_mgr.get_exams(sort_by=sort_choice, algorithm=algo_choice)

            exam_data = []
            for e in sorted_exams:
                exam_data.append({
                    "Subject": e.subject,
                    "Date": e.exam_date,
                    "Time": f"{e.start_time} - {e.end_time}",
                    "Venue": e.venue,
                    "Revision (%)": f"{e.revision_progress}%",
                    "Priority": e.priority,
                })
            st.dataframe(pd.DataFrame(exam_data), use_container_width=True)

    with tab2:
        st.subheader("FIFO Academic Service Request Queue (CO1)")
        st.caption("Demonstrating strict First-Come, First-Served queue processing using linked nodes.")

        pending_q = exam_mgr.get_pending_queue()
        st.write(f"**Pending Requests in Queue:** {len(pending_q)}")

        if pending_q:
            front_req = pending_q[0]
            st.info(f"**Front of Queue:** {front_req.request_id} &bull; {front_req.student_name} ({front_req.request_type} - {front_req.subject})")
            if st.button("Process Next in Line (Dequeue)"):
                req, msg = exam_mgr.process_next_request()
                st.success(msg)
                st.rerun()

        with st.form("form_enqueue_req"):
            st.write("Submit Academic Request")
            sname = st.text_input("Student Name", value="Alex Chen")
            rtype = st.selectbox("Request Type", ["Hall Ticket Generation", "Re-evaluation", "Doubt Session", "Supplementary Application"])
            rsub = st.text_input("Subject", value="Operating Systems")
            rdet = st.text_input("Details", value="Mid-Term Paper Re-check")
            sub_req = st.form_submit_button("Enqueue Request (O(1))")
            if sub_req:
                req = exam_mgr.submit_academic_request(sname, rtype, rsub, rdet)
                st.success(f"Request {req.request_id} enqueued at rear of queue.")
                st.rerun()

    with tab3:
        st.subheader("Schedule Examination")
        with st.form("form_add_exam"):
            esub = st.text_input("Subject Name")
            edate = st.date_input("Exam Date", value=datetime.now() + timedelta(days=10))
            c1, c2 = st.columns(2)
            with c1:
                stime = st.text_input("Start Time (HH:MM)", value="09:30")
                venue = st.text_input("Venue", value="Exam Hall A-101")
            with c2:
                etime = st.text_input("End Time (HH:MM)", value="12:30")
                eprio = st.selectbox("Priority", ["Critical", "High", "Medium", "Low"], index=1)
            erev = st.slider("Current Revision Completion (%)", 0.0, 100.0, 50.0)
            esyll = st.text_area("Syllabus Units")
            sub_exam = st.form_submit_button("Schedule Exam")

            if sub_exam:
                new_e = Exam(
                    subject=esub,
                    exam_date=edate.strftime("%Y-%m-%d"),
                    start_time=stime,
                    end_time=etime,
                    venue=venue,
                    priority=eprio,
                    revision_progress=erev,
                    syllabus=esyll,
                )
                ok, msg, eid = exam_mgr.add_exam(new_e)
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)


# ================= VIEW 4: PERFORMANCE =================
elif nav_choice == "Academic Performance":
    st.title("Academic Performance Analyzer")

    threshold = float(db.get_setting("warning_threshold", "60.0"))
    perf = PerformanceAnalyzerService.get_subject_summaries(threshold)

    c1, c2 = st.columns(2)
    c1.metric("Cumulative Average", f"{perf['overall_average']}%")
    c2.metric("Overall Letter Grade", perf["overall_grade"])

    st.subheader("Subject-Wise Performance & Decline Alerts")
    for subj, s in perf["subjects"].items():
        with st.expander(f"{subj}: {s['average_percentage']}% ({s['status']})"):
            st.write(f"Assessments recorded: {s['assessment_count']}")
            if s["is_declining"]:
                st.error(f"Decline Warning: {s['decline_reason']}")
            else:
                st.success("Performance is stable or improving.")

    st.markdown("---")
    st.subheader("Target Score Calculator")
    st.caption("Determine the exact score required on an upcoming assessment to reach your target average.")

    subj_list = list(perf["subjects"].keys())
    if subj_list:
        sel_subj = st.selectbox("Subject", subj_list)
        c_t1, c_t2, c_t3 = st.columns(3)
        with c_t1:
            target_avg = st.number_input("Target Subject Average (%)", 50.0, 100.0, 80.0, 5.0)
        with c_t2:
            max_m = st.number_input("Upcoming Max Marks", 10.0, 100.0, 100.0, 10.0)
        with c_t3:
            weight = st.number_input("Upcoming Weightage (%)", 5.0, 60.0, 30.0, 5.0)

        if st.button("Calculate Required Score"):
            calc = PerformanceAnalyzerService.calculate_required_score(sel_subj, target_avg, max_m, weight)
            if calc["is_achievable"]:
                st.success(calc["advice"])
            else:
                st.error(calc["advice"])


# ================= VIEW 5: RESCUE MODE =================
elif nav_choice == "Academic Rescue Mode":
    st.title("Academic Rescue Mode")
    st.caption("Flagship Academic Triage: Identifies critical bottlenecks and recommends immediate high-impact actions.")

    threshold = float(db.get_setting("warning_threshold", "60.0"))
    rescue = AcademicRescueService.analyze_rescue_state(threshold)

    st.metric("Academic Crisis Index", f"{rescue['crisis_index']}/100", rescue["status_level"])
    st.info(f"**Guidance:** {rescue['action_statement']}")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Overdue Tasks", rescue["overdue_tasks_count"])
    c2.metric("Due in < 48 Hours", rescue["due_soon_count"])
    c3.metric("Vulnerable Subjects", len(rescue["vulnerable_subjects"]))
    c4.metric("Exams in < 10 Days", rescue["imminent_exams_count"])

    st.subheader("Triage Recommendations")
    if not rescue["top_recommendations"]:
        st.success("No academic crises detected! Your schedule is on track.")
    else:
        for idx, item in enumerate(rescue["top_recommendations"]):
            t = item["task"]
            with st.container():
                st.markdown(f"### Recommendation #{idx + 1}: {t['title']}")
                st.write(f"**Subject:** {t['subject']} &bull; **Deadline:** {t['deadline']} &bull; **Effort:** {t['estimated_effort']} hours")
                st.write(f"**Why Recommended:** {item['rationale']}")
                if st.button(f"Mark Task #{t['id']} Done & Recalculate", key=f"rescue_{t['id']}"):
                    planner.toggle_status(t["id"], "Completed")
                    st.success("Task resolved! Recalculating Rescue priorities...")
                    st.rerun()
                st.markdown("---")


# ================= VIEW 6: DSA LAB =================
elif nav_choice == "DSA Performance Lab":
    st.title("DSA Performance Lab (CO2 & CO3)")
    st.caption("Empirical Big-O performance evaluations executed with manual algorithms on scaling datasets.")

    d_size = st.select_slider("Choose Benchmark Dataset Size (N)", options=[100, 500, 1000, 2500, 5000], value=1000)

    tab1, tab2, tab3 = st.tabs(["Searching Comparison (CO3)", "Sorting Comparison (CO3)", "Storage Comparison (CO2)"])

    with tab1:
        st.subheader(f"Searching Comparison (N = {d_size})")
        if st.button("Run Search Benchmark"):
            with st.spinner("Executing benchmarks..."):
                s_res = DSALabService.run_searching_benchmark(d_size)

                df_s = pd.DataFrame([
                    {"Algorithm": "Linear Search (Array)", "Comparisons": s_res["linear_array"]["comparisons"], "Time (ms)": s_res["linear_array"]["time_ms"], "Complexity": "O(n)"},
                    {"Algorithm": "Linear Search (Linked List)", "Comparisons": s_res["linked_list_search"]["comparisons"], "Time (ms)": s_res["linked_list_search"]["time_ms"], "Complexity": "O(n)"},
                    {"Algorithm": "Binary Search (Sorted Array)", "Comparisons": s_res["binary_search"]["comparisons"], "Time (ms)": s_res["binary_search"]["time_ms"], "Complexity": "O(log n)"},
                ])
                st.dataframe(df_s, use_container_width=True)
                st.success(f"Binary Search achieved a {s_res['speedup_factor']}x speedup over sequential linear search.")

    with tab2:
        st.subheader(f"Sorting Comparison (N = {d_size})")
        if st.button("Run Sorting Benchmark"):
            with st.spinner("Sorting datasets..."):
                sort_res = DSALabService.run_sorting_benchmark(d_size)

                df_sort = pd.DataFrame([
                    {"Algorithm": "Bubble Sort", "Time (ms)": sort_res["bubble"]["time_ms"], "Comparisons": sort_res["bubble"]["comparisons"], "Complexity": "O(n^2)"},
                    {"Algorithm": "Insertion Sort", "Time (ms)": sort_res["insertion"]["time_ms"], "Comparisons": sort_res["insertion"]["comparisons"], "Complexity": "O(n^2)"},
                    {"Algorithm": "Merge Sort", "Time (ms)": sort_res["merge"]["time_ms"], "Comparisons": sort_res["merge"]["comparisons"], "Complexity": "O(n log n)"},
                ])
                st.dataframe(df_sort, use_container_width=True)

    with tab3:
        st.subheader("Storage Comparison: Singly Linked List vs Python Array")
        if st.button("Run Storage Benchmark"):
            st_res = DSALabService.run_storage_benchmark(d_size)
            st.metric("Linked List Head Insert", f"{st_res['linked_list_head_insert_ms']} ms", "O(1)")
            st.metric("Python Array Head Insert", f"{st_res['array_head_insert_ms']} ms", "O(n)", delta_color="inverse")
            st.info(st_res["explanation"])
