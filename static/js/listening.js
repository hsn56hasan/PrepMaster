// PrepMaster Listening Simulator (HTML5 Audio Engine & Web Speech API Fallback)

window.listeningState = {
  tracks: [],
  currentTrack: null,
  audio: null,
  speechUtterance: null,
  isPlaying: false,
  playbackRate: 1.0,
  duration: 0,
  currentTime: 0,
  userNotes: "",
  answers: {},
  questionsRevealed: false
};


async function loadListeningHub(targetLevel = null) {
  const container = document.getElementById("listening-tracks-list");
  const filterBar = document.getElementById("listening-filter-bar");
  if (!container) return;

  const currentLevel = window.appState?.currentLevel || 'B2';
  const activeLevel = targetLevel !== null ? targetLevel : currentLevel;

  // Render Level Filter Bar
  if (filterBar) {
    const levels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'];
    filterBar.innerHTML = `
      <span class="text-xs font-bold text-slate-500 mr-2 flex items-center gap-1">
        <i data-lucide="filter" class="w-3.5 h-3.5"></i> Kur Filtresi:
      </span>
      ${levels.map(lvl => {
        const isSelected = activeLevel === lvl;
        return `
          <button onclick="loadListeningHub('${lvl}')" class="px-3 py-1 rounded-xl text-xs font-bold transition ${isSelected ? 'bg-blue-600 text-white shadow-sm' : 'bg-white text-slate-600 hover:bg-slate-200 border border-slate-200'}">
            ${lvl} ${lvl === currentLevel ? '★' : ''}
          </button>
        `;
      }).join('')}
      <button onclick="loadListeningHub('all')" class="px-3 py-1 rounded-xl text-xs font-bold transition ${activeLevel === 'all' ? 'bg-slate-800 text-white shadow-sm' : 'bg-white text-slate-600 hover:bg-slate-200 border border-slate-200'}">
        Tüm Kurlar
      </button>
    `;
  }

  container.innerHTML = `
    <div class="col-span-full p-8 text-center text-slate-400">
      <i data-lucide="loader-2" class="w-6 h-6 animate-spin mx-auto mb-2 text-blue-600"></i>
      ${activeLevel === 'all' ? 'Tüm' : activeLevel} seviyesi dinleme sınavları yükleniyor...
    </div>
  `;
  if (window.lucide) window.lucide.createIcons();

  try {
    const url = activeLevel && activeLevel !== 'all' ? `/api/listening?level=${activeLevel}` : '/api/listening';
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

function startListeningTrack(trackId) {
  const track = window.listeningState.tracks.find(t => t.id === trackId);
  if (!track) return;

  stopAudioPlayback();

  window.listeningState.currentTrack = track;
  window.listeningState.answers = {};
  window.listeningState.userNotes = "";
  window.listeningState.questionsRevealed = track.type !== 'note_taking';
  window.listeningState.currentTime = 0;
  window.listeningState.duration = track.lecture_duration_seconds || 90;

  // Initialize Audio
  initTrackAudio(track);

  // Switch to Runner UI
  document.getElementById("listening-hub-view")?.classList.add("hidden");
  document.getElementById("listening-runner-view")?.classList.remove("hidden");

  renderListeningRunner();
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
            <div class="flex items-center gap-2">
              <span class="text-xs text-slate-400 font-semibold">Hız:</span>
              <div class="flex bg-slate-800/80 p-1 rounded-xl border border-slate-700">
                <button onclick="setPlaybackRate(0.75)" class="px-2.5 py-1 text-xs font-bold rounded-lg rate-btn hover:text-white text-slate-400 transition" id="rate-075">0.75x</button>
                <button onclick="setPlaybackRate(1.0)" class="px-2.5 py-1 text-xs font-bold rounded-lg rate-btn bg-blue-600 text-white transition" id="rate-10">1.0x</button>
                <button onclick="setPlaybackRate(1.25)" class="px-2.5 py-1 text-xs font-bold rounded-lg rate-btn hover:text-white text-slate-400 transition" id="rate-125">1.25x</button>
              </div>
            </div>

            <div class="flex items-center gap-2">
              <i data-lucide="volume-2" class="w-4 h-4 text-slate-400"></i>
              <input type="range" id="audio-volume" min="0" max="1" step="0.05" value="1" oninput="setAudioVolume(this.value)" class="w-16 sm:w-20 accent-blue-500 h-1.5 rounded-lg cursor-pointer bg-slate-700" title="Ses Seviyesi">
            </div>
          </div>
        </div>

        <!-- İlerleme / Seek Bar & Süre Göstergesi -->
        <div class="pt-2">
          <div class="flex items-center gap-3">
            <span id="audio-time-current" class="text-xs font-mono text-slate-300 w-10 text-right">00:00</span>
            <input type="range" id="audio-seek-slider" min="0" max="100" value="0" step="0.1" oninput="onSeekSliderChange(this.value)" class="flex-1 h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-blue-500">
            <span id="audio-time-duration" class="text-xs font-mono text-slate-400 w-10">01:30</span>
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
            <div class="p-6 bg-gradient-to-r from-amber-500/10 to-orange-500/10 border-2 border-dashed border-amber-300 rounded-2xl text-center space-y-3">
              <i data-lucide="lock" class="w-8 h-8 mx-auto text-amber-600"></i>
              <h4 class="text-sm font-extrabold text-amber-900">Sorular Şu Anda Gizli (Gerçek Sınav Kuralı)</h4>
              <p class="text-xs text-amber-800 max-w-md mx-auto">
                Boğaziçi ve ODTÜ gibi üniversitelerde dinleme bitene kadar soru kağıdı verilmez. Dinlemeyi tamamlayıp notlarınızı aldıktan sonra soruları açın.
              </p>
              <button onclick="revealListeningQuestions()" class="px-6 py-2.5 bg-amber-600 hover:bg-amber-700 text-white text-xs font-bold rounded-xl shadow-md transition flex items-center gap-2 mx-auto">
                <i data-lucide="unlock" class="w-4 h-4"></i> Dinlemeyi Bitir ve Soruları Yanıtla
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
                ${q.options.map(opt => `
                  <button onclick="selectListeningAnswer('${q.id}', '${opt.key}')" id="opt-btn-${q.id}-${opt.key}" class="p-3 text-left text-xs bg-white hover:bg-blue-50 border border-slate-200 rounded-xl transition flex items-center gap-2.5 opt-choice-${q.id}">
                    <span class="w-5 h-5 rounded-full border border-slate-300 font-bold flex items-center justify-center text-[10px] text-slate-500">${opt.key}</span>
                    <span class="text-slate-700 font-medium">${opt.text}</span>
                  </button>
                `).join('')}
              </div>

              <!-- Çözüm & Açıklama (Sınav bitince görünür) -->
              <div id="explanation-${q.id}" class="hidden p-3 bg-emerald-50 border border-emerald-200 text-emerald-900 text-xs rounded-xl mt-2 leading-relaxed">
                <strong class="block mb-1 text-emerald-700">✓ Doğru Cevap: ${q.correct_answer}</strong>
                ${q.explanation_tr}
              </div>
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
}

function revealListeningQuestions() {
  pauseAudioPlayback();
  window.listeningState.questionsRevealed = true;
  renderListeningRunner();
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

// --- REAL HTML5 AUDIO & MP3 STREAMING ENGINE ---
function formatAudioTime(seconds) {
  if (isNaN(seconds) || seconds < 0) return "00:00";
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins < 10 ? '0' : ''}${mins}:${secs < 10 ? '0' : ''}${secs}`;
}

function initTrackAudio(track) {
  if (window.listeningState.audio) {
    try {
      window.listeningState.audio.pause();
      window.listeningState.audio.src = '';
    } catch (_) {}
    window.listeningState.audio = null;
  }

  // Primary: MP3 file from static audio directory
  const audioUrl = `/static/audio/${track.id}.mp3`;
  const audio = new Audio(audioUrl);
  audio.preload = 'metadata';
  audio.playbackRate = window.listeningState.playbackRate;

  audio.addEventListener('loadedmetadata', () => {
    window.listeningState.duration = audio.duration;
    const durEl = document.getElementById("audio-time-duration");
    if (durEl) durEl.innerText = formatAudioTime(audio.duration);
  });

  audio.addEventListener('timeupdate', () => {
    if (!audio.duration) return;
    window.listeningState.currentTime = audio.currentTime;
    const curEl = document.getElementById("audio-time-current");
    const slider = document.getElementById("audio-seek-slider");
    if (curEl) curEl.innerText = formatAudioTime(audio.currentTime);
    if (slider) slider.value = (audio.currentTime / audio.duration) * 100;
  });

  audio.addEventListener('ended', () => {
    window.listeningState.isPlaying = false;
    updateAudioControlsUI(false);
  });

  audio.addEventListener('error', (e) => {
    console.warn("HTML5 audio playback error, falling back to Web Speech Synthesis:", e);
  });

  window.listeningState.audio = audio;
}

function toggleAudioPlayback() {
  if (window.listeningState.isPlaying) {
    pauseAudioPlayback();
  } else {
    startAudioPlayback();
  }
}

function startAudioPlayback() {
  const track = window.listeningState.currentTrack;
  if (!track) return;

  const audio = window.listeningState.audio;
  if (audio && audio.src && !audio.error) {
    audio.playbackRate = window.listeningState.playbackRate;
    audio.play().then(() => {
      window.listeningState.isPlaying = true;
      updateAudioControlsUI(true);
    }).catch(err => {
      console.warn("Audio play failed, falling back to speech synthesis:", err);
      playAudioSynthesis();
    });
  } else {
    playAudioSynthesis();
  }
}

function pauseAudioPlayback() {
  if (window.listeningState.audio) {
    try { window.listeningState.audio.pause(); } catch (_) {}
  }
  if ('speechSynthesis' in window) {
    try { window.speechSynthesis.cancel(); } catch (_) {}
  }
  window.listeningState.isPlaying = false;
  updateAudioControlsUI(false);
}

function stopAudioPlayback() {
  pauseAudioPlayback();
  if (window.listeningState.audio) {
    try {
      window.listeningState.audio.currentTime = 0;
    } catch (_) {}
  }
  window.listeningState.currentTime = 0;
  const curEl = document.getElementById("audio-time-current");
  const slider = document.getElementById("audio-seek-slider");
  if (curEl) curEl.innerText = "00:00";
  if (slider) slider.value = 0;
}

function onSeekSliderChange(percentVal) {
  const percent = parseFloat(percentVal);
  const audio = window.listeningState.audio;
  if (audio && audio.duration) {
    audio.currentTime = (percent / 100) * audio.duration;
    window.listeningState.currentTime = audio.currentTime;
    const curEl = document.getElementById("audio-time-current");
    if (curEl) curEl.innerText = formatAudioTime(audio.currentTime);
  }
}

function setAudioVolume(volVal) {
  const vol = parseFloat(volVal);
  if (window.listeningState.audio) {
    window.listeningState.audio.volume = vol;
  }
}

function setPlaybackRate(rate) {
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
  if (window.listeningState.speechUtterance && window.listeningState.isPlaying) {
    playAudioSynthesis();
  }
}

function playAudioSynthesis() {
  const track = window.listeningState.currentTrack;
  if (!track || !('speechSynthesis' in window)) {
    alert("Tarayıcınız ses sentezini desteklemiyor veya parça seçilmedi.");
    return;
  }

  window.speechSynthesis.cancel();

  const utterance = new SpeechSynthesisUtterance(track.audio_script);
  utterance.lang = 'en-US';
  utterance.rate = window.listeningState.playbackRate;

  const voices = window.speechSynthesis.getVoices();
  const enVoice = voices.find(v => v.lang.startsWith('en')) || voices[0];
  if (enVoice) utterance.voice = enVoice;

  utterance.onstart = () => {
    window.listeningState.isPlaying = true;
    updateAudioControlsUI(true);
  };

  utterance.onend = () => {
    window.listeningState.isPlaying = false;
    updateAudioControlsUI(false);
  };

  utterance.onerror = (e) => {
    console.error("Speech error:", e);
    window.listeningState.isPlaying = false;
    updateAudioControlsUI(false);
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

    // Reveal explanation
    const expEl = document.getElementById(`explanation-${q.id}`);
    if (expEl) expEl.classList.remove("hidden");

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
        await fetch('/api/exam/submit', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            university_id: track.university_id,
            level: track.level,
            duration_seconds: 60,
            answers: { [q.id]: chosen }
          })
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


