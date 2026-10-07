let students = [];
let selectedStudent = null;
let predictionCount = 0;

const pageNames = {
  overview: "Dashboard",
  students: "Student Intelligence",
  predict: "Predictive Analytics",
  ai: "Generative Assistant",
  records: "Academic Records",
  about: "About CampusAI"
};

function updateClock() {
  const e = document.getElementById("systemTime");
  if (!e) return;
  e.textContent = new Date().toLocaleTimeString([], {hour:"2-digit", minute:"2-digit"});
}
updateClock();
setInterval(updateClock, 30000);

document.querySelectorAll(".nav").forEach(btn => {
  btn.addEventListener("click", () => showPage(btn.dataset.page));
});

function showPage(id) {
  document.querySelectorAll(".page").forEach(p => p.classList.remove("active"));
  document.getElementById(id)?.classList.add("active");
  document.querySelectorAll(".nav").forEach(b => b.classList.toggle("active", b.dataset.page === id));
  const crumb = document.getElementById("crumb");
  if (crumb) crumb.textContent = pageNames[id] || "Overview";
  if (id === "students") renderStudents();
  if (id === "records") populateSelect();
  window.scrollTo({top: 0, behavior: "smooth"});
}

async function getJSON(url, options = {}) {
  const res = await fetch(url, options);
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "Request failed");
  return data;
}

async function loadOverview() {
  try {
    const x = await getJSON("/api/overview");
    document.getElementById("statStudents").textContent = x.students;
    document.getElementById("statAverage").textContent = x.average + "%";
    document.getElementById("statRisk").textContent = x.at_risk;
    renderRiskBars(x.summary.risk_labels, x.students);
  } catch (e) { console.error(e); }
}

function renderRiskBars(rows, total) {
  const el = document.getElementById("riskBars");
  if (!el) return;
  el.innerHTML = rows.map(r => `
    <div class="risk-row">
      <span>${r.label}</span>
      <div class="risk-track"><div class="risk-fill ${r.label.toLowerCase()}" style="width:${Math.max(3, r.count / Math.max(1,total) * 100)}%"></div></div>
      <b>${r.count}</b>
    </div>`).join("");
}

async function loadStudents() {
  try {
    students = await getJSON("/api/students");
    renderStudents();
    populateSelect();
  } catch (e) { console.error(e); }
}

function initials(name) {
  return name.split(" ").map(x => x[0]).slice(0,2).join("").toUpperCase();
}

function renderStudents(list = students) {
  const box = document.getElementById("studentList");
  if (!box) return;
  if (!list.length) {
    box.innerHTML = `<div class="tiny-note" style="padding:20px">No matching students.</div>`;
    return;
  }
  box.innerHTML = list.map(s => `
    <div class="student-card ${selectedStudent?.id === s.id ? "selected" : ""}" onclick="selectStudent(${s.id})">
      <div class="student-avatar">${initials(s.name)}</div>
      <div><b>${escapeHtml(s.name)}</b><small>${escapeHtml(s.course)} · ${escapeHtml(s.year)}</small></div>
      <span class="risk-mini ${s.prediction.risk.toLowerCase()}">${s.prediction.risk}</span>
    </div>`).join("");
}

function filterStudents() {
  const q = (document.getElementById("studentSearch")?.value || "").toLowerCase();
  renderStudents(students.filter(s => `${s.name} ${s.course} ${s.year}`.toLowerCase().includes(q)));
}

function selectStudent(id) {
  selectedStudent = students.find(x => x.id === id);
  if (!selectedStudent) return;
  renderStudents();
  renderStudentDetail(selectedStudent);
}

function renderStudentDetail(s, freshPrediction = null) {
  const p = freshPrediction || s.prediction;
  const box = document.getElementById("studentDetail");
  const factorHtml = p.factors.map(f => `<div class="factor"><b>${escapeHtml(f.label)}</b> — ${escapeHtml(f.text)}</div>`).join("");
  const actions = (p.recommendation?.actions || []).map(a => `<li>${escapeHtml(a)}</li>`).join("");
  box.className = "panel";
  box.innerHTML = `
    <div class="profile-head">
      <div class="profile-identity">
        <div class="profile-big">${initials(s.name)}</div>
        <div><h2>${escapeHtml(s.name)}</h2><p>${escapeHtml(s.course)} · ${escapeHtml(s.year)}</p></div>
      </div>
      <span class="risk-badge ${p.risk.toLowerCase()}">${p.risk} risk</span>
    </div>
    <div class="profile-metrics">
      ${metric("Attendance", s.attendance + "%")}
      ${metric("Study", s.study + "h")}
      ${metric("Assignments", s.assignments + "%")}
      ${metric("Quizzes", s.quiz + "%")}
      ${metric("Previous", s.previous + "%")}
    </div>
    <div class="prediction-result">
      <div class="eyebrow">PREDICTIVE AI RESULT</div>
      <div class="pred-score">${p.score}% <small>predicted outlook</small></div>
      <div class="confidence">Model confidence: ${p.confidence}% · ${escapeHtml(p.level)}</div>
      <div class="factor-list">${factorHtml}</div>
      <div class="support-box"><h4>Recommended intervention · ${p.recommendation.priority} priority</h4><ul>${actions}</ul><div class="tiny-note">Suggested review: ${p.recommendation.next_review}</div></div>
      <div class="detail-actions">
        <button class="btn btn-primary btn-small" onclick="runPrediction(${s.id})">↻ Re-run prediction</button>
        <button class="btn btn-small" onclick="generateMessage(${s.id})">✦ Generate support message</button>
      </div>
      <div id="generatedMessage"></div>
    </div>`;
}

function metric(label, value) {
  return `<div class="metric-box"><span>${label}</span><b>${value}</b></div>`;
}

async function runPrediction(id) {
  const s = students.find(x => x.id === id);
  if (!s) return;
  try {
    const p = await getJSON("/api/predict", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(s)
    });
    s.prediction = p;
    predictionCount++;
    selectedStudent = s;
    renderStudentDetail(s, p);
    loadOverview();
  } catch (e) {
    alert(e.message);
  }
}

async function generateMessage(id) {
  const s = students.find(x => x.id === id);
  if (!s) return;
  try {
    const x = await getJSON("/api/intervention-message", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({name:s.name, risk:s.prediction.risk, actions:s.prediction.recommendation.actions})
    });
    const el = document.getElementById("generatedMessage");
    if (el) el.innerHTML = `<div class="support-box"><h4>Generative AI · Draft message</h4><p style="font-size:10px;line-height:1.6;color:#6f7789">${escapeHtml(x.message)}</p></div>`;
  } catch (e) { alert(e.message); }
}

function populateSelect() {
  const e = document.getElementById("sid");
  if (!e) return;
  e.innerHTML = students.map(s => `<option value="${s.id}">${escapeHtml(s.name)}</option>`).join("");
}

async function saveRecord() {
  const d = {
    id: document.getElementById("sid").value,
    attendance: document.getElementById("a").value,
    study: document.getElementById("st").value,
    assignments: document.getElementById("ass").value,
    quiz: document.getElementById("q").value,
    previous: document.getElementById("pr").value
  };
  try {
    const x = await getJSON("/api/record", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify(d)
    });
    const idx = students.findIndex(s => s.id === x.student.id);
    if (idx >= 0) students[idx] = x.student;
    document.getElementById("saved").textContent = "Saved — predictive profile refreshed.";
    loadOverview();
    renderStudents();
  } catch (e) {
    document.getElementById("saved").textContent = e.message;
  }
}

function addMessage(t, user = false) {
  const messages = document.getElementById("messages");
  if (!messages) return;
  const d = document.createElement("div");
  d.className = "message " + (user ? "user" : "ai");
  d.innerHTML = `<div class="msg-avatar">${user ? "You" : "✦"}</div><div><b>${user ? "You" : "CampusAI"}</b><p>${escapeHtml(t)}</p></div>`;
  messages.appendChild(d);
  messages.scrollTop = messages.scrollHeight;
}

async function sendChat() {
  const e = document.getElementById("chatInput");
  const t = e.value.trim();
  if (!t) return;
  e.value = "";
  addMessage(t, true);
  try {
    const x = await getJSON("/api/chat", {
      method:"POST", headers:{"Content-Type":"application/json"},
      body:JSON.stringify({message:t, student:selectedStudent})
    });
    addMessage(x.answer);
  } catch (err) {
    addMessage("I couldn't process that request. Please try again.");
  }
}

function quick(t) {
  const e = document.getElementById("chatInput");
  if (e) { e.value = t; sendChat(); }
}

async function makePlan() {
  const topic = document.getElementById("topic").value || "your topic";
  const hours = document.getElementById("hours").value || 6;
  try {
    const x = await getJSON("/api/study-plan", {
      method:"POST", headers:{"Content-Type":"application/json"},
      body:JSON.stringify({topic,hours})
    });
    document.getElementById("planout").innerHTML = x.plan.map(v => `
      <div class="plan-step"><div class="plan-day">${v.day}</div><div><b>${v.duration} min</b><small>${escapeHtml(v.task)}</small></div></div>`).join("");
  } catch (e) { alert(e.message); }
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, m => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[m]));
}

loadOverview();
loadStudents();
