/**
 * Master JavaScript Controller — Stickman AI Video Studio (Autonomous YouTube Engine).
 * Orchestrates all 16 Studio Sections, background job polling, YouTube OAuth,
 * topic discovery, and 1-click video production.
 */

let currentScriptData = null;
let currentTaskId = null;
let pollingInterval = null;
let studioPollInterval = null;

document.addEventListener("DOMContentLoaded", () => {
    initStudio();
});

async function initStudio() {
    setupNavigationTabs();
    setupEventListeners();
    setupAutomationControls();

    // Initial data fetch
    await refreshSystemStatus();
    await loadRecentJobs();
    await loadTopicQueue();
    await loadVideosLibrary();
    await loadPublishingQueue();
    await loadYouTubeChannelInfo();
    await loadCostReport();
    await loadPlatformSettings();
    await loadTrendRadar();

    // Start background status polling (every 3 seconds)
    studioPollInterval = setInterval(refreshSystemStatus, 3000);
}

// ========================================================
// 1. STUDIO 16-SECTION NAVIGATION TABS
// ========================================================
function setupNavigationTabs() {
    const tabs = document.querySelectorAll(".nav-tab");
    tabs.forEach(tab => {
        tab.addEventListener("click", () => {
            tabs.forEach(t => t.classList.remove("active"));
            tab.classList.add("active");

            const targetId = tab.getAttribute("data-target");
            document.querySelectorAll(".studio-section").forEach(sec => {
                sec.classList.remove("active");
            });

            const targetSection = document.getElementById(targetId);
            if (targetSection) {
                targetSection.classList.add("active");
            }
        });
    });
}

// ========================================================
// 2. REAL-TIME SYSTEM STATUS & DASHBOARD POLLING
// ========================================================
async function refreshSystemStatus() {
    try {
        const res = await fetch("/api/automation/status");
        if (!res.ok) return;
        const data = await res.json();
        const sched = data.scheduler || {};
        const activeJob = data.active_job;

        // Header Chips
        const isAuto = sched.automation_enabled;
        const dotAuto = document.getElementById("dotAutoStatus");
        const textAuto = document.getElementById("textAutoStatus");
        if (isAuto) {
            dotAuto.style.backgroundColor = "var(--neon-green)";
            textAuto.textContent = "Automation: ACTIVE";
        } else {
            dotAuto.style.backgroundColor = "var(--neon-red)";
            textAuto.textContent = "Automation: INACTIVE";
        }

        // Dashboard Metrics
        const metricVideos = document.getElementById("metricTodayVideos");
        if (metricVideos) {
            metricVideos.textContent = `${sched.videos_generated_today || 0} / ${sched.daily_video_limit || 2}`;
        }

        const metricRem = document.getElementById("metricTodayRemaining");
        if (metricRem) {
            metricRem.textContent = `${sched.remaining_quota_today || 0} slots available`;
        }

        const metricPub = document.getElementById("metricPublishTime");
        if (metricPub) {
            metricPub.textContent = `${sched.publishing_time || "19:00"} IST`;
        }

        // Toggle Switch state
        const toggleSwitch = document.getElementById("toggleMasterAuto");
        const toggleLabel = document.getElementById("toggleAutoLabel");
        if (toggleSwitch && !toggleSwitch.matches(":focus")) {
            toggleSwitch.checked = isAuto;
            if (toggleLabel) {
                toggleLabel.textContent = isAuto ? "Automation is ENABLED (Autonomous Production Active)" : "Automation is DISABLED";
            }
        }

        // Active Job Progress Bar in Dashboard
        const dashBar = document.getElementById("dashProgressBarFill");
        const dashPct = document.getElementById("dashProgressPercent");
        const dashMsg = document.getElementById("dashProgressMessage");
        const dashSub = document.getElementById("activeJobSubtext");

        if (activeJob) {
            dashBar.style.width = `${activeJob.percent || 0}%`;
            dashPct.textContent = `${activeJob.percent || 0}%`;
            dashMsg.textContent = `[${activeJob.stage_name || 'Active'}] ${activeJob.message || ''}`;
            if (dashSub) {
                dashSub.textContent = `Producing: "${activeJob.topic}" (Category: ${activeJob.category})`;
            }
        } else {
            if (dashBar) dashBar.style.width = "0%";
            if (dashPct) dashPct.textContent = "0%";
            if (dashMsg) dashMsg.textContent = sched.is_busy ? "Processing..." : "Auto-pilot is currently idle.";
            if (dashSub) {
                dashSub.textContent = "Auto-pilot is currently idle. Click 'Generate Now' or enable background automation.";
            }
        }

    } catch (e) {
        console.error("Status polling error:", e);
    }
}

// ========================================================
// 3. AUTOMATION & DASHBOARD CONTROLS
// ========================================================
function setupAutomationControls() {
    // Master Automation Toggle Switch
    const toggleAuto = document.getElementById("toggleMasterAuto");
    if (toggleAuto) {
        toggleAuto.addEventListener("change", async (e) => {
            try {
                const res = await fetch("/api/automation/toggle", { method: "POST" });
                const d = await res.json();
                showToast(d.automation_enabled ? "Autonomous Production Activated!" : "Automation Paused.");
                await refreshSystemStatus();
            } catch (err) {
                showToast("Error updating automation status");
            }
        });
    }

    // Dashboard Quick Actions
    const btnGenNow = document.getElementById("btnDashGenerateNow");
    if (btnGenNow) {
        btnGenNow.addEventListener("click", async () => {
            btnGenNow.disabled = true;
            btnGenNow.textContent = "⚡ Triggering Auto-Pilot...";
            try {
                const res = await fetch("/api/automation/generate-now", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({})
                });
                const d = await res.json();
                if (res.ok) {
                    showToast(`Autonomous Job ${d.job_id} started!`);
                    await refreshSystemStatus();
                    await loadRecentJobs();
                } else {
                    alert(d.detail || "Could not start automated job");
                }
            } catch (e) {
                alert(`Error: ${e.message}`);
            } finally {
                btnGenNow.disabled = false;
                btnGenNow.textContent = "⚡ Generate Now (Auto-Pilot)";
            }
        });
    }

    const btnPause = document.getElementById("btnDashPauseAuto");
    if (btnPause) {
        btnPause.addEventListener("click", async () => {
            await fetch("/api/automation/pause", { method: "POST" });
            showToast("Automation Paused");
            await refreshSystemStatus();
        });
    }

    const btnResume = document.getElementById("btnDashResumeAuto");
    if (btnResume) {
        btnResume.addEventListener("click", async () => {
            await fetch("/api/automation/resume", { method: "POST" });
            showToast("Automation Resumed");
            await refreshSystemStatus();
        });
    }

    const btnRefreshJobs = document.getElementById("btnRefreshJobs");
    if (btnRefreshJobs) {
        btnRefreshJobs.addEventListener("click", loadRecentJobs);
    }

    // Save Automation Configuration Settings
    const btnSaveAuto = document.getElementById("btnSaveAutoSettings");
    if (btnSaveAuto) {
        btnSaveAuto.addEventListener("click", async () => {
            const limit = document.getElementById("inputDailyLimit").value;
            const pubTime = document.getElementById("inputPublishTime").value;
            const budget = document.getElementById("inputDailyBudget").value;

            try {
                await fetch("/api/settings", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        settings: {
                            daily_video_limit: limit,
                            publishing_time: pubTime,
                            daily_budget_usd: budget
                        }
                    })
                });
                showToast("Automation Settings Saved Successfully!");
                await refreshSystemStatus();
            } catch (err) {
                showToast("Failed to save settings");
            }
        });
    }
}

// ========================================================
// 4. RECENT JOBS TABLE
// ========================================================
async function loadRecentJobs() {
    const tbody = document.getElementById("jobsTableBody");
    if (!tbody) return;

    try {
        const res = await fetch("/api/jobs?limit=20");
        const data = await res.json();
        const jobs = data.jobs || [];

        if (jobs.length === 0) {
            tbody.innerHTML = `<tr><td colspan="8" class="text-center">No production jobs logged yet.</td></tr>`;
            return;
        }

        tbody.innerHTML = jobs.map(j => {
            const qcBadge = j.qc_score > 0 
                ? `<span class="badge-pill active">${j.qc_score}/100</span>`
                : `<span class="badge-pill">N/A</span>`;

            const statusClass = j.status === "completed" ? "active" : (j.status === "failed" ? "danger" : "");

            return `
                <tr>
                    <td><code>${j.id}</code></td>
                    <td><strong>${escapeHtml(j.topic)}</strong></td>
                    <td>${j.category}</td>
                    <td><span class="badge-pill ${statusClass}">${j.status.toUpperCase()}</span></td>
                    <td>${qcBadge}</td>
                    <td>${j.total_duration ? j.total_duration.toFixed(1) + 's' : '-'}</td>
                    <td><small>${new Date(j.created_at).toLocaleTimeString()}</small></td>
                    <td>
                        ${j.video_filename ? `<a href="/api/video/${j.video_filename}" target="_blank" class="btn-radar-refresh">▶️ Watch</a>` : ''}
                        ${j.status === 'failed' ? `<button onclick="retryJob('${j.id}')" class="btn-radar-refresh">🔄 Retry</button>` : ''}
                    </td>
                </tr>
            `;
        }).join("");

    } catch (e) {
        console.error("Failed to load jobs:", e);
    }
}

async function retryJob(jobId) {
    if (!confirm(`Retry production job ${jobId}?`)) return;
    try {
        const res = await fetch(`/api/jobs/${jobId}/retry`, { method: "POST" });
        const d = await res.json();
        showToast(`Retrying job as ${d.new_job_id}...`);
        await loadRecentJobs();
    } catch (e) {
        alert("Error retrying job: " + e.message);
    }
}

// ========================================================
// 5. TOPIC DISCOVERY & QUEUE
// ========================================================
async function loadTopicQueue() {
    const tbody = document.getElementById("topicsTableBody");
    if (!tbody) return;

    try {
        const res = await fetch("/api/topics/queue");
        const data = await res.json();
        const queue = data.queue || [];

        if (queue.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" class="text-center">Topic queue is empty. Click 'Discover Real-Time Topics' to replenish.</td></tr>`;
            return;
        }

        tbody.innerHTML = queue.map(t => `
            <tr>
                <td><strong>${t.relevance_score}/100</strong></td>
                <td>${escapeHtml(t.topic)}</td>
                <td><span class="badge-pill">${t.category}</span></td>
                <td><small>${t.source}</small></td>
                <td><span class="badge-pill ${t.status === 'in_production' ? 'active' : ''}">${t.status}</span></td>
                <td>
                    <button onclick="produceTopic('${escapeHtml(t.topic)}', '${t.category}')" class="btn-radar-refresh">⚡ Produce Now</button>
                </td>
            </tr>
        `).join("");

    } catch (e) {
        console.error("Failed to load topic queue:", e);
    }
}

async function produceTopic(topic, category) {
    if (!confirm(`Start production for topic:\n"${topic}"?`)) return;
    try {
        const res = await fetch("/api/automation/generate-now", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ topic, category })
        });
        const d = await res.json();
        if (res.ok) {
            showToast(`Production Job ${d.job_id} launched!`);
            // Switch to Dashboard
            document.querySelector(".nav-tab[data-target='sec-dashboard']").click();
            await refreshSystemStatus();
            await loadRecentJobs();
        } else {
            alert(d.detail || "Could not launch job");
        }
    } catch (e) {
        alert(e.message);
    }
}

const btnTriggerDisc = document.getElementById("btnTriggerDiscovery");
if (btnTriggerDisc) {
    btnTriggerDisc.addEventListener("click", async () => {
        btnTriggerDisc.disabled = true;
        btnTriggerDisc.textContent = "⚡ Discovering...";
        try {
            const res = await fetch("/api/topics/discover", { method: "POST" });
            const d = await res.json();
            showToast(`Discovered ${d.discovered_count} new topics!`);
            await loadTopicQueue();
        } catch (e) {
            alert("Discovery error: " + e.message);
        } finally {
            btnTriggerDisc.disabled = false;
            btnTriggerDisc.textContent = "⚡ Discover Real-Time Topics";
        }
    });
}

const btnAddManual = document.getElementById("btnAddManualTopic");
if (btnAddManual) {
    btnAddManual.addEventListener("click", async () => {
        const topic = document.getElementById("manualTopicInput").value.trim();
        const category = document.getElementById("manualCategorySelect").value;
        if (!topic) {
            alert("Please enter a topic title.");
            return;
        }

        try {
            const res = await fetch("/api/topics/add", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ topic, category })
            });
            const d = await res.json();
            if (d.added) {
                showToast("Topic added to priority queue!");
                document.getElementById("manualTopicInput").value = "";
                await loadTopicQueue();
            } else {
                alert("Topic already exists in the queue (Deduplicated).");
            }
        } catch (e) {
            alert("Error adding topic: " + e.message);
        }
    });
}

// ========================================================
// 6. YOUTUBE CHANNEL CONNECT & PUBLISHING QUEUE
// ========================================================
async function loadYouTubeChannelInfo() {
    try {
        const res = await fetch("/api/youtube/status");
        const data = await res.json();
        const dot = document.getElementById("dotChannelStatus");
        const text = document.getElementById("textChannelStatus");
        const metricName = document.getElementById("metricChannelName");
        const metricSubs = document.getElementById("metricChannelSubs");

        const prompt = document.getElementById("ytAuthPrompt");
        const connInfo = document.getElementById("ytConnectedInfo");

        if (data.authenticated) {
            dot.style.backgroundColor = "var(--neon-green)";
            text.textContent = `YouTube: ${data.channel_name}`;
            if (metricName) metricName.textContent = data.channel_name;
            if (metricSubs) metricSubs.textContent = `${data.subscribers.toLocaleString()} Subscribers`;

            if (prompt) prompt.style.display = "none";
            if (connInfo) connInfo.style.display = "block";
            const chTitle = document.getElementById("ytChannelTitle");
            const chStats = document.getElementById("ytChannelStats");
            if (chTitle) chTitle.textContent = data.channel_name;
            if (chStats) chStats.textContent = `${data.subscribers} Subscribers · ${data.total_views} Views · ${data.video_count} Videos`;
        } else {
            dot.style.backgroundColor = "var(--neon-red)";
            text.textContent = "YouTube: Not Connected";
            if (prompt) prompt.style.display = "block";
            if (connInfo) connInfo.style.display = "none";
        }
    } catch (e) {
        console.error("YouTube status error:", e);
    }
}

const btnConnectYt = document.getElementById("btnConnectYouTube");
if (btnConnectYt) {
    btnConnectYt.addEventListener("click", async () => {
        try {
            const res = await fetch("/api/youtube/auth-url");
            const d = await res.json();
            if (d.configured && d.auth_url) {
                window.open(d.auth_url, "_blank", "width=600,height=700");
            } else {
                alert(d.error || "client_secrets.json not found in project root. Please download it from Google Cloud Console.");
            }
        } catch (e) {
            alert(e.message);
        }
    });
}

async function loadPublishingQueue() {
    const tbody = document.getElementById("publishingTableBody");
    if (!tbody) return;

    try {
        const res = await fetch("/api/publishing/queue");
        const data = await res.json();
        const queue = data.publishing_queue || [];

        if (queue.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" class="text-center">Publishing queue is currently empty.</td></tr>`;
            return;
        }

        tbody.innerHTML = queue.map(q => `
            <tr>
                <td>#${q.id}</td>
                <td><strong>${escapeHtml(q.title)}</strong></td>
                <td><span class="badge-pill">${q.privacy_status.toUpperCase()}</span></td>
                <td>${q.scheduled_time || 'Immediate upon QC Pass'}</td>
                <td><span class="badge-pill ${q.status === 'uploaded' ? 'active' : ''}">${q.status.toUpperCase()}</span></td>
                <td>
                    ${q.youtube_url ? `<a href="${q.youtube_url}" target="_blank" class="btn-radar-refresh">▶️ View on YouTube</a>` : ''}
                    ${q.status !== 'uploaded' ? `<button onclick="manualUploadVideo(${q.id})" class="btn-radar-refresh">🚀 Upload Now</button>` : ''}
                </td>
            </tr>
        `).join("");

    } catch (e) {
        console.error("Failed to load publishing queue:", e);
    }
}

async function manualUploadVideo(queueId) {
    if (!confirm("Upload this video to your authorized YouTube channel now?")) return;
    try {
        const res = await fetch(`/api/publishing/upload/${queueId}`, { method: "POST" });
        const d = await res.json();
        if (res.ok) {
            showToast(`Video successfully published to YouTube! URL: ${d.video_url}`);
            await loadPublishingQueue();
        } else {
            alert(d.detail || "Upload failed");
        }
    } catch (e) {
        alert(e.message);
    }
}

// ========================================================
// 7. COST & BUDGET REPORT
// ========================================================
async function loadCostReport() {
    try {
        const res = await fetch("/api/costs");
        const data = await res.json();

        const spentToday = document.getElementById("costSpentToday");
        const limit = document.getElementById("costDailyLimit");
        const spentMonth = document.getElementById("costSpentMonth");
        const rem = document.getElementById("costRemaining");
        const chipBudget = document.getElementById("textBudgetStatus");
        const metricSpent = document.getElementById("metricSpentToday");
        const metricRem = document.getElementById("metricBudgetRemaining");

        if (spentToday) spentToday.textContent = `$${data.spent_today_usd.toFixed(2)}`;
        if (limit) limit.textContent = `$${data.daily_budget_limit_usd.toFixed(2)}`;
        if (spentMonth) spentMonth.textContent = `$${data.spent_month_usd.toFixed(2)}`;
        if (rem) rem.textContent = `$${data.remaining_budget_today.toFixed(2)}`;
        if (chipBudget) chipBudget.textContent = `Daily Budget: $${data.spent_today_usd.toFixed(2)} / $${data.daily_budget_limit_usd.toFixed(2)}`;
        if (metricSpent) metricSpent.textContent = `Spent: $${data.spent_today_usd.toFixed(2)} today`;
        if (metricRem) metricRem.textContent = `$${data.remaining_budget_today.toFixed(2)}`;
    } catch (e) {
        console.error("Cost report error:", e);
    }
}

// ========================================================
// 8. ORIGINAL VIDEO PRODUCTION ENGINE (MANUAL WORKSPACE)
// ========================================================
function setupEventListeners() {
    // Generate Script Button
    const btnAiScript = document.getElementById("btnAiScript");
    if (btnAiScript) {
        btnAiScript.addEventListener("click", () => {
            const prompt = document.getElementById("promptInput").value.trim();
            if (!prompt) {
                alert("Please enter a topic prompt!");
                return;
            }
            generateAiScript(prompt);
        });
    }

    // Voice Pace Slider
    const paceSlider = document.getElementById("paceSlider");
    const paceVal = document.getElementById("paceVal");
    if (paceSlider && paceVal) {
        paceSlider.addEventListener("input", (e) => {
            paceVal.textContent = `${parseFloat(e.target.value).toFixed(2)}x`;
        });
    }

    // Style Card Selection (Stickman & Visual Background)
    const styleCards = document.querySelectorAll(".style-card");
    styleCards.forEach(card => {
        card.addEventListener("click", () => {
            const group = card.closest(".style-cards-group");
            if (group) {
                group.querySelectorAll(".style-card").forEach(c => c.classList.remove("active"));
            }
            card.classList.add("active");
            const radio = card.querySelector("input[type='radio']");
            if (radio) radio.checked = true;
        });
    });

    // Preview Tabs
    const tabVideo = document.getElementById("tabVideoPreview");
    const tabThumb = document.getElementById("tabThumbPreview");
    const tabSb = document.getElementById("tabStoryboardPreview");
    const tabQc = document.getElementById("tabQcPreview");

    const videoWrap = document.getElementById("videoPreviewWrap");
    const thumbWrap = document.getElementById("thumbPreviewWrap");
    const sbWrap = document.getElementById("storyboardPreviewWrap");
    const qcWrap = document.getElementById("qcPreviewWrap");

    const hideAllPreviews = () => {
        [tabVideo, tabThumb, tabSb, tabQc].forEach(t => t && t.classList.remove("active"));
        [videoWrap, thumbWrap, sbWrap, qcWrap].forEach(w => w && (w.style.display = "none"));
    };

    if (tabVideo) tabVideo.addEventListener("click", () => { hideAllPreviews(); tabVideo.classList.add("active"); if (videoWrap) videoWrap.style.display = "flex"; });
    if (tabThumb) tabThumb.addEventListener("click", () => { hideAllPreviews(); tabThumb.classList.add("active"); if (thumbWrap) thumbWrap.style.display = "flex"; });
    if (tabSb) tabSb.addEventListener("click", () => { hideAllPreviews(); tabSb.classList.add("active"); if (sbWrap) sbWrap.style.display = "block"; });
    if (tabQc) tabQc.addEventListener("click", () => { hideAllPreviews(); tabQc.classList.add("active"); if (qcWrap) qcWrap.style.display = "block"; });

    // Render 1-Click Short
    const btnRender = document.getElementById("btnRenderShort");
    if (btnRender) {
        btnRender.addEventListener("click", renderShortVideo);
    }
}

async function generateAiScript(prompt) {
    const btn = document.getElementById("btnAiScript");
    btn.disabled = true;
    btn.innerHTML = `<span class="btn-icon">⏳</span><span>Generating Script...</span>`;

    try {
        const res = await fetch("/api/generate-script", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ prompt: prompt })
        });
        if (!res.ok) throw new Error("Failed to generate script");

        const data = await res.json();
        currentScriptData = data;

        document.getElementById("editHook").value = data.hook || "";
        document.getElementById("editPoints").value = (data.points || []).join("\n");
        document.getElementById("editCta").value = data.cta || "";
        document.getElementById("editNarration").value = data.narration_text || "";

        showToast("Script generated successfully in Roman Hinglish!");
    } catch (err) {
        alert("Error generating script: " + err.message);
    } finally {
        btn.disabled = false;
        btn.innerHTML = `<span class="btn-icon">✨</span><span>Generate Script</span>`;
    }
}

async function renderShortVideo() {
    const hook = document.getElementById("editHook").value.trim();
    const points = document.getElementById("editPoints").value.split("\n").filter(p => p.trim());
    const cta = document.getElementById("editCta").value.trim();
    const narration = document.getElementById("editNarration").value.trim();

    if (!narration && (!hook || points.length === 0)) {
        alert("Please enter or generate a script narration first!");
        return;
    }

    const speaker = document.getElementById("speakerSelect").value;
    const pace = parseFloat(document.getElementById("paceSlider").value);

    let visualStyle = "sketch_notes";
    const vChecked = document.querySelector("input[name='visualStyle']:checked");
    if (vChecked) visualStyle = vChecked.value;

    let stickmanStyle = "modern_beanie";
    const sChecked = document.querySelector("input[name='stickmanStyle']:checked");
    if (sChecked) stickmanStyle = sChecked.value;

    const btnRender = document.getElementById("btnRenderShort");
    btnRender.disabled = true;
    btnRender.innerHTML = `<span class="rocket-icon">⏳</span><span class="render-text">QUEUED FOR RENDERING...</span>`;

    const progressSec = document.getElementById("progressSection");
    progressSec.style.display = "block";
    updateProgressBar(5, "Sending render request...");

    const payload = {
        title: currentScriptData ? currentScriptData.title : "Short Video",
        hook: hook,
        points: points,
        cta: cta,
        narration_text: narration,
        speaker: speaker,
        pace: pace,
        visual_style: visualStyle,
        stickman_style: stickmanStyle,
        seo: currentScriptData ? currentScriptData.seo : null,
        visual_keywords: currentScriptData ? currentScriptData.visual_keywords : ["tech", "ai", "study"]
    };

    try {
        const res = await fetch("/api/generate-video", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        const d = await res.json();
        currentTaskId = d.task_id;
        pollTaskStatus(currentTaskId);
    } catch (e) {
        alert("Render start failed: " + e.message);
        btnRender.disabled = false;
    }
}

function pollTaskStatus(taskId) {
    if (pollingInterval) clearInterval(pollingInterval);
    pollingInterval = setInterval(async () => {
        try {
            const res = await fetch(`/api/task-status/${taskId}`);
            const t = await res.json();
            updateProgressBar(t.percent, t.message);

            if (t.status === "completed") {
                clearInterval(pollingInterval);
                finishRenderSuccess(t);
            } else if (t.status === "failed") {
                clearInterval(pollingInterval);
                alert("Rendering failed: " + t.error);
                document.getElementById("btnRenderShort").disabled = false;
            }
        } catch (e) {
            console.error("Polling error:", e);
        }
    }, 1500);
}

function updateProgressBar(pct, msg) {
    const fill = document.getElementById("progressBarFill");
    const pText = document.getElementById("progressPercent");
    const mText = document.getElementById("progressMessage");
    if (fill) fill.style.width = `${pct}%`;
    if (pText) pText.textContent = `${pct}%`;
    if (mText) mText.textContent = msg;
}

function finishRenderSuccess(task) {
    showToast("Render completed! Video ready.");
    const btn = document.getElementById("btnRenderShort");
    btn.disabled = false;
    btn.innerHTML = `<span class="rocket-icon">🚀</span><span class="render-text">RENDER 1080x1920 SHORT & THUMBNAIL</span>`;

    // Load video
    if (task.video_url) {
        const v = document.getElementById("videoPlayer");
        const s = document.getElementById("videoSource");
        const placeholder = document.getElementById("playerPlaceholder");
        s.src = task.video_url;
        v.load();
        v.play().catch(() => {});
        if (placeholder) placeholder.style.display = "none";
    }

    // Load thumbnail
    if (task.thumb_url) {
        const tImg = document.getElementById("thumbImage");
        const tPlaceholder = document.getElementById("thumbPlaceholder");
        tImg.src = task.thumb_url;
        tImg.style.display = "block";
        if (tPlaceholder) tPlaceholder.style.display = "none";
    }

    // Deliverables bar
    const bar = document.getElementById("videoActionsBar");
    if (bar && task.bundle) {
        bar.style.display = "block";
    }

    loadVideosLibrary();
}

// ========================================================
// 9. VIDEO LIBRARY
// ========================================================
async function loadVideosLibrary() {
    const list = document.getElementById("libraryVideosList");
    if (!list) return;

    try {
        const res = await fetch("/api/videos");
        const videos = await res.json();

        if (videos.length === 0) {
            list.innerHTML = `<div class="empty-state">No videos generated yet.</div>`;
            return;
        }

        list.innerHTML = videos.map(v => `
            <div class="video-item-card">
                ${v.thumb_url ? `<img src="${v.thumb_url}" class="thumb-mini" alt="Thumb">` : '<div class="thumb-mini placeholder">🎬</div>'}
                <div class="video-item-info">
                    <strong>${v.filename}</strong>
                    <small>${v.size_mb} MB · ${v.modified}</small>
                </div>
                <div class="video-item-actions">
                    <a href="/api/video/${v.filename}" target="_blank" class="btn-radar-refresh">▶️ Play</a>
                    <a href="/api/video/${v.filename}" download class="btn-radar-refresh">⬇️ Save</a>
                </div>
            </div>
        `).join("");
    } catch (e) {
        console.error("Library load error:", e);
    }
}

// ========================================================
// 10. TREND RADAR & SETTINGS
// ========================================================
async function loadTrendRadar() {
    const container = document.getElementById("radarTrendsList");
    if (!container) return;

    try {
        const res = await fetch("/api/trends");
        const data = await res.json();
        const trends = data.trends || [];

        container.innerHTML = trends.map(t => `
            <div class="trend-chip" onclick="applyTrendTopic('${escapeHtml(t.title)}')">
                <span class="trend-name">${escapeHtml(t.title)}</span>
                <span class="trend-traffic">${t.traffic || 'Spike'}</span>
            </div>
        `).join("");
    } catch (e) {
        container.innerHTML = `<span class="loading-text">Live Trend Radar ready.</span>`;
    }
}

function applyTrendTopic(topic) {
    const input = document.getElementById("promptInput");
    if (input) {
        input.value = topic;
        document.querySelector(".nav-tab[data-target='sec-production']").click();
        generateAiScript(topic);
    }
}

async function loadPlatformSettings() {
    try {
        const res = await fetch("/api/settings");
        const data = await res.json();
        const s = data.settings || {};

        if (s.daily_video_limit && document.getElementById("inputDailyLimit")) {
            document.getElementById("inputDailyLimit").value = s.daily_video_limit;
        }
        if (s.publishing_time && document.getElementById("inputPublishTime")) {
            document.getElementById("inputPublishTime").value = s.publishing_time;
        }
        if (s.daily_budget_usd && document.getElementById("inputDailyBudget")) {
            document.getElementById("inputDailyBudget").value = s.daily_budget_usd;
        }
        if (s.default_privacy && document.getElementById("settingDefaultPrivacy")) {
            document.getElementById("settingDefaultPrivacy").value = s.default_privacy;
        }
        if (s.default_category && document.getElementById("settingDefaultCategory")) {
            document.getElementById("settingDefaultCategory").value = s.default_category;
        }
    } catch (e) {
        console.error("Settings load error:", e);
    }
}

// Utilities
function showToast(msg) {
    const toast = document.getElementById("toastNotification");
    if (!toast) return;
    toast.textContent = msg;
    toast.classList.add("show");
    setTimeout(() => toast.classList.remove("show"), 3500);
}

function escapeHtml(str) {
    if (!str) return "";
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}
