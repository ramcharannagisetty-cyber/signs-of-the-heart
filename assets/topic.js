/* Condition guide page: renders one topic from data.content.js by ?t=slug */
(function () {
  const { SITE, C, esc, topicBySlug, reveal, tearCards, makeEcgRule, prepTrace } = window.SOH;
  const $ = (s, r) => (r || document).querySelector(s);
  const $$ = (s, r) => Array.from((r || document).querySelectorAll(s));

  const slug = new URLSearchParams(location.search).get("t") || (SITE.wall && SITE.wall[0].slug);
  const t = topicBySlug(slug);
  const order = (SITE.wall || []).map((w) => w.slug);

  const label = (s, x) => { const w = (SITE.wall || []).find((e) => e.slug === s); return (w && w.label) || x.name; };
  $("#footer-topics").innerHTML = order.map((s) => { const x = topicBySlug(s); return x ? `<li><a href="topic.html?t=${s}">${esc(label(s, x))}</a></li>` : ""; }).join("");
  $("#more-topics").innerHTML = order.filter((s) => s !== slug).map((s) => { const x = topicBySlug(s); return x ? `<a href="topic.html?t=${s}">${esc(label(s, x))}</a>` : ""; }).join("");

  if (!t) {
    $("#t-title").textContent = "We couldn't find that guide";
    $("#t-dek").innerHTML = 'Pick a condition from <a class="textlink" href="index.html#conditions">the full list</a>.';
    return;
  }

  document.title = `${t.name} | ${SITE.org.name}`;
  $("#t-kicker").textContent = t.kicker || t.name;
  $("#t-title").textContent = t.headline || t.name;
  $("#t-dek").textContent = t.dek;
  const wallEntry = (SITE.wall || []).find((w) => w.slug === slug);
  if (wallEntry && wallEntry.tone === "red") $("#t-poster").classList.add("is-red");

  const list = (items, cls) => `<ul class="ticks ${cls || ""}">${(items || []).map((i) => `<li>${esc(i)}</li>`).join("")}</ul>`;
  const human = (k) => ({
    stages_simple: "The four stages",
    difference: "Heart attack or cardiac arrest?",
    cpr_steps: "Hands-only CPR, step by step",
    be_fast: "Spot a stroke: BE FAST",
    measure_tips: "How to measure at home",
    two_numbers: "What the two numbers mean",
    bp_categories: "Blood pressure ranges",
    bp_categories_2025: "Blood pressure ranges",
    treatment_goal: "Treatment goal",
    numbers_decoded: "Your numbers, decoded",
    screening_schedule: "When to get checked",
    fh_spotlight: "Spotlight: familial hypercholesterolemia (FH)",
    ldl_goals_2026: "LDL goals in the newest guideline",
    how_they_team_up: "How they team up",
    action_plan: "Your action plan",
    guideline_check: "What the newest guidelines say",
    fmd_body_map: "Where FMD can show up",
    fmd_scad_link: "How FMD and SCAD connect",
    pregnancy_note: "SCAD and pregnancy",
    stroke_path: "From AFib to stroke",
    top: "Top number", bottom: "Bottom number", example: "Example",
    heart_attack: "Heart attack", cardiac_arrest: "Cardiac arrest",
    what: "What it is", how_common: "How common", clue: "Clue", action: "What to do",
    bp_2025: "Blood pressure (2025)", cholesterol_2026: "Cholesterol (2026)",
  }[k] || k.replace(/_/g, " ").replace(/^./, (c) => c.toUpperCase()));

  const isSource = (v) => v && typeof v === "object" && !Array.isArray(v) && (v.url || v.urls) && v.name;
  const srcLinks = (v) => (v.urls || [v.url]).map((u, i) => `<a href="${esc(u)}" target="_blank" rel="noopener">${esc((v.names && v.names[i]) || (i ? "more" : v.name))}</a>`).join(", ");
  const HEAD_KEYS = ["letter", "stage", "category", "name", "title", "area", "who", "number"];

  function renderExtra(key, val) {
    if (Array.isArray(val) && val.every((v) => typeof v === "string")) {
      const ordered = /step|path/.test(key);
      return ordered ? `<ol class="cpr-steps">${val.map((v) => `<li>${esc(v)}</li>`).join("")}</ol>` : list(val, "do");
    }
    if (Array.isArray(val)) {
      return `<ul class="${key === "be_fast" ? "letter-list" : "stage-list"}">${val.map((o) => {
        const hk = HEAD_KEYS.find((k) => o[k] != null && typeof o[k] === "string") || Object.keys(o)[0];
        const rest = Object.entries(o).filter(([k]) => k !== hk && k !== "step");
        let body;
        if (key === "be_fast") body = `<strong>${esc(o.word || "")}</strong><br>${esc(o.meaning || "")}`;
        else if (rest.length === 1) body = esc(rest[0][1]);
        else body = rest.map(([k, v]) => `<span class="kv"><em>${esc(human(k))}:</em> ${esc(v)}</span>`).join("");
        return `<li><b>${esc(o[hk])}</b>${body}</li>`;
      }).join("")}</ul>`;
    }
    if (val && typeof val === "object") {
      const entries = Object.entries(val).filter(([, v]) => !isSource(v));
      const sources = Object.values(val).filter(isSource);
      return `<div class="compare">${entries.map(([k, v]) => `<div><h3>${esc(human(k))}</h3><p>${esc(Array.isArray(v) ? v.join(" ") : v)}</p></div>`).join("")}</div>` +
        (sources.length ? `<p class="hint" style="margin-top:0.8rem">Sources: ${sources.map(srcLinks).join("; ")}</p>` : "");
    }
    return `<p>${esc(val)}</p>`;
  }

  const sections = [];
  sections.push({ id: "what", title: "What it is", html:
    (t.what_it_is || []).map((p) => `<p>${esc(p)}</p>`).join("") +
    (t.stats && t.stats.length ? `<div class="topic-stats" style="margin-top:1.6rem">${t.stats.slice(0, 3).map((s) => `
      <div class="plate"><div class="plate-num">${esc(s.value)}</div><div class="plate-label">${esc(s.label)}</div>
      <div class="plate-src">Source: <a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.source)}</a></div></div>`).join("")}</div>` : "") +
    (t.stats && t.stats.length > 3 ? `<h3 class="more-nums-h">More numbers</h3><ul class="more-nums">${t.stats.slice(3).map((s) => `
      <li><b>${esc(s.value)}</b> ${esc(s.label)} <a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.source)}</a></li>`).join("")}</ul>` : "") });

  sections.push({ id: "signs", title: "Warning signs", html: list(t.warning_signs) +
    (t.emergency_signs && t.emergency_signs.length ? `<div class="alert-911" role="note"><h3>Call 911 right away if</h3>${list(t.emergency_signs, "danger")}<p style="margin:1rem 0 0"><a class="btn btn-ink" href="tel:911">Call 911</a></p></div>` : "") });

  // extra topic sections; "*_source" entries become citations under the section before them
  Object.entries(t.extra || {}).forEach(([k, v], i) => {
    if (isSource(v)) {
      const owner = sections.find((sec) => sec.key === k.replace(/_source$/, ""));
      const prev = owner || sections[sections.length - 1];
      if (prev) prev.html += `<p class="hint" style="margin-top:0.8rem">Source: ${srcLinks(v)}</p>`;
      return;
    }
    sections.push({ id: "x" + i, key: k, title: human(k), html: renderExtra(k, v) });
  });

  sections.push({ id: "risk", title: "Who's at risk", html: list(t.risk_factors) });
  sections.push({ id: "do", title: "What you can do", html: list(t.what_you_can_do, "do") });
  if (t.questions_for_doctor && t.questions_for_doctor.length)
    sections.push({ id: "ask", title: "Questions for your doctor", html: `<ol class="cpr-steps">${t.questions_for_doctor.map((q) => `<li>${esc(q)}</li>`).join("")}</ol>` });
  if (t.myths && t.myths.length)
    sections.push({ id: "myths", title: "Myth or fact", html: `<div class="myths">${t.myths.map((m) => `
      <div class="myth-wrap">
        <button class="myth" type="button" aria-pressed="false" aria-label="Myth: ${esc(m.myth)}. Flip to see the fact." data-myth="${esc(m.myth)}" data-fact="${esc(m.fact)}">
          <span class="myth-inner">
            <span class="myth-face myth-front"><span class="myth-tag">Myth</span><p>${esc(m.myth)}</p><span class="myth-hint">Tap to flip</span></span>
            <span class="myth-face myth-back"><span class="myth-tag">Fact</span><p>${esc(m.fact)}</p></span>
          </span></button>
        <a class="myth-src" href="${esc(m.url)}" target="_blank" rel="noopener">Source: ${esc(m.source)}</a>
      </div>`).join("")}</div>` });
  sections.push({ id: "sources", title: "Sources", html: `<ul class="sources">${(t.sources || []).map((s) => `<li><a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.name)}</a></li>`).join("")}</ul>
    <p class="disclaimer">Written by student volunteers from the public sources above. Last checked October 2026. Not yet reviewed by a clinician. This guide is for education, not diagnosis. Talk with a doctor about your own health.</p>` });

  const body = $("#t-body");
  body.innerHTML = sections.map((s) => `<section class="topic-sec" id="${s.id}" aria-labelledby="h-${s.id}"><h2 id="h-${s.id}">${esc(s.title)}</h2>${s.html}</section>`).join("");
  $("#toc").innerHTML = sections.map((s) => `<a href="#${s.id}">${esc(s.title)}</a>`).join("");

  // ECG rule under each heading draws as it scrolls in
  $$(".topic-sec h2", body).forEach((h) => {
    const rule = makeEcgRule();
    h.after(rule);
    prepTrace(rule);
    reveal(rule);
  });
  $$(".topic-stats .plate, .alert-911", body).forEach((el, i) => reveal(el, (i % 3) * 0.08));

  $$(".myth", body).forEach((b) => b.addEventListener("click", () => {
    const on = b.getAttribute("aria-pressed") !== "true";
    b.setAttribute("aria-pressed", String(on));
    b.setAttribute("aria-label", on ? `Fact: ${b.dataset.fact}` : `Myth: ${b.dataset.myth}. Flip to see the fact.`);
  }));

  // highlight current section in the side nav
  if ("IntersectionObserver" in window) {
    const links = $$("#toc a");
    const io = new IntersectionObserver((es) => {
      es.forEach((en) => {
        if (!en.isIntersecting) return;
        links.forEach((a) => a.classList.toggle("active", a.getAttribute("href") === "#" + en.target.id));
      });
    }, { rootMargin: "-30% 0px -60% 0px" });
    $$(".topic-sec", body).forEach((s) => io.observe(s));
  }
  tearCards();
})();
