/* Shared behaviour: nav, torn paper edges, paste-on reveals, count-ups, ECG traces. */
(function () {
  const SITE = window.SITE || {};
  const C = SITE.content || {};
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // ---------- helpers (exported) ----------
  function seeded(seed) {
    let s = seed >>> 0 || 1;
    return function () { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; };
  }
  function esc(str) {
    return String(str == null ? "" : str).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }
  function fmt(n) { return Math.round(n).toLocaleString("en-US"); }
  function topicBySlug(slug) { return (C.topics || []).find((t) => t.slug === slug); }
  function store(key, fallback) {
    try { const v = localStorage.getItem(key); return v ? JSON.parse(v) : fallback; } catch (e) { return fallback; }
  }
  function save(key, value) { try { localStorage.setItem(key, JSON.stringify(value)); } catch (e) { /* storage blocked: counts stay in memory */ } }

  // ---------- org name ----------
  document.querySelectorAll("[data-org-name]").forEach((el) => { if (SITE.org) el.textContent = SITE.org.name; });
  const yr = document.getElementById("year"); if (yr) yr.textContent = new Date().getFullYear();

  // ---------- nav ----------
  const toggle = document.querySelector(".nav-toggle");
  const links = document.getElementById("nav-links");
  if (toggle && links) {
    toggle.addEventListener("click", () => {
      const open = links.classList.toggle("open");
      toggle.setAttribute("aria-expanded", String(open));
    });
    links.addEventListener("click", (e) => {
      if (e.target.closest("a")) { links.classList.remove("open"); toggle.setAttribute("aria-expanded", "false"); }
    });
  }

  // ---------- torn edges ----------
  function tornPath(rand, w, h, step) {
    let d = `M0 ${h} L0 ${h * 0.55}`;
    for (let x = 0; x <= w; x += step * (0.5 + rand())) {
      const y = h * (0.15 + rand() * 0.55);
      d += ` L${x.toFixed(1)} ${y.toFixed(1)}`;
    }
    return d + ` L${w} ${h * 0.5} L${w} ${h} Z`;
  }
  function addTornEdges(root) {
    (root || document).querySelectorAll("[data-torn]").forEach((band, i) => {
      if (band.querySelector(":scope > .torn")) return;
      const color = getComputedStyle(band).getPropertyValue("--band").trim() || "#fff";
      const rand = seeded(97 + i * 31);
      const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
      svg.setAttribute("class", "torn torn-top");
      svg.setAttribute("viewBox", "0 0 1200 34");
      svg.setAttribute("preserveAspectRatio", "none");
      svg.setAttribute("aria-hidden", "true");
      const fiberPath = tornPath(rand, 1200, 34, 9);
      const edgePath = tornPath(seeded(13 + i * 7), 1200, 34, 11).replace(/ (\d+\.?\d*)(?= L| Z)/g, (m, y) => " " + (parseFloat(y) + 4).toFixed(1));
      svg.innerHTML = `<path class="fiber" d="${fiberPath}"/><path d="${edgePath}" fill="${color}"/>`;
      band.prepend(svg);
    });
  }

  // jagged clip outline for poster cards (top and bottom edges torn, sides straight)
  function tornClip(el, seed) {
    const rand = seeded(seed);
    const pts = [];
    const n = 18;
    for (let i = 0; i <= n; i++) pts.push(`${(i / n * 100).toFixed(2)}% ${(rand() * 7).toFixed(1)}px`);
    for (let i = n; i >= 0; i--) pts.push(`${(i / n * 100).toFixed(2)}% calc(100% - ${(rand() * 7).toFixed(1)}px)`);
    el.style.setProperty("--clip", `polygon(${pts.join(",")})`);
  }
  function tearCards(root) {
    (root || document).querySelectorAll("[data-torn-card]").forEach((el, i) => tornClip(el, 211 + i * 17));
  }

  // ---------- paste-on reveal ----------
  const io = "IntersectionObserver" in window && !reduceMotion
    ? new IntersectionObserver((entries) => {
        entries.forEach((en) => {
          if (!en.isIntersecting) return;
          en.target.classList.add("in");
          en.target.dispatchEvent(new CustomEvent("revealed"));
          io.unobserve(en.target);
        });
      }, { threshold: 0.18, rootMargin: "0px 0px -6% 0px" })
    : null;
  function reveal(el, delay) {
    if (delay) el.style.setProperty("--delay", delay + "s");
    el.classList.add("reveal");
    if (io) io.observe(el);
    else { el.classList.add("in"); requestAnimationFrame(() => el.dispatchEvent(new CustomEvent("revealed"))); }
  }
  function onVisible(el, fn) {
    if (!("IntersectionObserver" in window)) return fn();
    const o = new IntersectionObserver((es) => { if (es[0].isIntersecting) { o.disconnect(); fn(); } }, { threshold: 0.3 });
    o.observe(el);
  }

  // ---------- count-ups ----------
  function countUp(el, target, opts) {
    opts = opts || {};
    const pre = opts.prefix || "", suf = opts.suffix || "", dec = opts.decimals || 0;
    const render = (v) => { el.textContent = pre + (dec ? v.toFixed(dec) : fmt(v)) + suf; };
    if (reduceMotion || !isFinite(target)) { render(target || 0); return; }
    const dur = opts.duration || 1400;
    const t0 = performance.now();
    function frame(t) {
      const p = Math.min(1, (t - t0) / dur);
      const e = 1 - Math.pow(1 - p, 3);
      render(target * e);
      if (p < 1) requestAnimationFrame(frame); else render(target);
    }
    requestAnimationFrame(frame);
  }

  // ---------- ECG traces ----------
  function prepTrace(svg) {
    svg.querySelectorAll("path").forEach((p) => {
      try { svg.style.setProperty("--len", Math.ceil(p.getTotalLength() * 1.02)); } catch (e) {}
    });
  }
  function ecgRulePath(width, beats) {
    const seg = width / beats;
    let d = `M0 22`;
    for (let i = 0; i < beats; i++) {
      const x = i * seg;
      d += ` H${(x + seg * 0.35).toFixed(1)} l${(seg * 0.04).toFixed(1)} -5 l${(seg * 0.04).toFixed(1)} 5 H${(x + seg * 0.5).toFixed(1)} l4 5 l7 -22 l7 30 l5 -13 H${(x + seg * 0.8).toFixed(1)} l${(seg * 0.06).toFixed(1)} -7 l${(seg * 0.06).toFixed(1)} 7`;
    }
    return d + ` H${width}`;
  }
  function makeEcgRule() {
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("class", "ecg-rule");
    svg.setAttribute("viewBox", "0 0 1000 40");
    svg.setAttribute("preserveAspectRatio", "none");
    svg.setAttribute("aria-hidden", "true");
    svg.innerHTML = `<path d="${ecgRulePath(1000, 3)}"/>`;
    return svg;
  }

  // Email link to every founder address at once (contact.emails in data.base.js)
  function mailto(subject, body) {
    const to = ((SITE.contact && SITE.contact.emails) || []).join(",");
    const q = [];
    if (subject) q.push("subject=" + encodeURIComponent(subject));
    if (body) q.push("body=" + encodeURIComponent(body));
    return "mailto:" + to + (q.length ? "?" + q.join("&") : "");
  }
  document.querySelectorAll("[data-mailto]").forEach((a) => { a.href = mailto(a.dataset.mailto); });
  document.querySelectorAll("[data-emails]").forEach((el) => { el.textContent = ((SITE.contact && SITE.contact.emails) || []).join(" and "); });

  window.SOH = { SITE, C, seeded, esc, fmt, topicBySlug, store, save, reveal, onVisible, countUp, tearCards, addTornEdges, prepTrace, makeEcgRule, reduceMotion, mailto };

  document.addEventListener("DOMContentLoaded", () => {
    addTornEdges();
    tearCards();
    const hero = document.querySelector(".hero-ecg");
    if (hero) { prepTrace(hero); requestAnimationFrame(() => hero.classList.add("draw")); }
  });
})();
