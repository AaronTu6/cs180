"use strict";

const report = JSON.parse(document.getElementById("report-data").textContent);
const lookup = new Map(report.results.map(row => [`${row.filename}|${row.method}|${row.metric}`, row]));

document.querySelectorAll(".gallery-section").forEach(section => {
  section.querySelectorAll("[data-view]").forEach(button => {
    button.addEventListener("click", () => {
      const view = button.dataset.view;
      section.querySelectorAll("[data-view]").forEach(control => {
        control.setAttribute("aria-pressed", String(control === button));
      });
      section.querySelectorAll(".result-card").forEach(card => {
        const {filename, method} = card.dataset;
        const image = card.querySelector(".result-image");
        const link = card.querySelector(".result-link");
        const offset = card.querySelector(".result-offsets");
        const title = card.querySelector("h3").textContent;
        if (view === "unaligned") {
          image.src = `assets/${filename.replace(/\.[^.]+$/, "")}_unaligned.jpg`;
          image.alt = `${title}, before alignment`;
          link.href = image.getAttribute("src");
          link.setAttribute("aria-label", `Open unaligned preview of ${title}`);
          offset.textContent = "G (0, 0) · R (0, 0) · no alignment";
        } else {
          const row = lookup.get(`${filename}|${method}|${view}`);
          image.src = row.preview;
          image.alt = `${title}, aligned with ${method} ${view.toUpperCase()}`;
          link.href = row.output;
          link.setAttribute("aria-label", `Open full-resolution ${title}`);
          offset.textContent = `G (${row.green_dx}, ${row.green_dy}) · R (${row.red_dx}, ${row.red_dy}) · ${row.seconds.toFixed(2)} s`;
        }
      });
    });
  });
});
document.documentElement.classList.add("js-ready");
