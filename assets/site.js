(function () {
  "use strict";
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  function clamp(v, a, b) { return v < a ? a : v > b ? b : v; }
  function ease(t) { return 1 - Math.pow(1 - t, 3); }

  /* ---------- Header: menu, compact state, reading progress ---------- */
  var head = document.querySelector(".site-head");
  if (head) { var bar = document.createElement("div"); bar.className = "progress"; bar.setAttribute("aria-hidden", "true"); head.appendChild(bar); }
  var menuBtn = document.getElementById("menu-btn"), headRight = document.getElementById("head-right");
  if (menuBtn && headRight) menuBtn.addEventListener("click", function () {
    var open = headRight.classList.toggle("open");
    menuBtn.setAttribute("aria-expanded", open ? "true" : "false");
  });

  // Scroll-linked effects. Each reads how far its element has travelled through the viewport (0 entering, 1 gone).
  var drifters = [].slice.call(document.querySelectorAll("[data-drift]"));
  var growers = [].slice.call(document.querySelectorAll("[data-grow]"));
  var rivers = [].slice.call(document.querySelectorAll("[data-river]"));
  var slides = [].slice.call(document.querySelectorAll("[data-slide]"));
  var heroBits = [].slice.call(document.querySelectorAll("[data-hero]"));
  var pins = [].slice.call(document.querySelectorAll("[data-pin]"));
  var splits = [].slice.call(document.querySelectorAll("[data-split]"));
  var bgshift = [].slice.call(document.querySelectorAll(".window.team-hero, .window.shift"));
  var themeRows = [].slice.call(document.querySelectorAll("[data-theme]"));
  var t0 = performance.now();

  // Research themes: three lines leave the circle and run to the numbered questions.
  function layoutThemes() {
    themeRows.forEach(function (row) {
      var svg = row.querySelector(".theme-lines"), circ = row.querySelector(".theme-art .pic");
      var badges = [].slice.call(row.querySelectorAll(".qn"));
      var R = row.getBoundingClientRect(), C = circ.getBoundingClientRect();
      var cx = C.left + C.width / 2 - R.left, cy = C.top + C.height / 2 - R.top, rad = C.width / 2;
      var alt = row.classList.contains("alt");
      svg.setAttribute("viewBox", "0 0 " + R.width.toFixed(0) + " " + R.height.toFixed(0));
      var html = "";
      badges.forEach(function (b, i) {
        var B = b.getBoundingClientRect();
        var bx = (alt ? B.right + 4 : B.left - 4) - R.left, by = B.top + B.height / 2 - R.top;
        var dir = alt ? -1 : 1, off = clamp(by - cy, (i - 1.5) * rad * 0.45, (i - 0.5) * rad * 0.45);
        var sy = cy + off, sx = cx + dir * (Math.sqrt(Math.max(0, rad * rad - off * off)) + 12);
        var mx = sx + (bx - sx) * (0.25 + 0.22 * i);
        html += '<path pathLength="1" d="M' + sx.toFixed(1) + " " + sy.toFixed(1) + " H" + mx.toFixed(1) + " V" + by.toFixed(1) + " H" + bx.toFixed(1) + '"/>' +
          '<circle cx="' + sx.toFixed(1) + '" cy="' + sy.toFixed(1) + '" r="5"/>';
      });
      svg.innerHTML = html;
      row._paths = [].slice.call(svg.querySelectorAll("path"));
      row._dots = [].slice.call(svg.querySelectorAll("circle"));
      row._qs = [].slice.call(row.querySelectorAll("[data-q]"));
    });
  }

  function through(el, vh) {
    var r = el.getBoundingClientRect();
    return { r: r, p: (vh - r.top) / (vh + r.height), vis: r.bottom > -100 && r.top < vh + 100 };
  }

  function frame() {
    ticking = false;
    var vh = window.innerHeight, y = window.scrollY;
    if (head) {
      head.classList.toggle("scrolled", y > 24);
      var max = document.documentElement.scrollHeight - vh;
      head.style.setProperty("--read", max > 0 ? (y / max).toFixed(4) : 0);
    }
    if (reduceMotion) return;

    // Hero title shrinks, lifts and fades as the page moves up over the photo.
    heroBits.forEach(function (el, i) {
      var k = clamp(y / (vh * 0.8), 0, 1);
      el.style.transform = "translate3d(0," + (-k * (60 + i * 30)).toFixed(1) + "px,0) scale(" + (1 - k * 0.28).toFixed(3) + ")";
      el.style.opacity = (1 - k * 1.1).toFixed(3);
    });

    drifters.forEach(function (el) {
      var t = through(el, vh); if (!t.vis) return;
      el.style.transform = "translate3d(0," + ((t.p - 0.5) * -2 * Number(el.getAttribute("data-drift"))).toFixed(1) + "px,0)";
    });

    // Images grow from 84% to full size, and their contents ease back from a slight zoom.
    growers.forEach(function (el) {
      var t = through(el, vh); if (!t.vis) return;
      var k = ease(clamp(t.p / 0.55, 0, 1));
      el.style.setProperty("--g", (0.84 + 0.16 * k).toFixed(4));
      el.style.setProperty("--gi", (1.18 - 0.18 * k).toFixed(4));
    });

    themeRows.forEach(function (row) {
      if (!row._paths) return;
      var r = row.getBoundingClientRect(); if (r.bottom < -100 || r.top > vh + 100) return;
      var q = (vh - r.top) / vh;
      row._paths.forEach(function (p, i) {
        var k = clamp((q - 0.08 - i * 0.07) / 0.22, 0, 1);
        p.style.strokeDashoffset = (1 - k).toFixed(4);
        row._dots[i].style.opacity = k > 0 ? 1 : 0;
        var a = clamp((k - 0.4) / 0.4, 0, 1);
        row._qs[i].style.opacity = a.toFixed(3);
        row._qs[i].style.transform = "translateX(" + ((1 - a) * (row.classList.contains("alt") ? -14 : 14)).toFixed(1) + "px)";
      });
    });

    // Team members: the name shows first, then one photo appears and splits into two, and the text fades in between them.
    splits.forEach(function (el) {
      var t = through(el, vh); if (!t.vis) return;
      var q = (vh - t.r.top) / vh, k1 = clamp((q - 0.12) / 0.18, 0, 1), k2 = ease(clamp((q - 0.30) / 0.40, 0, 1));
      el.style.setProperty("--s1", k1.toFixed(3));
      el.style.setProperty("--s2", k2.toFixed(3));
    });

    // Banner photos slide a little slower than the page.
    bgshift.forEach(function (el) {
      var t = through(el, vh); if (!t.vis) return;
      el.style.setProperty("--by", (Math.max(0, -t.r.top) * 0.4).toFixed(1) + "px");
    });

    // Rivers draw downstream from left to right, then their tributaries join.
    rivers.forEach(function (el) {
      var t = through(el, vh); if (!t.vis) return;
      // Starts drawing as it enters and finishes once it is two thirds of the way up the screen.
      var k = clamp(((vh - t.r.top) / vh - 0.08) / 0.6, 0, 1);
      el.style.setProperty("--flow", ease(k).toFixed(4));
      el.style.setProperty("--bank", k > 0.02 ? 1 : 0);
    });

    // Rows of theme names slide in opposite directions.
    slides.forEach(function (el) {
      var t = through(el.parentElement, vh); if (!t.vis) return;
      var dir = Number(el.getAttribute("data-slide"));
      var span = el.scrollWidth / 2;
      el.style.transform = "translate3d(" + (dir < 0 ? -t.p * span * 0.5 : -span * 0.5 + t.p * span * 0.5).toFixed(1) + "px,0,0)";
    });

    // Pinned section: vertical scroll moves the photo strip sideways.
    pins.forEach(function (el) {
      var r = el.getBoundingClientRect(); if (r.bottom < 0 || r.top > vh) return;
      var track = el.querySelector("[data-track]");
      var k = clamp(-r.top / (r.height - vh), 0, 1);
      var dist = Math.max(0, track.scrollWidth - window.innerWidth);
      track.style.setProperty("--tx", (-k * dist).toFixed(1) + "px");
    });
  }

  var ticking = false;
  window.addEventListener("scroll", function () { if (!ticking) { ticking = true; requestAnimationFrame(frame); } }, { passive: true });
  window.addEventListener("resize", function () { layoutThemes(); frame(); });
  if (themeRows.length) { layoutThemes(); window.addEventListener("load", function () { layoutThemes(); frame(); }); }
  frame();

  /* ---------- Reveal blocks below the fold as they arrive ---------- */
  if (!reduceMotion && "IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        en.target.classList.add("in-view"); en.target.classList.remove("pre"); io.unobserve(en.target);
      });
    }, { rootMargin: "0px 0px -10% 0px" });
    document.querySelectorAll("[data-reveal]").forEach(function (el) {
      if (el.getBoundingClientRect().top > window.innerHeight) {
        el.classList.add("pre");
        el.style.transitionDelay = (Number(el.getAttribute("data-reveal")) || 0) * 120 + "ms";
        io.observe(el);
      }
    });
  }

  /* ---------- Justified photo gallery: each photo keeps its own shape ---------- */
  /* mosaic tiles: portraits stand tall, landscapes cycle through feature, wide and standard sizes */
  document.querySelectorAll(".jg.rect").forEach(function (g) {
    var n = 0, cycle = ["big", "", "", "wide", "", "big", "", "wide", ""];
    g.querySelectorAll(".jg-item img").forEach(function (im) {
      var b = im.parentNode;
      function set() {
        if (!im.naturalWidth) return;
        if (im.naturalWidth / im.naturalHeight < 0.9) b.classList.add("tall");
        else { var c = cycle[n++ % cycle.length]; if (c) b.classList.add(c); }
      }
      if (im.complete) set(); else im.addEventListener("load", set);
    });
  });

  /* ---------- Globe and world map (need d3 and topojson) ---------- */
  var LAND = "https://cdn.jsdelivr.net/npm/world-atlas@2.0.2/land-110m.json";
  var globeCanvas = document.getElementById("globe"), worldBox = document.getElementById("world");
  if ((globeCanvas || worldBox) && window.d3 && window.topojson) {
    d3.json(LAND).then(function (topo) {
      var land = topojson.feature(topo, topo.objects.land);
      var cs = getComputedStyle(document.documentElement);
      function col(n) { return cs.getPropertyValue(n).trim(); }
      if (globeCanvas) {
        var places = JSON.parse(globeCanvas.dataset.places || "[]");
        var size = 460, ctx = globeCanvas.getContext("2d"), dpr = Math.min(window.devicePixelRatio || 1, 2);
        globeCanvas.width = size * dpr; globeCanvas.height = size * dpr; ctx.scale(dpr, dpr);
        var proj = d3.geoOrthographic().scale(size / 2 - 30).translate([size / 2, size / 2]).clipAngle(90);
        var path = d3.geoPath(proj, ctx), grat = d3.geoGraticule10();
        var lon = 40, lat = -24, paused = false, last = performance.now();
        /* drag to spin: horizontal turns the globe, vertical tilts it */
        var drag = null, dragged = false;
        globeCanvas.style.touchAction = "none";
        globeCanvas.addEventListener("pointerdown", function (ev) {
          drag = { x: ev.clientX, y: ev.clientY, lon: lon, lat: lat }; dragged = false; paused = true;
          globeCanvas.setPointerCapture(ev.pointerId);
        });
        globeCanvas.addEventListener("pointermove", function (ev) {
          if (!drag) return;
          var r = globeCanvas.getBoundingClientRect(), k = 180 / r.width;
          var dx = ev.clientX - drag.x, dy = ev.clientY - drag.y;
          if (Math.abs(dx) + Math.abs(dy) > 4) dragged = true;
          lon = drag.lon + dx * k; lat = Math.max(-70, Math.min(70, drag.lat - dy * k));
          globeCanvas.style.cursor = "grabbing";
        });
        function endDrag(ev) {
          if (!drag) return; drag = null; globeCanvas.style.cursor = "";
          if (ev.pointerType !== "mouse") paused = false;
        }
        globeCanvas.addEventListener("pointerup", endDrag);
        globeCanvas.addEventListener("pointercancel", endDrag);
        globeCanvas.addEventListener("mouseenter", function () { paused = true; });
        globeCanvas.addEventListener("mouseleave", function () { paused = false; });
        var shown = [];
        var chooser = null;
        function closeChooser() { if (chooser) { chooser.remove(); chooser = null; } }
        document.addEventListener("click", function (e3) { if (chooser && !chooser.contains(e3.target) && e3.target !== globeCanvas) closeChooser(); });
        function goTrip(hit) { var m = /(fieldwork-[\w-]+)(?:\.html|\/(?:index\.html)?)?$/.exec(hit.href), sec = m && document.getElementById(m[1]); if (sec) { [].forEach.call(document.querySelectorAll(".trip-panel"), function (p) { p.hidden = p !== sec; }); sec.scrollIntoView({ behavior: "smooth", block: "start" }); } else if (!(m && window.glGo && window.glGo(m[1]))) location.href = hit.href; }
        var globeLink = globeCanvas.closest("a");
        globeCanvas.addEventListener("click", function (ev) {
          if (globeLink) { if (dragged) { dragged = false; ev.preventDefault(); } return; } /* home globe: any click opens the Gallery page */
          if (dragged) { dragged = false; return; }
          var r = globeCanvas.getBoundingClientRect(), x = (ev.clientX - r.left) * size / r.width, y = (ev.clientY - r.top) * size / r.height;
          // pins closer than a finger width (Fogo and São Nicolau) open a small chooser
          var near = shown.filter(function (p) { return Math.hypot(p.x - x, p.y - y) < 28; }).sort(function (a, b) { return Math.hypot(a.x - x, a.y - y) - Math.hypot(b.x - x, b.y - y); });
          var seen = {}, hits = near.filter(function (p) { if (seen[p.href]) return false; seen[p.href] = 1; return true; });
          closeChooser();
          if (!hits.length) return;
          ev.preventDefault();
          if (hits.length === 1) { goTrip(hits[0]); return; }
          paused = true;
          chooser = document.createElement("div"); chooser.className = "pin-chooser";
          hits.forEach(function (h) { var b = document.createElement("button"); b.type = "button"; b.textContent = h.name; b.addEventListener("click", function (e2) { e2.stopPropagation(); closeChooser(); goTrip(h); }); chooser.appendChild(b); });
          var host = globeCanvas.parentNode; if (getComputedStyle(host).position === "static") host.style.position = "relative";
          var hr = host.getBoundingClientRect(); chooser.style.left = (ev.clientX - hr.left) + "px"; chooser.style.top = (ev.clientY - hr.top) + "px";
          host.appendChild(chooser);
        });
        globeCanvas.addEventListener("mousemove", function (ev) {
          var r = globeCanvas.getBoundingClientRect(), x = (ev.clientX - r.left) * size / r.width, y = (ev.clientY - r.top) * size / r.height;
          if (drag) return;
          globeCanvas.style.cursor = globeLink ? "pointer" : shown.some(function (p) { return Math.hypot(p.x - x, p.y - y) < 28; }) ? "pointer" : "grab";
        });
        (function spin(now) {
          if (!paused && !reduceMotion) lon -= (now - last) * 0.008;
          last = now;
          proj.rotate([lon, lat]);
          ctx.clearRect(0, 0, size, size);
          ctx.beginPath(); path({ type: "Sphere" }); ctx.fillStyle = col("--dust-pale"); ctx.fill();
          ctx.beginPath(); path(land); ctx.fillStyle = col("--sand"); ctx.fill(); ctx.strokeStyle = "rgba(127,151,168,.35)"; ctx.lineWidth = .5; ctx.stroke();
          var pulse = (now % 1800) / 1800;
          shown = [];
          places.forEach(function (p) {
            var c = proj.rotate(), d = d3.geoDistance([p.lon, p.lat], [-c[0], -c[1]]);
            if (d > Math.PI / 2 - 0.08) return;
            var xy = proj([p.lon, p.lat]);
            shown.push({ x: xy[0], y: xy[1], href: p.href, name: p.name });
            ctx.beginPath(); ctx.arc(xy[0], xy[1], 6 + pulse * 16, 0, 7); ctx.fillStyle = "rgba(181,101,74," + (0.35 * (1 - pulse)).toFixed(3) + ")"; ctx.fill();
            ctx.beginPath(); ctx.arc(xy[0], xy[1], 6, 0, 7); ctx.fillStyle = col("--maroon"); ctx.fill();
            ctx.lineWidth = 2; ctx.strokeStyle = "#fff"; ctx.stroke();
          });
          requestAnimationFrame(spin);
        })(last);
      }
      if (worldBox) {
        var W = 960, H = 552, svg = d3.select(worldBox).append("svg").attr("viewBox", "0 0 " + W + " " + H);
        var pj = d3.geoNaturalEarth1().fitExtent([[6, 6], [W - 6, H - 6]], { type: "Sphere" }), gp = d3.geoPath(pj);
        svg.append("path").attr("class", "sphere").attr("d", gp({ type: "Sphere" }));
        svg.append("path").attr("class", "grat").attr("d", gp(d3.geoGraticule10()));
        svg.append("path").attr("class", "land").attr("d", gp(land));
        JSON.parse(worldBox.dataset.sites || "[]").forEach(function (p) {
          var xy = pj([p[1], p[0]]);
          svg.append("circle").attr("class", "site").attr("cx", xy[0]).attr("cy", xy[1]).attr("r", 4.5);
        });
        document.querySelectorAll(".pin-link").forEach(function (a) {
          var xy = pj([+a.dataset.lon, +a.dataset.lat]);
          var g = svg.append("g").attr("class", "mpin").attr("transform", "translate(" + xy + ")").on("click", function () { location.hash = a.getAttribute("href"); document.querySelector(a.getAttribute("href")).scrollIntoView({ behavior: "smooth" }); });
          g.append("circle").attr("class", "halo").attr("r", 9);
          g.append("circle").attr("r", 6);
          g.append("text").attr("x", 12).attr("y", 4).text(a.textContent);
        });
      }
    });
  }

  /* ---------- Mars globe: MOLA texture on a turning sphere ---------- */
  var marsCanvas = document.getElementById("mars");
  if (marsCanvas) {
    var tex = new Image();
    tex.onload = function () {
      var tw = tex.width, th = tex.height, tc = document.createElement("canvas");
      tc.width = tw; tc.height = th; var tctx = tc.getContext("2d"); tctx.drawImage(tex, 0, 0);
      var src = tctx.getImageData(0, 0, tw, th).data;
      var dpr = Math.min(window.devicePixelRatio || 1, 2), N = Math.round(400 * dpr), R = N / 2 - 2 * dpr;
      marsCanvas.width = N; marsCanvas.height = N;
      var mctx = marsCanvas.getContext("2d"), img = mctx.createImageData(N, N), dst = img.data;
      var tilt = 25 * Math.PI / 180, ct = Math.cos(tilt), st = Math.sin(tilt);
      var idx = [], rowOf = [], lonOf = [], lit = [];
      for (var y = 0; y < N; y++) for (var x = 0; x < N; x++) {
        var px = (x + .5 - N / 2) / R, py = (N / 2 - y - .5) / R, rr = px * px + py * py;
        if (rr > 1) continue;
        var pz = Math.sqrt(1 - rr);
        var Y = py * ct + pz * st, Z = -py * st + pz * ct;
        var la = Math.asin(Y), lo = Math.atan2(px, Z);
        idx.push((y * N + x) * 4);
        rowOf.push(Math.min(th - 1, Math.floor((0.5 - la / Math.PI) * th)) * tw);
        lonOf.push(lo / (2 * Math.PI) * tw);
        var edge = Math.min(1, (1 - Math.sqrt(rr)) * N / 3);
        lit.push([edge * 255, 0.82 + 0.18 * pz]);
      }
      var n = idx.length, lon = 0, last = performance.now(), paused = false;
      marsCanvas.addEventListener("mouseenter", function () { paused = true; });
      marsCanvas.addEventListener("mouseleave", function () { paused = false; });
      (function spin(now) {
        if (!paused && !reduceMotion) lon += (now - last) * 0.012 * tw / 360;
        last = now;
        for (var i = 0; i < n; i++) {
          var c = Math.floor(lonOf[i] + lon) % tw; if (c < 0) c += tw;
          var s = (rowOf[i] + c) * 4, d = idx[i], L = lit[i], k = L[1];
          dst[d] = src[s] * k; dst[d + 1] = src[s + 1] * k; dst[d + 2] = src[s + 2] * k; dst[d + 3] = L[0];
        }
        mctx.putImageData(img, 0, 0);
        if (!reduceMotion) requestAnimationFrame(spin);
      })(last);
    };
    tex.src = marsCanvas.dataset.tex;
  }

  /* ---------- Data & code banner: perspective wireframe of Mars topography ---------- */

  // Mars Legoscape: 96 x 48 grid of 2x2 plates, stacked to MOLA height, coloured by USGS unit. Drag to turn.
  var lego = document.querySelector("canvas.legoscape");
  if (lego) {
    fetch(lego.dataset.src).then(function (r) { return r.json(); }).then(function (g) {
      var W = g.w, H = g.h, ctx = lego.getContext("2d");
      var COL = [null, [169,85,0], [155,154,90], [111,148,122], [0,108,183], [53,33,8], [175,116,70], [103,130,151], [255,255,255], [72,158,206], [120,191,234]];
      var cells = [];
      for (var j = 0; j < H; j++) for (var i = 0; i < W; i++) {
        var k = j * W + i; if (g.top[k] > 0) cells.push({ x: i - W / 2, y: j - H / 2, z: g.top[k] * 0.4, c: COL[g.unit[k]] || [150,150,150] });
      }
      function shade(c, f) { return "rgb(" + Math.round(c[0] * f) + "," + Math.round(c[1] * f) + "," + Math.round(c[2] * f) + ")"; }
      var yaw = -0.3, tilt = 0.8, drag = null, idle = 0, visible = false, last = 0;
      function draw() {
        var box = lego.getBoundingClientRect(), dpr = Math.min(window.devicePixelRatio || 1, 2);
        var cw = Math.round(box.width * dpr), ch = Math.round(box.height * dpr);
        if (lego.width !== cw || lego.height !== ch) { lego.width = cw; lego.height = ch; }
        var ca = Math.cos(yaw), sa = Math.sin(yaw), ct = Math.cos(tilt), st = Math.sin(tilt);
        var bx = W / 2 + 1, by = H / 2 + 1, hx = bx * Math.abs(ca) + by * Math.abs(sa), hy = bx * Math.abs(sa) + by * Math.abs(ca), S = Math.min(cw / (2 * hx + 1), ch / (2 * hy * st + 6 * ct + 1)), ox = cw / 2, oy = ch / 2 + 3 * S * ct;
        function P(x, y, z) { var X = x * ca - y * sa, Y = x * sa + y * ca; return [ox + X * S, oy + Y * st * S - z * ct * S]; }
        function quad(a, b, c, d, fill) { ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); ctx.lineTo(c[0], c[1]); ctx.lineTo(d[0], d[1]); ctx.closePath(); ctx.fillStyle = fill; ctx.fill(); }
        ctx.clearRect(0, 0, cw, ch);
        // baseplate
        var bw = W / 2 + 1, bh = H / 2 + 1;
        quad(P(-bw, -bh, 0), P(bw, -bh, 0), P(bw, bh, 0), P(-bw, bh, 0), "#2b2f36");
        // which two side faces face the viewer
        var sides = [[1, 0], [-1, 0], [0, 1], [0, -1]].filter(function (n) { return n[0] * sa + n[1] * ca > 0; });
        cells.forEach(function (c) { c.d = c.x * sa + c.y * ca; });
        cells.sort(function (a, b) { return a.d - b.d; });
        var r = 0.28 * S, ry = r * st;
        for (var n = 0; n < cells.length; n++) {
          var c = cells[n], x0 = c.x, x1 = c.x + 1, y0 = c.y, y1 = c.y + 1, z = c.z;
          for (var q = 0; q < sides.length; q++) {
            var nx = sides[q][0], ny = sides[q][1], f = 0.62 + 0.18 * (nx * 0.6 + ny * 0.8);
            if (nx === 1) quad(P(x1, y0, 0), P(x1, y1, 0), P(x1, y1, z), P(x1, y0, z), shade(c.c, f));
            else if (nx === -1) quad(P(x0, y0, 0), P(x0, y1, 0), P(x0, y1, z), P(x0, y0, z), shade(c.c, f));
            else if (ny === 1) quad(P(x0, y1, 0), P(x1, y1, 0), P(x1, y1, z), P(x0, y1, z), shade(c.c, f));
            else quad(P(x0, y0, 0), P(x1, y0, 0), P(x1, y0, z), P(x0, y0, z), shade(c.c, f));
          }
          quad(P(x0, y0, z), P(x1, y0, z), P(x1, y1, z), P(x0, y1, z), shade(c.c, 1));
          if (S > 5) {
            var m = P(c.x + 0.5, c.y + 0.5, z);
            ctx.beginPath(); ctx.ellipse(m[0], m[1], r, ry, 0, 0, 6.2832); ctx.fillStyle = shade(c.c, 1.12); ctx.fill();
          }
        }
      }
      function loop(t) {
        if (!visible) return;
        if (!drag && !reduceMotion && t - idle > 1500) yaw += Math.min(50, t - (last || t)) * 0.00012;
        last = t; draw(); requestAnimationFrame(loop);
      }
      lego.addEventListener("pointerdown", function (ev) { drag = [ev.clientX, ev.clientY, yaw, tilt]; lego.setPointerCapture(ev.pointerId); });
      lego.addEventListener("pointermove", function (ev) {
        if (!drag) return;
        yaw = drag[2] + (ev.clientX - drag[0]) * 0.008;
        tilt = clamp(drag[3] - (ev.clientY - drag[1]) * 0.006, 0.35, 1.5);
        if (reduceMotion) draw();
      });
      function up() { drag = null; idle = performance.now(); }
      lego.addEventListener("pointerup", up); lego.addEventListener("pointercancel", up);
      new IntersectionObserver(function (es) {
        var was = visible; visible = es[0].isIntersecting;
        if (visible && !was) { last = 0; requestAnimationFrame(loop); }
      }).observe(lego);
      draw();
    });
  }
  var meshCanvas = document.querySelector("canvas.mesh");
  if (meshCanvas) {
    fetch(meshCanvas.dataset.src).then(function (r) { return r.json(); }).then(function (g) {
      var W = g.w, H = g.h, Z = g.z, ctx = meshCanvas.getContext("2d"), zmax = Math.max.apply(null, Z);
      function draw() {
        var box = meshCanvas.getBoundingClientRect(), dpr = Math.min(window.devicePixelRatio || 1, 2);
        var cw = Math.round(box.width * dpr), ch = Math.round(box.height * dpr);
        if (meshCanvas.width !== cw || meshCanvas.height !== ch) { meshCanvas.width = cw; meshCanvas.height = ch; }
        var scrolled = Math.max(0, Math.min(1, -box.top / Math.max(1, box.height)));
        var yaw = -0.25 + (reduceMotion ? 0 : scrolled * 0.45), cy = Math.cos(yaw), sy = Math.sin(yaw);
        var t = 0.66, ct = Math.cos(t), st = Math.sin(t), D = 0.5 * W, F = Math.max(cw * 0.62, ch * 1.6), ex = g.unit * 7;
        function P(i, j) {
          var x = i - W / 2, y = j - H / 2, z = Z[j * W + i] * ex - 6;
          var X = x * cy - y * sy, Y = x * sy + y * cy;
          var vx = X, vy = Y - D * ct, vz = z - D * st;
          var depth = -(vy * ct + vz * st), up = -vy * st + vz * ct;
          return [cw / 2 + vx * F / depth, ch * 0.42 - up * F / depth];
        }
        ctx.clearRect(0, 0, cw, ch);
        ctx.lineWidth = Math.max(0.6, 0.7 * dpr);
        var pts = [], i, j, k;
        for (j = 0; j < H; j++) for (i = 0; i < W; i++) pts.push(P(i, j));
        for (j = 0; j < H; j++) {
          ctx.beginPath();
          for (i = 0; i < W; i++) { k = pts[j * W + i]; if (i) ctx.lineTo(k[0], k[1]); else ctx.moveTo(k[0], k[1]); }
          ctx.strokeStyle = "rgba(255,255,255," + (0.18 + 0.4 * (1 - j / H)).toFixed(3) + ")"; ctx.stroke();
        }
        ctx.strokeStyle = "rgba(255,255,255,.22)";
        for (i = 0; i < W; i += 1) {
          ctx.beginPath();
          for (j = 0; j < H; j++) { k = pts[j * W + i]; if (j) ctx.lineTo(k[0], k[1]); else ctx.moveTo(k[0], k[1]); }
          ctx.stroke();
        }
      }
      var queued = false;
      function req() { if (!queued) { queued = true; requestAnimationFrame(function () { queued = false; draw(); }); } }
      draw(); window.addEventListener("resize", req); if (!reduceMotion) window.addEventListener("scroll", req, { passive: true });
    });
  }

  /* ---------- Flip circles: tap to turn over on touch screens ---------- */
  document.querySelectorAll(".flip-in").forEach(function (b) {
    b.addEventListener("click", function () { b.parentNode.classList.toggle("on"); });
  });

  /* ---------- Before/after slider ---------- */
  document.querySelectorAll(".compare").forEach(function (c) {
    var r = c.querySelector("input");
    function set() { c.style.setProperty("--pos", r.value + "%"); }
    r.addEventListener("input", set); set();
  });

  /* ---------- Embeds load when clicked ---------- */
  document.querySelectorAll(".embed .facade").forEach(function (b) {
    b.addEventListener("click", function () {
      var f = document.createElement("iframe");
      f.src = b.getAttribute("data-src");
      f.title = b.getAttribute("data-title") || "Embedded media";
      f.allow = "autoplay; encrypted-media; fullscreen; picture-in-picture";
      f.allowFullscreen = true;
      b.replaceWith(f);
    });
  });
  var sound = document.getElementById("sound");
  if (sound) sound.addEventListener("click", function () {
    var box = document.getElementById("sound-frame");
    if (box.firstChild) { box.innerHTML = ""; return; }
    box.innerHTML = '<iframe title="River sounds on Spotify" allow="autoplay; encrypted-media" src="https://open.spotify.com/embed/artist/34H7XemCvXS6iDsnPPjMcx?utm_source=generator"></iframe>';
  });

  /* ---------- Publications: highlight current year, search ---------- */
  var yearLinks = document.querySelectorAll(".yearnav a[href^='#y']");
  var ynav = document.querySelector(".yearnav");
  if (ynav) {
    var ygroups = [].slice.call(document.querySelectorAll(".year-group"));
    var spy = function () {
      ynav.classList.toggle("stuck", ynav.getBoundingClientRect().top <= 60);
      var cur = null;
      ygroups.forEach(function (g) { if (!g.hidden && g.getBoundingClientRect().top < window.innerHeight * 0.4) cur = g.querySelector(".year").id; });
      if (!cur && ygroups[0]) cur = ygroups[0].querySelector(".year").id;
      yearLinks.forEach(function (a) { a.classList.toggle("on", a.getAttribute("href") === "#" + cur); });
    };
    window.addEventListener("scroll", spy, { passive: true }); spy();
  }
  var q = document.getElementById("pub-search");
  if (q) {
    var pubs = document.querySelectorAll(".pub"), blocks = document.querySelectorAll(".year-group"), count = document.getElementById("pub-count");
    q.addEventListener("input", function () {
      var term = q.value.trim().toLowerCase(), shown = 0;
      pubs.forEach(function (p) { var hit = !term || p.textContent.toLowerCase().indexOf(term) !== -1; p.hidden = !hit; if (hit) shown++; });
      blocks.forEach(function (b) { b.hidden = !b.querySelector(".pub:not([hidden])"); });
      if (count) count.textContent = shown + (shown === 1 ? " paper" : " papers");
    });
  }

  /* ---------- Drainage network model (Themes page) ---------- */
  var canvas = document.getElementById("drainage");
  if (canvas) {
    var NX = 176, NY = 121, state = null, raf = 0;
    function rng(seed) { return function () { seed |= 0; seed = (seed + 0x6D2B79F5) | 0; var t = Math.imul(seed ^ (seed >>> 15), 1 | seed); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
    function valueNoise(rand, cells) {
      var g = [], i, j;
      for (j = 0; j <= cells + 1; j++) { g[j] = []; for (i = 0; i <= cells + 1; i++) g[j][i] = rand(); }
      return function (x, y) {
        var gx = x * cells, gy = y * cells, i0 = Math.floor(gx), j0 = Math.floor(gy), fx = gx - i0, fy = gy - j0;
        var sx = fx * fx * (3 - 2 * fx), sy = fy * fy * (3 - 2 * fy), a = g[j0][i0], b = g[j0][i0 + 1], c = g[j0 + 1][i0], d = g[j0 + 1][i0 + 1];
        return a + (b - a) * sx + (c - a) * sy + (a - b - c + d) * sx * sy;
      };
    }
    function terrain(seed) {
      var rand = rng(seed), z = new Float64Array(NX * NY);
      var oct = [valueNoise(rand, 3), valueNoise(rand, 7), valueNoise(rand, 15), valueNoise(rand, 31)], amp = [1, 0.55, 0.3, 0.18], tiltX = (rand() - 0.5) * 0.6;
      for (var y = 0; y < NY; y++) for (var x = 0; x < NX; x++) { var u = x / NX, v = y / NY, h = 0; for (var k = 0; k < 4; k++) h += amp[k] * oct[k](u, v); z[y * NX + x] = h * 1.5 + (1 - v) * 0.9 + u * tiltX; }
      return z;
    }
    function newSeed() { return (Math.random() * 1e9) | 0; }
    // extra roughness at short wavelengths, so channels wander
    function addNoise(z) {
      var r = rng(newSeed()), n1 = valueNoise(r, 45), n2 = valueNoise(r, 88);
      for (var y = 0; y < NY; y++) for (var x = 0; x < NX; x++) { var u = x / NX, v = y / NY; z[y * NX + x] += (n1(u, v) - 0.5) * 0.32 + (n2(u, v) - 0.5) * 0.14; }
    }
    // add a radial shape f(d) around (cx, cy) out to distance rmax (in cells)
    // pits only show as lakes inside crater bowls, so the random base terrain stays dry
    var bowl = new Uint8Array(NX * NY);
    function stamp(z, cx, cy, rmax, f, rb) {
      var x0 = Math.max(0, Math.floor(cx - rmax)), x1 = Math.min(NX - 1, Math.ceil(cx + rmax)), y0 = Math.max(0, Math.floor(cy - rmax)), y1 = Math.min(NY - 1, Math.ceil(cy + rmax));
      for (var y = y0; y <= y1; y++) for (var x = x0; x <= x1; x++) { var d = Math.hypot(x - cx, y - cy); if (d < rmax) { z[y * NX + x] += f(d); if (d < rb) bowl[y * NX + x] = 1; } }
    }
    // bowl-shaped impact craters with raised rims; small craters are more common than large ones
    function addCraters(z) {
      var r = rng(newSeed()), n = 3 + Math.floor(r() * 4);
      for (var c = 0; c < n; c++) {
        var R = Math.min(22, 4 * Math.pow(r() + 0.03, -0.55)), D = Math.min(0.9, 0.3 + 0.03 * R), rim = 0.3 * D;
        stamp(z, r() * NX, r() * (NY - 8), 3 * R, function (d) { return d < R ? -D + (D + rim) * (d / R) * (d / R) : rim * Math.pow(R / d, 3); }, R);
      }
    }
    // cone-shaped volcanoes with a small summit crater
    function addVolcanoes(z) {
      var r = rng(newSeed()), n = 1 + Math.floor(r() * 2);
      for (var c = 0; c < n; c++) {
        var R = 14 + r() * 18, H = 1.3 + r() * 0.8, Rc = 0.12 * R;
        stamp(z, 10 + r() * (NX - 20), 8 + r() * (NY - 30), R, function (d) { return H * Math.pow(1 - d / R, 1.6) - (d < Rc ? 0.2 * H * (1 - (d / Rc) * (d / Rc)) : 0); }, Rc);
      }
    }
    // fill pits (lakes), route each cell to its steepest downhill neighbour and accumulate drainage area
    function route(z) {
      var rand = rng(7), N = NX * NY;
      var filled = new Float64Array(N), done = new Uint8Array(N), heap = [];
      function push(i) { heap.push(i); var c = heap.length - 1; while (c > 0) { var p = (c - 1) >> 1; if (filled[heap[p]] <= filled[heap[c]]) break; var t = heap[p]; heap[p] = heap[c]; heap[c] = t; c = p; } }
      function pop() { var top = heap[0], last = heap.pop(); if (heap.length) { heap[0] = last; var c = 0; for (;;) { var l = 2 * c + 1, r = l + 1, m = c; if (l < heap.length && filled[heap[l]] < filled[heap[m]]) m = l; if (r < heap.length && filled[heap[r]] < filled[heap[m]]) m = r; if (m === c) break; var t = heap[m]; heap[m] = heap[c]; heap[c] = t; c = m; } } return top; }
      for (var xi = 0; xi < NX; xi++) { var b0 = (NY - 1) * NX + xi; filled[b0] = z[b0]; done[b0] = 1; push(b0); }
      var DX = [-1, 0, 1, -1, 1, -1, 0, 1], DY = [-1, -1, -1, 0, 0, 1, 1, 1], order = [];
      while (heap.length) { var c = pop(); order.push(c); var cx = c % NX, cy = (c / NX) | 0; for (var n = 0; n < 8; n++) { var nx = cx + DX[n], ny = cy + DY[n]; if (nx < 0 || ny < 0 || nx >= NX || ny >= NY) continue; var ni = ny * NX + nx; if (done[ni]) continue; done[ni] = 1; filled[ni] = Math.max(z[ni], filled[c] + 1e-6 * (1 + rand())); push(ni); } }
      var rec = new Int32Array(N).fill(-1);
      for (var i = 0; i < N; i++) { var ix = i % NX, iy = (i / NX) | 0; if (iy === NY - 1) continue; var best = 0, bi = -1; for (var m = 0; m < 8; m++) { var jx = ix + DX[m], jy = iy + DY[m]; if (jx < 0 || jy < 0 || jx >= NX || jy >= NY) continue; var j = jy * NX + jx, dist = (DX[m] && DY[m]) ? 1.4142 : 1, s = (filled[i] - filled[j]) / dist; if (s > best) { best = s; bi = j; } } rec[i] = bi; }
      var area = new Float64Array(N).fill(1), maxA = 1, lake = new Uint8Array(N);
      for (var o = order.length - 1; o >= 0; o--) { var qq = order[o]; if (rec[qq] >= 0) area[rec[qq]] += area[qq]; }
      for (var a2 = 0; a2 < N; a2++) { if (area[a2] > maxA) maxA = area[a2]; if (bowl[a2] && filled[a2] - z[a2] > 0.004) lake[a2] = 1; }
      var segs = []; for (var s2 = 0; s2 < N; s2++) if (rec[s2] >= 0 && area[s2] >= 30 && !lake[s2]) segs.push(s2);
      segs.sort(function (p, q2) { return area[q2] - area[p]; });
      return { z: filled, rec: rec, area: area, maxA: maxA, segs: segs, lake: lake };
    }
    function draw(threshold) {
      var ctx = canvas.getContext("2d"), W = canvas.width, H = canvas.height, sx = W / NX, sy = H / NY, cs = getComputedStyle(document.documentElement);
      var zmin = Infinity, zmax = -Infinity, i;
      for (i = 0; i < state.z.length; i++) { if (state.z[i] < zmin) zmin = state.z[i]; if (state.z[i] > zmax) zmax = state.z[i]; }
      // elevation tint: pale sand in the valleys to rusty rose on the ridges
      var lo = [246, 240, 232], hi = [214, 150, 120];
      for (var yy = 0; yy < NY; yy++) for (var xx = 0; xx < NX; xx++) { var t2 = (state.z[yy * NX + xx] - zmin) / (zmax - zmin || 1); var ci = yy * NX + xx, gx = state.z[xx > 0 ? ci - 1 : ci] - state.z[xx < NX - 1 ? ci + 1 : ci], gy = state.z[yy > 0 ? ci - NX : ci] - state.z[yy < NY - 1 ? ci + NX : ci], hs = Math.max(0.88, Math.min(1.05, 1 + 1.2 * (gx + gy))); ctx.fillStyle = "rgb(" + Math.round((lo[0] + (hi[0] - lo[0]) * t2) * hs) + "," + Math.round((lo[1] + (hi[1] - lo[1]) * t2) * hs) + "," + Math.round((lo[2] + (hi[2] - lo[2]) * t2) * hs) + ")"; ctx.fillRect(Math.floor(xx * sx), Math.floor(yy * sy), Math.ceil(sx) + 1, Math.ceil(sy) + 1); }
      // ponded water (filled pits such as crater lakes) in river blue
      ctx.fillStyle = "rgb(156,200,234)";
      for (i = 0; i < state.lake.length; i++) if (state.lake[i]) { var lx = i % NX, ly = (i / NX) | 0; ctx.fillRect(Math.floor(lx * sx), Math.floor(ly * sy), Math.ceil(sx) + 1, Math.ceil(sy) + 1); }
      var step = (zmax - zmin) / 22; ctx.fillStyle = "rgba(148,80,58,.45)";
      for (var y = 0; y < NY - 1; y++) for (var x = 0; x < NX - 1; x++) { var a = Math.floor((state.z[y * NX + x] - zmin) / step), b = Math.floor((state.z[y * NX + x + 1] - zmin) / step), c = Math.floor((state.z[(y + 1) * NX + x] - zmin) / step); if (a !== b || a !== c) ctx.fillRect(x * sx + sx / 2 - 0.7, y * sy + sy / 2 - 0.7, 1.4, 1.4); }
      ctx.strokeStyle = cs.getPropertyValue("--dust-deep").trim(); ctx.lineCap = "round";
      var dpr = W / canvas.clientWidth || 1;
      for (var k = 0; k < state.segs.length; k++) { var s = state.segs[k], A = state.area[s]; if (A < threshold) break; var r = state.rec[s]; ctx.lineWidth = (0.45 + 0.08 * Math.sqrt(A)) * dpr; ctx.beginPath(); ctx.moveTo((s % NX + 0.5) * sx, (((s / NX) | 0) + 0.5) * sy); ctx.lineTo((r % NX + 0.5) * sx, (((r / NX) | 0) + 0.5) * sy); ctx.stroke(); }
    }
    function size() { var dpr = Math.min(window.devicePixelRatio || 1, 2); canvas.width = Math.round(canvas.clientWidth * dpr); canvas.height = Math.round(canvas.clientWidth * dpr * NY / NX); }
    var seed = 20231009, base = terrain(seed), cur = base.slice();
    function run() {
      cancelAnimationFrame(raf); state = route(cur); size();
      var minA = 30, maxA = state.maxA;
      if (reduceMotion) { draw(minA); return; }
      var st = performance.now(), dur = 2600;
      (function f(t) { var p = Math.min(1, (t - st) / dur), e2 = 1 - Math.pow(1 - p, 3); draw(Math.exp(Math.log(maxA) + (Math.log(minA) - Math.log(maxA)) * e2)); if (p < 1) raf = requestAnimationFrame(f); })(st);
    }
    run();
    var acts = {
      "drainage-again": function () { seed = newSeed(); base = terrain(seed); cur = base.slice(); bowl.fill(0); },
      "drainage-noise": function () { addNoise(cur); },
      "drainage-craters": function () { addCraters(cur); },
      "drainage-volcanoes": function () { addVolcanoes(cur); },
    };
    Object.keys(acts).forEach(function (id) { var b = document.getElementById(id); if (b) b.addEventListener("click", function () { acts[id](); run(); }); });
    window.addEventListener("resize", function () { if (state) { size(); draw(30); } });
  }

  /* ---------- Lightbox for figures and photos ---------- */
  var groups = document.querySelectorAll("[data-gallery]");
  if (groups.length) {
    var dlg = document.createElement("dialog"); dlg.className = "lb";
    dlg.innerHTML = '<img alt=""><div class="lb-bar"><span class="lb-count"></span><span><button type="button" data-step="-1">Previous</button> <button type="button" data-step="1">Next</button> <button type="button" data-close>Close</button></span></div>';
    document.body.appendChild(dlg);
    var lbImg = dlg.querySelector("img"), lbCount = dlg.querySelector(".lb-count"), list = [], idx = 0;
    function show() { lbImg.src = list[idx].src; lbImg.alt = list[idx].alt; lbCount.textContent = (idx + 1) + " of " + list.length; }
    groups.forEach(function (g) {
      var btns = g.querySelectorAll("button");
      btns.forEach(function (b, i) { b.addEventListener("click", function () { list = [].map.call(btns, function (x) { var im = x.querySelector("img"); return { src: im.src, alt: im.alt }; }); idx = i; show(); dlg.showModal(); }); });
    });
    dlg.addEventListener("click", function (e) { var t = e.target; if (t === dlg || t.hasAttribute("data-close")) dlg.close(); else if (t.hasAttribute("data-step")) { idx = (idx + list.length + Number(t.getAttribute("data-step"))) % list.length; show(); } });
    dlg.addEventListener("keydown", function (e) { if (e.key === "ArrowRight") { idx = (idx + 1) % list.length; show(); } if (e.key === "ArrowLeft") { idx = (idx + list.length - 1) % list.length; show(); } });
  }

  /* ---------- Email: the address is only assembled on click, so it is not in the page source ---------- */
  function addr(el) { return atob(el.getAttribute("data-m")).split("").reverse().join(""); }
  document.querySelectorAll("a[data-m]").forEach(function (a) {
    a.addEventListener("click", function (ev) { ev.preventDefault(); location.href = "mailto:" + addr(a) + "?subject=%5BThe%20Gaia%20Lab%5D%20"; });
  });
  var copy = document.getElementById("copy-email");
  if (copy) copy.addEventListener("click", function () {
    var t = addr(copy);
    if (navigator.clipboard) navigator.clipboard.writeText(t).then(function () { copy.textContent = "Copied"; }, function () { copy.textContent = t; });
    else copy.textContent = t;
  });
})();
