/* CanonLoom site JS — theme toggle, mobile nav, interactive S0–S6 demo. */

(function () {
  "use strict";

  /* ---------- theme ---------- */
  var root = document.documentElement;
  var savedTheme = null;
  try { savedTheme = localStorage.getItem("canonloom-theme"); } catch (e) {}

  function applyTheme(theme) {
    root.setAttribute("data-theme", theme);
    try { localStorage.setItem("canonloom-theme", theme); } catch (e) {}
  }
  if (savedTheme === "dark") {
    applyTheme("dark");
  } else if (savedTheme === "light") {
    applyTheme("light");
  } else {
    // OS default
    applyTheme(window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
  }

  /* ---------- mobile nav ---------- */
  var navToggle = document.querySelector(".nav-toggle");
  var nav = document.querySelector(".site-nav");
  if (navToggle && nav) {
    navToggle.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      navToggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  /* ---------- interactive S0–S6 demo ---------- */
  var STAGES = [
    { id: "S0", name: "章契", action: "作者选择方案，冻结章契与上下文包" },
    { id: "S1", name: "草稿", action: "Agent 按契约生成候选正文（drafts/）" },
    { id: "S2", name: "快速检查", action: "确定性校验通过，无 BLOCKER" },
    { id: "S3", name: "修订", action: "按 Finding 受限修订，不发明新事实" },
    { id: "S4", name: "严格检查", action: "结构 / 连续性检查通过" },
    { id: "S5", name: "独立审查", action: "独立审查报告，无阻断性 Finding" },
    { id: "S5b", name: "交叉验证", action: "隔离报告交叉验证，结论一致" },
    { id: "S6", name: "结算", action: "作者批准 → 正文进入 manuscript/，状态结算" }
  ];

  var tracksEl = document.getElementById("demo-tracks");
  var logEl = document.getElementById("demo-log");
  var nextBtn = document.getElementById("demo-next");
  var resetBtn = document.getElementById("demo-reset");
  var current = -1;

  if (tracksEl && logEl && nextBtn && resetBtn) {
    STAGES.forEach(function (s) {
      var el = document.createElement("div");
      el.className = "demo-track";
      el.id = "track-" + s.id;
      el.innerHTML = '<span class="t-track">' + s.id + "</span><span>" + s.name + "</span>";
      tracksEl.appendChild(el);
    });

    function log(line, cls) {
      var body = logEl.querySelector(".demo-log-body");
      var l = document.createElement("span");
      l.className = "line " + (cls || "");
      l.textContent = line;
      body.appendChild(l);
      body.scrollTop = body.scrollHeight;
    }

    function clearLog() {
      var body = logEl.querySelector(".demo-log-body");
      body.innerHTML = '<p class="demo-log-empty">点击「下一步」开始模拟一章生产。</p>';
    }

    function setStage(i, state) {
      var el = document.getElementById("track-" + STAGES[i].id);
      el.className = "demo-track " + state;
    }

    function runStep() {
      current += 1;
      if (current >= STAGES.length) {
        current = STAGES.length - 1;
        nextBtn.disabled = true;
        return;
      }
      var s = STAGES[current];
      setStage(current, "active");
      log("$ " + s.id + "  " + s.name, "l-prompt");
      setTimeout(function () {
        setStage(current, "done");
        log("✓ " + s.action, "l-ok");
        if (current === STAGES.length - 1) {
          log("S6 结算完成：draft → manuscript/，状态已批准", "l-accent");
          nextBtn.disabled = true;
        }
      }, 350);
    }

    function resetDemo() {
      current = -1;
      STAGES.forEach(function (s, i) { setStage(i, ""); });
      clearLog();
      nextBtn.disabled = false;
    }

    nextBtn.addEventListener("click", runStep);
    resetBtn.addEventListener("click", resetDemo);
  }
})();
