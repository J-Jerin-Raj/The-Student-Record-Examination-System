/**
 * Acadence - Student Academic & Examination Assistant
 * Frontend Application Controller
 * Handles data fetching, UI transitions, modals, live timers, and DSA lab benchmarks.
 */

// Global Application State
const state = {
  currentView: "dashboard",
  tasks: [],
  exams: [],
  requests: { pending: [], history: [] },
  settings: { warning_threshold: 60.0, target_percentage: 80.0, theme: "dark" },
  activeTimerInterval: null,
};

// ---------------- Initialization ----------------
document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  initSidebar();
  loadSettings();
  switchView("dashboard");
});

function initTheme() {
  const saved = localStorage.getItem("acadence_theme") || "dark";
  document.documentElement.setAttribute("data-theme", saved);
  state.settings.theme = saved;
}

function toggleTheme() {
  const current = document.documentElement.getAttribute("data-theme") || "dark";
  const target = current === "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", target);
  localStorage.setItem("acadence_theme", target);
  state.settings.theme = target;
  showToast(`Switched to ${target} mode`);
}

function initSidebar() {
  const toggleBtn = document.getElementById("btnSidebarToggle");
  const sidebar = document.getElementById("mainSidebar");
  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener("click", () => {
      sidebar.classList.toggle("collapsed");
    });
  }
}

function showToast(message) {
  const toast = document.getElementById("toast");
  if (toast) {
    toast.textContent = message;
    toast.style.display = "block";
    setTimeout(() => {
      toast.style.display = "none";
    }, 3000);
  }
}

// ---------------- View Navigation ----------------
function switchView(viewName) {
  state.currentView = viewName;

  // Update nav buttons
  document.querySelectorAll(".nav-item button").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.view === viewName);
  });

  // Update views
  document.querySelectorAll(".view-section").forEach((sec) => {
    sec.style.display = sec.id === `view-${viewName}` ? "block" : "none";
  });

  // Update top header title
  const titles = {
    dashboard: "Academic Dashboard",
    planner: "Smart Academic Planner",
    exams: "Examination Management",
    performance: "Performance Analyzer",
    rescue: "Academic Rescue Mode",
    dsalab: "DSA Performance Lab",
  };
  const titleEl = document.getElementById("topPageTitle");
  if (titleEl) titleEl.textContent = titles[viewName] || "Acadence";

  // Load view-specific data
  if (viewName === "dashboard") loadDashboard();
  else if (viewName === "planner") loadPlanner();
  else if (viewName === "exams") loadExams();
  else if (viewName === "performance") loadPerformance();
  else if (viewName === "rescue") loadRescueMode();
  else if (viewName === "dsalab") loadDSALab();

  // Always refresh top undo button state
  refreshUndoState();
}

async function loadSettings() {
  try {
    const res = await fetch("/api/settings");
    if (res.ok) {
      state.settings = await res.json();
    }
  } catch (err) {
    console.error("Failed to load settings:", err);
  }
}

async function refreshUndoState() {
  try {
    const res = await fetch("/api/undo/peek");
    const data = await res.json();
    const undoBtn = document.getElementById("btnTopUndo");
    if (undoBtn) {
      undoBtn.disabled = !data.has_undo;
      undoBtn.title = data.has_undo ? `Undo: ${data.description}` : "No actions to undo";
    }
  } catch (err) {
    console.error("Failed to peek undo:", err);
  }
}

async function triggerUndo() {
  try {
    const res = await fetch("/api/undo", { method: "POST" });
    const data = await res.json();
    showToast(data.message);
    refreshUndoState();
    // Reload current view to reflect reversion
    switchView(state.currentView);
  } catch (err) {
    showToast("Undo failed");
  }
}

// ---------------- 1. Dashboard View ----------------
async function loadDashboard() {
  try {
    const res = await fetch("/api/dashboard");
    const data = await res.json();

    // 1. Task Metrics
    const tm = data.task_metrics;
    document.getElementById("statPending").textContent = tm.pending;
    document.getElementById("statInProgress").textContent = tm.in_progress;
    document.getElementById("statCompleted").textContent = tm.completed;
    document.getElementById("statOverdue").textContent = tm.overdue;

    // 2. Exam Conflicts Warning
    const conflictBox = document.getElementById("dashConflictAlert");
    if (data.exam_conflicts && data.exam_conflicts.length > 0) {
      conflictBox.style.display = "block";
      conflictBox.innerHTML = `
        <strong>Warning: Examination Schedule Clash Detected!</strong><br>
        Clashing slots: ${data.exam_conflicts.map((c) => c.slot1 + " vs " + c.slot2).join("; ")}
      `;
    } else {
      conflictBox.style.display = "none";
    }

    // 3. Next Exam Countdown
    renderCountdown(data.next_exam_countdown);

    // 4. Academic Performance Overview
    const perf = data.performance_summary;
    document.getElementById("dashOverallAvg").textContent = `${perf.overall_average}%`;
    document.getElementById("dashOverallGrade").textContent = perf.overall_grade;
    document.getElementById("dashVulnerableCount").textContent = `${perf.vulnerable_subjects_count} subjects need attention`;

    // 5. Academic Rescue Overview
    const r = data.rescue_summary;
    document.getElementById("dashCrisisScore").textContent = `${r.crisis_index}/100`;
    document.getElementById("dashCrisisLevel").textContent = r.status_level;
    document.getElementById("dashRescueAdvice").textContent = r.action_statement;

    // 6. "What Should I Do Next?"
    const nextList = document.getElementById("dashNextTasksList");
    nextList.innerHTML = "";
    if (!data.what_to_do_next || data.what_to_do_next.length === 0) {
      nextList.innerHTML = `<div style="color: var(--text-dim); padding: 12px 0;">All caught up! No high-priority pending tasks.</div>`;
    } else {
      data.what_to_do_next.forEach((item, idx) => {
        const t = item.task;
        const div = document.createElement("div");
        div.className = "card";
        div.style.marginBottom = "10px";
        div.style.padding = "14px";
        div.style.background = "var(--surface-hover)";

        div.innerHTML = `
          <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 8px;">
            <div>
              <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                <span class="badge ${getPriorityBadge(t.priority)}">${t.priority}</span>
                <span style="font-size: 0.75rem; color: var(--text-dim);">${t.subject}</span>
              </div>
              <strong style="font-size: 0.92rem; color: var(--text-main);">${idx + 1}. ${t.title}</strong>
              <div style="font-size: 0.78rem; color: var(--text-muted); margin-top: 4px;">
                <strong>Why prioritized:</strong> ${item.rationale}
              </div>
            </div>
            <button class="btn btn-primary" style="padding: 4px 10px; font-size: 0.75rem;" onclick="quickCompleteTask(${t.id})">Mark Done</button>
          </div>
        `;
        nextList.appendChild(div);
      });
    }
  } catch (err) {
    console.error("Failed to load dashboard:", err);
  }
}

function renderCountdown(countdown) {
  const banner = document.getElementById("dashCountdownBanner");
  if (!countdown) {
    banner.style.display = "none";
    return;
  }
  banner.style.display = "flex";
  document.getElementById("nextExamSubject").textContent = countdown.exam.subject;
  document.getElementById("nextExamTimeVenue").textContent = `${countdown.target_datetime} (${countdown.exam.venue})`;

  document.getElementById("cdDays").textContent = String(countdown.days).padStart(2, "0");
  document.getElementById("cdHours").textContent = String(countdown.hours).padStart(2, "0");
  document.getElementById("cdMins").textContent = String(countdown.minutes).padStart(2, "0");
}

async function quickCompleteTask(taskId) {
  try {
    const res = await fetch(`/api/tasks/${taskId}/status`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: "Completed" }),
    });
    const data = await res.json();
    showToast(data.message);
    refreshUndoState();
    loadDashboard();
  } catch (err) {
    showToast("Failed to update task");
  }
}

// ---------------- 2. Academic Planner View ----------------
async function loadPlanner() {
  const statusFilter = document.getElementById("plannerStatusFilter")?.value || "All";
  const subjectFilter = document.getElementById("plannerSubjectFilter")?.value || "All";

  try {
    const res = await fetch(`/api/tasks?status=${encodeURIComponent(statusFilter)}&subject=${encodeURIComponent(subjectFilter)}`);
    const tasks = await res.json();
    state.tasks = tasks;

    const tbody = document.getElementById("plannerTasksTbody");
    tbody.innerHTML = "";

    if (tasks.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--text-dim); padding: 24px;">No tasks found matching criteria.</td></tr>`;
      return;
    }

    tasks.forEach((t) => {
      const tr = document.createElement("tr");
      const overdueTag = t.is_overdue ? `<span class="badge badge-critical" style="margin-left: 6px;">Overdue</span>` : "";

      tr.innerHTML = `
        <td><strong>${t.title}</strong></td>
        <td>${t.subject}</td>
        <td><span class="badge ${getPriorityBadge(t.priority)}">${t.priority}</span></td>
        <td>${t.deadline} ${overdueTag}</td>
        <td>${t.estimated_effort}h</td>
        <td>
          <select onchange="updateTaskStatus(${t.id}, this.value)" style="margin: 0; padding: 4px 8px; font-size: 0.78rem;">
            <option value="Pending" ${t.status === "Pending" ? "selected" : ""}>Pending</option>
            <option value="In Progress" ${t.status === "In Progress" ? "selected" : ""}>In Progress</option>
            <option value="Completed" ${t.status === "Completed" ? "selected" : ""}>Completed</option>
          </select>
        </td>
        <td>
          <button class="btn btn-danger" style="padding: 2px 6px; font-size: 0.72rem;" onclick="deleteTask(${t.id})">Delete</button>
        </td>
      `;
      tbody.appendChild(tr);
    });

    // Populate subject filter dropdown if empty
    populateSubjectDropdown("plannerSubjectFilter", tasks);
  } catch (err) {
    console.error("Failed to load planner:", err);
  }
}

async function updateTaskStatus(taskId, newStatus) {
  try {
    const res = await fetch(`/api/tasks/${taskId}/status`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: newStatus }),
    });
    const data = await res.json();
    showToast(data.message);
    refreshUndoState();
    loadPlanner();
  } catch (err) {
    showToast("Status update failed");
  }
}

async function deleteTask(taskId) {
  if (!confirm("Delete this task? Operation can be reversed via Undo.")) return;
  try {
    const res = await fetch(`/api/tasks/${taskId}`, { method: "DELETE" });
    const data = await res.json();
    showToast(data.message);
    refreshUndoState();
    loadPlanner();
  } catch (err) {
    showToast("Delete failed");
  }
}

async function calculateDailySchedule() {
  const hoursInput = document.getElementById("dailyHoursInput");
  const hours = parseFloat(hoursInput?.value || "3.5");

  try {
    const res = await fetch(`/api/planner/daily-schedule?hours=${hours}`);
    const data = await res.json();

    const container = document.getElementById("dailyScheduleResults");
    container.style.display = "block";
    document.getElementById("dailyHoursAllocated").textContent = `${data.allocated_hours} of ${data.available_hours} hours planned (${data.selected_count} tasks)`;

    const list = document.getElementById("dailyScheduleList");
    list.innerHTML = "";

    if (data.tasks.length === 0) {
      list.innerHTML = `<div style="color: var(--text-dim); padding: 8px;">No suitable pending tasks fit into this study duration.</div>`;
      return;
    }

    data.tasks.forEach((item, idx) => {
      const t = item.task;
      const card = document.createElement("div");
      card.className = "card";
      card.style.marginBottom = "8px";
      card.style.padding = "12px";
      card.style.background = "var(--surface-hover)";
      card.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <div>
            <strong style="font-size: 0.9rem;">${idx + 1}. ${t.title}</strong>
            <span style="font-size: 0.75rem; color: var(--text-dim); margin-left: 8px;">[${t.subject} - ${t.estimated_effort}h]</span>
            <div style="font-size: 0.78rem; color: var(--text-muted); margin-top: 3px;">
              <strong>Rationale:</strong> ${item.rationale}
            </div>
          </div>
          <span class="badge ${getPriorityBadge(t.priority)}">${t.priority}</span>
        </div>
      `;
      list.appendChild(card);
    });
  } catch (err) {
    showToast("Failed to calculate study schedule");
  }
}

// ---------------- 3. Examinations View ----------------
async function loadExams() {
  const sortBy = document.getElementById("examSortBy")?.value || "date";
  const algo = document.getElementById("examSortAlgo")?.value || "merge";

  try {
    const res = await fetch(`/api/exams?sort_by=${sortBy}&algorithm=${algo}`);
    const exams = await res.json();
    state.exams = exams;

    const tbody = document.getElementById("examsTbody");
    tbody.innerHTML = "";

    if (exams.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--text-dim); padding: 24px;">No exams scheduled.</td></tr>`;
      return;
    }

    exams.forEach((e) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td><strong>${e.subject}</strong></td>
        <td>${e.exam_date}</td>
        <td>${e.start_time} - ${e.end_time}</td>
        <td>${e.venue}</td>
        <td>
          <div style="display: flex; align-items: center; gap: 8px;">
            <div style="flex: 1; background: var(--bg-color); height: 6px; border-radius: 3px; overflow: hidden;">
              <div style="width: ${e.revision_progress}%; background: var(--primary); height: 100%;"></div>
            </div>
            <span style="font-size: 0.75rem; font-weight: 600;">${e.revision_progress}%</span>
          </div>
        </td>
        <td><span class="badge ${getPriorityBadge(e.priority)}">${e.priority}</span></td>
        <td>
          <button class="btn btn-danger" style="padding: 2px 6px; font-size: 0.72rem;" onclick="deleteExam(${e.id})">Delete</button>
        </td>
      `;
      tbody.appendChild(tr);
    });

    // Load Requests Queue
    loadRequestsQueue();
  } catch (err) {
    console.error("Failed to load exams:", err);
  }
}

async function deleteExam(examId) {
  if (!confirm("Remove this exam from schedule?")) return;
  try {
    const res = await fetch(`/api/exams/${examId}`, { method: "DELETE" });
    const data = await res.json();
    showToast(data.message);
    loadExams();
  } catch (err) {
    showToast("Failed to delete exam");
  }
}

async function loadRequestsQueue() {
  try {
    const res = await fetch("/api/requests");
    const data = await res.json();
    state.requests = data;

    const track = document.getElementById("examQueueTrack");
    track.innerHTML = "";

    if (data.pending.length === 0) {
      track.innerHTML = `<div style="color: var(--text-dim); padding: 10px; font-size: 0.8rem;">[ Academic Request Queue is Empty ]</div>`;
    } else {
      data.pending.forEach((r, idx) => {
        const isFront = idx === 0;
        const div = document.createElement("div");
        div.style.background = isFront ? "var(--surface-hover)" : "var(--surface-color)";
        div.style.border = `1px solid ${isFront ? "var(--primary)" : "var(--border-color)"}`;
        div.style.borderRadius = "var(--radius-md)";
        div.style.padding = "10px 14px";
        div.style.minWidth = "180px";
        div.style.flexShrink = "0";

        div.innerHTML = `
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
            <strong style="color: var(--primary); font-size: 0.8rem;">${r.request_id}</strong>
            ${isFront ? '<span class="badge badge-medium" style="font-size: 0.65rem;">FRONT</span>' : ""}
          </div>
          <div style="font-weight: 600; font-size: 0.82rem;">${r.student_name}</div>
          <div style="font-size: 0.72rem; color: var(--text-muted);">${r.request_type} (${r.subject})</div>
        `;
        track.appendChild(div);
      });
    }

    // Processed history
    const hTbody = document.getElementById("examQueueHistoryTbody");
    hTbody.innerHTML = "";
    data.history.forEach((h) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td><strong>${h.request_id}</strong></td>
        <td>${h.student_name}</td>
        <td>${h.request_type}</td>
        <td>${h.subject}</td>
        <td><span class="badge badge-success">Processed</span></td>
      `;
      hTbody.appendChild(tr);
    });
  } catch (err) {
    console.error("Failed to load requests queue:", err);
  }
}

async function processQueueItem() {
  try {
    const res = await fetch("/api/requests/process", { method: "POST" });
    const data = await res.json();
    showToast(data.message);
    loadRequestsQueue();
  } catch (err) {
    showToast("Processing queue failed");
  }
}

// ---------------- 4. Performance View ----------------
async function loadPerformance() {
  try {
    const res = await fetch("/api/performance");
    const data = await res.json();

    document.getElementById("perfSummaryAvg").textContent = `${data.overall_average}%`;
    document.getElementById("perfSummaryGrade").textContent = data.overall_grade;

    const grid = document.getElementById("perfSubjectGrid");
    grid.innerHTML = "";

    const subjects = Object.values(data.subjects);
    if (subjects.length === 0) {
      grid.innerHTML = `<div style="color: var(--text-dim); padding: 20px;">No assessment records found. Click 'Record Assessment' to begin tracking.</div>`;
      return;
    }

    subjects.forEach((s) => {
      const card = document.createElement("div");
      card.className = "card";
      card.style.background = "var(--surface-hover)";

      const declineAlert = s.is_declining
        ? `<div style="margin-top: 8px; padding: 6px 10px; background: rgba(239, 68, 68, 0.1); border-left: 3px solid var(--danger); font-size: 0.75rem; color: var(--danger);">
             <strong>Decline Alert:</strong> ${s.decline_reason}
           </div>`
        : "";

      card.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
          <div>
            <strong style="font-size: 0.95rem; color: var(--text-main);">${s.subject}</strong>
            <div style="font-size: 0.75rem; color: var(--text-dim);">${s.assessment_count} assessments recorded</div>
          </div>
          <span class="badge ${getStatusBadge(s.status)}">${s.status}</span>
        </div>
        <div style="display: flex; align-items: baseline; gap: 8px; margin: 8px 0;">
          <span style="font-size: 1.6rem; font-weight: 700; color: var(--primary);">${s.average_percentage}%</span>
          <span style="font-size: 0.75rem; color: var(--text-muted);">avg score</span>
        </div>
        ${declineAlert}
      `;
      grid.appendChild(card);
    });

    // Populate Target Score Subject Select
    const targetSelect = document.getElementById("targetScoreSubject");
    if (targetSelect) {
      targetSelect.innerHTML = "";
      subjects.forEach((s) => {
        const opt = document.createElement("option");
        opt.value = s.subject;
        opt.textContent = `${s.subject} (Current: ${s.average_percentage}%)`;
        targetSelect.appendChild(opt);
      });
    }

    // Load Revision Priorities
    loadRevisionPriorities();
  } catch (err) {
    console.error("Failed to load performance:", err);
  }
}

async function loadRevisionPriorities() {
  try {
    const res = await fetch("/api/performance/revision-priorities");
    const data = await res.json();
    const tbody = document.getElementById("revisionPrioritiesTbody");
    tbody.innerHTML = "";

    data.forEach((r, idx) => {
      const tr = document.createElement("tr");
      const daysText = r.days_to_exam !== null ? `${r.days_to_exam} days remaining` : "No upcoming exam";
      tr.innerHTML = `
        <td><strong>#${idx + 1}</strong></td>
        <td><strong>${r.subject}</strong></td>
        <td>${r.average_percentage}%</td>
        <td><span class="badge ${getStatusBadge(r.status)}">${r.status}</span></td>
        <td>${daysText}</td>
        <td>${r.revision_progress}%</td>
        <td><strong>${r.priority_score}</strong></td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error("Failed to load revision priorities:", err);
  }
}

async function calculateTargetScore() {
  const subject = document.getElementById("targetScoreSubject")?.value;
  const targetAvg = parseFloat(document.getElementById("targetScoreInput")?.value || "80.0");
  const maxMarks = parseFloat(document.getElementById("targetMaxMarks")?.value || "100.0");
  const weight = parseFloat(document.getElementById("targetWeightage")?.value || "30.0");

  try {
    const res = await fetch("/api/performance/target-score", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        subject: subject,
        target_average: targetAvg,
        upcoming_max_marks: maxMarks,
        upcoming_weightage: weight,
      }),
    });
    const data = await res.json();

    const box = document.getElementById("targetScoreResultBox");
    box.style.display = "block";
    box.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
        <strong>Target Analysis: ${data.subject}</strong>
        <span class="badge ${data.is_achievable ? "badge-success" : "badge-critical"}">
          ${data.is_achievable ? "Mathematically Attainable" : "Exceeds Maximum Possible"}
        </span>
      </div>
      <p style="font-size: 0.85rem; color: var(--text-main); margin-bottom: 8px;">${data.advice}</p>
      <div style="font-size: 0.78rem; color: var(--text-dim);">
        Current Avg: ${data.current_average}% | Desired Avg: ${data.target_average}% | Required Score: ${data.required_marks} / ${data.upcoming_max_marks}
      </div>
    `;
  } catch (err) {
    showToast("Calculation failed");
  }
}

// ---------------- 5. Academic Rescue Mode View ----------------
async function loadRescueMode() {
  try {
    const res = await fetch("/api/rescue");
    const data = await res.json();

    document.getElementById("rescueCrisisIndex").textContent = `${data.crisis_index} / 100`;
    document.getElementById("rescueStatusLevel").textContent = data.status_level;
    document.getElementById("rescueActionStatement").textContent = data.action_statement;

    document.getElementById("rescueOverdueCount").textContent = data.overdue_tasks_count;
    document.getElementById("rescueDueSoonCount").textContent = data.due_soon_count;
    document.getElementById("rescueVulnerableCount").textContent = data.vulnerable_subjects.length;
    document.getElementById("rescueImminentExamsCount").textContent = data.imminent_exams_count;

    const recContainer = document.getElementById("rescueRecommendationsList");
    recContainer.innerHTML = "";

    if (data.top_recommendations.length === 0) {
      recContainer.innerHTML = `
        <div style="text-align: center; color: var(--text-muted); padding: 30px;">
          No critical academic emergencies detected. Your current deadlines and subjects are within healthy thresholds.
        </div>
      `;
      return;
    }

    data.top_recommendations.forEach((item, idx) => {
      const t = item.task;
      const card = document.createElement("div");
      card.className = "card";
      card.style.background = "var(--surface-hover)";
      card.style.borderLeft = `4px solid ${idx === 0 ? "var(--danger)" : "var(--warning)"}`;
      card.style.marginBottom = "14px";
      card.style.padding = "16px";

      card.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; flex-wrap: wrap;">
          <div style="flex: 1;">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
              <span class="badge ${getPriorityBadge(t.priority)}">${t.priority}</span>
              <strong style="color: var(--primary); font-size: 0.85rem;">${t.subject}</strong>
              <span style="font-size: 0.75rem; color: var(--text-dim);">(Rescue Score: ${item.rescue_score})</span>
            </div>
            <h4 style="font-size: 1rem; color: var(--text-main); margin-bottom: 6px;">
              Recommendation #${idx + 1}: ${t.title}
            </h4>
            <div style="font-size: 0.82rem; color: var(--text-muted); margin-bottom: 4px;">
              <strong>Action Rationale:</strong> ${item.rationale}
            </div>
            <div style="font-size: 0.78rem; color: var(--text-dim);">
              Deadline: ${t.deadline} | Estimated Work: ${t.estimated_effort} hours
            </div>
          </div>
          <div>
            <button class="btn btn-success" onclick="rescueMarkComplete(${t.id})">Mark Completed & Recalculate</button>
          </div>
        </div>
      `;
      recContainer.appendChild(card);
    });
  } catch (err) {
    console.error("Failed to load rescue mode:", err);
  }
}

async function rescueMarkComplete(taskId) {
  try {
    const res = await fetch(`/api/tasks/${taskId}/status`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: "Completed" }),
    });
    const data = await res.json();
    showToast(`Task resolved! Recalculating Rescue priorities...`);
    refreshUndoState();
    loadRescueMode();
  } catch (err) {
    showToast("Failed to complete task");
  }
}

// ---------------- 6. DSA Performance Lab View ----------------
async function runSearchBenchmark() {
  const size = parseInt(document.getElementById("dsaDatasetSize")?.value || "1000");
  try {
    const res = await fetch("/api/dsa/search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ size: size }),
    });
    const data = await res.json();

    document.getElementById("dsaSearchResultsBox").style.display = "block";
    const tbody = document.getElementById("dsaSearchTbody");
    tbody.innerHTML = `
      <tr>
        <td><strong>Linear Search</strong></td>
        <td>Python Array / List</td>
        <td>${data.linear_array.comparisons}</td>
        <td>${data.linear_array.time_ms} ms</td>
        <td><code>${data.linear_array.complexity}</code></td>
      </tr>
      <tr>
        <td><strong>Linear Search</strong></td>
        <td>Singly Linked List (Node Traversal)</td>
        <td>${data.linked_list_search.comparisons}</td>
        <td>${data.linked_list_search.time_ms} ms</td>
        <td><code>${data.linked_list_search.complexity}</code></td>
      </tr>
      <tr>
        <td><strong style="color: var(--primary);">Binary Search</strong></td>
        <td>Sorted Array (O(1) Middle Index)</td>
        <td><strong style="color: var(--primary);">${data.binary_search.comparisons}</strong></td>
        <td><strong style="color: var(--primary);">${data.binary_search.time_ms} ms</strong></td>
        <td><code>${data.binary_search.complexity}</code></td>
      </tr>
    `;

    document.getElementById("dsaSearchSpeedup").textContent = `Binary Search achieved a ${data.speedup_factor}x speedup over sequential linear search at N=${data.dataset_size}.`;
  } catch (err) {
    showToast("Search benchmark failed");
  }
}

async function runSortBenchmark() {
  const size = parseInt(document.getElementById("dsaDatasetSize")?.value || "1000");
  try {
    const res = await fetch("/api/dsa/sort", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ size: size }),
    });
    const data = await res.json();

    document.getElementById("dsaSortResultsBox").style.display = "block";
    const tbody = document.getElementById("dsaSortTbody");
    tbody.innerHTML = `
      <tr>
        <td><strong>Bubble Sort</strong></td>
        <td>${data.bubble.time_ms} ms</td>
        <td>${data.bubble.comparisons}</td>
        <td>${data.bubble.swaps}</td>
        <td><code>${data.bubble.complexity}</code></td>
      </tr>
      <tr>
        <td><strong>Insertion Sort</strong></td>
        <td>${data.insertion.time_ms} ms</td>
        <td>${data.insertion.comparisons}</td>
        <td>${data.insertion.swaps}</td>
        <td><code>${data.insertion.complexity}</code></td>
      </tr>
      <tr>
        <td><strong style="color: var(--primary);">Merge Sort</strong></td>
        <td><strong style="color: var(--primary);">${data.merge.time_ms} ms</strong></td>
        <td>${data.merge.comparisons}</td>
        <td>${data.merge.swaps}</td>
        <td><code>${data.merge.complexity}</code></td>
      </tr>
    `;
  } catch (err) {
    showToast("Sort benchmark failed");
  }
}

async function runStorageBenchmark() {
  try {
    const res = await fetch("/api/dsa/storage", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ size: 3000 }),
    });
    const data = await res.json();

    const box = document.getElementById("dsaStorageResultsBox");
    box.style.display = "block";
    box.innerHTML = `
      <div style="margin-bottom: 8px;"><strong>CO2 Evaluation: Head Insertion (Index 0) at N = ${data.dataset_size}</strong></div>
      <div class="grid-2" style="margin-bottom: 10px;">
        <div class="stat-box">
          <div class="stat-value" style="color: var(--success);">${data.linked_list_head_insert_ms} ms</div>
          <div class="stat-label">Singly Linked List (Pointer Relinking O(1))</div>
        </div>
        <div class="stat-box">
          <div class="stat-value" style="color: var(--danger);">${data.array_head_insert_ms} ms</div>
          <div class="stat-label">Python Array (Contiguous Element Shifting O(n))</div>
        </div>
      </div>
      <p style="font-size: 0.82rem; color: var(--text-muted);">${data.explanation}</p>
    `;
  } catch (err) {
    showToast("Storage benchmark failed");
  }
}

// ---------------- Admin & Modals ----------------
async function resetDemoData() {
  if (!confirm("Reset database with fresh sample student academic data?")) return;
  try {
    const res = await fetch("/api/admin/reset-demo", { method: "POST" });
    const data = await res.json();
    showToast(data.message);
    switchView(state.currentView);
  } catch (err) {
    showToast("Reset failed");
  }
}

async function clearAllData() {
  if (!confirm("Clear ALL data from database? This creates a completely empty workspace.")) return;
  try {
    const res = await fetch("/api/admin/clear-data", { method: "POST" });
    const data = await res.json();
    showToast(data.message);
    switchView(state.currentView);
  } catch (err) {
    showToast("Clear failed");
  }
}

function openModal(id) {
  const el = document.getElementById(id);
  if (el) el.style.display = "flex";
}

function closeModal(id) {
  const el = document.getElementById(id);
  if (el) el.style.display = "none";
}

// Form Handlers
async function handleAddTask(e) {
  e.preventDefault();
  const payload = {
    title: document.getElementById("taskFormTitle").value,
    subject: document.getElementById("taskFormSubject").value,
    task_type: document.getElementById("taskFormType").value,
    deadline: document.getElementById("taskFormDeadline").value,
    estimated_effort: parseFloat(document.getElementById("taskFormEffort").value),
    priority: document.getElementById("taskFormPriority").value,
    notes: document.getElementById("taskFormNotes").value,
  };

  try {
    const res = await fetch("/api/tasks", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    showToast(data.message);
    closeModal("modalAddTask");
    document.getElementById("formAddTask").reset();
    refreshUndoState();
    if (state.currentView === "planner") loadPlanner();
    else if (state.currentView === "dashboard") loadDashboard();
  } catch (err) {
    showToast("Failed to create task");
  }
}

async function handleAddExam(e) {
  e.preventDefault();
  const payload = {
    subject: document.getElementById("examFormSubject").value,
    exam_date: document.getElementById("examFormDate").value,
    start_time: document.getElementById("examFormStartTime").value,
    end_time: document.getElementById("examFormEndTime").value,
    venue: document.getElementById("examFormVenue").value,
    syllabus: document.getElementById("examFormSyllabus").value,
    revision_progress: parseFloat(document.getElementById("examFormRevision").value),
    priority: document.getElementById("examFormPriority").value,
  };

  try {
    const res = await fetch("/api/exams", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    showToast(data.message);
    closeModal("modalAddExam");
    document.getElementById("formAddExam").reset();
    if (state.currentView === "exams") loadExams();
    else if (state.currentView === "dashboard") loadDashboard();
  } catch (err) {
    showToast("Failed to add exam");
  }
}

async function handleAddAssessment(e) {
  e.preventDefault();
  const payload = {
    subject: document.getElementById("assessFormSubject").value,
    assessment_name: document.getElementById("assessFormName").value,
    assessment_type: document.getElementById("assessFormType").value,
    max_marks: parseFloat(document.getElementById("assessFormMax").value),
    marks_obtained: parseFloat(document.getElementById("assessFormMarks").value),
    weightage: parseFloat(document.getElementById("assessFormWeight").value),
    assessment_date: document.getElementById("assessFormDate").value,
  };

  try {
    const res = await fetch("/api/assessments", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    showToast(data.message);
    closeModal("modalAddAssessment");
    document.getElementById("formAddAssessment").reset();
    if (state.currentView === "performance") loadPerformance();
    else if (state.currentView === "dashboard") loadDashboard();
  } catch (err) {
    showToast("Failed to record marks");
  }
}

async function handleEnqueueRequest(e) {
  e.preventDefault();
  const payload = {
    student_name: document.getElementById("reqFormName").value,
    request_type: document.getElementById("reqFormType").value,
    subject: document.getElementById("reqFormSubject").value,
    details: document.getElementById("reqFormDetails").value,
  };

  try {
    const res = await fetch("/api/requests", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    showToast(`Request ${data.request.request_id} enqueued at rear of FIFO Queue.`);
    document.getElementById("formEnqueueRequest").reset();
    loadRequestsQueue();
  } catch (err) {
    showToast("Failed to enqueue request");
  }
}

// ---------------- Helpers ----------------
function getPriorityBadge(priority) {
  switch (priority) {
    case "Critical": return "badge-critical";
    case "High": return "badge-high";
    case "Medium": return "badge-medium";
    case "Low": return "badge-low";
    default: return "badge-medium";
  }
}

function getStatusBadge(status) {
  switch (status) {
    case "Critical": return "badge-critical";
    case "Vulnerable": return "badge-high";
    case "Proficient": return "badge-medium";
    case "Exemplary": return "badge-success";
    default: return "badge-medium";
  }
}

function populateSubjectDropdown(elementId, items) {
  const el = document.getElementById(elementId);
  if (!el || el.options.length > 1) return;
  const unique = [...new Set(items.map((i) => i.subject))];
  unique.forEach((s) => {
    const opt = document.createElement("option");
    opt.value = s;
    opt.textContent = s;
    el.appendChild(opt);
  });
}
