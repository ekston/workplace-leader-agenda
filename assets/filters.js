// Appendix filters: lens, severity, sort. No dependencies, no tracking.
(function () {
  var list = document.querySelector("[data-items]");
  if (!list) return;
  var state = { lens: "All", sev: "All", sort: "severity" };
  var rank = { High: 0, Medium: 1, Low: 2 };
  var items = Array.prototype.slice.call(list.querySelectorAll(".item"));
  var shownEl = document.querySelector("[data-shown]");
  function apply() {
    var visible = items.filter(function (el) {
      var okL = state.lens === "All" || el.dataset.lenses.split(" ").indexOf(state.lens) > -1;
      var okS = state.sev === "All" || el.dataset.sev === state.sev;
      el.hidden = !(okL && okS);
      return okL && okS;
    });
    items.slice().sort(function (a, b) {
      var s = rank[a.dataset.sev] - rank[b.dataset.sev], d = a.dataset.date.localeCompare(b.dataset.date);
      return state.sort === "severity" ? (s || d) : (d || s);
    }).forEach(function (el) { list.appendChild(el); });
    var n = 0;
    items.slice().sort(function (a, b) { return Array.prototype.indexOf.call(list.children, a) - Array.prototype.indexOf.call(list.children, b); })
      .forEach(function (el) { if (!el.hidden) { n++; el.querySelector(".idx").textContent = "A." + (n < 10 ? "0" + n : n); } });
    if (shownEl) shownEl.textContent = visible.length + " of " + items.length + " shown";
  }
  document.querySelectorAll(".filter button").forEach(function (b) {
    b.addEventListener("click", function () {
      var k = b.dataset.key;
      state[k] = b.dataset.value;
      document.querySelectorAll('.filter button[data-key="' + k + '"]').forEach(function (o) { o.setAttribute("aria-pressed", o === b ? "true" : "false"); });
      apply();
    });
  });
  apply();
})();
