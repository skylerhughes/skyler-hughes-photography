(function () {
  "use strict";

  const main = document.getElementById("main-content");
  const sidebar = document.getElementById("sidebar");
  const navToggle = document.getElementById("nav-toggle");

  const lightbox = document.getElementById("lightbox");
  const lightboxImg = lightbox.querySelector(".lightbox-img");
  let currentImages = [];
  let currentIndex = 0;

  function assetPath(file, isImage) {
    const prefix = window.PAGE && window.PAGE.depth ? "../" : "";
    return prefix + (isImage ? "images/" : "") + file;
  }

  const GAP = 6;

  function targetRowHeight() {
    return window.innerWidth <= 860 ? 220 : 380;
  }

  function layoutRows(container, images, rowHeight) {
    const containerWidth = container.clientWidth;
    let row = [];
    let rowAspectSum = 0;

    function flushRow(isLastRow) {
      if (!row.length) return;
      const rowGaps = GAP * (row.length - 1);
      const naturalWidth = rowAspectSum * rowHeight + rowGaps;
      const fill = !isLastRow || naturalWidth > containerWidth;

      const rowEl = document.createElement("div");
      rowEl.className = "grid-row" + (fill ? " grid-row--fill" : "");

      row.forEach(function (entry) {
        const cell = document.createElement("div");
        cell.className = "grid-item";
        cell.style.setProperty("--row-height", rowHeight + "px");
        if (fill) {
          cell.style.flexGrow = String(entry.aspect);
        } else {
          cell.style.width = (entry.aspect * rowHeight) + "px";
        }
        const img = document.createElement("img");
        img.src = assetPath(entry.item.file, true);
        img.alt = entry.item.alt;
        if (entry.index === 0) {
          img.loading = "eager";
          img.fetchPriority = "high";
        } else if (entry.index === 1) {
          img.loading = "eager";
        } else {
          img.loading = "lazy";
        }
        cell.appendChild(img);
        cell.addEventListener("click", function () {
          openLightbox(images, entry.index);
        });
        rowEl.appendChild(cell);
      });

      container.appendChild(rowEl);
      row = [];
      rowAspectSum = 0;
    }

    images.forEach(function (item, index) {
      const aspect = (item.w && item.h) ? item.w / item.h : 4 / 3;
      row.push({ item: item, index: index, aspect: aspect });
      rowAspectSum += aspect;
      const rowGaps = GAP * (row.length - 1);
      const widthAtTarget = rowAspectSum * rowHeight + rowGaps;
      if (widthAtTarget >= containerWidth) {
        flushRow(false);
      }
    });
    flushRow(true);
  }

  function renderGrid(images) {
    let grid = document.getElementById("photo-grid");
    if (grid) {
      grid.innerHTML = "";
    } else {
      grid = document.createElement("div");
      grid.className = "grid";
      grid.id = "photo-grid";
    }
    requestAnimationFrame(function () {
      layoutRows(grid, images, targetRowHeight());
    });

    let resizeTimer = null;
    window.addEventListener("resize", function () {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(function () {
        grid.innerHTML = "";
        layoutRows(grid, images, targetRowHeight());
      }, 150);
    });

    return grid;
  }

  function renderHome() {
    main.appendChild(renderGrid(SITE_DATA.home));
  }

  function renderGallery(id) {
    const images = SITE_DATA.galleries[id];
    main.appendChild(renderGrid(images));
  }

  function renderPage() {
    const page = window.PAGE || { type: "home" };
    if (page.type === "home") {
      renderHome();
    } else if (page.type === "gallery" && SITE_DATA.galleries[page.id]) {
      renderGallery(page.id);
    }
  }

  // ---------- Lightbox ----------

  function openLightbox(images, index) {
    currentImages = images;
    currentIndex = index;
    showCurrentImage();
    lightbox.hidden = false;
  }

  function showCurrentImage() {
    const item = currentImages[currentIndex];
    lightboxImg.src = assetPath(item.file, true);
    lightboxImg.alt = item.alt;
  }

  function closeLightbox() {
    lightbox.hidden = true;
    lightboxImg.src = "";
  }

  function showNext(delta) {
    if (!currentImages.length) return;
    currentIndex = (currentIndex + delta + currentImages.length) % currentImages.length;
    showCurrentImage();
  }

  lightbox.querySelector(".lightbox-close").addEventListener("click", closeLightbox);
  lightbox.querySelector(".lightbox-prev").addEventListener("click", function () { showNext(-1); });
  lightbox.querySelector(".lightbox-next").addEventListener("click", function () { showNext(1); });
  lightbox.addEventListener("click", function (e) {
    if (e.target === lightbox) closeLightbox();
  });

  document.addEventListener("keydown", function (e) {
    if (lightbox.hidden) return;
    if (e.key === "Escape") closeLightbox();
    if (e.key === "ArrowLeft") showNext(-1);
    if (e.key === "ArrowRight") showNext(1);
  });

  // ---------- Mobile nav ----------

  navToggle.addEventListener("click", function () {
    const open = sidebar.classList.toggle("open");
    navToggle.setAttribute("aria-expanded", String(open));
  });

  renderPage();
})();
