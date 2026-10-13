/* Billboards page (for partners): the 18 designs, the download form and "I put one up" reports. */
(function () {
  const { SITE, esc, store, save, onVisible, tearCards, mailto, reveal } = window.SOH;
  const $ = (s, r) => (r || document).querySelector(s);
  const $$ = (s, r) => Array.from((r || document).querySelectorAll(s));
  const emailsText = ((SITE.contact && SITE.contact.emails) || []).join(" and ");

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

  // decorative heartbeat line under the road sign
  const pulse2 = $(".road-pulse");
  if (pulse2 && !pulse2.classList.contains("reveal")) { window.SOH.prepTrace(pulse2); reveal(pulse2); }
})();
