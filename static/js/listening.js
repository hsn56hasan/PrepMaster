// PrepKampüs Listening Simulator (HTML5 Audio Engine & Web Speech API Fallback)

window.listeningState = {
  tracks: [],
  currentTrack: null,
  audio: null,
  speechUtterance: null,
  speechTimer: null,
  usingSpeechFallback: false,
  speechCharOffset: 0,
  isPlaying: false,
  playbackRate: 1.0,
  duration: 0,
  currentTime: 0,
  userNotes: "",
  answers: {},
  questionsRevealed: false,
  // Not tutarak dinleme (gerçek sınav kuralı) için:
  audioCompleted: false,   // ses sonuna kadar çalındı mı
  playCount: 0,            // kaç kez başlatıldı (tek dinleme kuralı)
  kurallar: null,          // o parçanın kuralları, listeningKurallari() ile kurulur
  notesSaveTimer: null     // notların sunucuya yazılması için geciktirme
};

// Parçanın türüne göre kurallar. Tek yerde durur ki aynı oynatıcı hem not tutma
// modunda (sorular kilitli, tek dinleme) hem de while_listening modunda (sorular
// baştan açık, serbest dinleme) çalışsın; ileride tam deneme de bunu kullanacak.
function listeningKurallari(track) {
  const notModu = !!track && track.type === 'note_taking';
  return {
    notModu,
    sorulariKilitle: notModu,    // sorular ses bitmeden açılmaz
    tekDinleme: notModu,         // ses yalnızca bir kez çalınır
    sarmaSerbest: !notModu,      // ileri-geri sarma
    hizDegisebilir: !notModu,    // oynatma hızı
    duraklatilabilir: !notModu   // başladıktan sonra duraklatma
  };
}

function aktifKurallar() {
  return window.listeningState.kurallar || listeningKurallari(window.listeningState.currentTrack);
}


function setListeningPoolMode(mode) {
  window.listeningState.poolMode = mode;
  loadListeningHub(window.listeningState.activeLevelFilter || 'all');
}
window.setListeningPoolMode = setListeningPoolMode;

async function loadListeningHub(targetLevel = null) {
  const container = document.getElementById("listening-tracks-list");
  const filterBar = document.getElementById("listening-filter-bar");
  if (!container) return;

  const currentLevel = window.appState?.currentLevel || 'B2';
  const activeLevel = targetLevel !== null ? targetLevel : 'all';
  window.listeningState.activeLevelFilter = activeLevel;
  const poolMode = window.listeningState.poolMode || 'school';
  window.listeningState.poolMode = poolMode;

  const uniObj = window.appState?.currentUniversity || { id: 'itu', short_name: 'İTÜ' };
  const uniId = uniObj.id || 'itu';
  const shortName = uniObj.short_name || uniId.toUpperCase();

  // Render Level Filter Bar
  if (filterBar) {
    const levels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'];
    filterBar.innerHTML = `
      <div class="flex items-center gap-1.5 flex-wrap">
        <span class="text-xs font-bold text-slate-500 mr-1 flex items-center gap-1">
          <i data-lucide="filter" class="w-3.5 h-3.5"></i> Kur:
        </span>
        <button onclick="loadListeningHub('all')" class="px-3 py-1 rounded-xl text-xs font-bold transition ${activeLevel === 'all' ? 'bg-slate-900 text-white shadow-sm' : 'bg-white text-slate-600 hover:bg-slate-200 border border-slate-200'}">
          Tüm Kurlar (24 Ders)
        </button>
        ${levels.map(lvl => {
          const isSelected = activeLevel === lvl;
          return `
            <button onclick="loadListeningHub('${lvl}')" class="px-3 py-1 rounded-xl text-xs font-bold transition ${isSelected ? 'bg-blue-600 text-white shadow-sm' : 'bg-white text-slate-600 hover:bg-slate-200 border border-slate-200'}">
              ${lvl} (4) ${lvl === currentLevel ? '★' : ''}
            </button>
          `;
        }).join('')}
      </div>
      <div class="ml-auto flex items-center gap-1 bg-white p-1 rounded-xl border border-slate-200 text-[11px] font-bold">
        <button onclick="setListeningPoolMode('school')" class="px-2.5 py-1 rounded-lg transition ${poolMode === 'school' ? 'bg-blue-600 text-white' : 'text-slate-600 hover:bg-slate-100'}">
          Sadece ${shortName} Özel (24 Ders)
        </button>
        <button onclick="setListeningPoolMode('all')" class="px-2.5 py-1 rounded-lg transition ${poolMode === 'all' ? 'bg-blue-600 text-white' : 'text-slate-600 hover:bg-slate-100'}">
          ${shortName} + Genel Havuz
        </button>
      </div>
    `;
  }

  container.innerHTML = `
    <div class="col-span-full p-8 text-center text-slate-400">
      <i data-lucide="loader-2" class="w-6 h-6 animate-spin mx-auto mb-2 text-blue-600"></i>
      ${shortName} dinleme sınavları yükleniyor...
    </div>
  `;
  if (window.lucide) window.lucide.createIcons();

  try {
    const params = new URLSearchParams();
    if (activeLevel && activeLevel !== 'all') params.set('level', activeLevel);
    if (uniId && uniId !== 'general') {
      params.set('university_id', uniId);
      if (poolMode === 'school') params.set('strict_uni', 'true');
    }
    const url = `/api/listening?${params.toString()}`;
    const res = await fetch(url);
    const tracks = await res.json();
    window.listeningState.tracks = tracks;

    if (!tracks || tracks.length === 0) {
      container.innerHTML = `
        <div class="col-span-full p-8 text-center bg-white rounded-3xl border border-slate-200">
          <p class="text-sm font-bold text-slate-700 mb-2">${activeLevel} seviyesinde dinleme parçası bulunamadı.</p>
          <button onclick="loadListeningHub('all')" class="px-4 py-2 bg-blue-600 text-white text-xs font-bold rounded-xl hover:bg-blue-700 transition">
            Tüm Dinleme Sınavlarını Görüntüle
          </button>
        </div>
      `;
      if (window.lucide) window.lucide.createIcons();
      return;
    }

    container.innerHTML = tracks.map(t => {
      const isNoteTaking = t.type === 'note_taking';
      return `
        <div class="bg-white rounded-3xl p-6 border border-slate-200/80 hover:border-blue-400 hover:shadow-md transition flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between mb-3">
              <span class="px-2.5 py-1 text-[11px] font-extrabold rounded-full ${isNoteTaking ? 'bg-amber-100 text-amber-800 border border-amber-200' : 'bg-blue-100 text-blue-800 border border-blue-200'}">
                ${isNoteTaking ? '📝 Note-Taking' : '🎧 While-Listening'}
              </span>
              <span class="px-2.5 py-0.5 bg-blue-50 text-blue-700 border border-blue-100 rounded-lg text-xs font-black">
                ${t.level}
              </span>
            </div>

            <h3 class="text-base font-extrabold text-slate-800 mb-1 leading-snug">${t.title}</h3>
            <p class="text-xs font-bold text-blue-600 mb-3">${t.subtitle}</p>
            <p class="text-xs text-slate-500 leading-relaxed mb-4">${t.instructions_tr}</p>
          </div>

          <div class="pt-4 border-t border-slate-100 flex items-center justify-between">
            <span class="text-xs text-slate-400 flex items-center gap-1 font-medium">
              <i data-lucide="clock" class="w-3.5 h-3.5"></i> ${t.questions.length} Soru • ~${Math.round(t.lecture_duration_seconds / 60)} dk
            </span>
            <button onclick="startListeningTrack('${t.id}')" class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold rounded-xl transition flex items-center gap-1.5 shadow-sm shadow-blue-500/20">
              <i data-lucide="play" class="w-3.5 h-3.5"></i> Başlat
            </button>
          </div>
        </div>
      `;
    }).join('');

    if (window.lucide) window.lucide.createIcons();
  } catch (err) {
    console.error("Listening tracks error:", err);
    container.innerHTML = `<p class="col-span-full text-xs text-rose-500 text-center">Dinleme parçaları yüklenemedi.</p>`;
  }
}

function estimateTrackDuration(track) {
  if (!track) return 90;
  if (track.audio_script && track.audio_script.trim().length > 0) {
    const words = track.audio_script.trim().split(/\s+/).length;
    const estSeconds = Math.max(20, Math.round(words / 2.4));
    return track.lecture_duration_seconds || estSeconds;
  }
  return track.lecture_duration_seconds || 90;
}

function startListeningTrack(trackId) {
  const track = window.listeningState.tracks.find(t => t.id === trackId);
  if (!track) return;

  stopAudioPlayback();

  const kurallar = listeningKurallari(track);
  window.listeningState.kurallar = kurallar;
  window.listeningState.currentTrack = track;
  window.listeningState.answers = {};
  window.listeningState.userNotes = "";
  window.listeningState.questionsRevealed = !kurallar.sorulariKilitle;
  window.listeningState.audioCompleted = false;
  window.listeningState.playCount = 0;
  window.listeningState.currentTime = 0;
  window.listeningState.speechCharOffset = 0;
  window.listeningState.usingSpeechFallback = false;
  window.listeningState.duration = estimateTrackDuration(track);

  // Switch to Runner UI first so DOM elements exist before audio metadata loads
  document.getElementById("listening-hub-view")?.classList.add("hidden");
  document.getElementById("listening-runner-view")?.classList.remove("hidden");

  renderListeningRunner();

  // Initialize Audio after DOM is rendered
  initTrackAudio(track);
  syncAudioProgressUI();

  // Daha önce alınmış notlar varsa geri yükle (oturum açıksa).
  if (kurallar.notModu) loadUserNotes(track.id);
}

function exitListeningRunner() {
  stopAudioPlayback();
  document.getElementById("listening-runner-view")?.classList.add("hidden");
  document.getElementById("listening-hub-view")?.classList.remove("hidden");
}

function renderListeningRunner() {
  const t = window.listeningState.currentTrack;
  if (!t) return;

  const isNoteTaking = t.type === 'note_taking';
  const k = aktifKurallar();
  const sesBitti = window.listeningState.audioCompleted;
  const curFormatted = formatAudioTime(window.listeningState.currentTime || 0);
  const durFormatted = formatAudioTime(window.listeningState.duration || estimateTrackDuration(t));
  const sliderVal = (window.listeningState.duration > 0)
    ? Math.min(100, Math.max(0, ((window.listeningState.currentTime || 0) / window.listeningState.duration) * 100))
    : 0;

  const container = document.getElementById("listening-runner-content");
  if (!container) return;

  container.innerHTML = `
    <!-- Sınav Başlığı ve Kontroller -->
    <div class="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200/80 shadow-sm space-y-6">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-100">
        <div>
          <div class="flex items-center gap-2 mb-2">
            <span class="px-3 py-1 rounded-full text-xs font-extrabold ${isNoteTaking ? 'bg-amber-100 text-amber-800' : 'bg-blue-100 text-blue-800'}">
              ${isNoteTaking ? '📝 Note-Taking Modu' : '🎧 While-Listening Modu'}
            </span>
            <span class="px-2.5 py-0.5 bg-slate-100 text-slate-700 text-xs font-bold rounded-lg">${t.target_university}</span>
          </div>
          <h2 class="text-xl sm:text-2xl font-extrabold text-slate-800">${t.title}</h2>
          <p class="text-xs text-slate-500 mt-1">${t.subtitle}</p>
        </div>

        <button onclick="exitListeningRunner()" class="self-start sm:self-auto px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold rounded-xl transition">
          Geri Dön
        </button>
      </div>

      <!-- GERÇEK MP3 AUDIO ENGINE & PLAYER -->
      <div class="bg-gradient-to-r from-slate-900 to-indigo-950 text-white rounded-2xl p-6 shadow-lg space-y-4">
        <div class="flex flex-col md:flex-row items-center justify-between gap-4">
          <div class="flex items-center gap-4 w-full md:w-auto">
            <button id="audio-play-btn" onclick="toggleAudioPlayback()" class="w-14 h-14 rounded-2xl bg-blue-600 hover:bg-blue-500 text-white flex items-center justify-center shrink-0 shadow-lg shadow-blue-500/30 transition">
              <i data-lucide="play" class="w-7 h-7"></i>
            </button>
            <div>
              <span class="text-xs font-bold uppercase tracking-wider text-blue-400 block mb-0.5">Akademik Dinleme Kaydı (MP3 Audio)</span>
              <h4 class="text-sm font-extrabold text-white">${t.title}</h4>
              <span id="audio-status-text" class="text-xs text-slate-400">Başlatmak için oynat butonuna basın</span>
            </div>
          </div>

          <!-- Hız ve Ses Kontrolleri -->
          <div class="flex items-center gap-4 flex-wrap">
            ${k.hizDegisebilir ? `
            <div class="flex items-center gap-2">
              <span class="text-xs text-slate-400 font-semibold">Hız:</span>
              <div class="flex bg-slate-800/80 p-1 rounded-xl border border-slate-700">
                <button onclick="setPlaybackRate(0.75)" class="px-2.5 py-1 text-xs font-bold rounded-lg rate-btn hover:text-white text-slate-400 transition" id="rate-075">0.75x</button>
                <button onclick="setPlaybackRate(1.0)" class="px-2.5 py-1 text-xs font-bold rounded-lg rate-btn bg-blue-600 text-white transition" id="rate-10">1.0x</button>
                <button onclick="setPlaybackRate(1.25)" class="px-2.5 py-1 text-xs font-bold rounded-lg rate-btn hover:text-white text-slate-400 transition" id="rate-125">1.25x</button>
              </div>
            </div>
            ` : `
            <span class="text-[11px] text-slate-400 font-semibold flex items-center gap-1.5" title="Gerçek sınavda kayıt tek hızda ve bir kez çalınır">
              <i data-lucide="lock" class="w-3.5 h-3.5"></i> Sınav kuralı: tek dinleme, normal hız
            </span>
            `}

            <div class="flex items-center gap-2">
              <i data-lucide="volume-2" class="w-4 h-4 text-slate-400"></i>
              <input type="range" id="audio-volume" min="0" max="1" step="0.05" value="1" oninput="setAudioVolume(this.value)" class="w-16 sm:w-20 accent-blue-500 h-1.5 rounded-lg cursor-pointer bg-slate-700" title="Ses Seviyesi">
            </div>
          </div>
        </div>

        <!-- İlerleme / Seek Bar & Süre Göstergesi -->
        <div class="pt-2">
          <div class="flex items-center gap-3">
            <span id="audio-time-current" class="text-xs font-mono text-slate-300 w-10 text-right">${curFormatted}</span>
            <input type="range" id="audio-seek-slider" min="0" max="100" value="${sliderVal}" step="0.1" oninput="onSeekSliderChange(this.value)" ${k.sarmaSerbest ? '' : 'disabled title="Sınav kuralı: ileri-geri sarma kapalı"'} class="flex-1 h-2 bg-slate-800 rounded-lg appearance-none ${k.sarmaSerbest ? 'cursor-pointer accent-blue-500' : 'cursor-not-allowed accent-slate-500 opacity-60'}">
            <span id="audio-time-duration" class="text-xs font-mono text-slate-400 w-10">${durFormatted}</span>
          </div>
        </div>
      </div>


      <!-- NOTE-TAKING DIJITAL NOT DEFTERİ -->
      ${isNoteTaking ? `
        <div class="space-y-3">
          <div class="flex items-center justify-between">
            <label class="text-xs font-extrabold text-slate-700 uppercase tracking-wider flex items-center gap-2">
              <i data-lucide="file-edit" class="w-4 h-4 text-amber-600"></i> Dijital Not Defteriniz (Note Sheet)
            </label>
            <span class="text-[11px] text-amber-700 font-bold bg-amber-50 px-2.5 py-1 rounded-lg border border-amber-200">
              💡 İpucu: Kısaltmalar ve anahtar kavramları not alın!
            </span>
          </div>
          <textarea id="listening-notes-input" oninput="saveUserNotes(this.value)" rows="5" class="w-full p-4 text-xs font-mono bg-amber-50/40 border border-amber-200 rounded-2xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-amber-400 placeholder:text-slate-400 leading-relaxed" placeholder="Örn: - Confirmation bias: Peter Wason 1960&#10;- Framing effect: Kahneman & Tversky 1981 (%90 survival vs %10 mortality)...">${window.listeningState.userNotes}</textarea>

          ${!window.listeningState.questionsRevealed ? `
            <div id="listening-questions-lock-box" class="p-6 bg-gradient-to-r from-amber-500/10 to-orange-500/10 border-2 border-dashed border-amber-300 rounded-2xl text-center space-y-3">
              <i data-lucide="lock" class="w-8 h-8 mx-auto text-amber-600"></i>
              <h4 class="text-sm font-extrabold text-amber-900">Sorular Şu Anda Gizli (Gerçek Sınav Kuralı)</h4>
              <p class="text-xs text-amber-800 max-w-md mx-auto">
                Boğaziçi ve ODTÜ gibi üniversitelerde dinleme bitene kadar soru kağıdı verilmez. Kayıt bir kez çalınır; durdurma, sarma ve hız değiştirme kapalıdır. Dinleme bitince sorular açılır.
              </p>
              <button id="listening-unlock-btn" onclick="revealListeningQuestions()" ${sesBitti ? '' : 'disabled'}
                class="px-6 py-2.5 text-xs font-bold rounded-xl shadow-md transition flex items-center gap-2 mx-auto ${sesBitti ? 'bg-amber-600 hover:bg-amber-700 text-white cursor-pointer' : 'bg-slate-200 text-slate-400 cursor-not-allowed'}">
                <i data-lucide="${sesBitti ? 'unlock' : 'lock'}" class="w-4 h-4"></i>
                <span id="listening-unlock-label">${sesBitti ? 'Soruları Yanıtla' : 'Kayıt bitince açılır'}</span>
              </button>
            </div>
          ` : ''}
        </div>
      ` : ''}

      <!-- SORULAR ALANI -->
      <div id="listening-questions-container" class="${isNoteTaking && !window.listeningState.questionsRevealed ? 'hidden' : 'space-y-6 pt-4'}">
        <h3 class="text-base font-extrabold text-slate-800 flex items-center gap-2">
          <i data-lucide="help-circle" class="w-4 h-4 text-blue-600"></i> Sorular (${t.questions.length} Soru)
        </h3>

        <div class="space-y-4">
          ${t.questions.map((q, idx) => `
            <div class="p-5 bg-slate-50 border border-slate-200 rounded-2xl space-y-3" id="q-box-${q.id}">
              <div class="flex items-center gap-2">
                <span class="w-6 h-6 rounded-lg bg-blue-600 text-white text-xs font-bold flex items-center justify-center">${idx + 1}</span>
                <p class="text-xs font-bold text-slate-800">${q.question}</p>
              </div>

              <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-1">
                ${(!Array.isArray(q.options) || !q.options.length) ? '<div class="p-3 text-xs rounded-xl border border-amber-200 bg-amber-50 text-amber-800 font-medium">Bu soru tipi bu ekranda henüz desteklenmiyor.</div>' : q.options.map(opt => `
                  <button onclick="selectListeningAnswer('${q.id}', '${opt.key}')" id="opt-btn-${q.id}-${opt.key}" class="p-3 text-left text-xs bg-white hover:bg-blue-50 border border-slate-200 rounded-xl transition flex items-center gap-2.5 opt-choice-${q.id}">
                    <span class="w-5 h-5 rounded-full border border-slate-300 font-bold flex items-center justify-center text-[10px] text-slate-500">${opt.key}</span>
                    <span class="text-slate-700 font-medium">${opt.text}</span>
                  </button>
                `).join('')}
              </div>

              <!-- Çözüm & Açıklama: BOŞ render edilir, içeriği sınav bitince doldurulur.
                   Eskiden doğru cevap burada DOM'a yazılıp yalnızca "hidden" sınıfıyla gizleniyordu;
                   öğrenci eleman denetleyicisinden okuyabiliyordu. -->
              <div id="explanation-${q.id}" class="hidden p-3 bg-emerald-50 border border-emerald-200 text-emerald-900 text-xs rounded-xl mt-2 leading-relaxed"></div>
            </div>
          `).join('')}
        </div>

        <div class="pt-4 border-t border-slate-100 flex items-center justify-end gap-3">
          <button id="finish-listening-btn" onclick="submitListeningExam()" class="px-6 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-xl shadow-md transition flex items-center gap-2">
            <i data-lucide="check-circle" class="w-4 h-4"></i> Cevapları Kontrol Et & Puanla
          </button>
        </div>
      </div>

    </div>
  `;

  if (window.lucide) window.lucide.createIcons();
}

function saveUserNotes(val) {
  window.listeningState.userNotes = val;

  // Sunucuya yazmayı geciktir: her tuş vuruşunda istek atmayalım.
  const track = window.listeningState.currentTrack;
  if (!track || !aktifKurallar().notModu) return;
  if (window.listeningState.notesSaveTimer) clearTimeout(window.listeningState.notesSaveTimer);
  window.listeningState.notesSaveTimer = setTimeout(() => {
    window.listeningState.notesSaveTimer = null;
    persistUserNotes(track.id, window.listeningState.userNotes);
  }, 1500);
}

// Notları sunucuya yazar. Oturum yoksa (401) sessizce vazgeçer: notlar yine
// ekranda durur, yalnızca kalıcı olmaz.
async function persistUserNotes(trackId, notes) {
  try {
    await fetch('/api/listening/notes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ track_id: trackId, notes: (notes || '').slice(0, 8000) })
    });
  } catch (e) {
    console.warn('Notlar kaydedilemedi:', e);
  }
}

// Daha önce kaydedilmiş notları geri yükler.
async function loadUserNotes(trackId) {
  try {
    const res = await fetch('/api/listening/notes/' + encodeURIComponent(trackId));
    if (!res.ok) return;
    const data = await res.json();
    const notes = typeof data.notes === 'string' ? data.notes : '';
    if (!notes) return;
    // Parça değişmediyse yaz (yavaş yanıt başka parçaya taşmasın)
    if (window.listeningState.currentTrack?.id !== trackId) return;
    window.listeningState.userNotes = notes;
    const alan = document.getElementById('listening-notes-input');
    if (alan && !alan.value) alan.value = notes;
  } catch (e) {
    console.warn('Önceki notlar alınamadı:', e);
  }
}

// Ses sonuna kadar çalındığında çağrılır. Soruların kilidini açma yetkisi
// YALNIZCA buradan gelir; tahmini süreye değil, gerçek bitiş olayına dayanır.
function markAudioCompleted() {
  if (window.listeningState.audioCompleted) return;
  window.listeningState.audioCompleted = true;

  const btn = document.getElementById("listening-unlock-btn");
  if (btn) {
    btn.disabled = false;
    btn.classList.remove("bg-slate-200", "text-slate-400", "cursor-not-allowed");
    btn.classList.add("bg-amber-600", "hover:bg-amber-700", "text-white", "cursor-pointer");
    btn.innerHTML = `<i data-lucide="unlock" class="w-4 h-4"></i><span id="listening-unlock-label">Soruları Yanıtla</span>`;
    if (window.lucide) window.lucide.createIcons();
  }
  const statusEl = document.getElementById("audio-status-text");
  if (statusEl && aktifKurallar().notModu) {
    statusEl.innerText = "Kayıt bitti. Soruları açabilirsiniz.";
  }
}

function revealListeningQuestions() {
  const k = aktifKurallar();
  if (k.sorulariKilitle && !window.listeningState.audioCompleted) {
    const statusEl = document.getElementById("audio-status-text");
    if (statusEl) statusEl.innerText = "Sorular kayıt bitmeden açılamaz.";
    return;
  }
  pauseAudioPlayback();
  window.listeningState.questionsRevealed = true;
  const lockBox = document.getElementById("listening-questions-lock-box");
  if (lockBox) lockBox.classList.add("hidden");
  const qContainer = document.getElementById("listening-questions-container");
  if (qContainer) {
    qContainer.classList.remove("hidden");
    qContainer.classList.add("space-y-6", "pt-4");
  }
}

function selectListeningAnswer(qId, key) {
  window.listeningState.answers[qId] = key;

  // Update styles
  document.querySelectorAll(`.opt-choice-${qId}`).forEach(btn => {
    btn.classList.remove("bg-blue-600", "text-white", "border-blue-600");
    btn.classList.add("bg-white", "text-slate-700");
  });

  const selectedBtn = document.getElementById(`opt-btn-${qId}-${key}`);
  if (selectedBtn) {
    selectedBtn.classList.add("bg-blue-600", "text-white", "border-blue-600");
    selectedBtn.classList.remove("bg-white", "text-slate-700");
  }
}

// --- REAL HTML5 AUDIO & WEB SPEECH SYNTHESIS TIMER ENGINE ---
function formatAudioTime(seconds) {
  if (!isFinite(seconds) || isNaN(seconds) || seconds < 0) return "00:00";
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins < 10 ? '0' : ''}${mins}:${secs < 10 ? '0' : ''}${secs}`;
}

function getEffectiveDuration() {
  const audio = window.listeningState.audio;
  if (!window.listeningState.usingSpeechFallback && audio && audio.duration && isFinite(audio.duration) && audio.duration > 0) {
    return audio.duration;
  }
  if (window.listeningState.duration && isFinite(window.listeningState.duration) && window.listeningState.duration > 0) {
    return window.listeningState.duration;
  }
  return estimateTrackDuration(window.listeningState.currentTrack);
}

function syncAudioProgressUI() {
  const cur = Math.max(0, window.listeningState.currentTime || 0);
  const dur = Math.max(1, getEffectiveDuration());
  window.listeningState.duration = dur;

  const curEl = document.getElementById("audio-time-current");
  const durEl = document.getElementById("audio-time-duration");
  const slider = document.getElementById("audio-seek-slider");

  if (curEl) curEl.innerText = formatAudioTime(cur);
  if (durEl) durEl.innerText = formatAudioTime(dur);
  if (slider) slider.value = Math.min(100, Math.max(0, (cur / dur) * 100));
}

// Bir parçanın gerçek MP3'ü varsa backend onu `audio_url` alanıyla bildirir
// (backend/generate_audio.py üretirken data/listening.json'a yazar).
// Alan yoksa tarayıcının kendi seslendirmesi devreye girer.
// Eskiden burada elle yazılmış bir kimlik listesi vardı; veri kimlikleri
// değişince liste bayatlamış ve 656 parçanın TAMAMI sentezlenen sese düşmüştü.
// Yalnızca iki kaynağa izin verilir: kendi /static/audio/ yolumuz (yerel geliştirme ve
// yedek) ve ses kovasının TEK alan adı. Kalıp bilerek dar: yalnızca https, tek alan adı,
// /listening/ önü, .mp3 sonu, sorgu dizesi yok. listening.json ya da API yanıtı bir
// şekilde kirlenirse üçüncü bir alan adından ses yüklenmesi böyle engellenir.
const AUDIO_IZINLI_URL = /^https:\/\/ses\.prepkampus\.com\/listening\/[A-Za-z0-9._-]+\.mp3$/;

function trackAudioUrl(track) {
  const url = track && typeof track.audio_url === 'string' ? track.audio_url.trim() : '';
  if (!url || url.includes('..')) return '';
  if (url.startsWith('/static/audio/')) return url;
  return AUDIO_IZINLI_URL.test(url) ? url : '';
}

function startPlaybackTicker() {
  stopPlaybackTicker();
  let lastTick = performance.now();

  window.listeningState.speechTimer = setInterval(() => {
    const now = performance.now();
    const deltaSec = Math.max(0.05, Math.min(1.0, (now - lastTick) / 1000));
    lastTick = now;

    if (!window.listeningState.isPlaying) return;

    const audio = window.listeningState.audio;
    const rate = window.listeningState.playbackRate || 1.0;

    if (!window.listeningState.usingSpeechFallback && audio && !audio.paused && !audio.error) {
      if (typeof audio.currentTime === 'number' && audio.currentTime > 0) {
        window.listeningState.currentTime = audio.currentTime;
      } else {
        window.listeningState.currentTime = (window.listeningState.currentTime || 0) + deltaSec * rate;
      }
      if (audio.duration && isFinite(audio.duration) && audio.duration > 0) {
        window.listeningState.duration = audio.duration;
      }
      syncAudioProgressUI();
    } else if (window.listeningState.usingSpeechFallback) {
      const dur = getEffectiveDuration();
      window.listeningState.currentTime = Math.min(dur, (window.listeningState.currentTime || 0) + deltaSec * rate);
      syncAudioProgressUI();

      if (window.listeningState.currentTime >= dur) {
        window.listeningState.isPlaying = false;
        stopPlaybackTicker();
        updateAudioControlsUI(false);
        markAudioCompleted();
      }
    }
  }, 250);
}

function stopPlaybackTicker() {
  if (window.listeningState.speechTimer) {
    clearInterval(window.listeningState.speechTimer);
    window.listeningState.speechTimer = null;
  }
}

function initTrackAudio(track) {
  stopPlaybackTicker();
  if (window.listeningState.audio) {
    try {
      window.listeningState.audio.pause();
      window.listeningState.audio.src = '';
    } catch (_) {}
    window.listeningState.audio = null;
  }

  // Gerçek MP3'ü olmayan parçada doğrudan tarayıcı seslendirmesine geç (404 üretmeden)
  const audioUrl = trackAudioUrl(track);
  if (!audioUrl) {
    window.listeningState.usingSpeechFallback = true;
    syncAudioProgressUI();
    return;
  }

  window.listeningState.usingSpeechFallback = false;
  const audio = new Audio(audioUrl);
  audio.preload = 'metadata';
  audio.playbackRate = window.listeningState.playbackRate;

  audio.addEventListener('loadedmetadata', () => {
    if (audio.duration && isFinite(audio.duration) && audio.duration > 0) {
      window.listeningState.duration = audio.duration;
    }
    syncAudioProgressUI();
  });

  audio.addEventListener('timeupdate', () => {
    if (window.listeningState.usingSpeechFallback) return;
    window.listeningState.currentTime = audio.currentTime || 0;
    if (audio.duration && isFinite(audio.duration) && audio.duration > 0) {
      window.listeningState.duration = audio.duration;
    }
    syncAudioProgressUI();
  });

  audio.addEventListener('ended', () => {
    stopPlaybackTicker();
    window.listeningState.isPlaying = false;
    window.listeningState.currentTime = getEffectiveDuration();
    syncAudioProgressUI();
    updateAudioControlsUI(false);
    markAudioCompleted();
  });

  audio.addEventListener('error', () => {
    window.listeningState.usingSpeechFallback = true;
    syncAudioProgressUI();
  });

  window.listeningState.audio = audio;
}

function toggleAudioPlayback() {
  const k = aktifKurallar();
  if (window.listeningState.isPlaying) {
    // Sınav kuralı: not tutma modunda kayıt başladıktan sonra duraklatılamaz.
    if (!k.duraklatilabilir) {
      const statusEl = document.getElementById("audio-status-text");
      if (statusEl) statusEl.innerText = "Sınav kuralı: kayıt duraklatılamaz.";
      return;
    }
    pauseAudioPlayback();
  } else {
    startAudioPlayback();
  }
}

function startAudioPlayback() {
  const track = window.listeningState.currentTrack;
  if (!track) return;

  const k = aktifKurallar();
  // Sınav kuralı: kayıt yalnızca bir kez çalınır.
  if (k.tekDinleme && window.listeningState.playCount >= 1) {
    const statusEl = document.getElementById("audio-status-text");
    if (statusEl) {
      statusEl.innerText = window.listeningState.audioCompleted
        ? "Kayıt bir kez çalınır; tekrar dinlenemez."
        : "Kayıt zaten başladı; baştan alınamaz.";
    }
    return;
  }
  window.listeningState.playCount += 1;

  // Reset to 0 if previously finished
  const dur = getEffectiveDuration();
  if (window.listeningState.currentTime >= dur - 0.5) {
    window.listeningState.currentTime = 0;
    window.listeningState.speechCharOffset = 0;
    if (window.listeningState.audio) {
      try { window.listeningState.audio.currentTime = 0; } catch (_) {}
    }
  }

  const audio = window.listeningState.audio;
  if (!window.listeningState.usingSpeechFallback && audio && audio.src && !audio.error) {
    audio.playbackRate = window.listeningState.playbackRate;
    audio.play().then(() => {
      window.listeningState.usingSpeechFallback = false;
      window.listeningState.isPlaying = true;
      updateAudioControlsUI(true);
      startPlaybackTicker();
    }).catch(err => {
      console.warn("Audio play failed, falling back to speech synthesis:", err);
      window.listeningState.usingSpeechFallback = true;
      playAudioSynthesis();
    });
  } else {
    window.listeningState.usingSpeechFallback = true;
    playAudioSynthesis();
  }
}

function pauseAudioPlayback() {
  stopPlaybackTicker();
  if (window.listeningState.audio) {
    try { window.listeningState.audio.pause(); } catch (_) {}
  }
  if ('speechSynthesis' in window) {
    try { window.speechSynthesis.cancel(); } catch (_) {}
  }
  window.listeningState.isPlaying = false;
  updateAudioControlsUI(false);
  syncAudioProgressUI();
}

function stopAudioPlayback() {
  pauseAudioPlayback();
  if (window.listeningState.audio) {
    try {
      window.listeningState.audio.currentTime = 0;
    } catch (_) {}
  }
  window.listeningState.currentTime = 0;
  window.listeningState.speechCharOffset = 0;
  syncAudioProgressUI();
}

function onSeekSliderChange(percentVal) {
  // Sınav kuralı: not tutma modunda ileri-geri sarma yok.
  if (!aktifKurallar().sarmaSerbest) {
    syncAudioProgressUI();
    return;
  }
  const percent = Math.min(100, Math.max(0, parseFloat(percentVal) || 0));
  const dur = getEffectiveDuration();
  const targetTime = (percent / 100) * dur;
  window.listeningState.currentTime = targetTime;

  const audio = window.listeningState.audio;
  if (!window.listeningState.usingSpeechFallback && audio && !audio.error && audio.duration && isFinite(audio.duration)) {
    try {
      audio.currentTime = (percent / 100) * audio.duration;
    } catch (_) {}
  } else if (window.listeningState.currentTrack?.audio_script) {
    const script = window.listeningState.currentTrack.audio_script;
    window.listeningState.speechCharOffset = Math.floor((percent / 100) * script.length);
    if (window.listeningState.isPlaying) {
      playAudioSynthesis();
    }
  }

  syncAudioProgressUI();
}

function setAudioVolume(volVal) {
  const vol = parseFloat(volVal);
  if (window.listeningState.audio) {
    window.listeningState.audio.volume = vol;
  }
}

function setPlaybackRate(rate) {
  // Sınav kuralı: not tutma modunda hız sabittir.
  if (!aktifKurallar().hizDegisebilir) return;
  window.listeningState.playbackRate = rate;

  document.querySelectorAll(".rate-btn").forEach(b => {
    b.classList.remove("bg-blue-600", "text-white");
    b.classList.add("text-slate-400");
  });

  const rateKey = rate === 0.75 ? '075' : (rate === 1.0 ? '10' : '125');
  const targetBtn = document.getElementById(`rate-${rateKey}`);
  if (targetBtn) {
    targetBtn.classList.add("bg-blue-600", "text-white");
    targetBtn.classList.remove("text-slate-400");
  }

  if (window.listeningState.audio) {
    window.listeningState.audio.playbackRate = rate;
  }
  if (window.listeningState.usingSpeechFallback && window.listeningState.isPlaying) {
    playAudioSynthesis();
  }
}

function playAudioSynthesis() {
  const track = window.listeningState.currentTrack;
  if (!track || !('speechSynthesis' in window)) {
    alert("Tarayıcınız ses sentezini desteklemiyor veya parça seçilmedi.");
    return;
  }

  window.listeningState.usingSpeechFallback = true;
  stopPlaybackTicker();
  try { window.speechSynthesis.cancel(); } catch (_) {}

  const fullScript = track.audio_script || "";
  const dur = getEffectiveDuration();
  const ratio = dur > 0 ? Math.min(0.98, Math.max(0, (window.listeningState.currentTime || 0) / dur)) : 0;

  let startIdx = Math.floor(ratio * fullScript.length);
  if (startIdx > 0 && startIdx < fullScript.length) {
    const nextSpace = fullScript.indexOf(" ", startIdx);
    if (nextSpace !== -1 && nextSpace - startIdx < 25) {
      startIdx = nextSpace + 1;
    }
  }
  window.listeningState.speechCharOffset = startIdx;

  const remainingScript = fullScript.slice(startIdx).trim() || fullScript;
  const utterance = new SpeechSynthesisUtterance(remainingScript);
  utterance.lang = 'en-US';
  utterance.rate = window.listeningState.playbackRate || 1.0;

  const volInput = document.getElementById("audio-volume");
  if (volInput) {
    utterance.volume = parseFloat(volInput.value) || 1.0;
  }

  const voices = window.speechSynthesis.getVoices();
  const enVoice = voices.find(v => v.lang && v.lang.toLowerCase().startsWith('en')) || voices[0];
  if (enVoice) utterance.voice = enVoice;

  // Immediately activate UI and ticker so seconds count up smoothly
  window.listeningState.isPlaying = true;
  updateAudioControlsUI(true);
  syncAudioProgressUI();
  startPlaybackTicker();

  utterance.onstart = () => {
    window.listeningState.isPlaying = true;
    updateAudioControlsUI(true);
    if (!window.listeningState.speechTimer) {
      startPlaybackTicker();
    }
  };

  utterance.onboundary = (event) => {
    if (typeof event.charIndex === 'number' && fullScript.length > 0) {
      const absChar = Math.min(fullScript.length, startIdx + event.charIndex);
      window.listeningState.speechCharOffset = absChar;
    }
  };

  utterance.onend = () => {
    // Ignore onend caused by manual cancel/pause
    if (!window.listeningState.isPlaying) return;
    stopPlaybackTicker();
    window.listeningState.isPlaying = false;
    window.listeningState.currentTime = getEffectiveDuration();
    syncAudioProgressUI();
    updateAudioControlsUI(false);
    markAudioCompleted();
  };

  utterance.onerror = (e) => {
    if (e && (e.error === 'canceled' || e.error === 'interrupted')) return;
    console.warn("Speech synthesis warning:", e);
  };

  window.listeningState.speechUtterance = utterance;
  window.speechSynthesis.speak(utterance);
}

function updateAudioControlsUI(isPlaying) {
  const btn = document.getElementById("audio-play-btn");
  const statusEl = document.getElementById("audio-status-text");

  if (!btn) return;

  if (isPlaying) {
    btn.innerHTML = `<i data-lucide="pause" class="w-7 h-7"></i>`;
    btn.classList.add("bg-amber-600", "hover:bg-amber-500");
    btn.classList.remove("bg-blue-600", "hover:bg-blue-500");
    if (statusEl) statusEl.innerText = "▶ Oynatılıyor... Notlarınızı alın";
  } else {
    btn.innerHTML = `<i data-lucide="play" class="w-7 h-7"></i>`;
    btn.classList.remove("bg-amber-600", "hover:bg-amber-500");
    btn.classList.add("bg-blue-600", "hover:bg-blue-500");
    if (statusEl) statusEl.innerText = "Durduruldu / Tamamlandı";
  }

  if (window.lucide) window.lucide.createIcons();
}


async function submitListeningExam() {
  const track = window.listeningState.currentTrack;
  if (!track) return;

  stopAudioPlayback();

  let correctCount = 0;
  const total = track.questions.length;

  for (const q of track.questions) {
    const chosen = window.listeningState.answers[q.id];
    const isCorrect = chosen === q.correct_answer;
    if (isCorrect) correctCount++;

    // Çözümü şimdi yaz: sınav bitmeden doğru cevap DOM'a hiç girmez.
    const expEl = document.getElementById(`explanation-${q.id}`);
    if (expEl) {
      expEl.innerHTML = `<strong class="block mb-1 text-emerald-700">✓ Doğru Cevap: ${q.correct_answer}</strong>${q.explanation_tr || ""}`;
      expEl.classList.remove("hidden");
    }

    // Highlight choices
    q.options.forEach(opt => {
      const btn = document.getElementById(`opt-btn-${q.id}-${opt.key}`);
      if (!btn) return;
      btn.disabled = true;

      if (opt.key === q.correct_answer) {
        btn.classList.add("bg-emerald-600", "text-white", "border-emerald-600");
      } else if (opt.key === chosen && !isCorrect) {
        btn.classList.add("bg-rose-600", "text-white", "border-rose-600");
      }
    });

    // If wrong, register mistake in backend
    if (!isCorrect && chosen) {
      try {
        await fetch('/api/listening/answer', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question_id: q.id, chosen_answer: chosen })
        });
      } catch (e) {
        console.warn("Could not sync mistake:", e);
      }
    }
  }

  const score = Math.round((correctCount / total) * 100);
  const finishBtn = document.getElementById("finish-listening-btn");
  if (finishBtn) {
    finishBtn.disabled = true;
    finishBtn.innerHTML = `Tamamlandı • Sonuç: ${correctCount}/${total} (%${score})`;
    finishBtn.classList.remove("bg-emerald-600");
    finishBtn.classList.add("bg-slate-700");
  }

  alert(`Dinleme Sınavı Tamamlandı!\nDoğru: ${correctCount} / ${total}\nBaşarı Oranı: %${score}`);
}

window.loadListeningHub = loadListeningHub;
window.startListeningTrack = startListeningTrack;
window.exitListeningRunner = exitListeningRunner;
window.saveUserNotes = saveUserNotes;
window.loadUserNotes = loadUserNotes;
window.markAudioCompleted = markAudioCompleted;
window.listeningKurallari = listeningKurallari;
window.revealListeningQuestions = revealListeningQuestions;
window.selectListeningAnswer = selectListeningAnswer;
window.toggleAudioPlayback = toggleAudioPlayback;
window.startAudioPlayback = startAudioPlayback;
window.pauseAudioPlayback = pauseAudioPlayback;
window.stopAudioPlayback = stopAudioPlayback;
window.onSeekSliderChange = onSeekSliderChange;
window.setAudioVolume = setAudioVolume;
window.toggleAudioSynthesis = toggleAudioPlayback;
window.playAudioSynthesis = playAudioSynthesis;
window.stopAudioSynthesis = stopAudioPlayback;
window.setPlaybackRate = setPlaybackRate;
window.submitListeningExam = submitListeningExam;


