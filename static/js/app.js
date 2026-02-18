/**
 * AI CAD Architect — Frontend Logic
 * Handles: Voice recording, Image preview, API calls, State management, History
 */

// ========== DOM Elements ==========
const textInput = document.getElementById('textInput');
const recordBtn = document.getElementById('recordBtn');
const micIcon = document.getElementById('micIcon');
const recordText = document.getElementById('recordText');
const imageInput = document.getElementById('imageInput');
const imagePreviewContainer = document.getElementById('imagePreviewContainer');
const imgPreview = document.getElementById('imgPreview');
const imgName = document.getElementById('imgName');
const generateBtn = document.getElementById('generateBtn');

// States
const emptyState = document.getElementById('emptyState');
const loadingState = document.getElementById('loadingState');
const successState = document.getElementById('successState');
const loadingText = document.getElementById('loadingText');

// Results
const paramsTable = document.getElementById('paramsTable');
const downloadBtn = document.getElementById('downloadBtn');
const svgContainer = document.getElementById('svgPreviewArea');

// History
const historyList = document.getElementById('historyList');
const historyEmpty = document.getElementById('historyEmpty');
const historyCount = document.getElementById('historyCount');

// Audio recording
let mediaRecorder;
let audioChunks = [];
let audioBlob = null;

// ========== Voice Recording ==========
recordBtn.addEventListener('mousedown', startRec);
recordBtn.addEventListener('touchstart', (e) => { e.preventDefault(); startRec(); });
window.addEventListener('mouseup', stopRec);
window.addEventListener('touchend', stopRec);

async function startRec() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
        mediaRecorder.onstop = () => {
            audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            micIcon.className = "w-12 h-12 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center text-xl mb-2 transition-colors";
            recordText.innerText = "Suara Tersimpan ✓";
            recordBtn.classList.add('border-emerald-200', 'bg-emerald-50/10');
            stream.getTracks().forEach(track => track.stop());
        };

        mediaRecorder.start();
        micIcon.className = "w-12 h-12 bg-red-500 text-white rounded-full flex items-center justify-center text-xl mb-2 recording-pulse z-10";
        recordText.innerText = "Merekam...";

    } catch (err) {
        showToast("Butuh akses mikrofon untuk merekam.", "error");
    }
}

function stopRec() {
    if (mediaRecorder && mediaRecorder.state === "recording") {
        mediaRecorder.stop();
    }
}

// ========== Image Preview ==========
function handleImagePreview(input) {
    if (input.files && input.files[0]) {
        const file = input.files[0];
        if (file.size > 5 * 1024 * 1024) {
            showToast("Ukuran gambar maksimal 5MB.", "error");
            input.value = "";
            return;
        }
        const reader = new FileReader();
        reader.onload = function (e) {
            imgPreview.src = e.target.result;
            imgName.innerText = file.name;
            imagePreviewContainer.classList.remove('hidden');
        }
        reader.readAsDataURL(file);
    }
}

function clearImage() {
    imageInput.value = "";
    imagePreviewContainer.classList.add('hidden');
}

// ========== Clear All Inputs ==========
function clearAllInputs() {
    // Clear text
    textInput.value = '';

    // Clear audio
    audioBlob = null;
    audioChunks = [];
    micIcon.className = "w-12 h-12 bg-indigo-500/20 text-brand-400 rounded-full flex items-center justify-center text-xl mb-2 group-hover:scale-110 transition-transform";
    recordText.innerText = "Tahan untuk Bicara";
    recordBtn.classList.remove('border-emerald-200', 'bg-emerald-50/10');

    // Clear image
    clearImage();
}

// ========== API & State Management ==========
async function generateCAD() {
    const hasText = textInput.value.trim().length > 0;
    const hasAudio = audioBlob !== null;
    const hasImage = imageInput.files && imageInput.files[0];

    if (!hasText && !hasAudio && !hasImage) {
        showToast("Berikan minimal satu input: teks, suara, atau gambar.", "error");
        return;
    }

    setUIState('loading');

    const steps = [
        "Memproses input...",
        "Menganalisis dengan AI...",
        "Ekstraksi parameter geometri...",
        "Membuat DXF blueprint...",
        "Merender preview...",
    ];
    let stepIdx = 0;
    const stepInterval = setInterval(() => {
        stepIdx = Math.min(stepIdx + 1, steps.length - 1);
        loadingText.innerText = steps[stepIdx];
    }, 1500);

    const formData = new FormData();
    if (hasText) formData.append('text_prompt', textInput.value);
    if (hasAudio) formData.append('audio_file', audioBlob, 'recording.wav');
    if (hasImage) formData.append('image_file', imageInput.files[0]);

    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        clearInterval(stepInterval);

        if (result.status === 'success') {
            // Clear all inputs AFTER successful generation
            clearAllInputs();
            showSuccess(result, 'generate');
            loadHistory();   // refresh history panel
        } else {
            showToast('Gagal: ' + (result.message || 'Unknown error'), 'error');
            setUIState('empty');
        }
    } catch (error) {
        clearInterval(stepInterval);
        console.error(error);
        showToast('Terjadi kesalahan jaringan.', 'error');
        setUIState('empty');
    }
}

function showSuccess(result, source = 'generate') {
    setUIState('success');

    paramsTable.innerHTML = '';
    for (const [key, value] of Object.entries(result.data)) {
        if (key === 'description') continue;
        if (value === null || value === undefined) continue;

        let displayValue = value;
        if (Array.isArray(value)) {
            displayValue = value.map(v =>
                typeof v === 'object' ? `${v.wall}: ${v.width}cm` : v
            ).join(', ');
        }

        const row = `
            <tr class="border-b border-slate-100/10 last:border-0">
                <td class="py-2 font-semibold capitalize text-slate-400">${key.replace(/_/g, ' ')}</td>
                <td class="py-2 text-right font-bold text-slate-200">${displayValue}</td>
            </tr>
        `;
        paramsTable.innerHTML += row;
    }

    if (result.data.description) {
        document.getElementById('resultDescription').innerText = result.data.description;
        document.getElementById('resultDescription').classList.remove('hidden');
    }

    downloadBtn.href = result.download_url;
    downloadBtn.setAttribute('download', '');

    if (result.svg_preview && svgContainer) {
        svgContainer.innerHTML = result.svg_preview;
    }

    window._currentDxfFile = result.download_url.split('/').pop();

    if (source === 'generate') {
        showToast('CAD Blueprint berhasil dibuat!', 'success');
    } else if (source === 'history') {
        showToast('History loaded', 'info');
    }
}

async function export3D() {
    if (!window._currentDxfFile) {
        showToast('Generate CAD terlebih dahulu.', 'error');
        return;
    }

    const btn = document.getElementById('export3dBtn');
    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-spinner animate-spin mr-2"></i>Exporting...';

    try {
        const response = await fetch(`/api/export-3d/${window._currentDxfFile}`, { method: 'POST' });
        const result = await response.json();

        if (result.status === 'success') {
            const a = document.createElement('a');
            a.href = result.download_url;
            a.download = '';
            a.click();
            showToast('File STL berhasil di-export!', 'success');
        } else {
            showToast('3D export gagal: ' + result.message, 'error');
        }
    } catch (error) {
        showToast('Gagal export 3D.', 'error');
    }

    btn.disabled = false;
    btn.innerHTML = '<i class="fa-solid fa-cube mr-2"></i>Export 3D (STL)';
}

// ========== UI State Management ==========
function setUIState(state) {
    emptyState.classList.add('hidden');
    loadingState.classList.add('hidden');
    successState.classList.add('hidden');

    if (state === 'empty') {
        emptyState.classList.remove('hidden');
        generateBtn.disabled = false;
        generateBtn.classList.remove('opacity-50', 'cursor-not-allowed');
    } else if (state === 'loading') {
        loadingState.classList.remove('hidden');
        loadingText.innerText = 'Memproses input...';
        generateBtn.disabled = true;
        generateBtn.classList.add('opacity-50', 'cursor-not-allowed');
    } else if (state === 'success') {
        successState.classList.remove('hidden');
        generateBtn.disabled = false;
        generateBtn.classList.remove('opacity-50', 'cursor-not-allowed');
    }
}

function resetUI() {
    setUIState('empty');
    clearAllInputs();
    if (svgContainer) svgContainer.innerHTML = '';
}

// ========== History Panel ==========
async function loadHistory() {
    try {
        const res = await fetch('/api/history');
        const result = await res.json();

        if (result.status !== 'success') return;

        const entries = result.data;
        historyCount.innerText = entries.length;

        if (entries.length === 0) {
            historyEmpty.classList.remove('hidden');
            historyList.innerHTML = '';
            return;
        }

        historyEmpty.classList.add('hidden');
        historyList.innerHTML = entries.map(entry => {
            const date = new Date(entry.created_at).toLocaleString('id-ID', {
                day: '2-digit', month: 'short', year: 'numeric',
                hour: '2-digit', minute: '2-digit'
            });
            const shape = entry.params?.shape_type || 'unknown';
            const prompt = (entry.prompt || '').substring(0, 60) + (entry.prompt?.length > 60 ? '...' : '');

            return `
                <div class="group bg-slate-800/50 border border-slate-700/50 rounded-xl p-3 hover:border-brand-500/40 transition-all cursor-pointer" onclick="viewHistoryEntry('${entry.id}')">
                    <div class="flex justify-between items-start">
                        <div class="flex-1 min-w-0">
                            <div class="flex items-center gap-2 mb-1">
                                <span class="text-[10px] uppercase tracking-wider font-bold text-brand-400 bg-brand-500/10 px-2 py-0.5 rounded">${shape}</span>
                                <span class="text-[10px] text-slate-600">${date}</span>
                            </div>
                            <p class="text-xs text-slate-400 truncate">${prompt}</p>
                        </div>
                        <button onclick="event.stopPropagation(); deleteHistoryEntry('${entry.id}')" class="opacity-0 group-hover:opacity-100 text-red-400 hover:bg-red-500/20 p-1.5 rounded-lg transition-all ml-2" title="Hapus">
                            <i class="fa-solid fa-trash-can text-xs"></i>
                        </button>
                    </div>
                </div>
            `;
        }).join('');

    } catch (err) {
        console.error('Failed to load history:', err);
    }
}

async function viewHistoryEntry(id) {
    try {
        const res = await fetch(`/api/history/${id}`);
        const result = await res.json();

        if (result.status !== 'success') return;

        const entry = result.data;

        // Show the result in the result panel
        showSuccess({
            data: entry.params,
            download_url: `/download/${entry.dxf_filename}`,
            svg_preview: entry.svg_preview || '',
        }, 'history');
    } catch (err) {
        showToast('Gagal memuat history.', 'error');
    }
}

// ========== Delete Modal ==========
let _pendingDeleteId = null;   // null = clear all, string = single entry id

function openDeleteModal(title, message, entryId = null) {
    _pendingDeleteId = entryId;
    document.getElementById('deleteModalTitle').innerText = title;
    document.getElementById('deleteModalMsg').innerText = message;
    const modal = document.getElementById('deleteModal');
    modal.classList.remove('hidden');
    modal.classList.add('flex');
}

function closeDeleteModal() {
    const modal = document.getElementById('deleteModal');
    modal.classList.add('hidden');
    modal.classList.remove('flex');
    _pendingDeleteId = null;
}

async function confirmDelete() {
    const targetId = _pendingDeleteId;  // save before close nulls it
    closeDeleteModal();

    if (targetId === '__clear_all__') {
        // Clear all history
        try {
            const res = await fetch('/api/history', { method: 'DELETE' });
            const result = await res.json();
            showToast(result.message, 'info');
            loadHistory();
        } catch (err) {
            showToast('Gagal menghapus history.', 'error');
        }
    } else if (targetId) {
        // Delete single entry
        try {
            const res = await fetch(`/api/history/${targetId}`, { method: 'DELETE' });
            const result = await res.json();
            if (result.status === 'success') {
                showToast('Entry dihapus.', 'info');
                loadHistory();
            }
        } catch (err) {
            showToast('Gagal menghapus.', 'error');
        }
    }
}

function deleteHistoryEntry(id) {
    openDeleteModal(
        'Hapus Entry?',
        'Entry ini akan dihapus permanen dan tidak dapat dikembalikan.',
        id
    );
}

function clearAllHistory() {
    openDeleteModal(
        'Hapus Semua History?',
        'Seluruh history akan dihapus permanen. Tindakan ini tidak dapat dibatalkan.',
        '__clear_all__'
    );
}

// ========== Toast Notifications ==========
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerText = message;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.3s';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ========== Init ==========
document.addEventListener('DOMContentLoaded', () => {
    loadHistory();
});
