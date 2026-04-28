# MVoice Intelligence API

Backend modern untuk dashboard intelijen kreatif, dibangun dengan FastAPI. Proyek ini dirancang agar modular,scalable, dan siap untuk integrasi fitur AI di masa depan.

## 🚀 Fitur Utama
- **Modular Architecture**: Pemisahan yang jelas antara API Routes, Business Logic (Services), dan Configuration.
- **Service-Oriented**: Logika data dipisah menjadi layanan khusus (Analytics, Brands, Creatives).
- **Type Safety**: Menggunakan Pydantic untuk validasi skema data dan pengaturan.
- **Scalable**: Struktur folder siap untuk penambahan fitur kompleks dan integrasi database di masa depan.

## 📁 Struktur Proyek
```text
backend/
├── app/
│   ├── api/            # API Route handlers
│   │   ├── endpoints/  # Resource-specific routes (analytics, brands, etc.)
│   │   └── deps.py     # API Dependencies
│   ├── core/           # Core configuration & settings
│   ├── models/         # Pydantic schemas (data models)
│   ├── services/       # Business logic / Data management
│   └── main.py         # App entry point
├── .env                # Environment variables
├── requirements.txt    # Python dependencies
└── creatives_dummy.csv # Source data
```

## 🛠️ Cara Menjalankan

### 1. Install Dependencies
Pastikan Anda berada di virtual environment (`.venv`), lalu jalankan:
```bash
pip install -r requirements.txt
```

### 2. Jalankan Server
Gunakan perintah berikut untuk menjalankan server dalam mode pengembangan (auto-reload):
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Server akan berjalan di [http://localhost:8000](http://localhost:8000).

### 3. Dokumentasi API (Interactive Docs)
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## 🔧 Konfigurasi (.env)
Anda dapat mengatur variabel berikut di file `.env`:
- `PROJECT_NAME`: Nama aplikasi.
- `CSV_PATH`: Jalur ke file data CSV.
- `CORS_ORIGINS`: Daftar origin yang diizinkan untuk CORS.

## 🤖 Roadmap AI (Next Steps)
Struktur ini sudah siap untuk:
1. Menambahkan `app/services/ai_service.py` untuk pemrosesan LLM.
2. Integrasi Vector Database di `app/core/vector_db.py`.
3. Endpoint baru di `app/api/endpoints/ai.py` untuk summary otomatis.
