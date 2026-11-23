// PrepKampüs — oturum başlığı katmanı
// Sunucu kullanıcı kimliğini artık YALNIZCA "Authorization: Bearer <token>" başlığından alır;
// istek gövdesindeki/sorgudaki user_id yok sayılır. Bu dosya, aynı kökene giden her /api/
// isteğine kayıtlı oturum token'ını ekler. Diğer betiklerden ÖNCE yüklenmelidir.
(function () {
  const TOKEN_KEY = "prepmaster_token";
  const originalFetch = window.fetch.bind(window);

  function isOwnApi(input) {
    try {
      const url = new URL(typeof input === "string" ? input : input.url, window.location.href);
      return url.origin === window.location.origin && url.pathname.startsWith("/api/");
    } catch (_) {
      return false;
    }
  }

  window.getAuthToken = function () {
    return localStorage.getItem(TOKEN_KEY);
  };

  window.fetch = async function (input, init) {
    const token = localStorage.getItem(TOKEN_KEY);
    if (token && isOwnApi(input)) {
      init = init || {};
      const headers = new Headers(init.headers || (input instanceof Request ? input.headers : undefined));
      if (!headers.has("Authorization")) headers.set("Authorization", "Bearer " + token);
      init = Object.assign({}, init, { headers });
    }
    const res = await originalFetch(input, init);

    // Süresi dolmuş/geçersiz oturum: yerel kullanıcıyı temizle ki arayüz giriş istesin.
    if (res.status === 401 && token && isOwnApi(input)) {
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem("auth_user");
      if (window.appState) window.appState.currentUser = null;
      if (typeof window.openAuthModal === "function") {
        try { window.openAuthModal(true); } catch (_) {}
      }
    }
    return res;
  };
})();
