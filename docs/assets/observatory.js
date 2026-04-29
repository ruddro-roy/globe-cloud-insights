/* Live Observatory
 * Sky atlas: Aladin Lite (CDS Strasbourg), embedded under its terms of use.
 * Solar window: Helioviewer Project public API of NASA SDO data, with a
 * graceful fallback to the publicly mirrored latest images at sdo.gsfc.nasa.gov.
 */
(function () {
  "use strict";

  // ---------- Aladin Lite ----------
  function initAladin() {
    var status = document.getElementById("aladin-status");
    var container = document.getElementById("aladin-lite-div");
    if (!container) return;

    if (typeof A === "undefined" || !A || !A.init) {
      if (status) {
        status.textContent =
          "Sky atlas script could not be loaded. Aladin Lite is served from aladin.cds.unistra.fr.";
        status.classList.add("is-error");
      }
      return;
    }

    A.init.then(function () {
      var aladin = A.aladin("#aladin-lite-div", {
        survey: "P/DSS2/color",
        fov: 1.6,
        target: "M45",
        cooFrame: "ICRSd",
        showReticle: true,
        showZoomControl: true,
        showLayersControl: true,
        showFullscreenControl: true,
        showCooGridControl: false,
        showSimbadPointerControl: true,
        showFrame: true,
        showCoordinates: true,
        showShareControl: false,
      });

      var surveySel = document.getElementById("aladin-survey");
      if (surveySel) {
        surveySel.addEventListener("change", function () {
          aladin.setImageSurvey(surveySel.value);
        });
      }

      var targetInput = document.getElementById("aladin-target");
      var goBtn = document.getElementById("aladin-go");
      function applyTarget() {
        var v = (targetInput && targetInput.value || "").trim();
        if (!v) return;
        try {
          aladin.gotoObject(v);
          if (status) {
            status.textContent = "Target set, " + v + ".";
            status.classList.remove("is-error");
            status.classList.add("is-ready");
          }
        } catch (e) {
          if (status) {
            status.textContent = "Could not resolve target: " + v;
            status.classList.add("is-error");
          }
        }
      }
      if (goBtn) goBtn.addEventListener("click", applyTarget);
      if (targetInput) {
        targetInput.addEventListener("keydown", function (e) {
          if (e.key === "Enter") {
            e.preventDefault();
            applyTarget();
          }
        });
      }

      if (status) {
        status.textContent =
          "Sky atlas ready. Centred on the Pleiades, M45.";
        status.classList.remove("is-error");
        status.classList.add("is-ready");
      }
    }).catch(function () {
      if (status) {
        status.textContent =
          "Sky atlas could not initialise in this browser.";
        status.classList.add("is-error");
      }
    });
  }

  // ---------- Solar window ----------
  // SDO sourceId values used by Helioviewer for the AIA and HMI products.
  // See https://api.helioviewer.org/docs/v1/ for the canonical list.
  var SDO_FALLBACK_FILES = {
    "9":  "latest_512_0131.jpg",  // AIA 131
    "10": "latest_512_0171.jpg",  // AIA 171
    "11": "latest_512_0193.jpg",  // AIA 193
    "12": "latest_512_0211.jpg",  // AIA 211
    "13": "latest_512_0304.jpg",  // AIA 304
    "15": "latest_512_1600.jpg",  // AIA 1600
    "18": "latest_512_HMIIC.jpg", // HMI continuum
    "19": "latest_512_HMIB.jpg",  // HMI magnetogram (Bz)
  };

  var WAVELENGTH_LAYER = {
    // Helioviewer layer string: [Observatory, Instrument, Detector, Measurement, visible, opacity]
    "9":  "[SDO,AIA,AIA,131,1,100]",
    "10": "[SDO,AIA,AIA,171,1,100]",
    "11": "[SDO,AIA,AIA,193,1,100]",
    "12": "[SDO,AIA,AIA,211,1,100]",
    "13": "[SDO,AIA,AIA,304,1,100]",
    "15": "[SDO,AIA,AIA,1600,1,100]",
    "18": "[SDO,HMI,HMI,continuum,1,100]",
    "19": "[SDO,HMI,HMI,magnetogram,1,100]",
  };

  function pad(n) { return n < 10 ? "0" + n : "" + n; }
  function nowIsoUTC() {
    var d = new Date();
    return (
      d.getUTCFullYear() + "-" +
      pad(d.getUTCMonth() + 1) + "-" +
      pad(d.getUTCDate()) + "T" +
      pad(d.getUTCHours()) + ":" +
      pad(d.getUTCMinutes()) + ":" +
      pad(d.getUTCSeconds()) + ".000Z"
    );
  }
  function fmtUTC(d) {
    return (
      d.getUTCFullYear() + "-" +
      pad(d.getUTCMonth() + 1) + "-" +
      pad(d.getUTCDate()) + " " +
      pad(d.getUTCHours()) + ":" +
      pad(d.getUTCMinutes()) + ":" +
      pad(d.getUTCSeconds()) + " UTC"
    );
  }

  function buildHelioviewerUrl(sourceId, isoDate) {
    var layers = WAVELENGTH_LAYER[sourceId] || WAVELENGTH_LAYER["13"];
    var params =
      "date=" + encodeURIComponent(isoDate) +
      "&imageScale=2.4" +
      "&layers=" + encodeURIComponent(layers) +
      "&events=" +
      "&eventLabels=false" +
      "&scale=false" +
      "&x0=0&y0=0" +
      "&width=1024&height=1024" +
      "&display=true" +
      "&watermark=false";
    return "https://api.helioviewer.org/v2/takeScreenshot/?" + params;
  }

  function buildSdoFallbackUrl(sourceId) {
    var name = SDO_FALLBACK_FILES[sourceId] || SDO_FALLBACK_FILES["13"];
    return "https://sdo.gsfc.nasa.gov/assets/img/latest/" + name;
  }

  function setStatus(el, msg, kind) {
    if (!el) return;
    el.textContent = msg;
    el.classList.remove("is-error", "is-ready");
    if (kind) el.classList.add(kind);
  }

  function initSun() {
    var img = document.getElementById("sun-image");
    var overlay = document.getElementById("sun-overlay");
    var sel = document.getElementById("sun-wavelength");
    var btn = document.getElementById("sun-refresh");
    var status = document.getElementById("sun-status");
    var sourceLabel = document.getElementById("sun-source");
    var acquired = document.getElementById("sun-acquired");
    var loaded = document.getElementById("sun-loaded");
    var caption = document.getElementById("sun-caption");
    if (!img || !sel) return;

    var pendingFallback = false;

    function currentLabel() {
      var opt = sel.options[sel.selectedIndex];
      return (opt && opt.getAttribute("data-label")) || opt.text;
    }

    function showOverlay(show) {
      if (overlay) overlay.hidden = !show;
      if (show) img.classList.add("is-loading");
      else img.classList.remove("is-loading");
    }

    function loadImage(useFallback) {
      var sourceId = sel.value;
      var requestedAt = new Date();
      var iso = nowIsoUTC();
      var url;
      if (useFallback) {
        url = buildSdoFallbackUrl(sourceId) + "?t=" + requestedAt.getTime();
        if (sourceLabel) {
          sourceLabel.textContent =
            "NASA SDO mirror, sdo.gsfc.nasa.gov (fallback)";
        }
      } else {
        url = buildHelioviewerUrl(sourceId, iso);
        if (sourceLabel) {
          sourceLabel.textContent = "Helioviewer Project · NASA SDO";
        }
      }
      pendingFallback = !useFallback;
      btn.disabled = true;
      showOverlay(true);
      setStatus(
        status,
        useFallback
          ? "Fetching latest mirrored image, " + currentLabel() + "."
          : "Requesting closest available image, " + currentLabel() + ".",
        null
      );
      if (acquired) {
        acquired.textContent = useFallback
          ? "latest available"
          : "closest to " + fmtUTC(requestedAt);
      }
      if (loaded) loaded.textContent = "—";
      if (caption) {
        caption.textContent = useFallback
          ? "NASA Solar Dynamics Observatory, latest mirrored image at sdo.gsfc.nasa.gov."
          : "Solar Dynamics Observatory, near-real-time imagery via the Helioviewer Project public API.";
      }
      img.alt = "SDO solar image, " + currentLabel();
      img.src = url;
    }

    img.addEventListener("load", function () {
      btn.disabled = false;
      showOverlay(false);
      var now = new Date();
      if (loaded) loaded.textContent = fmtUTC(now);
      setStatus(
        status,
        "Image loaded at " + fmtUTC(now) + ".",
        "is-ready"
      );
      pendingFallback = false;
    });

    img.addEventListener("error", function () {
      if (pendingFallback) {
        pendingFallback = false;
        setStatus(
          status,
          "Helioviewer endpoint unreachable, falling back to NASA SDO mirror.",
          null
        );
        loadImage(true);
      } else {
        btn.disabled = false;
        showOverlay(false);
        setStatus(
          status,
          "Could not load solar image. Try a different wavelength or refresh.",
          "is-error"
        );
      }
    });

    btn.addEventListener("click", function () { loadImage(false); });
    sel.addEventListener("change", function () { loadImage(false); });

    loadImage(false);
  }

  function ready(fn) {
    if (document.readyState !== "loading") fn();
    else document.addEventListener("DOMContentLoaded", fn);
  }

  ready(function () {
    initAladin();
    initSun();
  });
})();
