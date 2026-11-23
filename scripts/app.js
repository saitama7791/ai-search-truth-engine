(function () {
  "use strict";
  document.documentElement.classList.replace("no-js", "js");
  var dataEl = document.getElementById("truth-data");
  var board = document.getElementById("board");
  var nores = document.getElementById("nores");
  var countEl = document.getElementById("count");
  var input = document.getElementById("q");
  var copyBtn = document.getElementById("copySnap");
  var toastEl = document.getElementById("toast");
  if (!board || !dataEl) return;
  var DATA = {};
  try { DATA = JSON.parse(dataEl.textContent); } catch (err) { return; }
  var state = { q: "", v: "all", p: "all" };
  var cards = Array.prototype.slice.call(board.children);

  function toks(s) {
    return String(s).toLowerCase().split(/[^a-z0-9.]+/).filter(Boolean);
  }

  function matches(card, qtoks) {
    if (state.v !== "all" && card.getAttribute("data-verdict") !== state.v) return false;
    if (state.p !== "all") {
      var plats = (card.getAttribute("data-plats") || "").split(",");
      if (plats.indexOf(state.p) === -1) return false;
    }
    if (qtoks.length) {
      var hay = (card.getAttribute("data-s") || "").toLowerCase();
      var name = card.querySelector(".tname");
      if (name) hay += " " + name.textContent.toLowerCase();
      for (var i = 0; i < qtoks.length; i++) {
        if (hay.indexOf(qtoks[i]) === -1) return false;
      }
    }
    return true;
  }

  function apply() {
    var qtoks = toks(state.q);
    var shown = 0;
    cards.forEach(function (c) {
      var ok = matches(c, qtoks);
      c.hidden = !ok;
      if (ok) shown++;
    });
    if (nores) nores.hidden = shown > 0;
    if (countEl) {
      countEl.hidden = false;
      countEl.textContent = "Showing " + shown + " of " + cards.length + " verdicts" + (state.q ? ' matching "' + state.q + '"' : "");
    }
  }

  function setChipGroup(sel, attr) {
    var btns = document.querySelectorAll(sel);
    Array.prototype.forEach.call(btns, function (btn) {
      btn.addEventListener("click", function () {
        Array.prototype.forEach.call(btns, function (b) {
          b.setAttribute("aria-pressed", b === btn ? "true" : "false");
        });
        state[attr] = btn.getAttribute("data-" + attr);
        apply();
      });
    });
  }
  setChipGroup("[data-v]", "v");
  setChipGroup("[data-p]", "p");

  Array.prototype.forEach.call(document.querySelectorAll(".quickchips [data-q]"), function (btn) {
    btn.addEventListener("click", function () {
      input.value = btn.getAttribute("data-q");
      state.q = input.value;
      apply();
      board.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  });

  if (input) {
    input.addEventListener("input", function () { state.q = input.value; apply(); });
    input.addEventListener("keydown", function (ev) {
      if (ev.key === "Enter") { ev.preventDefault(); board.scrollIntoView({ behavior: "smooth", block: "start" }); }
    });
  }

  try {
    var qp = new URLSearchParams(location.search).get("q");
    if (qp && input) { input.value = qp; state.q = qp; }
  } catch (err) { /* older browsers */ }

  apply();

  var toastTimer;
  function say(msg) {
    if (!toastEl) return;
    toastEl.textContent = msg;
    toastEl.classList.add("on");
    if (toastTimer) clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toastEl.classList.remove("on"); }, 2800);
  }

  function snapshotText() {
    var lines = ["AI Search Truth Board - verified " + (DATA.sweep_date || ""), "https://aisearchos.com/truth-engine", ""];
    (DATA.tactics || []).forEach(function (t) {
      lines.push("- [" + String(t.verdict || "").toUpperCase() + "] " + t.name + " - " + t.one_liner);
    });
    lines.push("");
    lines.push("Every verdict carries its source at the URL above.");
    return lines.join("\n");
  }

  function fallbackCopy(text) {
    var ta = document.createElement("textarea");
    ta.value = text;
    ta.setAttribute("readonly", "");
    ta.style.position = "fixed";
    ta.style.left = "-9999px";
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand("copy"); say("Board snapshot copied - paste it anywhere."); }
    catch (err) { say("Copy failed - select the board and copy manually."); }
    document.body.removeChild(ta);
  }

  if (copyBtn) {
    copyBtn.addEventListener("click", function () {
      var text = snapshotText();
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(function () {
          say("Board snapshot copied - paste it anywhere.");
        }, function () { fallbackCopy(text); });
      } else { fallbackCopy(text); }
    });
  }
})();
