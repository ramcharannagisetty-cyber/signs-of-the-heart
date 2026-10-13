/* Homepage: stats, condition wall, tools, billboards + download gate, stories, team, signup. */
(function () {
  const { SITE, C, esc, fmt, topicBySlug, store, save, reveal, onVisible, countUp, tearCards, mailto } = window.SOH;
  const phTag = (text, dark) => `<span class="ph-tag${dark ? " ph-tag-dark" : ""}">${esc(text || "Placeholder")}</span>`;
  const $ = (s, r) => (r || document).querySelector(s);
  const $$ = (s, r) => Array.from((r || document).querySelectorAll(s));
  const arrow = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h13M13 6l6 6-6 6" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></svg>';

  // ---------- stats plates ----------
  const statsEl = $("#home-stats");
  const stats = C.home_stats || [];
  statsEl.innerHTML = stats.map((s, i) => `
    <div class="plate" data-i="${i}">
      <div class="plate-num" data-num="${Number(s.number) || 0}">${esc(s.value)}</div>
      <div class="plate-label">${esc(s.label)}</div>
      <div class="plate-src">Source: <a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.source)}</a></div>
    </div>`).join("");
  $$(".plate", statsEl).forEach((plate, i) => {
    reveal(plate, i * 0.08);
    const s = stats[i];
    const numEl = $(".plate-num", plate);
    // Count up only when the displayed value is a plain number (keeps "1 in 5" style values as written)
    const plain = /^[^\d]*[\d,.]+[^\d]*$/.test(s.value) && s.number;
    if (plain) {
      const m = String(s.value).match(/^([^\d]*)([\d,.]+)(.*)$/);
      const decimals = (m[2].split(".")[1] || "").length;
      onVisible(plate, () => countUp(numEl, Number(m[2].replace(/,/g, "")), { prefix: m[1], suffix: m[3], decimals }));
    }
  });

  // ---------- condition wall ----------
  const wall = $("#wall");
  const tones = { red: "is-red", caution: "is-caution", ecg: "is-ecg", dark: "is-dark", paper: "" };
  wall.innerHTML = (SITE.wall || []).map((w) => {
    const t = topicBySlug(w.slug) || { name: w.slug, kicker: "", dek: "" };
    return `<a class="poster w-${w.span} ${tones[w.tone] || ""}" href="topic.html?t=${encodeURIComponent(w.slug)}" style="--tilt:${w.tilt}deg" data-tilt data-torn-card>
      <span class="route">${esc(w.kicker || t.kicker || "Guide")}</span>
      <h3 class="h-card">${esc(w.label || t.name)}</h3>
      <p class="dek">${esc(t.dek)}</p>
      ${w.span >= 4 && t.stats && t.stats[0] ? `<p class="poster-stat"><b>${esc(t.stats[0].value)}</b>${esc(t.stats[0].label)}</p>` : ""}
      <span class="go">Read the guide ${arrow}</span>
    </a>`;
  }).join("");
  tearCards(wall);
  $$(".poster", wall).forEach((p, i) => reveal(p, (i % 3) * 0.08));
  const ft = $("#footer-topics");
  if (ft) ft.innerHTML = (SITE.wall || []).map((w) => { const t = topicBySlug(w.slug); return t ? `<li><a href="topic.html?t=${w.slug}">${esc(w.label || t.name)}</a></li>` : ""; }).join("");

  // ---------- tool tabs ----------
  const tabs = $$(".tool-tab");
  function selectTab(tab) {
    tabs.forEach((t) => {
      const on = t === tab;
      t.setAttribute("aria-selected", String(on));
      t.tabIndex = on ? 0 : -1;
      $("#" + t.getAttribute("aria-controls")).hidden = !on;
    });
    tearCards($("#check"));
  }
  tabs.forEach((tab, i) => {
    tab.addEventListener("click", () => selectTab(tab));
    tab.addEventListener("keydown", (e) => {
      const d = e.key === "ArrowRight" ? 1 : e.key === "ArrowLeft" ? -1 : 0;
      if (!d) return;
      e.preventDefault();
      const next = tabs[(i + d + tabs.length) % tabs.length];
      next.focus(); selectTab(next);
    });
  });
  reveal($("#check .tool-tabs"));

  // ---------- symptom checklist ----------
  const sc = C.symptom_checker;
  if (sc) {
    $("#sc-intro").textContent = sc.intro;
    $("#sc-disclaimer").textContent = sc.disclaimer;
    $("#sc-list").innerHTML = sc.symptoms.map((s) => `
      <li><label class="check"><input type="checkbox" name="sym" value="${esc(s.id)}" data-level="${esc(s.level)}"><span>${esc(s.label)}</span></label></li>`).join("");
    const out = $("#sc-result");
    $("#sc-form").addEventListener("submit", (e) => {
      e.preventDefault();
      const picked = $$("input[name=sym]:checked");
      const level = picked.some((i) => i.dataset.level === "emergency") ? "emergency" : picked.length ? "soon" : "none";
      const r = sc.results[level];
      out.className = "result " + level;
      out.innerHTML = `<h4>${esc(r.title)}</h4>${level === "emergency" ? '<a class="big911" href="tel:911">Call 911</a>' : ""}<p>${esc(r.text)}</p>`;
      out.hidden = false;
      out.scrollIntoView({ behavior: window.SOH.reduceMotion ? "auto" : "smooth", block: "nearest" });
    });
    $("#sc-form").addEventListener("reset", () => { out.hidden = true; });
  }

  // ---------- know your numbers ----------
  const N = C.numbers;
  if (N) {
    $("#numbers-disclaimer").textContent = N.disclaimer;
    $("#bp-src").innerHTML = `Ranges: <a href="${esc(N.bp_source.url)}" target="_blank" rel="noopener">${esc(N.bp_source.name)}</a>`;
    $("#chol-src").innerHTML = `Ranges: <a href="${esc(N.cholesterol_source.url)}" target="_blank" rel="noopener">${esc(N.cholesterol_source.name)}</a>`;

    // BP: categories come in guideline order (lowest to highest). Thresholds parsed from the data strings.
    const parseRange = (str) => {
      const s = String(str).replace(/[–—]/g, "-").replace(/\s/g, "").toLowerCase();
      let m;
      if ((m = s.match(/^(?:lessthan|under|below|<)(\d+)/))) return [-Infinity, Number(m[1]) - 1];
      if ((m = s.match(/^(\d+)-(\d+)/))) return [Number(m[1]), Number(m[2])];
      if ((m = s.match(/^(?:≥|>=|atleast)(\d+)/))) return [Number(m[1]), Infinity];
      if ((m = s.match(/^(?:higherthan|over|>)(\d+)/))) return [Number(m[1]) + 1, Infinity];
      if ((m = s.match(/^(\d+)(?:orhigher|\+|ormore)/))) return [Number(m[1]), Infinity];
      return null;
    };
    const inR = (v, r) => r && v >= r[0] && v <= r[1];
    function bpCategory(sys, dia) {
      let match = null;
      N.bp.forEach((c) => {
        const rs = parseRange(c.systolic), rd = parseRange(c.diastolic);
        const logic = String(c.logic).toLowerCase().includes("or") ? "or" : "and";
        const hit = logic === "or" ? inR(sys, rs) || inR(dia, rd) : inR(sys, rs) && inR(dia, rd);
        if (hit) match = c; // later (higher) categories win
      });
      return match;
    }
    const bpColors = ["#bfe3cf", "#fff0b3", "#ffd29a", "#f7a08f", "#e0475c"];
    $("#bp-form").addEventListener("submit", (e) => {
      e.preventDefault();
      const sys = Math.round(Number($("#bp-sys").value)), dia = Math.round(Number($("#bp-dia").value));
      const out = $("#bp-out");
      out.hidden = false;
      if (!sys || !dia) { out.innerHTML = "<p>Enter both numbers, for example 128 over 82.</p>"; return; }
      const cat = bpCategory(sys, dia);
      if (!cat) { out.innerHTML = "<p>Those numbers look unusual. Double-check the reading and try again.</p>"; return; }
      const idx = N.bp.indexOf(cat);
      out.innerHTML = `<strong>${esc(cat.name)}</strong><p>${sys}/${dia} mm Hg. ${esc(cat.advice)}</p>
        <div class="roadscale"><div class="roadscale-marker"><i style="left:${((idx + 0.5) / N.bp.length) * 100}%"></i></div>
        <div class="roadscale-bar">${N.bp.map((_, i) => `<span style="background:${bpColors[Math.min(i, bpColors.length - 1)]}"></span>`).join("")}</div>
        <div class="roadscale-labels">${N.bp.map((c) => `<span>${esc(c.name)}</span>`).join("")}</div></div>`;
    });

    // green = healthy, amber = in between, red = high risk (low is the risky end for HDL)
    function bandColor(m, b) {
      const n = b.name.toLowerCase();
      if (/hdl/i.test(m.measure)) return n.includes("low") ? "#f7a08f" : "#bfe3cf";
      if (/very|^high/.test(n)) return "#f7a08f";
      if (/borderline|elevated/.test(n)) return "#ffd29a";
      return "#bfe3cf";
    }
    const sel = $("#chol-measure");
    sel.innerHTML = N.cholesterol.map((m, i) => `<option value="${i}">${esc(m.measure)}</option>`).join("");
    $("#chol-form").addEventListener("submit", (e) => {
      e.preventDefault();
      const m = N.cholesterol[Number(sel.value)];
      const v = Math.round(Number($("#chol-val").value));
      const out = $("#chol-out");
      out.hidden = false;
      if (!v) { out.innerHTML = "<p>Enter a number in mg/dL, for example 190.</p>"; return; }
      const band = m.bands.find((b) => (b.min == null || v >= b.min) && (b.max == null || v <= b.max));
      if (!band) { out.innerHTML = "<p>That number is outside the ranges we show. Check the value and units (mg/dL).</p>"; return; }
      const idx = m.bands.indexOf(band);
      out.innerHTML = `<strong>${esc(m.measure)}: ${esc(band.name)}</strong><p>${v} mg/dL. Range: ${esc(band.range)}.</p>
        <div class="roadscale"><div class="roadscale-marker"><i style="left:${((idx + 0.5) / m.bands.length) * 100}%"></i></div>
        <div class="roadscale-bar">${m.bands.map((b) => `<span style="background:${bandColor(m, b)}"></span>`).join("")}</div>
        <div class="roadscale-labels">${m.bands.map((b) => `<span>${esc(b.name)}</span>`).join("")}</div></div>`;
    });
  }

  // ---------- myth cards ----------
  const myths = C.myth_cards || [];
  $("#myths").innerHTML = myths.map((m, i) => `
    <div class="myth-wrap">
      <button class="myth" type="button" aria-pressed="false" aria-label="Myth: ${esc(m.myth)}. Flip to see the fact.">
        <span class="myth-inner">
          <span class="myth-face myth-front"><span class="myth-tag">Myth</span><p>${esc(m.myth)}</p><span class="myth-hint">Tap to flip</span></span>
          <span class="myth-face myth-back"><span class="myth-tag">Fact</span><p>${esc(m.fact)}</p></span>
        </span>
      </button>
      <a class="myth-src" href="${esc(m.url)}" target="_blank" rel="noopener">Source: ${esc(m.source)}</a>
    </div>`).join("");
  $$("#myths .myth").forEach((b, i) => b.addEventListener("click", () => {
    const on = b.getAttribute("aria-pressed") !== "true";
    b.setAttribute("aria-pressed", String(on));
    b.setAttribute("aria-label", on ? `Fact: ${myths[i].fact}` : `Myth: ${myths[i].myth}. Flip to see the fact.`);
  }));

  // ---------- CPR trainer ----------
  const cpr = C.cpr;
  if (cpr) {
    const lo = cpr.rate_min, hi = cpr.rate_max;
    $("#cpr-intro").textContent = `Hands-only CPR means pushing hard and fast in the center of the chest at ${lo} to ${hi} pushes a minute, ${cpr.depth}. Practice the beat here.`;
    $("#cpr-steps").innerHTML = (cpr.steps || []).map((s) => `<li>${esc(s)}</li>`).join("");
    $("#cpr-help").textContent = cpr.songs && cpr.songs.length ? `Songs with the right beat: ${cpr.songs.join(", ")}.` : "";
    $("#cpr-src").innerHTML = `Source: <a href="${esc(cpr.url)}" target="_blank" rel="noopener">${esc(cpr.source)}</a>. Practice only. Take a real CPR class to learn properly.`;
    $(".cpr-scale").innerHTML = `<span>70</span><span>${lo}</span><span>${hi}</span><span>160</span>`;
    const meter = $(".cpr-meter");
    const pct = (v) => ((Math.min(160, Math.max(70, v)) - 70) / 90) * 100;
    meter.style.background = `linear-gradient(90deg, #f0d6d2 0 ${pct(lo)}%, #bfe3cf ${pct(lo)}% ${pct(hi)}%, #f0d6d2 ${pct(hi)}%)`;
    const scale = $(".cpr-scale");
    scale.style.position = "relative"; scale.style.height = "1.2em";
    $$("span", scale).forEach((s, i) => { s.style.position = "absolute"; s.style.left = pct([70, lo, hi, 160][i]) + "%"; s.style.translate = "-50% 0"; });

    const pad = $("#cpr-pad"), bpmEl = $("#cpr-bpm"), zone = $("#cpr-zone"), needle = $("#cpr-needle");
    let taps = [];
    function tap() {
      const now = performance.now();
      taps = taps.filter((t) => now - t < 4000);
      taps.push(now);
      pad.classList.add("hit"); setTimeout(() => pad.classList.remove("hit"), 90);
      if (taps.length < 3) { zone.textContent = "Keep going…"; zone.className = "zone"; return; }
      const gaps = taps.slice(1).map((t, i) => t - taps[i]).slice(-6);
      const bpm = 60000 / (gaps.reduce((a, b) => a + b, 0) / gaps.length);
      bpmEl.textContent = Math.round(bpm);
      needle.style.left = pct(bpm) + "%";
      if (bpm < lo) { zone.textContent = "Faster. Push a little quicker."; zone.className = "zone slow"; }
      else if (bpm > hi) { zone.textContent = "Slow down a little."; zone.className = "zone fast"; }
      else { zone.textContent = "That's the beat. Keep it steady."; zone.className = "zone good"; }
    }
    pad.addEventListener("pointerdown", (e) => { e.preventDefault(); tap(); });
    pad.addEventListener("keydown", (e) => { if (e.key === " " || e.key === "Enter") { e.preventDefault(); if (!e.repeat) tap(); } });
    pad.addEventListener("click", (e) => { if (e.detail === 0) return; }); // pointerdown already counted

    let ctx = null, timer = null;
    const metro = $("#cpr-metro");
    const beat = Math.round((lo + hi) / 2);
    metro.textContent = `Play a ${beat} beat`;
    metro.addEventListener("click", () => {
      const on = metro.getAttribute("aria-pressed") !== "true";
      metro.setAttribute("aria-pressed", String(on));
      metro.textContent = on ? "Stop the beat" : `Play a ${beat} beat`;
      if (!on) { clearInterval(timer); return; }
      try {
        ctx = ctx || new (window.AudioContext || window.webkitAudioContext)();
        const click = () => {
          const o = ctx.createOscillator(), g = ctx.createGain();
          o.frequency.value = 880; g.gain.setValueAtTime(0.25, ctx.currentTime); g.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.08);
          o.connect(g).connect(ctx.destination); o.start(); o.stop(ctx.currentTime + 0.09);
          pad.classList.add("hit"); setTimeout(() => pad.classList.remove("hit"), 90);
        };
        click(); timer = setInterval(click, 60000 / beat);
      } catch (e) { metro.textContent = "Sound isn't available in this browser"; }
    });
  }

  // ---------- billboards ----------
  const BB = SITE.billboards;
  const local = store("soh-billboards", { downloads: 0, placed: 0, reached: 0, perTemplate: {}, reports: [] });
  // Shown counts are the placeholder seed only. There is no shared backend yet, so this
  // browser's own downloads/reports are kept locally and never mixed into the displayed numbers.

  const boards = $("#boards");
  boards.innerHTML = BB.templates.map((t) => `
    <article class="board" data-id="${esc(t.id)}">
      <div class="board-frame${t.image ? " has-img" : ""}">
        <div class="board-lamps" aria-hidden="true"><i></i><i></i><i></i></div>
        <div class="board-face">
          ${t.image ? `<img src="${esc(t.image)}" alt="${esc(t.alt || t.title + " billboard design")}" loading="lazy">` : `<div><span class="slot-label">${t.placeholder ? "Placeholder template" : "Your design here"}</span><span class="slot-size">${t.placeholder ? "Final design coming soon" : esc(t.title) + " template"}</span></div>`}
        </div>
      </div>
      <div class="board-catwalk" aria-hidden="true"></div>
      <div class="board-posts" aria-hidden="true"><span></span><span></span></div>
      <div class="board-meta">
        <div><h3>${esc(t.title)}</h3>${t.design ? `<span class="dl-count">${esc(t.design)}</span>` : ""}</div>
        <button class="btn btn-caution" type="button" data-download="${esc(t.id)}" aria-label="Download ${esc(t.title)} ${esc(t.design || "")}">Download</button>
      </div>
    </article>`).join("");
  $$(".board", boards).forEach((b) => onVisible(b, () => b.classList.add("lit")));
  // decorative road sign + heartbeat line in place of counters
  const pulse = $(".road-pulse");
  if (pulse) { window.SOH.prepTrace(pulse); reveal(pulse); reveal($(".road-sign svg")); }
  const step = () => ($(".board", boards).getBoundingClientRect().width + 40);
  $("#boards-prev").addEventListener("click", () => boards.scrollBy({ left: -step(), behavior: "smooth" }));
  $("#boards-next").addEventListener("click", () => boards.scrollBy({ left: step(), behavior: "smooth" }));



  // ---------- download gate ----------
  const gate = $("#gate"), form = $("#gate-form"), placement = $("#placement");
  let current = null, reportOnly = false;
  function setPlacement(mode) {
    if (mode !== "putting" && mode !== "placed") { placement.hidden = true; placement.innerHTML = ""; return; }
    if (!placement.firstChild) {
      placement.appendChild($("#placement-fields").content.cloneNode(true));
      if (reportOnly) {
        const f = document.createElement("div");
        f.className = "field";
        f.innerHTML = `<label for="pl-template">Which design?</label><select id="pl-template" name="template" required>${BB.templates.map((t) => `<option value="${esc(t.id)}">${esc(t.title)}${t.design ? " – " + esc(t.design) : ""}</option>`).join("")}</select>`;
        placement.prepend(f);
      }
    }
    placement.hidden = false;
    $("[data-date-label]", placement).textContent = mode === "placed" ? "Date it went up" : "Date it goes up";
    $("[data-photo-field]", placement).hidden = mode !== "placed";
  }
  form.addEventListener("change", (e) => { if (e.target.name === "use") setPlacement(e.target.value); });

  function openGate(id, report) {
    reportOnly = !!report;
    current = BB.templates.find((t) => t.id === id) || BB.templates[0];
    form.reset(); placement.innerHTML = ""; placement.hidden = true;
    $("#gate-error").textContent = "";
    $("#gate-ask").hidden = false; $("#gate-thanks").hidden = true;
    $("#gate-title").textContent = reportOnly ? "Tell us where it went up" : "Before you download";
    $(".choices", gate).hidden = reportOnly;
    $("#gate-ask .tool-intro").innerHTML = reportOnly
      ? "Thank you for spreading the word. Fill this in, then you'll email us the details so we can count it."
      : `It's free. Tell us what you plan to do with the <b>${esc(current.title)}${current.design ? " (" + esc(current.design) + ")" : ""}</b> billboard. Your answer stays in this browser and isn't sent to us. If you put one up, you'll be able to email us the details so we can count it.${current.placeholder ? " <b>Note:</b> this is a placeholder template with layout guides only. The final design is coming soon." : ""}`;
    $("#gate-submit").textContent = reportOnly ? "Next: write the email" : "Download template";
    if (reportOnly) { $('input[value="placed"]', form).checked = true; setPlacement("placed"); }
    tearCards(gate);
    gate.showModal();
  }
  $$("[data-download]").forEach((b) => b.addEventListener("click", () => openGate(b.dataset.download)));
  $("#report-btn").addEventListener("click", () => openGate(null, true));
  gate.addEventListener("click", (e) => { if (e.target.closest("[data-close]") || e.target === gate) gate.close(); });

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const use = (new FormData(form).get("use")) || "";
    const err = $("#gate-error");
    if (!use) { err.textContent = "Choose one option to continue."; return; }
    if (use === "putting" || use === "placed") {
      const missing = $$("[required]", placement).filter((i) => !String(i.value).trim());
      if (missing.length) { err.textContent = "Fill in the place name, city and place type."; missing[0].focus(); return; }
    }
    err.textContent = "";
    const fd = new FormData(form);
    const views = Math.max(0, Number(fd.get("views")) || 0);
    const tid = reportOnly ? fd.get("template") : current.id;
    if (!reportOnly) {
      local.downloads += 1;
      local.perTemplate[tid] = (local.perTemplate[tid] || 0) + 1;
    }
    if (use === "placed") { local.placed += 1; local.reached += views; }
    const photo = fd.get("photo");
    local.reports.push({
      template: tid, use, place: fd.get("place") || "", city: fd.get("city") || "", type: fd.get("type") || "",
      date: fd.get("date") || "", views, photo: photo && photo.name ? photo.name : "", at: new Date().toISOString(),
    });
    save("soh-billboards", local);

    const msgs = {
      looking: current && current.placeholder
        ? "This is a placeholder template. Check back for the final design, and tap “I put one up” if you use it."
        : "Enjoy the design. If you end up putting it somewhere, come back and tap “I put one up”.",
      proposing: "Good luck with your pitch. Once it's up, tap “I put one up” and email us so we can count it.",
      putting: "Thank you. Send us the details below so we know it's coming, and tap “I put one up” once it's up.",
      placed: "Thank you for putting it up. To be counted, send us the details below. Attach your photo to the email if you have one.",
    };
    $("#gate-ask").hidden = true; $("#gate-thanks").hidden = false;
    $("#gate-thanks h2").textContent = reportOnly ? "Almost done" : "Downloading now";
    $("#gate-thanks-text").textContent = reportOnly ? msgs.placed : msgs[use];
    const emailBtn = $("#gate-email");
    const tpl = BB.templates.find((x) => x.id === tid);
    if (use === "putting" || use === "placed") {
      const lines = [
        use === "placed" ? "I put up one of your designs." : "I'm planning to put up one of your designs.",
        "",
        "Design: " + (tpl ? tpl.title + (tpl.design ? " " + tpl.design : "") : tid),
        "Place: " + (fd.get("place") || ""),
        "City and state: " + (fd.get("city") || ""),
        "Place type: " + (fd.get("type") || ""),
        "Date: " + (fd.get("date") || ""),
        "Estimated daily views: " + (views || ""),
        use === "placed" ? (photo && photo.name ? "Photo: please attach " + photo.name + " to this email before sending" : "Photo: attach one if you have it") : "",
      ];
      emailBtn.href = mailto((use === "placed" ? "Billboard placed: " : "Billboard planned: ") + (fd.get("place") || ""), lines.join("\n"));
      emailBtn.hidden = false;
      $("#gate-thanks-text").textContent += ` Nothing opens when you tap the button? Write to ${emailsText}.`;
    } else emailBtn.hidden = true;
    if (!reportOnly) {
      downloadTemplate(current);
      if (current.svg) $("#gate-thanks-text").insertAdjacentHTML("beforeend",
        ` <br><a class="textlink" href="${esc(current.svg)}" download="${esc(current.id)}-billboard-vector.svg">Need it for a print shop? Get the vector file (SVG).</a>`);
    }
  });

  // Builds a blank billboard template (48:14) as an SVG file with safe-area guides.
  function downloadTemplate(t) {
    if (t.file) {
      const link = document.createElement("a");
      link.href = t.file;
      link.download = `signs-of-the-heart-${t.id}.jpg`;
      document.body.appendChild(link); link.click(); link.remove();
      return;
    }
    const W = 4800, H = 1400, m = 140;
    const svg = `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
  <title>${esc(t.title)} billboard template, ${esc(SITE.org.name)}</title>
  <rect width="${W}" height="${H}" fill="#fffbfa"/>
  <rect x="0" y="0" width="${W * 0.36}" height="${H}" fill="#c8102e"/>
  <rect x="${m}" y="${m}" width="${W - 2 * m}" height="${H - 2 * m}" fill="none" stroke="#ffc72c" stroke-width="8" stroke-dasharray="40 30"/>
  <text x="${m + 60}" y="${m + 220}" font-family="EB Garamond, Garamond, serif" font-weight="800" font-size="${t.title.length > 14 ? 130 : 170}" fill="#fff">${esc(t.title)}</text>
  <text x="${W * 0.36 + 140}" y="${H / 2 - 40}" font-family="EB Garamond, Garamond, serif" font-weight="800" font-size="260" fill="#1c1517">Your message here</text>
  <text x="${W * 0.36 + 140}" y="${H / 2 + 140}" font-family="Overpass, Arial, sans-serif" font-weight="700" font-size="110" fill="#4d4245">Keep it to 7 words or fewer.</text>
  <text x="${m + 60}" y="${H - m - 60}" font-family="Overpass, Arial, sans-serif" font-weight="800" font-size="90" fill="#fff">${esc(SITE.org.name)}</text>
  <text x="${W - m - 40}" y="${H - m - 60}" text-anchor="end" font-family="Overpass, Arial, sans-serif" font-size="70" fill="#4d4245">Source: add the source for your message here</text>
  <text x="${W - m - 40}" y="${m - 40}" text-anchor="end" font-family="Overpass, Arial, sans-serif" font-size="56" fill="#9a8f8d">Dashed line = safe area. Template size ${esc(BB.size)}.</text>${t.placeholder ? `
  <text x="${W * 0.36 + 140}" y="${m + 150}" font-family="Overpass, Arial, sans-serif" font-weight="900" font-size="90" fill="#c8102e">PLACEHOLDER TEMPLATE: final design coming soon</text>` : ""}
</svg>`;
    const blob = new Blob([svg], { type: "image/svg+xml" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `${t.id}-billboard-template${t.placeholder ? "-placeholder" : ""}.svg`;
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 4000);
  }

  // "be the first" card: button opens one email to both founders; addresses also shown for webmail users
  const emailsText = ((SITE.contact && SITE.contact.emails) || []).join(" and ");
  const firstCard = (f, cls) => f ? `
    <div class="first-card ${cls || ""}">
      <b>${esc(f.title)}</b>
      <p>${esc(f.text)}</p>
      <a class="btn" href="${esc(mailto(f.subject, f.body))}">Click here to be the first one</a>
      ${emailsText ? `<span class="first-mail">Or write to ${esc(emailsText)}</span>` : ""}
    </div>` : "";

  // ---------- stories ----------
  $("#stories-list").innerHTML = (SITE.stories || []).map((s, i) => `
    <figure class="poster ${i === 1 ? "is-ecg" : ""}" style="--tilt:${[-0.8, 0.6, -0.4][i % 3]}deg" data-tilt data-torn-card>
      <span class="tape" aria-hidden="true"></span>
      ${s.placeholder ? `<p style="margin:0 0 0.9rem">${phTag("Placeholder story")}</p>` : ""}
      <blockquote class="quote">“${esc(s.quote)}”</blockquote>
      <figcaption class="quote-by">${esc(s.name)}<span>${esc(s.role)}</span></figcaption>
    </figure>`).join("");
  $("#stories-list").insertAdjacentHTML("beforeend", firstCard((SITE.firstOne || {}).stories));
  tearCards($("#stories-list"));
  $$("#stories-list .poster").forEach((p, i) => reveal(p, i * 0.1));

  // ---------- team ----------
  const person = '<svg viewBox="0 0 40 40" aria-hidden="true"><circle cx="20" cy="14" r="8" fill="#c8102e"/><path d="M4 40c0-10 7-16 16-16s16 6 16 16" fill="#c8102e"/></svg>';
  const F = SITE.firstOne || {};
  $("#team").innerHTML = (SITE.team || []).map((m) => `
    <div class="member"><div class="arch">${m.photo ? `<img src="${esc(m.photo)}" alt="${esc(m.name)}">` : person}</div>
      <b>${esc(m.name)}</b><span>${esc(m.role)}</span>${m.placeholder ? `<span style="margin-top:0.35rem">${phTag("Placeholder")}</span>` : ""}</div>`).join("") +
    firstCard(F.team, "in-team") + firstCard(F.advisor, "in-team");

  // ---------- newsletter: opens the visitor's email app with a sign-up note to the founders ----------
  $("#signup").addEventListener("submit", (e) => {
    e.preventDefault();
    const input = $("#signup-email"), msg = $("#signup-msg");
    if (!input.checkValidity()) { msg.textContent = "Enter a valid email address, like you@example.com."; input.focus(); return; }
    window.location.href = mailto("Monthly heart tip sign-up", `Please add me to the monthly heart tip list: ${input.value}`);
    msg.textContent = `Your email app should open with a sign-up note. Press send to join. Nothing opened? Write to ${emailsText} with the subject "Monthly heart tip sign-up".`;
  });
})();
