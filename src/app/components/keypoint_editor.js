// Pose & hands keypoint editor (preprocess tab)
// เปิดด้วย window.__kpOpen(payloadJson) จากปุ่ม select ของ keypoint_gallery
// แก้ตำแหน่ง joint โดยลากที่ label -> กด OK ส่งกลับผ่าน #kp_result + #kp_save_btn
(function () {
  const NS = "http://www.w3.org/2000/svg";
  let S = null; // state ของ session ที่กำลังแก้
  let ov = null; // overlay element

  function buildOverlay() {
    if (ov) return ov;
    ov = document.createElement("div");
    ov.id = "kp-overlay";
    ov.className = "kp-overlay";
    ov.innerHTML = `
      <div class="kp-modal">
        <div class="kp-toolbar">
          <span class="kp-title">แก้ไขท่าทาง (Pose &amp; Hands)</span>
          <span class="kp-spacer"></span>
          <button type="button" class="kp-btn" data-act="zoomout">−</button>
          <span class="kp-zoom" data-zoom>100%</span>
          <button type="button" class="kp-btn" data-act="zoomin">+</button>
          <button type="button" class="kp-btn" data-act="reset">Reset</button>
          <button type="button" class="kp-btn kp-cancel" data-act="cancel">Cancel</button>
          <button type="button" class="kp-btn kp-ok" data-act="ok">OK</button>
        </div>
        <div class="kp-viewport" data-viewport>
          <div class="kp-stage" data-stage>
            <img class="kp-img" data-img/>
            <svg class="kp-svg" data-svg></svg>
          </div>
        </div>
        <div class="kp-hint">ลากชื่อ joint เพื่อย้ายตำแหน่ง · ลากพื้นหลังเพื่อเลื่อน (pan) · scroll เพื่อ zoom</div>
      </div>`;
    document.body.appendChild(ov);

    ov.querySelector(".kp-toolbar").addEventListener("click", (e) => {
      const act = e.target && e.target.getAttribute("data-act");
      if (!act) return;
      if (act === "zoomin") zoomAt(1.2);
      else if (act === "zoomout") zoomAt(1 / 1.2);
      else if (act === "reset") fitView();
      else if (act === "cancel") closeEditor();
      else if (act === "ok") submitEdits();
    });

    const vp = ov.querySelector("[data-viewport]");
    vp.addEventListener("wheel", onWheel, { passive: false });
    vp.addEventListener("pointerdown", onPanStart);
    window.addEventListener("pointermove", onPointerMove);
    window.addEventListener("pointerup", onPointerUp);
    return ov;
  }

  const GROUP_COLOR = {
    head: "#ffd23f",
    body: "#3aa0ff",
    right_hand: "#ff7a00",
    left_hand: "#19c37d",
  };

  function nodeById(i) {
    return S.byId[i];
  }

  function applyTransform() {
    const stage = S.stage;
    const px = Math.round(S.imgW * S.scale);
    const py = Math.round(S.imgH * S.scale);
    stage.style.width = px + "px";
    stage.style.height = py + "px";
    stage.style.transform = `translate(${S.panX}px, ${S.panY}px)`;
    ov.querySelector("[data-zoom]").textContent =
      Math.round(S.scale * 100) + "%";
    applySizes();
  }

  function applySizes() {
    const k = 1 / S.scale; // user-units ต่อ screen-px (ให้ขนาดคงที่บนจอ)
    const r = 5 * k,
      fs = 12 * k,
      sw = 2 * k,
      off = 8 * k;
    S.joints.forEach((j) => {
      const e = S.els[j.i];
      e.c.setAttribute("r", r);
      e.t.setAttribute("font-size", fs);
      e.t.setAttribute("x", j.x + off);
      e.t.setAttribute("y", j.y - off);
      e.t.setAttribute("stroke-width", 3 * k);
    });
    S.edgeEls.forEach((e) => e.ln.setAttribute("stroke-width", sw));
  }

  function placeJoint(j) {
    const e = S.els[j.i];
    e.c.setAttribute("cx", j.x);
    e.c.setAttribute("cy", j.y);
    const k = 1 / S.scale;
    e.t.setAttribute("x", j.x + 8 * k);
    e.t.setAttribute("y", j.y - 8 * k);
    (S.adj[j.i] || []).forEach((edge) => {
      if (edge.a === j.i) {
        edge.ln.setAttribute("x1", j.x);
        edge.ln.setAttribute("y1", j.y);
      } else {
        edge.ln.setAttribute("x2", j.x);
        edge.ln.setAttribute("y2", j.y);
      }
    });
  }

  function drawScene() {
    const svg = S.svg;
    svg.setAttribute("viewBox", `0 0 ${S.imgW} ${S.imgH}`);
    svg.innerHTML = "";

    S.edgeEls = S.edges.map(([a, b]) => {
      const ln = document.createElementNS(NS, "line");
      ln.setAttribute("class", "kp-edge");
      const ja = nodeById(a),
        jb = nodeById(b);
      ln.setAttribute("x1", ja.x);
      ln.setAttribute("y1", ja.y);
      ln.setAttribute("x2", jb.x);
      ln.setAttribute("y2", jb.y);
      svg.appendChild(ln);
      return { ln, a, b };
    });

    S.adj = {};
    S.edgeEls.forEach((e) => {
      (S.adj[e.a] = S.adj[e.a] || []).push(e);
      (S.adj[e.b] = S.adj[e.b] || []).push(e);
    });

    S.els = {};
    S.joints.forEach((j) => {
      const g = document.createElementNS(NS, "g");
      g.setAttribute("class", "kp-joint");
      g.dataset.i = j.i;
      const color = GROUP_COLOR[j.group] || "#fff";
      const c = document.createElementNS(NS, "circle");
      c.setAttribute("class", "kp-dot");
      c.setAttribute("fill", color);
      const t = document.createElementNS(NS, "text");
      t.setAttribute("class", "kp-label");
      t.setAttribute("fill", color);
      t.textContent = j.name;
      g.appendChild(c);
      g.appendChild(t);
      g.addEventListener("pointerdown", onJointStart);
      svg.appendChild(g);
      S.els[j.i] = { g, c, t };
      placeJoint(j);
    });
    applySizes();
  }

  function toUser(evt) {
    const ctm = S.svg.getScreenCTM();
    if (!ctm) return null;
    const pt = S.svg.createSVGPoint();
    pt.x = evt.clientX;
    pt.y = evt.clientY;
    return pt.matrixTransform(ctm.inverse());
  }

  // ----- drag joint -----
  function onJointStart(evt) {
    evt.preventDefault();
    evt.stopPropagation();
    const i = parseInt(evt.currentTarget.dataset.i, 10);
    S.drag = { i };
    S.els[i].g.classList.add("kp-active");
  }

  // ----- pan -----
  function onPanStart(evt) {
    if (S.drag) return;
    if (evt.target.closest && evt.target.closest(".kp-joint")) return;
    S.pan = {
      x: evt.clientX,
      y: evt.clientY,
      px: S.panX,
      py: S.panY,
    };
    S.viewport.classList.add("kp-panning");
  }

  function onPointerMove(evt) {
    if (S.drag) {
      const p = toUser(evt);
      if (!p) return;
      const j = nodeById(S.drag.i);
      j.x = p.x;
      j.y = p.y;
      j.moved = true;
      placeJoint(j);
    } else if (S.pan) {
      S.panX = S.pan.px + (evt.clientX - S.pan.x);
      S.panY = S.pan.py + (evt.clientY - S.pan.y);
      S.stage.style.transform = `translate(${S.panX}px, ${S.panY}px)`;
    }
  }

  function onPointerUp() {
    if (S && S.drag) {
      S.els[S.drag.i].g.classList.remove("kp-active");
      S.drag = null;
    }
    if (S && S.pan) {
      S.pan = null;
      S.viewport.classList.remove("kp-panning");
    }
  }

  // ----- zoom -----
  function setScale(newScale, cx, cy) {
    newScale = Math.min(12, Math.max(0.1, newScale));
    const rect = S.viewport.getBoundingClientRect();
    if (cx == null) cx = rect.width / 2;
    if (cy == null) cy = rect.height / 2;
    // user-point ใต้ cursor ก่อน zoom
    const ux = (cx - S.panX) / S.scale;
    const uy = (cy - S.panY) / S.scale;
    S.scale = newScale;
    S.panX = cx - ux * S.scale;
    S.panY = cy - uy * S.scale;
    applyTransform();
  }

  function zoomAt(factor) {
    setScale(S.scale * factor, null, null);
  }

  function onWheel(evt) {
    evt.preventDefault();
    const rect = S.viewport.getBoundingClientRect();
    const factor = evt.deltaY < 0 ? 1.1 : 1 / 1.1;
    setScale(S.scale * factor, evt.clientX - rect.left, evt.clientY - rect.top);
  }

  function fitView() {
    const rect = S.viewport.getBoundingClientRect();
    const s = Math.min(rect.width / S.imgW, rect.height / S.imgH) * 0.95;
    S.scale = s > 0 ? s : 1;
    S.panX = (rect.width - S.imgW * S.scale) / 2;
    S.panY = (rect.height - S.imgH * S.scale) / 2;
    applyTransform();
  }

  // ----- open / close / submit -----
  function openEditor(payloadStr) {
    if (!payloadStr) return;
    let data;
    try {
      data = JSON.parse(payloadStr);
    } catch (e) {
      return;
    }
    buildOverlay();
    const size = data.image_size || [600, 600];
    S = {
      video_id: data.video_id,
      image_name: data.image_name,
      imgW: size[0],
      imgH: size[1],
      joints: data.joints.map((j) => ({ ...j, moved: false })),
      edges: data.edges,
      scale: 1,
      panX: 0,
      panY: 0,
      drag: null,
      pan: null,
      viewport: ov.querySelector("[data-viewport]"),
      stage: ov.querySelector("[data-stage]"),
      svg: ov.querySelector("[data-svg]"),
      img: ov.querySelector("[data-img]"),
    };
    S.byId = {};
    S.joints.forEach((j) => (S.byId[j.i] = j));

    S.img.src = data.image;
    ov.classList.add("kp-open");
    drawScene();
    // viewport มีขนาดจริงหลังจาก display แล้ว
    requestAnimationFrame(fitView);
  }

  function closeEditor() {
    if (ov) ov.classList.remove("kp-open");
    S = null;
  }

  function submitEdits() {
    const edits = S.joints
      .filter((j) => j.moved)
      .map((j) => ({ i: j.i, x: j.x, y: j.y }));
    const out = JSON.stringify({
      video_id: S.video_id,
      image_name: S.image_name,
      edits: edits,
    });

    const ta = document.querySelector("#kp_result textarea, #kp_result input");
    if (ta) {
      const proto =
        ta.tagName === "TEXTAREA"
          ? window.HTMLTextAreaElement.prototype
          : window.HTMLInputElement.prototype;
      const setter = Object.getOwnPropertyDescriptor(proto, "value").set;
      setter.call(ta, out);
      ta.dispatchEvent(new Event("input", { bubbles: true }));
    }
    const btn =
      document.querySelector("#kp_save_btn button") ||
      document.querySelector("#kp_save_btn");
    closeEditor();
    setTimeout(() => btn && btn.click(), 40);
  }

  window.__kpOpen = openEditor;
  window.__kpClose = closeEditor;
})();
