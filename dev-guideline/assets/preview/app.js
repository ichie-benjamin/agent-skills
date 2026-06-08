// dev-guideline preview frontend
(function () {
  var state = {
    tasks: { active: [], completed: [], archived: [] },
    other: [],
    selected: null,
    selectedOther: null,
    mtime: 0,
    activeTab: "tasks",
    expanded: { active: false, completed: false, archived: false },
  };
  var PAGE = 10;

  function $(id) { return document.getElementById(id); }
  function $$(sel) { return Array.prototype.slice.call(document.querySelectorAll(sel)); }
  function esc(s) { return (s || "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); }

  function fmtAge(dateStr) {
    if (!dateStr) return "";
    var d = new Date(dateStr);
    if (isNaN(d)) return dateStr;
    var diff = (Date.now() - d.getTime()) / 86400000;
    if (diff < 1) return "today";
    if (diff < 2) return "yesterday";
    if (diff < 30) return Math.floor(diff) + "d ago";
    return d.toISOString().slice(0, 10);
  }
  function fmtNum(n) {
    if (n >= 1000) return (n / 1000).toFixed(n >= 10000 ? 0 : 1) + "k";
    return String(n);
  }
  function stripFrontmatter(md) {
    if (!md) return md;
    if (!md.startsWith("---")) return md;
    var end = md.indexOf("\n---", 4);
    if (end === -1) return md;
    return md.slice(end + 4).replace(/^\n+/, "");
  }
  function fmtBytes(n) {
    if (n < 1024) return n + " B";
    if (n < 1024 * 1024) return (n / 1024).toFixed(n < 10 * 1024 ? 1 : 0) + " KB";
    return (n / 1024 / 1024).toFixed(1) + " MB";
  }
  function extGlyph(name, kind) {
    if (kind === "dir") return "▸";
    var ext = (name.split(".").pop() || "").toLowerCase();
    return { md: "≡", json: "{}", txt: "T", yaml: "y", yml: "y" }[ext] || "·";
  }

  function setTab(name) {
    state.activeTab = name;
    $$(".tab").forEach(function (t) { t.classList.toggle("active", t.dataset.tab === name); });
    $$(".tab-panel").forEach(function (p) { p.classList.toggle("active", p.dataset.panel === name); });
  }

  function renderTaskList(items, parent, bucket, btn) {
    parent.innerHTML = "";
    if (!items.length) {
      parent.classList.add("empty");
      var li = document.createElement("li");
      li.textContent = "—";
      parent.appendChild(li);
      if (btn) btn.classList.add("hidden");
      return;
    }
    parent.classList.remove("empty");
    var slice = state.expanded[bucket] ? items : items.slice(0, PAGE);
    slice.forEach(function (t) {
      var li = document.createElement("li");
      var sel = state.selected && state.selected.slug === t.slug && state.selected.bucket === t.bucket;
      li.className = "task-item" + (sel ? " selected" : "");
      li.innerHTML =
        '<div class="ti-top">' +
          '<span class="ti-status ' + esc(t.status) + '"></span>' +
          '<span class="ti-title">' + esc(t.title) + '</span>' +
        '</div>' +
        (t.next_step ? '<div class="ti-next">' + esc(t.next_step) + '</div>' : '');
      li.addEventListener("click", function () { selectTask(t.bucket, t.slug); });
      parent.appendChild(li);
    });
    if (btn) {
      if (items.length > PAGE && !state.expanded[bucket]) {
        btn.textContent = "load all (" + (items.length - PAGE) + " more)";
        btn.classList.remove("hidden");
      } else if (items.length > PAGE && state.expanded[bucket]) {
        btn.textContent = "show less";
        btn.classList.remove("hidden");
      } else {
        btn.classList.add("hidden");
      }
    }
  }

  function renderAllTaskLists() {
    renderTaskList(state.tasks.active, $("activeList"), "active", $("loadMoreActive"));
    renderTaskList(state.tasks.completed, $("completedList"), "completed", $("loadMoreCompleted"));
    renderTaskList(state.tasks.archived, $("archivedList"), "archived", $("loadMoreArchived"));
    // hide archived section entirely if empty
    var hasArchived = state.tasks.archived.length > 0;
    $("archivedHead").classList.toggle("hidden", !hasArchived);
    $("archivedList").classList.toggle("hidden", !hasArchived);
  }

  function renderTaskView(task) {
    var view = $("taskView");
    if (!task) {
      view.className = "task-view empty";
      view.innerHTML = '<div class="empty-state"><div class="empty-glyph">·</div><div class="empty-text">select a task</div></div>';
      return;
    }
    view.className = "task-view";
    var fm = task.frontmatter || {};
    var meta = [];
    if (fm.status) meta.push('<span class="badge ' + esc(fm.status) + '">' + esc(fm.status) + '</span>');
    if (fm.updated) meta.push('<span class="age">updated ' + esc(fmtAge(fm.updated)) + '</span>');
    if (fm.owner) meta.push('<span class="age">owner ' + esc(fm.owner) + '</span>');
    if (fm.external_ref) meta.push('<span class="age">ref ' + esc(fm.external_ref) + '</span>');
    view.innerHTML =
      '<div class="task-header">' +
        '<div class="row"><h1>' + esc(fm.title || task.slug) + '</h1></div>' +
        '<div class="row">' + meta.join("") + '</div>' +
      '</div>' +
      '<div class="md">' + window.marked.parse(task.body || "") + '</div>';
  }

  function selectTask(bucket, slug) {
    fetch("/api/task/" + bucket + "/" + encodeURIComponent(slug))
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (t) {
        state.selected = t ? { bucket: bucket, slug: slug } : null;
        renderTaskView(t);
        renderAllTaskLists();
      });
  }

  // remember which folders the user has opened
  var openDirs = state.openDirs = {};

  function renderOtherList(items) {
    var parent = $("otherList");
    parent.innerHTML = "";
    if (!items.length) {
      parent.innerHTML = '<li class="other-item" style="color:var(--text-3);cursor:default">— empty —</li>';
      return;
    }
    // root files first, then folders — each group alphabetical
    var files = items.filter(function (it) { return it.kind === "file"; })
                     .sort(function (a, b) { return a.name.localeCompare(b.name); });
    var dirs  = items.filter(function (it) { return it.kind === "dir"; })
                     .sort(function (a, b) { return a.name.localeCompare(b.name); });

    files.forEach(function (it) {
      var li = document.createElement("li");
      var sel = state.selectedOther === it.name;
      li.className = "other-item" + (sel ? " selected" : "");
      li.innerHTML =
        '<span class="glyph">' + esc(extGlyph(it.name, it.kind)) + '</span>' +
        '<span class="nm">' + esc(it.name) + '</span>' +
        '<span class="sz">' + esc(fmtBytes(it.size)) + '</span>';
      li.addEventListener("click", function () { selectOther(it.name); });
      parent.appendChild(li);
    });

    dirs.forEach(function (it) {
      var open = !!openDirs[it.name];
      var li = document.createElement("li");
      li.className = "other-item other-dir" + (open ? " open" : "");
      li.innerHTML =
        '<span class="caret">' + (open ? "▼" : "▶") + '</span>' +
        '<span class="nm dir-name">' + esc(it.name) + '/</span>' +
        '<span class="sz">' + it.count + (it.count === 1 ? " file" : " files") + '</span>';
      li.addEventListener("click", function () {
        openDirs[it.name] = !openDirs[it.name];
        renderOtherList(state.other);
      });
      parent.appendChild(li);

      if (open && it.files && it.files.length) {
        var ul = document.createElement("ul");
        ul.className = "other-dir-files";
        it.files.forEach(function (fname) {
          var full = it.name + "/" + fname;
          var sub = document.createElement("li");
          var subSel = state.selectedOther === full;
          sub.className = "other-item other-subfile" + (subSel ? " selected" : "");
          sub.innerHTML =
            '<span class="glyph">' + esc(extGlyph(fname, "file")) + '</span>' +
            '<span class="nm">' + esc(fname) + '</span>';
          sub.addEventListener("click", function (e) {
            e.stopPropagation();
            selectOther(full);
          });
          ul.appendChild(sub);
        });
        parent.appendChild(ul);
      }
    });
  }

  function selectOther(name) {
    fetch("/api/other/" + name.split("/").map(encodeURIComponent).join("/"))
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (item) {
        state.selectedOther = item ? name : null;
        renderOtherView(item);
        renderOtherList(state.other);
      });
  }

  function renderOtherView(item) {
    var view = $("otherView");
    if (!item) {
      view.className = "task-view empty";
      view.innerHTML = '<div class="empty-state"><div class="empty-glyph">·</div><div class="empty-text">select a file</div></div>';
      return;
    }
    view.className = "task-view";
    var isMd = /\.md$/i.test(item.name);
    var isJson = /\.json$/i.test(item.name);
    var body;
    if (isMd) {
      body = '<div class="md">' + window.marked.parse(stripFrontmatter(item.raw) || "") + '</div>';
    } else if (isJson) {
      var pretty;
      try { pretty = JSON.stringify(JSON.parse(item.raw), null, 2); }
      catch (e) { pretty = item.raw; }
      body = '<pre><code>' + esc(pretty) + '</code></pre>';
    } else {
      body = '<pre><code>' + esc(item.raw) + '</code></pre>';
    }
    view.innerHTML =
      '<div class="task-header">' +
        '<div class="row"><h1>' + esc(item.name) + '</h1></div>' +
        '<div class="row">' +
          '<span class="badge">' + fmtNum(item.chars) + ' chars</span>' +
          '<span class="ext">' + item.lines + ' lines</span>' +
        '</div>' +
      '</div>' + body;
  }

  function refresh() {
    fetch("/api/state").then(function (r) { return r.json(); }).then(function (s) {
      state.tasks = s.tasks;
      state.other = s.other || [];
      state.mtime = s.mtime;

      $("projectName").textContent = s.project_name;
      $("lastSync").textContent = new Date().toLocaleTimeString();

      var totalTasks = s.tasks.active.length + s.tasks.completed.length + (s.tasks.archived||[]).length;
      $("cnt-tasks").textContent = totalTasks;
      $("cnt-other").textContent = state.other.length;
      $("tab-other").classList.toggle("hidden", state.other.length === 0);

      $("activeCount").textContent = s.tasks.active.length;
      $("completedCount").textContent = s.tasks.completed.length;
      $("archivedCount").textContent = (s.tasks.archived || []).length;
      renderAllTaskLists();

      $("memEntries").textContent = fmtNum(s.memory.entries);
      $("memLines").textContent = fmtNum(s.memory.lines);
      $("memChars").textContent = fmtNum(s.memory.chars);
      $("memoryUpdated").textContent = s.memory.last_updated || "—";
      $("memoryBody").innerHTML = window.marked.parse(stripFrontmatter(s.memory.raw) || "");
      var lp = Math.min(s.memory.lines / 150, 1);
      var ep = Math.min(s.memory.entries / 40, 1);
      var pct = Math.round(Math.max(lp, ep) * 100);
      $("memThresholdFill").style.width = pct + "%";
      $("memThresholdFill").classList.toggle("warn", pct >= 80);
      $("memThresholdText").textContent = pct + "% (" + s.memory.lines + "/150 lines · " + s.memory.entries + "/40 entries)";
      $("memWarn").classList.toggle("hidden", !s.memory.over_threshold);

      $("shippedN").textContent = s.progress.shipped;
      $("inProgressN").textContent = s.progress.in_progress;
      $("pendingN").textContent = s.progress.pending;
      $("progChars").textContent = fmtNum(s.progress.chars);
      $("progressUpdated").textContent = s.progress.last_updated || "—";
      $("progressBody").innerHTML = window.marked.parse(stripFrontmatter(s.progress.raw) || "");

      $("otherCountInner").textContent = state.other.length;
      renderOtherList(state.other);

      if (state.selected) selectTask(state.selected.bucket, state.selected.slug);
      if (state.selectedOther) selectOther(state.selectedOther);
    });
  }

  function startSSE() {
    var es = new EventSource("/api/events");
    es.onmessage = function (e) {
      try {
        var data = JSON.parse(e.data);
        if (data.mtime !== state.mtime) {
          refresh();
          var dot = $("liveDot");
          dot.classList.add("flash");
          setTimeout(function () { dot.classList.remove("flash"); }, 600);
        }
      } catch (err) {}
    };
    es.onerror = function () { $("liveDot").classList.add("stale"); };
    es.onopen  = function () { $("liveDot").classList.remove("stale"); };
  }

  $$(".tab").forEach(function (t) {
    t.addEventListener("click", function () { setTab(t.dataset.tab); });
  });
  ["active", "completed", "archived"].forEach(function (b) {
    var btn = $("loadMore" + b.charAt(0).toUpperCase() + b.slice(1));
    if (btn) btn.addEventListener("click", function () {
      state.expanded[b] = !state.expanded[b];
      renderAllTaskLists();
    });
  });
  window.addEventListener("keydown", function (e) {
    if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA") return;
    var map = { "1": "tasks", "2": "memory", "3": "progress", "4": "other" };
    if (map[e.key]) setTab(map[e.key]);
  });

  // honor ?tab=name on initial load
  var params = new URLSearchParams(location.search);
  if (params.get("tab")) setTab(params.get("tab"));

  refresh();
  startSSE();
})();
