/* Homepage: stats, condition wall, tools, free-check finder, team, signup. */
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

  // ---------- free checks near you ----------
  const KINDS = [
    { id: "bp", tab: "Free blood pressure machines", q: "pharmacy",
      title: "Pharmacies and grocery stores",
      text: "Many have a free blood pressure machine near the pharmacy counter. No appointment needed. For a good reading, sit quietly for 5 minutes first, feet flat, arm resting at heart level." },
    { id: "chc", tab: "Blood pressure + cholesterol checks", q: "community health center",
      title: "Community health centers",
      text: "They charge based on your income, and for some people it's free. Ask for a blood pressure check and a cholesterol test (lipid panel).",
      link: { href: "https://findahealthcenter.hrsa.gov/", label: "Search the official health center finder" } },
    { id: "dept", tab: "Health department events", q: "county health department",
      title: "Your local health department",
      text: "Health departments often run free screening events. Call or check their website for upcoming dates." },
  ];
  let kind = KINDS[0], where = null;
  const fTabs = $("#finder-tabs"), fInfo = $("#finder-info"), fMap = $("#finder-map"), fEmpty = $("#finder-empty"), fMsg = $("#finder-msg");
  if (fTabs) {
    fTabs.innerHTML = KINDS.map((k, i) => `<button class="tool-tab" type="button" role="tab" aria-selected="${i === 0}" data-kind="${k.id}">${esc(k.tab)}</button>`).join("");
    const render = () => {
      $$(".tool-tab", fTabs).forEach((b) => b.setAttribute("aria-selected", String(b.dataset.kind === kind.id)));
      const query = where ? `${kind.q} near ${where}` : "";
      fInfo.innerHTML = `<h3 class="h-card">${esc(kind.title)}</h3><p>${esc(kind.text)}</p>`
        + (query ? `<p><a class="btn btn-ink" href="https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(query)}" target="_blank" rel="noopener">Open in Maps</a></p>` : "")
        + (kind.link ? `<p><a class="textlink" href="${esc(kind.link.href)}" target="_blank" rel="noopener">${esc(kind.link.label)}</a></p>` : "");
      if (query) {
        fMap.src = `https://maps.google.com/maps?q=${encodeURIComponent(query)}&z=13&output=embed`;
        fMap.hidden = false; fEmpty.hidden = true;
      }
    };
    fTabs.addEventListener("click", (e) => {
      const b = e.target.closest("[data-kind]");
      if (!b) return;
      kind = KINDS.find((k) => k.id === b.dataset.kind);
      render();
    });
    $("#finder-form").addEventListener("submit", (e) => {
      e.preventDefault();
      const zip = $("#finder-zip").value.trim();
      if (!/^\d{5}$/.test(zip)) { fMsg.textContent = "Enter a 5-digit ZIP code, like 94536."; $("#finder-zip").focus(); return; }
      fMsg.textContent = ""; where = zip; render();
    });
    $("#finder-geo").addEventListener("click", () => {
      if (!navigator.geolocation) { fMsg.textContent = "Location isn't available in this browser. Type your ZIP code instead."; return; }
      fMsg.textContent = "Finding your location\u2026";
      navigator.geolocation.getCurrentPosition(
        (pos) => { where = `${pos.coords.latitude.toFixed(3)},${pos.coords.longitude.toFixed(3)}`; fMsg.textContent = ""; render(); },
        () => { fMsg.textContent = "Couldn't get your location. Type your ZIP code instead."; },
        { timeout: 10000, maximumAge: 600000 });
    });
    render();
    reveal($(".finder"));
  }

  // call-to-action card: button opens one email to both founders; addresses also shown for webmail users
  const emailsText = ((SITE.contact && SITE.contact.emails) || []).join(" and ");
  const firstCard = (f, cls) => f ? `
    <div class="first-card ${cls || ""}">
      <b>${esc(f.title)}</b>
      <p>${esc(f.text)}</p>
      <a class="btn" href="${esc(mailto(f.subject, f.body))}">${esc(f.cta || "Email us")}</a>
      ${emailsText ? `<span class="first-mail">Or write to ${esc(emailsText)}</span>` : ""}
    </div>` : "";

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
