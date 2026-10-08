// Two Way Miss Studio — shared page behavior (filters, gallery, lightbox, request form)
(function () {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];

  /* ---------- lightbox ---------- */
  const lb = $("#lb");
  let lbList = [], lbI = 0, lbTitle = "", lbPrefix = "";
  function lbShow(i) {
    lbI = (i + lbList.length) % lbList.length;
    const [f, alt] = lbList[lbI];
    const img = $("#lb-img");
    img.src = lbPrefix + "img/" + f;
    img.alt = alt;
    $("#lb-t").textContent = lbTitle;
    $("#lb-m").textContent = alt + (lbList.length > 1 ? ` · ${lbI + 1} / ${lbList.length}` : "");
    const multi = lbList.length > 1;
    $("#lb-p").hidden = !multi;
    $("#lb-n").hidden = !multi;
  }
  function lbOpen(list, i, title, prefix) {
    if (!lb) return;
    lbList = list; lbTitle = title; lbPrefix = prefix;
    lbShow(i);
    if (lb.showModal) lb.showModal(); else lb.setAttribute("open", "");
  }
  if (lb) {
    $("#lb-p").onclick = () => lbShow(lbI - 1);
    $("#lb-n").onclick = () => lbShow(lbI + 1);
    $("#lb-x").onclick = () => lb.close();
    lb.addEventListener("click", (e) => { if (e.target === lb) lb.close(); });
    lb.addEventListener("keydown", (e) => {
      if (e.key === "ArrowLeft") lbShow(lbI - 1);
      if (e.key === "ArrowRight") lbShow(lbI + 1);
    });
  }

  /* ---------- home: shop filters ---------- */
  const grid = $("#shopgrid");
  if (grid) {
    const setFilter = (f) => {
      $$(".filters button").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.f === f)));
      $$(".card", grid).forEach((c) => { c.hidden = !(f === "all" || c.dataset.c === f); });
    };
    $$(".filters button").forEach((b) => (b.onclick = () => setFilter(b.dataset.f)));
    $$("[data-go]").forEach((b) => (b.onclick = () => {
      setFilter(b.dataset.go);
      $("#shop").scrollIntoView({ behavior: "smooth" });
    }));
    const params = new URLSearchParams(location.search);
    const c = params.get("c");
    if (c && $(`.filters button[data-f="${CSS.escape(c)}"]`)) setFilter(c);
  }

  /* ---------- listing: photo gallery ---------- */
  const gal = $("#gallery");
  if (gal) {
    const data = JSON.parse(gal.dataset.gallery);
    const photos = data.photos;
    const img = $("#stage-img");
    const pos = $(".stage .pos");
    let cur = 0;
    const show = (i) => {
      cur = (i + photos.length) % photos.length;
      img.src = "../../img/" + photos[cur][0];
      img.alt = photos[cur][1];
      $$(".thumbs button").forEach((b, k) => b.setAttribute("aria-current", String(k === cur)));
      if (pos) pos.textContent = `${cur + 1} / ${photos.length}`;
      const t = $$(".thumbs button")[cur];
      if (t) t.scrollIntoView({ block: "nearest", inline: "nearest" });
    };
    $$(".thumbs button").forEach((b) => (b.onclick = () => show(+b.dataset.i)));
    const prev = $(".stage .prev"), next = $(".stage .next");
    if (prev) prev.onclick = (e) => { e.stopPropagation(); show(cur - 1); };
    if (next) next.onclick = (e) => { e.stopPropagation(); show(cur + 1); };
    $("#stage").addEventListener("click", () => lbOpen(photos, cur, data.title, "../../"));
    document.addEventListener("keydown", (e) => {
      if (lb && lb.open) return;
      if (e.key === "ArrowLeft") show(cur - 1);
      if (e.key === "ArrowRight") show(cur + 1);
    });
    // swipe on phones
    let x0 = null;
    $("#stage").addEventListener("touchstart", (e) => { x0 = e.touches[0].clientX; }, { passive: true });
    $("#stage").addEventListener("touchend", (e) => {
      if (x0 === null) return;
      const dx = e.changedTouches[0].clientX - x0;
      if (Math.abs(dx) > 40) show(cur + (dx < 0 ? 1 : -1));
      x0 = null;
    });
    // preload the rest
    photos.slice(1).forEach(([f]) => { const i = new Image(); i.src = "../../img/" + f; });
  }

  /* ---------- home: commission form ---------- */
  const form = $("#req");
  if (form) {
    const params = new URLSearchParams(location.search);
    const type = params.get("type"), course = params.get("course");
    if (type) {
      const sel = $("#f-type");
      [...sel.options].forEach((o) => { if (o.text === type) sel.value = o.value; });
    }
    if (course) $("#f-course").value = course;

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const v = (id) => $("#" + id).value.trim();
      const lines = [
        `Request: ${v("f-type")}`,
        v("f-course") && `Course: ${v("f-course")}`,
        v("f-hole") && `Hole: ${v("f-hole")}`,
        v("f-date") && `Date: ${v("f-date")}`,
        v("f-yds") && `Yards: ${v("f-yds")}`,
        v("f-club") && `Club: ${v("f-club")}`,
        v("f-name") && `Name: ${v("f-name")}`,
        v("f-notes") && `Notes: ${v("f-notes")}`,
      ].filter(Boolean).join("\n");
      const out = $("#out");
      out.textContent = lines;
      out.hidden = false;
      const note = $("#note");
      try {
        await navigator.clipboard.writeText(lines);
        note.textContent = "Copied. Paste it into a message to the shop on Etsy.";
      } catch {
        const r = document.createRange();
        r.selectNodeContents(out);
        const s = getSelection();
        s.removeAllRanges();
        s.addRange(r);
        note.textContent = "Your request is selected above. Copy it, then paste it into an Etsy message.";
      }
    });
  }
})();
