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
  // Premium "Orman & Kağıt": soğuk gri (slate) yerine hafif yeşil kırıklı sıcak nötrler.
  // Aydınlıkta kağıt zemin ve mürekkep metin; karanlıkta orman gecesi yüzeyleri.
  var ink = {
    50: "#fbfaf6", 100: "#f5f3ec", 200: "#ece9df", 300: "#dad6c9", 400: "#8e9993",
    500: "#5f6e67", 600: "#46554e", 700: "#2b3a34", 800: "#13261f", 900: "#0b1a15", 950: "#06110d",
  };
  window.PREPKAMPUS_PALETTE = { emerald: emerald, sage: sage, ink: ink };
  if (!window.tailwind) return;
  var cfg = window.tailwind.config || {};
  var theme = cfg.theme || {};
  var extend = theme.extend || {};
  var colors = Object.assign({}, extend.colors || {}, { blue: emerald, sky: emerald, indigo: sage, brand: emerald, sage: sage, slate: ink, gray: ink });
  window.tailwind.config = Object.assign({}, cfg, {
    theme: Object.assign({}, theme, { extend: Object.assign({}, extend, { colors: colors }) }),
  });
})();
