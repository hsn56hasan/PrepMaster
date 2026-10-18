/**
 * PrepMaster Authentication Module (static/js/auth.js)
 * Implements Google OAuth 2.0 Client & Forgot/Reset Password Flow
 * Compatible with backend /api/auth/google, /api/auth/forgot-password, /api/auth/reset-password
 */

(function () {
  // Google Sign-In Client Handler
  async function signInWithGoogle() {
    const btn = document.getElementById("btn-google-login");
    const errEl = document.getElementById("login-error-msg");
    if (errEl) errEl.classList.add("hidden");

    let googleEmail = prompt(
      "Google Hesabı ile Giriş (Simülasyon / Sandbox):\nLütfen Google e-posta adresinizi giriniz:",
      "ogrenci.google@gmail.com"
    );
    if (!googleEmail || !googleEmail.trim()) return;
    googleEmail = googleEmail.trim();

    let googleName = "Google Öğrenci";
    if (googleEmail.includes("@")) {
      const rawPrefix = googleEmail.split("@")[0].replace(/[._-]/g, " ");
      googleName = rawPrefix.charAt(0).toUpperCase() + rawPrefix.slice(1);
    }

    if (btn) {
      btn.disabled = true;
      btn.innerHTML = `<span class="animate-spin inline-block mr-2">⏳</span> Giriş Yapılıyor...`;
    }

    try {
      const res = await fetch("/api/auth/google", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          token: "mock-google-id-token-" + Date.now(),
          email: googleEmail,
          name: googleName,
          full_name: googleName,
          avatar_url: "https://lh3.googleusercontent.com/a/default_avatar"
        })
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || "Google girişi başarısız oldu.");
      }

      const user = data.user;
      const token = data.access_token || data.token;

      if (window.appState) {
        window.appState.currentUser = user;
        if (user.university) {
          window.appState.currentUniversity = user.university;
          if (typeof renderUniversityHeader === "function") renderUniversityHeader();
        }
      }

      localStorage.setItem("auth_user", JSON.stringify(user));
      if (token) localStorage.setItem("prepmaster_token", token);

      const nameEl = document.getElementById("header-user-name");
      if (nameEl) nameEl.innerText = (user.full_name || user.username).split(" ")[0];

      const modal = document.getElementById("auth-modal");
      if (modal) modal.removeAttribute("data-mandatory");
      if (typeof closeAuthModal === "function") closeAuthModal();

      if (typeof showNotification === "function") {
        showNotification(`✓ Google ile başarıyla giriş yapıldı. Hoş geldin, ${user.full_name}!`, "emerald");
      }

      if (user.verification_status !== "verified" && typeof openDocScanModal === "function") {
        setTimeout(() => openDocScanModal(true), 600);
      }
    } catch (err) {
      if (errEl) {
        errEl.innerText = err.message;
        errEl.classList.remove("hidden");
      } else if (typeof showNotification === "function") {
        showNotification("Google Giriş Hatası: " + err.message, "rose");
      }
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = `
          <svg class="w-4 h-4 mr-2 inline" viewBox="0 0 24 24">
            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/>
            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/>
          </svg>
          Google ile Giriş Yap
        `;
      }
    }
  }

  // Open Forgot Password Tab/View
  function openForgotPassword() {
    const formLogin = document.getElementById("form-login");
    const formReg = document.getElementById("form-register");
    const formForgot = document.getElementById("form-forgot-password");
    const titleEl = document.getElementById("auth-modal-title");

    if (formLogin) formLogin.classList.add("hidden");
    if (formReg) formReg.classList.add("hidden");
    if (formForgot) formForgot.classList.remove("hidden");

    if (titleEl) titleEl.innerText = "Şifremi Unuttum";

    // Show Phase A, Hide Phase B
    const stepReq = document.getElementById("forgot-step-request");
    const stepReset = document.getElementById("forgot-step-reset");
    if (stepReq) stepReq.classList.remove("hidden");
    if (stepReset) stepReset.classList.add("hidden");

    // Reset error messages
    const errReq = document.getElementById("forgot-error-msg");
    const succReq = document.getElementById("forgot-success-msg");
    const errReset = document.getElementById("reset-error-msg");
    if (errReq) errReq.classList.add("hidden");
    if (succReq) succReq.classList.add("hidden");
    if (errReset) errReset.classList.add("hidden");

    // Pre-fill email from login if available
    const loginIdent = document.getElementById("login-identifier")?.value || "";
    if (loginIdent && loginIdent.includes("@")) {
      const forgotEmail = document.getElementById("forgot-email");
      if (forgotEmail) forgotEmail.value = loginIdent;
    }

    if (window.lucide) window.lucide.createIcons();
  }

  // Submit Forgot Password Request (Step 1)
  async function submitForgotPasswordRequest() {
    const emailInput = document.getElementById("forgot-email");
    const email = emailInput ? emailInput.value.trim() : "";
    const errEl = document.getElementById("forgot-error-msg");
    const succEl = document.getElementById("forgot-success-msg");
    const btn = document.getElementById("btn-forgot-request");

    if (errEl) errEl.classList.add("hidden");
    if (succEl) succEl.classList.add("hidden");

    if (!email || !email.includes("@")) {
      if (errEl) {
        errEl.innerText = "Lütfen geçerli bir e-posta adresi giriniz.";
        errEl.classList.remove("hidden");
      }
      return;
    }

    if (btn) {
      btn.disabled = true;
      btn.innerHTML = `<span class="animate-spin inline-block mr-2">⏳</span> Kod Gönderiliyor...`;
    }

    try {
      const res = await fetch("/api/auth/forgot-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email })
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || "Şifre sıfırlama kodu gönderilemedi.");
      }

      if (succEl) {
        succEl.innerText = data.message || "6 haneli doğrulama kodu e-posta adresinize iletildi.";
        succEl.classList.remove("hidden");
      }

      const sandboxCode = data.reset_code_sandbox || data.reset_code || data.demo_code;
      const codeInput = document.getElementById("reset-code");
      const pill = document.getElementById("forgot-sandbox-code-pill");

      if (sandboxCode) {
        if (codeInput) codeInput.value = sandboxCode;
        if (pill) {
          pill.innerText = "Kod: " + sandboxCode;
          pill.classList.remove("hidden");
        }
      }

      // Transition to Step B
      setTimeout(() => {
        const stepReq = document.getElementById("forgot-step-request");
        const stepReset = document.getElementById("forgot-step-reset");
        if (stepReq) stepReq.classList.add("hidden");
        if (stepReset) stepReset.classList.remove("hidden");
        const newPwInput = document.getElementById("reset-new-password");
        if (newPwInput) setTimeout(() => newPwInput.focus(), 100);
        if (window.lucide) window.lucide.createIcons();
      }, 700);

    } catch (err) {
      if (errEl) {
        errEl.innerText = err.message;
        errEl.classList.remove("hidden");
      }
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = `<i data-lucide="send" class="w-4 h-4"></i> Sıfırlama Kodu Gönder`;
        if (window.lucide) window.lucide.createIcons();
      }
    }
  }

  // Submit Password Reset (Step 2)
  async function submitResetPassword() {
    const emailInput = document.getElementById("forgot-email");
    const codeInput = document.getElementById("reset-code");
    const newPwInput = document.getElementById("reset-new-password");
    const errEl = document.getElementById("reset-error-msg");
    const btn = document.getElementById("btn-reset-confirm");

    const email = emailInput ? emailInput.value.trim() : "";
    const reset_code = codeInput ? codeInput.value.trim() : "";
    const new_password = newPwInput ? newPwInput.value.trim() : "";

    if (errEl) errEl.classList.add("hidden");

    if (!reset_code || reset_code.length !== 6 || !/^\d{6}$/.test(reset_code)) {
      if (errEl) {
        errEl.innerText = "Lütfen 6 haneli sayısal doğrulama kodunu giriniz.";
        errEl.classList.remove("hidden");
      }
      return;
    }

    if (!new_password || new_password.length < 6) {
      if (errEl) {
        errEl.innerText = "Yeni şifreniz en az 6 karakter olmalıdır.";
        errEl.classList.remove("hidden");
      }
      return;
    }

    if (btn) {
      btn.disabled = true;
      btn.innerHTML = `<span class="animate-spin inline-block mr-2">⏳</span> Şifre Güncelleniyor...`;
    }

    try {
      const res = await fetch("/api/auth/reset-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, reset_code, new_password })
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || "Şifre sıfırlama işlemi başarısız.");
      }

      if (typeof showNotification === "function") {
        showNotification("✓ Şifreniz başarıyla güncellendi! Yeni şifrenizle giriş yapabilirsiniz.", "emerald");
      }

      // Return to login screen and fill credentials
      if (typeof switchAuthTab === "function") {
        switchAuthTab("login");
      }
      const loginIdent = document.getElementById("login-identifier");
      const loginPw = document.getElementById("login-password");
      if (loginIdent) loginIdent.value = email;
      if (loginPw) loginPw.value = new_password;

      const titleEl = document.getElementById("auth-modal-title");
      if (titleEl) titleEl.innerText = "Öğrenci Girişi & Kayıt";

    } catch (err) {
      if (errEl) {
        errEl.innerText = err.message;
        errEl.classList.remove("hidden");
      }
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = `<i data-lucide="check" class="w-4 h-4"></i> Şifreyi Güncelle ve Giriş Yap`;
        if (window.lucide) window.lucide.createIcons();
      }
    }
  }

  // Hook existing switchAuthTab to hide forgot-password container
  const _origSwitchAuthTab = window.switchAuthTab;
  window.switchAuthTab = function (tab) {
    const formForgot = document.getElementById("form-forgot-password");
    if (formForgot) formForgot.classList.add("hidden");

    const titleEl = document.getElementById("auth-modal-title");
    if (titleEl) titleEl.innerText = "Öğrenci Girişi & Kayıt";

    if (_origSwitchAuthTab && typeof _origSwitchAuthTab === "function") {
      _origSwitchAuthTab(tab);
    }
  };

  // Export functions globally
  window.signInWithGoogle = signInWithGoogle;
  window.openForgotPassword = openForgotPassword;
  window.submitForgotPasswordRequest = submitForgotPasswordRequest;
  window.submitResetPassword = submitResetPassword;
})();
