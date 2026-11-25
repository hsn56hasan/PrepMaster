// PrepKampüs renk paleti: mavi tonlar yerine zümrüt ve adaçayı (#6FA287).
// Tailwind'in "blue", "sky" ve "indigo" paletleri burada yeniden tanımlanır; böylece sayfalardaki
// bg-blue-600, text-indigo-600 gibi tüm sınıflar kendiliğinden yeni renklere geçer.
// Tailwind CDN betiğinden ve (varsa) sayfanın kendi tailwind.config'inden SONRA yüklenmelidir.
(function () {
  var emerald = {
    50: "#effaf4", 100: "#d9f2e5", 200: "#b6e3cc", 300: "#8fcdb0", 400: "#6FA287",
    500: "#10b981", 600: "#059669", 700: "#047857", 800: "#065f46", 900: "#064e3b", 950: "#022c22",
  };
  var sage = {
    50: "#f1f6f3", 100: "#dde9e2", 200: "#bdd4c7", 300: "#9cbfad", 400: "#6FA287",
    500: "#5b8c72", 600: "#4a775f", 700: "#3d624e", 800: "#2f4c3d", 900: "#23392e", 950: "#14221b",
  };
  window.PREPKAMPUS_PALETTE = { emerald: emerald, sage: sage };
  if (!window.tailwind) return;
  var cfg = window.tailwind.config || {};
  var theme = cfg.theme || {};
  var extend = theme.extend || {};
  var colors = Object.assign({}, extend.colors || {}, { blue: emerald, sky: emerald, indigo: sage, brand: emerald, sage: sage });
  window.tailwind.config = Object.assign({}, cfg, {
    theme: Object.assign({}, theme, { extend: Object.assign({}, extend, { colors: colors }) }),
  });
})();
