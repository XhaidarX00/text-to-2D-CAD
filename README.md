# 📐 AI CAD Architect — Text to CAD Engineering Platform

> Mengubah deskripsi teks, suara, dan sketsa menjadi gambar teknis CAD 2D (DXF/SVG) dengan bonus 3D Export (STL), didukung oleh AI Generatif.

---

## 📋 Daftar Isi

- [Tentang Project](#-tentang-project)
- [Pemenuhan Requirement Task](#-pemenuhan-requirement-task)
- [Daftar Improvisasi](#-daftar-improvisasi)
- [Arsitektur & Teknologi](#-arsitektur--teknologi)
- [Instalasi & Setup](#-instalasi--setup)
- [Cara Penggunaan](#-cara-penggunaan)
- [Contoh Output](#-contoh-output)
- [API Endpoints](#-api-endpoints)
- [Unit Testing](#-unit-testing)
- [Struktur Project](#-struktur-project)
- [Asumsi & Simplifikasi](#-asumsi--simplifikasi)
- [Lisensi](#-lisensi)

---

## 📖 Tentang Project

Project ini dibuat sebagai **Test Kandidat Python Engineer** yang diminta oleh HRD. Task asli meminta pembuatan program Python yang mampu mengkonversi deskripsi teks menjadi output desain 2D CAD (tampak atas & tampak depan) dalam format DXF/SVG, dengan bonus 3D export.

Saya menambahkan **tampak samping** (side view) sebagai proyeksi ortografik ketiga yang menjadi standar dalam gambar teknik profesional.

Saya mengambil pendekatan **full-stack engineering** — tidak hanya memenuhi requirement minimum, tetapi juga mengimprovisasi seluruh pipeline menjadi platform berbasis web yang production-ready dengan integrasi AI generatif.

---

## ✅ Pemenuhan Requirement Task

Berikut adalah daftar **requirement asli** dari `Test Kandidat Python Engineer.txt` dan status pemenuhannya:

| No | Requirement Asli | Status | Implementasi |
|----|-----------------|--------|-------------|
| 1 | **Input teks deskripsi** → menghasilkan CAD | ✅ Terpenuhi | User mengetik deskripsi di textarea, AI mengekstrak parameter geometri |
| 2 | **Output file DXF** berisi tampak atas + tampak depan | ✅ Terpenuhi+ | Menggunakan `ezdxf` — setiap shape punya `draw_top_view()` + `draw_front_view()` + **`draw_side_view()`** (improvisasi) pada layer terpisah |
| 3 | **Output file SVG** | ✅ Terpenuhi | DXF di-convert ke SVG untuk preview browser melalui `svg_exporter.py` |
| 4 | **Kursi**: kotak (dudukan) + titik kaki tampak atas, dudukan + 4 kaki tampak depan | ✅ Terpenuhi | `ChairShape` — seat rectangle + 4 circle kaki (top), backrest + seat + legs (front) |
| 5 | **Ruangan**: persegi panjang 4×5 dengan simbol pintu/jendela | ✅ Terpenuhi | `RoomShape` — wall outline + door arc 90° + window triple-line (top), wall elevation + openings (front) |
| 6 | **Bonus 3D**: ekstrusi 2D → model 3D (STL/OBJ) | ✅ Terpenuhi | `exporter_3d.py` — box, cylinder, dan chair mesh menggunakan `trimesh` → STL export |
| 7 | **Library**: ezdxf, svgwrite, trimesh, numpy-stl | ✅ Dipakai | Semua library yang disarankan terinstall di `requirements.txt` |
| 8 | **README** dengan penjelasan asumsi/simplifikasi | ✅ Terpenuhi | Dokumen ini |
| 9 | **Source code** upload ke GitHub | ✅ Siap | `.gitignore` sudah dikonfigurasi |

---

## 🚀 Daftar Improvisasi

Berikut adalah fitur-fitur tambahan yang melampaui requirement asli, beserta **alasan teknis** dan **kelebihannya**:

---

### 1. 🤖 Integrasi AI Generatif (Groq LLM)

| Aspek | Task Asli | Improvisasi |
|-------|----------|-------------|
| **Parsing input** | Manual / hardcoded | AI LLM (Llama 3.3 70B) mengekstrak parameter otomatis dari natural language |
| **Format output AI** | Tidak ada | JSON terstruktur dengan schema yang ketat |
| **Streaming** | Tidak ada | Response streaming untuk feedback real-time |

**Alasan:** Task asli hanya meminta "deskripsi teks" sebagai input, tetapi tidak mendefinisikan cara parsing. Dengan LLM, user bisa menulis dalam bahasa alami (Indonesia/Inggris) tanpa format khusus. AI mengenali objek, dimensi, dan properti secara otomatis.

**Kelebihan:**
- User tidak perlu belajar format input khusus
- Mendukung variasi bahasa (e.g., "kursi", "chair", "bangku" semuanya dipahami)
- Parameter default mengikuti standar ergonomi jika user tidak menyebut ukuran
- Streaming response memberikan feedback cepat ke user

**File terkait:** `app/services/reasoning_service.py`

---

### 2. 🎤 Voice Input (Speech-to-Text)

| Aspek | Task Asli | Improvisasi |
|-------|----------|-------------|
| **Input** | Teks saja | Teks + Suara (Whisper Large v3 Turbo) |

**Alasan:** Dalam workflow desain nyata, arsitek/engineer sering mendiktekan instruksi. Voice input mempercepat proses dan membuat aplikasi lebih accessible.

**Kelebihan:**
- Push-to-talk UX yang intuitif (tahan tombol, bicara, lepas)
- Transkripsi menggunakan Whisper Large v3 Turbo — akurasi tinggi untuk Bahasa Indonesia
- Hasil transkripsi langsung diteruskan ke LLM untuk ekstraksi parameter
- Zero-configuration: tidak perlu install engine STT lokal

**File terkait:** `app/services/audio_service.py`

---

### 3. 📷 Image/Sketch Input (AI Vision)

| Aspek | Task Asli | Improvisasi |
|-------|----------|-------------|
| **Input** | Teks saja | Teks + Suara + Gambar/Sketsa (Llama 4 Scout Vision) |

**Alasan:** Banyak desain berawal dari coretan tangan. Dengan vision AI, user bisa upload foto sketsa dan AI akan menganalisis objek serta dimensinya.

**Kelebihan:**
- Multimodal: mendukung JPEG, PNG, WebP
- AI mengidentifikasi tipe objek, estimasi dimensi, dan detail konstruksi
- Dapat dikombinasikan dengan input teks (e.g., upload sketsa + tambah catatan tertulis)
- Tidak butuh OCR engine terpisah — semua dalam satu API call

**File terkait:** `app/services/vision_service.py`

---

### 4. 🌐 Web-Based UI (FastAPI + Tailwind CSS)

| Aspek | Task Asli | Improvisasi |
|-------|----------|-------------|
| **Interface** | CLI / script | Full web application (FastAPI + Jinja2 + Tailwind) |
| **Interaksi** | Jalankan script | Browser-based, multi-modal input |
| **Preview** | Buka file DXF di software CAD | SVG preview langsung di browser |

**Alasan:** Task asli hanya meminta "program Python", tetapi sebuah web app jauh lebih user-friendly, demo-able, dan production-ready.

**Kelebihan:**
- Dark-mode UI premium dengan glassmorphism, gradient, dan micro-animations
- 3-state management (Idle → Processing → Result) dengan loading progress steps
- SVG preview menampilkan gambar CAD langsung di browser tanpa perlu software CAD
- Responsive layout (desktop + mobile)
- Toast notification system untuk feedback user

**File terkait:** `main.py`, `templates/index.html`, `static/css/custom.css`, `static/js/app.js`

---

### 5. 📦 Multi-Shape Factory Pattern

| Aspek | Task Asli | Improvisasi |
|-------|----------|-------------|
| **Shape** | Kursi dan Ruangan | Box, Cylinder, Chair, Room (4 shape + extensible) |
| **Arsitektur** | Tidak dispesifikasi | Factory + Registry Pattern, Open-Closed Principle |

**Alasan:** Menggunakan abstract base class + factory pattern memudahkan penambahan shape baru tanpa mengubah kode yang sudah ada (SOLID principles).

**Kelebihan:**
- `CADObject` abstract base class dengan standar layer (TOP_VIEW, FRONT_VIEW, SIDE_VIEW, DIMENSIONS, ANNOTATIONS, CENTER_LINES)
- Factory dengan alias registry — mendukung nama Indonesia: "kursi" → ChairShape, "ruangan" → RoomShape, dll
- Dimension lines otomatis pada setiap shape
- Extensible: tambah shape baru cukup buat class + register di factory

**File terkait:** `app/cad_engine/base.py`, `app/cad_engine/shapes.py`, `app/cad_engine/advanced_shapes.py`, `app/cad_engine/factory.py`

---

### 6. 📊 History Database (JSON CRUD)

| Aspek | Task Asli | Improvisasi |
|-------|----------|-------------|
| **Penyimpanan** | Tidak ada | JSON file database dengan CRUD API |
| **Riwayat** | Tidak ada | Seluruh history generate tersimpan, dapat di-load ulang |

**Alasan:** Dalam workflow nyata, engineer perlu melacak iterasi desain. History memungkinkan revisit, bandingkan, dan kelola hasil generate.

**Kelebihan:**
- Auto-save setelah setiap generate (prompt, params, DXF filename, SVG preview)
- Full REST API: GET (list/detail), PUT (edit), DELETE (single/clear all)
- History panel di UI — klik untuk load ulang hasil, hover untuk hapus
- Data persisten di `history.json`

**File terkait:** `app/services/history_service.py`, `main.py` (5 CRUD endpoints)

---

### 7. 🧊 3D Export dengan Chair Mesh

| Aspek | Task Asli | Improvisasi |
|-------|----------|-------------|
| **3D** | Bonus — ekstrusi sederhana | Box + Cylinder + Chair mesh (multi-part composite) |
| **Library** | trimesh | trimesh.creation primitives (tanpa dependency triangulation tambahan) |

**Alasan:** Task hanya meminta ekstrusi sederhana. Kami membuat chair mesh dari 6 box primitives (seat + 4 legs + backrest) untuk demonstrasi yang lebih mengesankan.

**Kelebihan:**
- Tidak butuh `mapbox-earcut` atau triangulation engine — menggunakan trimesh built-in primitives
- Chair mesh: seat plate + 4 kaki + backrest sebagai composite mesh
- Dimensi mengikuti parameter yang sama dengan 2D (konsisten)

**File terkait:** `app/cad_engine/exporter_3d.py`

---

### 8. 🧪 Unit Testing

| Aspek | Task Asli | Improvisasi |
|-------|----------|-------------|
| **Testing** | Tidak diminta | 20+ unit tests dengan pytest |

**Alasan:** Testing adalah standar profesional yang menunjukkan kualitas kode dan memudahkan maintenance.

**Kelebihan:**
- Test coverage: BoxShape, CylinderShape, ChairShape, RoomShape
- Factory tests: registry, aliases (kursi → chair), unknown fallback
- SVG exporter tests: DXF → SVG conversion validation
- Semua test dapat dijalankan offline tanpa API key

**File terkait:** `tests/test_cad_engine.py`

---

## 🏗 Arsitektur & Teknologi

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Browser)                     │
│        Tailwind CSS + Vanilla JS + Jinja2 Templates      │
├─────────────────────────────────────────────────────────┤
│                    FastAPI Backend                        │
│            main.py — Routes + API Endpoints              │
├───────────────┬──────────────┬──────────────────────────┤
│   AI Services │  CAD Engine  │     History Service       │
│ ┌───────────┐ │ ┌──────────┐ │  ┌────────────────────┐  │
│ │ Reasoning │ │ │  Shapes  │ │  │  JSON CRUD         │  │
│ │ (Llama3.3)│ │ │ (Box,Cyl)│ │  │  (history.json)    │  │
│ ├───────────┤ │ ├──────────┤ │  └────────────────────┘  │
│ │   Audio   │ │ │ Advanced │ │                          │
│ │ (Whisper) │ │ │(Chair,   │ │                          │
│ ├───────────┤ │ │ Room)    │ │                          │
│ │  Vision   │ │ ├──────────┤ │                          │
│ │(Llama4    │ │ │ Factory  │ │                          │
│ │ Scout)    │ │ ├──────────┤ │                          │
│ └───────────┘ │ │SVG Export│ │                          │
│               │ ├──────────┤ │                          │
│               │ │3D Export │ │                          │
│               │ └──────────┘ │                          │
├───────────────┴──────────────┴──────────────────────────┤
│                  Groq Cloud API                          │
│     Llama 3.3 70B · Llama 4 Scout · Whisper v3 Turbo    │
└─────────────────────────────────────────────────────────┘
```

| Layer | Teknologi | Keterangan |
|-------|-----------|-----------|
| Backend | FastAPI + Uvicorn | Async web framework, auto-docs di `/docs` |
| AI — Text | Groq + Llama 3.3 70B | Streaming, JSON mode, parameter extraction |
| AI — Vision | Groq + Llama 4 Scout 17B | Multimodal image analysis |
| AI — Audio | Groq + Whisper Large v3 Turbo | Speech-to-text, verbose JSON |
| CAD Engine | ezdxf (DXF) | R2010 format, multi-layer, dimension lines |
| SVG Preview | Custom converter | DXF → SVG with dark theme, auto-scale |
| 3D Engine | trimesh | Box/cylinder/chair primitives → STL |
| Frontend | Tailwind CSS + Vanilla JS | Dark mode, animations, responsive |
| Database | JSON file | Lightweight, zero-config, persistent |
| Testing | pytest | 20+ unit tests, offline-capable |

---

## ⚙ Instalasi & Setup

### Prasyarat

- Python 3.10+
- Groq API Key (gratis di [console.groq.com](https://console.groq.com))

### Langkah 1: Clone Repository

```bash
git clone https://github.com/<username>/ai-cad-architect.git
cd ai-cad-architect
```

### Langkah 2: Buat Virtual Environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

### Langkah 3: Install Dependencies

```bash
pip install -r requirements.txt
```

Dependencies yang akan terinstall:
```
fastapi          - Web framework
uvicorn          - ASGI server
python-multipart - File upload handling
jinja2           - HTML templating
groq             - AI API client
ezdxf            - DXF file generation
svgwrite         - SVG file generation (available)
trimesh          - 3D mesh creation
numpy-stl        - STL export support
numpy            - Numerical operations
pydantic         - Data validation
Pillow           - Image processing
python-dotenv    - Environment config
pytest           - Unit testing
httpx            - HTTP client for tests
```

### Langkah 4: Konfigurasi API Key

Edit file `.env` di root project:

```env
GROQ_API_KEY=gsk_your_actual_api_key_here
```

> **Cara mendapatkan API Key:**
> 1. Buka [console.groq.com](https://console.groq.com)
> 2. Register/Login
> 3. Buka menu "API Keys"
> 4. Klik "Create API Key"
> 5. Copy dan paste ke `.env`

### Langkah 5: Jalankan Server

```bash
python main.py
```

Server akan berjalan di: **http://localhost:8000**

---

## 🎯 Cara Penggunaan

### Mode 1: Input Teks

1. Buka **http://localhost:8000** di browser
2. Ketik deskripsi objek di textarea:
   - `"Kursi dengan 4 kaki, dudukan persegi 40x40 cm, tinggi 45 cm"`
   - `"Ruangan ukuran 4x5 meter, dengan 1 pintu di sisi barat dan 1 jendela di sisi utara"`
   - `"Meja kerja 120x60 cm tinggi 75 cm"`
   - `"Silinder diameter 30cm tinggi 50cm"`
3. Klik **Generate CAD Blueprint**
4. Lihat preview SVG, download DXF, atau export 3D STL

### Mode 2: Input Suara

1. Tekan dan **tahan** tombol mikrofon 🎤
2. Ucapkan deskripsi objek (dalam Bahasa Indonesia atau Inggris)
3. Lepas tombol — audio akan ditranskripsikan otomatis
4. Klik **Generate CAD Blueprint**

### Mode 3: Input Gambar/Sketsa

1. Klik tombol kamera 📷
2. Pilih foto atau sketsa objek (max 5MB)
3. AI Vision akan menganalisis gambar secara otomatis
4. Klik **Generate CAD Blueprint**

### Mode 4: Kombinasi

Anda dapat mengkombinasikan beberapa input sekaligus:
- Ketik teks + rekam suara
- Upload gambar + tambah catatan teks
- Ketiga input sekaligus

AI akan menggabungkan seluruh informasi sebagai konteks untuk menghasilkan parameter CAD yang lebih akurat.

### Download & Export

- **Download DXF** — File CAD yang dapat dibuka di AutoCAD, FreeCAD, atau LibreCAD
- **Export 3D (STL)** — Model 3D yang dapat dibuka di Blender, PrusaSlicer, atau 3D viewer lainnya
- **SVG Preview** — Ditampilkan langsung di browser

### History

- Setiap hasil generate otomatis tersimpan di panel **History** (bagian bawah halaman)
- Klik entry history untuk memuat ulang hasilnya
- Hover entry untuk tombol hapus → muncul **confirmation modal** sebelum menghapus
- Tombol **Hapus Semua** → modal konfirmasi dengan pesan berbeda
- Modal dark-themed dengan backdrop blur dan tombol Batal/Hapus

---

## 📐 Contoh Output

### Contoh Input & Hasil

| Input | Shape | Tampak Atas | Tampak Depan | Tampak Samping |
|-------|-------|-------------|-------------|----------------|
| "Kursi 4 kaki, 40x40, tinggi 45cm" | ChairShape | Persegi dudukan + 4 lingkaran kaki | Backrest + seat + 2 kaki depan | Profil: backrest + seat + 2 kaki samping |
| "Ruangan 4x5m, pintu barat, jendela utara" | RoomShape | Denah lantai + arc pintu + simbol jendela | Elevasi dinding + bukaan | Elevasi samping + bukaan east/west |
| "Meja 120x60 tinggi 75cm" | BoxShape | Persegi panjang (W×L) | Persegi panjang (W×H) | Persegi panjang (L×H) |
| "Tiang silinder diameter 30cm" | CylinderShape | Lingkaran + garis pusat | Persegi panjang (D×H) | Persegi panjang (D×H) + center line |

### Layer DXF

Setiap file DXF menggunakan layer standar:

| Layer | Warna DXF | Warna SVG | Fungsi |
|-------|-----------|-----------|--------|
| `TOP_VIEW` | White (7) | `#e2e8f0` | Gambar tampak atas |
| `FRONT_VIEW` | Blue (5) | `#93c5fd` | Gambar tampak depan |
| `SIDE_VIEW` | Cyan (4) | `#22d3ee` | Gambar tampak samping |
| `DIMENSIONS` | Red (1) | `#f87171` | Garis ukuran + angka |
| `ANNOTATIONS` | Green (3) | `#4ade80` | Judul dan label |
| `CENTER_LINES` | Yellow (2) | `#fbbf24` | Garis pusat (silinder) |

---

## 🔌 API Endpoints

| Method | Endpoint | Fungsi |
|--------|---------|--------|
| `GET` | `/` | Halaman utama (UI) |
| `POST` | `/api/generate` | Generate CAD dari input multimodal |
| `GET` | `/download/{filename}` | Download file DXF |
| `POST` | `/api/export-3d/{filename}` | Export DXF → STL 3D |
| `GET` | `/download-3d/{filename}` | Download file STL |
| `GET` | `/api/history` | List semua history |
| `GET` | `/api/history/{id}` | Detail satu entry |
| `PUT` | `/api/history/{id}` | Update entry (prompt/params) |
| `DELETE` | `/api/history/{id}` | Hapus satu entry |
| `DELETE` | `/api/history` | Hapus semua history |

Dokumentasi API interaktif tersedia di: **http://localhost:8000/docs** (Swagger UI)

---

## 🧪 Unit Testing

Jalankan seluruh test:

```bash
pytest tests/ -v
```

Test yang tersedia:

| Test Class | Coverage |
|-----------|----------|
| `TestBoxShape` | DXF validity, layer creation, dimension usage |
| `TestCylinderShape` | Circle top view, radius calculation, DXF output |
| `TestChairShape` | 4 leg circles, front view polylines |
| `TestRoomShape` | Wall outline, door arc symbol, window triple-lines |
| `TestCADFactory` | Registry lookup, alias resolution (kursi → chair), unknown fallback |
| `TestSVGExporter` | DXF → SVG conversion, viewBox generation |

> **Note:** Unit test CAD Engine berjalan **offline** tanpa membutuhkan API key. Hanya endpoint test yang membutuhkan Groq API key aktif.

---

## 📁 Struktur Project

```
CADPROJECT/
├── main.py                        # FastAPI entry point + semua API routes
├── requirements.txt               # Dependencies
├── .env                           # API Key configuration
├── .gitignore                     # Git ignore rules
├── history.json                   # History database (auto-generated)
│
├── app/
│   ├── __init__.py
│   ├── core/
│   │   ├── config.py              # Centralized settings (model names, etc)
│   │   ├── llm_client.py          # Groq client singleton (lazy init)
│   │   └── exceptions.py          # Custom exception hierarchy
│   │
│   ├── models/
│   │   └── schemas.py             # Pydantic models (CADParameters, DoorSpec, etc)
│   │
│   ├── services/
│   │   ├── reasoning_service.py   # Llama 3.3 — text → JSON params (streaming)
│   │   ├── audio_service.py       # Whisper — audio → text transcription
│   │   ├── vision_service.py      # Llama 4 Scout — image → text description
│   │   └── history_service.py     # JSON CRUD for generation history
│   │
│   └── cad_engine/
│       ├── base.py                # Abstract CADObject (layers, dimensions)
│       ├── shapes.py              # BoxShape + CylinderShape
│       ├── advanced_shapes.py     # ChairShape + RoomShape
│       ├── factory.py             # Shape Factory + alias registry
│       ├── svg_exporter.py        # DXF → SVG converter (dark theme)
│       └── exporter_3d.py         # 2D → 3D STL export (trimesh)
│
├── templates/
│   └── index.html                 # UI (Tailwind CSS + Jinja2)
│
├── static/
│   ├── css/custom.css             # Custom animations
│   └── js/app.js                  # Frontend logic (recording, API, history)
│
├── tests/
│   └── test_cad_engine.py         # 20+ unit tests
│
└── outputs/                       # Generated DXF/SVG/STL files
```

---

## 📏 Asumsi & Simplifikasi

Sesuai dengan aturan task: *"Anda boleh menambahkan asumsi atau simplifikasi jika input terlalu abstrak, selama dijelaskan dalam README."*

| Asumsi / Simplifikasi | Penjelasan |
|----------------------|-----------|
| **Satuan default: sentimeter (cm)** | Jika user menyebut "meter", AI akan mengonversi ke cm (× 100). Jika tidak menyebut satuan, diasumsikan cm. |
| **Dimensi default ergonomi** | Jika user tidak menyebut ukuran, digunakan standar ergonomi: kursi 40×40×45cm, meja 120×60×75cm |
| **Shape mapping** | Input yang ambigu di-map oleh factory: "meja" → BoxShape, "tiang" → CylinderShape |
| **L-Shape fallback** | Input `l_shape` saat ini di-fallback ke BoxShape karena kompleksitas geometri L tidak termasuk dalam scope dasar |
| **Pintu 90° swing** | Semua pintu diasumsikan membuka 90° dengan arc symbol standard |
| **Jendela triple-line** | Simbol jendela menggunakan 3 garis paralel sesuai standar gambar arsitektur |
| **DXF R2010** | Format DXF R2010 dipilih untuk kompatibilitas luas (AutoCAD, FreeCAD, LibreCAD) |
| **3D → meter** | Unit 3D menggunakan meter (cm ÷ 100) karena STL viewers umumnya mengasumsikan meter |
| **Single floor** | RoomShape menggambar satu lantai — denah multi-lantai diluar scope |

---

## 📄 Lisensi

MIT License — Free to use, modify, and distribute.

---

<div align="center">

**AI CAD Architect v1.0**

Dibuat oleh Muhamad Siskandar Zulkarnain

*Powered by Groq AI · ezdxf · trimesh · FastAPI*

</div>
