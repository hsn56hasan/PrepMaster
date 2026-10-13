// Flashcards Module for PrepMaster
let currentVocabList = [];
let currentVocabIndex = 0;
let isFlipped = false;

async function loadFlashcards(level = null) {
  try {
    const selectedLevel = level || window.appState.currentLevel || "all";
    const res = await fetch(`/api/vocabulary?level=${selectedLevel}`);
    currentVocabList = await res.json();
    currentVocabIndex = 0;
    isFlipped = false;
    renderFlashcardUI();
  } catch (err) {
    console.error("Error loading flashcards:", err);
  }
}

function renderFlashcardUI() {
  const container = document.getElementById("flashcard-container");
  const countBadge = document.getElementById("flashcard-progress-text");
  
  if (!container) return;
  
  if (currentVocabList.length === 0) {
    container.innerHTML = `
      <div class="p-8 text-center bg-white rounded-2xl shadow-sm border border-slate-200">
        <p class="text-slate-500 font-medium">Bu seviye için henüz kelime bulunamadı veya aramanızla eşleşmedi.</p>
      </div>
    `;
    if (countBadge) countBadge.innerText = "0 / 0";
    return;
  }

  const word = currentVocabList[currentVocabIndex];
  if (countBadge) {
    countBadge.innerText = `${currentVocabIndex + 1} / ${currentVocabList.length}`;
  }

  const isMastered = word.status === "mastered";

  container.innerHTML = `
    <div class="relative w-full max-w-xl mx-auto perspective-1000 min-h-[380px] cursor-pointer" onclick="flipFlashcard()">
      <div id="flashcard-inner" class="flashcard-inner relative w-full h-full transform-style-3d ${isFlipped ? 'flipped' : ''}">
        
        <!-- Ön Yüz (English) -->
        <div class="absolute inset-0 w-full min-h-[380px] bg-white rounded-3xl p-8 shadow-xl border border-slate-100 flex flex-col justify-between backface-hidden">
          <div class="flex items-center justify-between">
            <span class="px-3 py-1 text-xs font-bold rounded-full uppercase tracking-wider ${getLevelBadgeColor(word.level)}">
              ${word.level} Seviyesi
            </span>
            <div class="flex items-center space-x-2">
              <span class="text-xs text-slate-400 capitalize">${word.part_of_speech}</span>
              <button onclick="speakWord(event, '${word.word}')" title="Telaffuz Dinle" class="p-2 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded-full transition-colors">
                <i data-lucide="volume-2" class="w-5 h-5"></i>
              </button>
            </div>
          </div>

          <div class="text-center py-6">
            <h2 class="text-4xl font-extrabold text-slate-800 tracking-tight mb-2">${word.word}</h2>
            <p class="text-sm font-mono text-slate-400 mb-4">${word.pronunciation || ''}</p>
            <p class="text-sm text-slate-600 italic bg-slate-50 p-3 rounded-xl border border-slate-100">
              "${word.collocation || 'Akademik Bağlam'}"
            </p>
          </div>

          <div class="flex items-center justify-between text-xs text-slate-400 border-t border-slate-100 pt-4">
            <span class="flex items-center gap-1">
              <i data-lucide="rotate-cw" class="w-3.5 h-3.5"></i> Çevirmek için tıkla
            </span>
            <span class="${isMastered ? 'text-emerald-600 font-semibold flex items-center gap-1' : 'text-slate-400'}">
              ${isMastered ? '✓ Öğrenildi' : '○ Öğreniliyor'}
            </span>
          </div>
        </div>

        <!-- Arka Yüz (Turkish & Explanation) -->
        <div class="absolute inset-0 w-full min-h-[380px] bg-gradient-to-br from-blue-900 to-indigo-900 text-white rounded-3xl p-8 shadow-xl rotate-y-180 backface-hidden flex flex-col justify-between">
          <div class="flex items-center justify-between">
            <span class="px-3 py-1 text-xs font-bold bg-white/20 text-white rounded-full">
              Türkçe Anlam & Detay
            </span>
            <span class="text-xs text-blue-200 capitalize">${word.part_of_speech}</span>
          </div>

          <div class="py-4">
            <div class="text-2xl font-bold text-amber-300 mb-2">${word.meaning_tr}</div>
            <p class="text-xs text-blue-100 leading-relaxed mb-4">${word.definition_en}</p>
            
            <div class="bg-white/10 rounded-xl p-3 text-xs mb-3 border border-white/10">
              <span class="text-amber-200 font-semibold block mb-1">Örnek Cümle:</span>
              <p class="italic text-slate-100 font-serif">"${word.example_sentence}"</p>
            </div>

            ${word.synonyms && word.synonyms.length > 0 ? `
              <div class="text-xs text-blue-200">
                <span class="font-semibold text-white">Eş Anlamlılar:</span> ${word.synonyms.join(', ')}
              </div>
            ` : ''}
          </div>

          <div class="flex items-center justify-between text-xs text-blue-300 border-t border-white/10 pt-4">
            <span>Tekrar çevirmek için tıkla</span>
            <span class="font-mono">${word.word}</span>
          </div>
        </div>

      </div>
    </div>

    <!-- Kontrol Butonları -->
    <div class="flex items-center justify-center gap-4 mt-6">
      <button onclick="prevFlashcard()" class="p-3 bg-white hover:bg-slate-50 text-slate-700 rounded-full shadow border border-slate-200 transition">
        <i data-lucide="chevron-left" class="w-6 h-6"></i>
      </button>

      <button onclick="markWordStatus(event, 'learning')" class="px-5 py-2.5 bg-amber-50 hover:bg-amber-100 text-amber-700 font-semibold rounded-xl text-sm border border-amber-200 transition flex items-center gap-1.5">
        <i data-lucide="clock" class="w-4 h-4"></i> Tekrar Et
      </button>

      <button onclick="markWordStatus(event, 'mastered')" class="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold rounded-xl text-sm shadow-md transition flex items-center gap-1.5">
        <i data-lucide="check" class="w-4 h-4"></i> Öğrendim
      </button>

      <button onclick="nextFlashcard()" class="p-3 bg-white hover:bg-slate-50 text-slate-700 rounded-full shadow border border-slate-200 transition">
        <i data-lucide="chevron-right" class="w-6 h-6"></i>
      </button>
    </div>
  `;

  if (window.lucide) {
    window.lucide.createIcons();
  }
}

function flipFlashcard() {
  isFlipped = !isFlipped;
  const card = document.getElementById("flashcard-inner");
  if (card) {
    if (isFlipped) card.classList.add("flipped");
    else card.classList.remove("flipped");
  }
}

function nextFlashcard() {
  if (currentVocabList.length === 0) return;
  currentVocabIndex = (currentVocabIndex + 1) % currentVocabList.length;
  isFlipped = false;
  renderFlashcardUI();
}

function prevFlashcard() {
  if (currentVocabList.length === 0) return;
  currentVocabIndex = (currentVocabIndex - 1 + currentVocabList.length) % currentVocabList.length;
  isFlipped = false;
  renderFlashcardUI();
}

function speakWord(event, text) {
  if (event) event.stopPropagation();
  if ('speechSynthesis' in window) {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'en-US';
    utterance.rate = 0.9;
    window.speechSynthesis.speak(utterance);
  }
}

async function markWordStatus(event, status) {
  if (event) event.stopPropagation();
  if (currentVocabList.length === 0) return;
  const word = currentVocabList[currentVocabIndex];
  
  try {
    await fetch(`/api/vocabulary/${word.id}/status`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status })
    });
    word.status = status;
    nextFlashcard();
  } catch (err) {
    console.error("Failed to update status:", err);
  }
}

function getLevelBadgeColor(level) {
  switch (level) {
    case 'A1': return 'bg-emerald-100 text-emerald-800';
    case 'A2': return 'bg-teal-100 text-teal-800';
    case 'B1': return 'bg-blue-100 text-blue-800';
    case 'B2': return 'bg-indigo-100 text-indigo-800';
    case 'C1': return 'bg-purple-100 text-purple-800';
    case 'C2': return 'bg-rose-100 text-rose-800';
    default: return 'bg-slate-100 text-slate-800';
  }
}

window.loadFlashcards = loadFlashcards;
window.flipFlashcard = flipFlashcard;
window.nextFlashcard = nextFlashcard;
window.prevFlashcard = prevFlashcard;
window.speakWord = speakWord;
window.markWordStatus = markWordStatus;
