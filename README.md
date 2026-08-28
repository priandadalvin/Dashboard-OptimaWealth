# Data Dashboard & Preprocessing: OptimaWealth 📈

Repositori ini berisi *dashboard* analitik dan *pipeline* pemrosesan data yang bertugas mengeksplorasi, membersihkan, serta memvisualisasikan dataset transaksi keuangan. Keseluruhan alur kerja dalam *dashboard* ini dirancang secara khusus untuk menyiapkan data pelatihan yang berkualitas tinggi bagi model *machine learning* pada **OptimaWealth**, sebuah aplikasi *Smart Personal Finance Advisor* yang berfokus pada analisis perilaku transaksi generasi muda.

## 🎯 Tujuan Proyek

*Dashboard* ini berfungsi sebagai ruang kerja analitik sebelum tahap rekayasa model. Tujuannya adalah untuk memahami pola distribusi data historis, menangani anomali, dan menyusun format data deret waktu (*time series*) yang ideal sebelum dieksekusi oleh arsitektur model **LSTM-Attention** untuk prediksi arus kas.

## 🚀 Fitur Dashboard Analitik

- **Exploratory Data Analysis (EDA):** Mengidentifikasi pola pengeluaran bulanan, musiman, serta anomali dalam riwayat transaksi pengguna.
- **Visualisasi Tren Komprehensif:** Menyajikan grafik interaktif yang mudah diinterpretasikan. Setiap visualisasi diagram batang secara eksplisit menampilkan angka di atas bar beserta metrik persentase pertumbuhannya, memastikan setiap fluktuasi kas dapat dianalisis dengan cepat dan akurat.
- **Data Preprocessing Pipeline:** Modul terintegrasi untuk melakukan normalisasi, penanganan *missing values*, dan transformasi data tabular menjadi format sekuensial yang siap dikonsumsi oleh model *Deep Learning*.
- **Feature Engineering:** Ekstraksi fitur-fitur temporal (seperti hari dalam seminggu, minggu dalam bulan) yang memperkuat kemampuan model dalam menangkap kebiasaan finansial pengguna.

## 🛠️ Teknologi & Library

- **Bahasa Pemrograman:** Python
- **Eksplorasi & Manipulasi Data:** Pandas, NumPy
- **Visualisasi Data:** Streamlit, Matplotlib, Plotly, atau Seaborn
- **Persiapan Model:** Scikit-Learn (untuk penskalaan dan pemisahan data *train/test*)

## 💻 Cara Menjalankan Dashboard secara Lokal

1. **Clone Repositori**
   ```bash
   git clone [https://github.com/priandadalvin/Dashboard-OptimaWealth.git](https://github.com/priandadalvin/Dashboard-OptimaWealth.git)
   cd Dashboard-OptimaWealth

2. **Buat Virtual Environment**
    ```bash
   python -m venv env
    # Untuk Linux/Mac:
    source env/bin/activate
    # Untuk Windows:
    env\Scripts\activate

3. **Instal Dependensi**
   ```bash
   pip install -r requirements.txt

4. **Jalankan Dashboard Streamlit**
   ```bash
   streamlit run dashboard.py


```📂 **Struktur Direktori**
Dashboard-OptimaWealth/
│
├── data/                  # Folder untuk dataset transaksi mentah dan hasil preprocessing
├── src/                   # Skrip modular untuk pembersihan dan transformasi data
├── notebooks/             # Jupyter Notebooks untuk riset awal dan uji coba pemodelan
├── dashboard.py           # Skrip utama antarmuka dashboard analitik (Streamlit)
├── requirements.txt       # Daftar dependensi library
└── README.md              # Dokumentasi repositori
