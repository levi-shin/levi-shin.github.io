/* Legacy inline onclick compatibility layer.
 * Keeps existing HTML onclick handlers working while ES modules load.
 */
(function () {
  window.switchSection = function (evt, sectionId) {
    document.querySelectorAll('.content-section').forEach(function (sec) {
      sec.classList.remove('active');
    });
    document.querySelectorAll('.nav-menu button').forEach(function (btn) {
      btn.classList.remove('active');
      var onclick = btn.getAttribute('onclick') || '';
      if (onclick.indexOf("'" + sectionId + "'") !== -1 || onclick.indexOf('"' + sectionId + '"') !== -1) {
        btn.classList.add('active');
      }
    });
    var section = document.getElementById(sectionId);
    if (section) section.classList.add('active');
    if (evt && evt.currentTarget) evt.currentTarget.classList.add('active');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  window.filterBuilds = function (evt, tag) {
    document.querySelectorAll('.filter-tags .filter-btn').forEach(function (b) {
      b.classList.remove('active');
    });
    if (evt && evt.currentTarget) evt.currentTarget.classList.add('active');
    document.querySelectorAll('#buildCardsGrid .card').forEach(function (card) {
      var tags = (card.getAttribute('data-tags') || '').split(',').map(function (t) { return t.trim(); }).filter(Boolean);
      card.style.display = (tag === 'all' || tags.indexOf(tag) !== -1) ? 'flex' : 'none';
    });
  };

  window.filterContent = function () {
    var input = document.getElementById('searchInput');
    if (!input) return;
    var filter = input.value.toLowerCase().trim();
    document.querySelectorAll('.searchable-item').forEach(function (item) {
      var text = (item.textContent || item.innerText || '').toLowerCase();
      var visible = text.indexOf(filter) > -1;
      if (item.tagName === 'TR') item.style.display = visible ? 'table-row' : 'none';
      else if (item.classList.contains('card')) item.style.display = visible ? 'flex' : 'none';
      else item.style.display = visible ? 'block' : 'none';
    });
  };
})();
