import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker
import matplotlib.colors as mcolors 
from babel.numbers import format_currency
from collections import Counter
from pathlib import Path

# ==========================================
# 0. KONFIGURASI HALAMAN 
# ==========================================
st.set_page_config(
    page_title="OptimaWealth Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- SUNTIKAN CSS GLOBAL UNTUK TEMA ---
st.markdown("""
<style>
/* Trik CSS Khusus untuk Pills (Kuning/Biru) */
div:has(> .profesi-marker) + div div[data-testid="stPills"] label[data-checked="true"] {
    background-color: #ffc107 !important;
    color: #333333 !important;
    border-color: #ffc107 !important;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# NAVIGASI MULTIPAGE (SIDEBAR)
# ==========================================

st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=80)
st.sidebar.title("OptimaWealth Dashboard")
halaman = st.sidebar.radio("Pilih Halaman Dashboard:", 
                           ["Daily Cashflow", 
                            "Teks Deskripsi Transaksi"])

st.sidebar.markdown("---")

# ==============================================================================
# HALAMAN 1: Daily Cashflow
# ==============================================================================
if halaman == "Daily Cashflow":
    
    def format_idr(value):
        """Fungsi format Rupiah utuh"""
        if pd.isna(value):
            return "Rp 0"
        formatted = format_currency(int(round(value)), 'IDR', locale='id_ID', format='¤ #,##0')
        # Pastikan ada spasi setelah Rp, hapus desimal ,00, lalu gunakan non-breaking space (\xa0)
        formatted = formatted.replace('Rp', 'Rp ').replace(',00', '').replace('  ', ' ')
        return formatted.replace(' ', '\xa0')

    def format_number_only(value):
        """Fungsi format angka saja untuk sumbu Y/X (Tanpa Rp)"""
        if pd.isna(value):
            return "0"
        return f"{int(round(value)):,}".replace(',', '.')

    def create_tren_harian_df(df):
        return df.groupby('date')[['daily_income', 'daily_expense']].sum().reset_index()

    def create_rata_profesi_df(df):
        return df.groupby('profesi_clean')['daily_cashflow'].mean().sort_values(ascending=False)

    def create_rata_kota_df(df):
        return df.groupby('kota_clean')['daily_expense'].mean().sort_values(ascending=False)

    def create_df_aktif_weekend(df):
        return df[df['daily_expense'] > 0].copy()

    @st.cache_data
    def load_data_kas():
        df_kas = pd.read_csv('dataset_arus_kas_harian_cleaned.csv')
        df_kas['date'] = pd.to_datetime(df_kas['date'])

        map_hari = {1: 'Senin', 2: 'Selasa', 3: 'Rabu', 4: 'Kamis', 5: 'Jumat', 6: 'Sabtu', 7: 'Minggu'}
        df_kas['nama_hari'] = pd.Categorical(
            df_kas['hari_dalam_minggu'].map(map_hari),
            categories=['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu'],
            ordered=True
        )
        return df_kas

    df_kas = load_data_kas()

    # --- KOMPONEN FILTER (SIDEBAR) ---
    st.sidebar.subheader("Filter Data Daily Cashflow")
    min_date = df_kas['date'].min()
    max_date = df_kas['date'].max()
    date_range = st.sidebar.date_input("📅 Pilih Rentang Waktu", [min_date, max_date])

    pilihan_kota = st.sidebar.pills("🏙️ Pilih Kota", options=df_kas['kota_clean'].unique(), default=df_kas['kota_clean'].unique(), selection_mode="multi")
    
    st.sidebar.markdown('<div class="profesi-marker"></div>', unsafe_allow_html=True)
    pilihan_profesi = st.sidebar.pills("💼 Pilih Profesi", options=df_kas['profesi_clean'].unique(), default=df_kas['profesi_clean'].unique(), selection_mode="multi")

    if len(date_range) == 2:
        start_date, end_date = date_range
        df_filtered = df_kas[
            (df_kas['date'].dt.date >= start_date) & 
            (df_kas['date'].dt.date <= end_date) &
            (df_kas['kota_clean'].isin(pilihan_kota)) &
            (df_kas['profesi_clean'].isin(pilihan_profesi))
        ]
    else:
        df_filtered = df_kas.copy()

    tren_harian = create_tren_harian_df(df_filtered)
    rata_profesi = create_rata_profesi_df(df_filtered)
    rata_kota = create_rata_kota_df(df_filtered)
    df_aktif = create_df_aktif_weekend(df_filtered)

    # --- TAMPILAN DASHBOARD (UTAMA) ---
    st.title("💸 Daily Cashflow")
    st.markdown("Dashboard untuk menampilkan perilaku pengeluaran dan kesehatan finansial kelompok user untuk model LSTM.")
    st.markdown("---")

    if df_filtered.empty:
        st.warning("⚠️ Tidak ada data yang cocok dengan kombinasi filter Anda. Silakan atur ulang filter di sidebar.")
        st.stop()

    # --- BAGIAN 6.1: METRIK RINGKASAN (KPI CARDS KUSTOM HTML) ---
    total_income = df_filtered['daily_income'].sum()
    total_expense = df_filtered['daily_expense'].sum()
    total_cashflow = df_filtered['daily_cashflow'].sum()
    avg_transaksi = df_filtered[df_filtered['n_transaksi'] > 0]['avg_transaction'].mean()

    col1, col2, col3, col4 = st.columns(4)

    # Template HTML Kustom persis dengan desain referensi
    kpi_card_html = """
    <div style="background-color: {bg_color}; padding: 20px 10px; border-radius: 10px; border-left: 8px solid {border_color}; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
        <p style="margin: 0; font-size: 1.05rem; font-weight: 600; color: #444444; white-space: nowrap;">{title}</p>
        <h3 style="margin: 10px 0 0 0; font-size: 1.4rem; font-weight: 800; color: #222222; white-space: nowrap;">{value}</h3>
    </div>
    """

    with col1:
        st.markdown(kpi_card_html.format(bg_color="#eaf2f8", border_color="#3498db", title="📈 Total Pemasukan", value=format_idr(total_income)), unsafe_allow_html=True)
    with col2:
        st.markdown(kpi_card_html.format(bg_color="#fdf6e3", border_color="#f1c40f", title="📉 Total Pengeluaran", value=format_idr(total_expense)), unsafe_allow_html=True)
    with col3:
        st.markdown(kpi_card_html.format(bg_color="#eafaf1", border_color="#2ecc71", title="💰 Net Cashflow", value=format_idr(total_cashflow)), unsafe_allow_html=True)
    with col4:
        st.markdown(kpi_card_html.format(bg_color="#fdedec", border_color="#e74c3c", title="💳 Rata-rata Transaksi", value=format_idr(avg_transaksi)), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")
    sns.set_theme(style="whitegrid") 

    # --- BAGIAN 6.2: GRAFIK 1 (TREN LINE CHART) ---
    st.subheader("Tren Harian Total Pemasukan vs Pengeluaran")
    fig_tren, ax_tren = plt.subplots(figsize=(15, 4.5))
    sns.lineplot(data=tren_harian, x='date', y='daily_income', label='Pemasukan', color='#2ecc71', linewidth=2.5, ax=ax_tren)
    sns.lineplot(data=tren_harian, x='date', y='daily_expense', label='Pengeluaran', color='#e74c3c', linewidth=2.5, ax=ax_tren)

    ax_tren.set_xlabel("")
    ax_tren.set_ylabel("Nominal (Rp)", fontweight='bold')
    ax_tren.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: format_number_only(x)))
    ax_tren.legend(loc='upper left', frameon=True, shadow=True)
    sns.despine()
    st.pyplot(fig_tren)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- BAGIAN 6.3: GRAFIK 2 & 3 (DEMOGRAFI BAR CHART BERDAMPINGAN) ---
    st.subheader("Analisis Berdasarkan Profesi dan Kota")
    col_bar1, col_bar2 = st.columns(2)

    with col_bar1:
        st.write("**👨‍💻 Rata-rata Cashflow by Profesi**")
        fig_prof, ax_prof = plt.subplots(figsize=(8, 6))
        
        sns.barplot(
            data=df_filtered, x='daily_cashflow', y='profesi_clean', estimator=np.mean, 
            ax=ax_prof, palette=sns.color_palette("Greens_r", n_colors=len(rata_profesi)),
            hue='profesi_clean', legend=False, order=rata_profesi.index, 
            hue_order=rata_profesi.index, errorbar=None
        )
        ax_prof.set_xlabel('Rata-rata Arus Kas (Rp)', fontweight='bold')
        ax_prof.set_ylabel('')
        ax_prof.axvline(0, color='black', linestyle='--', linewidth=1)
        ax_prof.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: format_number_only(x)))
        
        for container in ax_prof.containers:
            labels = [format_idr(v.get_width()) for v in container]
            ax_prof.bar_label(container, labels=labels, padding=5, fontweight='bold', fontsize=9)
            
        sns.despine(left=True, bottom=False)
        st.pyplot(fig_prof)

    with col_bar2:
        st.write("**🏙️ Rata-rata Pengeluaran by Kota**")
        fig_kota, ax_kota = plt.subplots(figsize=(8, 6))
        
        sns.barplot(
            data=df_filtered, x='daily_expense', y='kota_clean', estimator=np.mean, 
            ax=ax_kota, palette=sns.color_palette("Reds_r", n_colors=len(rata_kota)),
            hue='kota_clean', legend=False, order=rata_kota.index, 
            hue_order=rata_kota.index, errorbar=None
        )
        ax_kota.set_xlabel('Rata-rata Pengeluaran (Rp)', fontweight='bold')
        ax_kota.set_ylabel('')
        ax_kota.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: format_number_only(x)))
        
        for container in ax_kota.containers:
            labels = [format_idr(v.get_width()) for v in container]
            ax_kota.bar_label(container, labels=labels, padding=5, fontweight='bold', fontsize=9)
            
        sns.despine(left=True, bottom=False)
        st.pyplot(fig_kota)

    st.markdown("---")

    # --- BAGIAN 6.4: GRAFIK 4 (PERBANDINGAN WEEKEND) ---
    st.subheader("Perbandingan Perilaku: Hari Kerja vs Akhir Pekan")
    if not df_aktif.empty:
        fig_weekend, axes_week = plt.subplots(1, 2, figsize=(16, 5))
        warna_kustom = ['#3498db', '#e74c3c']

        ax1 = sns.barplot(
            data=df_aktif, x='is_weekend', y='daily_expense', estimator=np.mean, 
            ax=axes_week[0], palette=warna_kustom, hue='is_weekend', legend=False, errorbar=None 
        )
        axes_week[0].set_title('Rata-rata Pengeluaran Harian', fontweight='bold', pad=15)
        axes_week[0].set_ylabel('Nominal (Rp)', fontweight='bold')
        axes_week[0].set_xlabel('') 
        axes_week[0].set_xticks([0, 1])
        axes_week[0].set_xticklabels(['Hari Kerja', 'Akhir Pekan'], fontweight='bold')
        axes_week[0].yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: format_number_only(x)))
        
        for container in ax1.containers:
            labels = [format_idr(val) for val in container.datavalues]
            ax1.bar_label(container, labels=labels, padding=5, fontweight='bold', color='#333333')

        ax2 = sns.barplot(
            data=df_aktif, x='is_weekend', y='avg_transaction', estimator=np.mean, 
            ax=axes_week[1], palette=warna_kustom, hue='is_weekend', legend=False, errorbar=None 
        )
        axes_week[1].set_title('Rata-rata Nilai per Transaksi', fontweight='bold', pad=15)
        axes_week[1].set_ylabel('Nominal (Rp)', fontweight='bold')
        axes_week[1].set_xlabel('') 
        axes_week[1].set_xticks([0, 1])
        axes_week[1].set_xticklabels(['Hari Kerja', 'Akhir Pekan'], fontweight='bold')
        axes_week[1].yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: format_number_only(x)))

        for container in ax2.containers:
            labels = [format_idr(val) for val in container.datavalues]
            ax2.bar_label(container, labels=labels, padding=5, fontweight='bold', color='#333333')

        sns.despine(left=True, bottom=False)
        axes_week[0].margins(y=0.20)
        axes_week[1].margins(y=0.20)
        plt.tight_layout()
        st.pyplot(fig_weekend)
    else:
        st.info("Tidak ada data pengeluaran aktif pada filter yang dipilih.")

    st.markdown("---")

    # --- BAGIAN 6.5: GRAFIK 5 (RATA-RATA PENGELUARAN PER HARI AKTIF) ---
    st.subheader("Analisis Berdasarkan Hari Aktif")
    if not df_aktif.empty:
        rata2_per_hari = df_aktif.groupby('nama_hari', observed=False)['daily_expense'].mean()
        norm = mcolors.Normalize(vmin=rata2_per_hari.min(), vmax=rata2_per_hari.max())
        colormap = plt.get_cmap('YlOrBr')
        
        warna_dinamis = {
            hari: colormap(0.3 + 0.7 * norm(nilai)) 
            for hari, nilai in rata2_per_hari.items()
        }
        
        fig_hari, ax_hari = plt.subplots(figsize=(12, 6))
        
        sns.barplot(
            data=df_aktif, 
            x='nama_hari', 
            y='daily_expense', 
            estimator=np.mean, 
            hue='nama_hari', 
            palette=warna_dinamis, 
            legend=False,
            errorbar=None,
            dodge=False, 
            ax=ax_hari
        )
        
        ax_hari.set_title('Rata-rata Pengeluaran per Hari Aktif', fontsize=14, fontweight='bold', pad=15)
        ax_hari.set_xlabel('') 
        ax_hari.set_ylabel('Rata-rata Pengeluaran (Rp)', fontweight='bold')
        ax_hari.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: format_number_only(x)))
        
        for container in ax_hari.containers:
            labels = [format_idr(val) for val in container.datavalues]
            ax_hari.bar_label(container, labels=labels, padding=5, fontweight='bold', color='#333333', fontsize=10)
            
        sns.despine(left=True, bottom=False)
        ax_hari.margins(y=0.20)
        plt.tight_layout()
        st.pyplot(fig_hari)
    else:
        st.info("Tidak ada data pengeluaran harian aktif pada filter yang dipilih.")


# ==============================================================================
# HALAMAN 2: Teks Deskripsi Transaksi
# ==============================================================================
elif halaman == "Teks Deskripsi Transaksi":
    st.title("📝 Teks Deskripsi Transaksi")
    st.markdown("Dashboard untuk menampilkan teks deskripsi transaksi dan sebaran N-Gram untuk model IndoBERT.")
    st.markdown("---")

    @st.cache_data
    def load_eda_data():
        df_eda = pd.read_csv('dataset_combined_augmented.csv')
        df_eda['char_length'] = df_eda['description'].astype(str).apply(len)
        df_eda['word_count'] = df_eda['description'].astype(str).apply(lambda x: len(x.split()))
        return df_eda
        
    df_eda = load_eda_data()
    
    # Filter Interaktif di Sidebar menggunakan st.pills
    st.sidebar.subheader("Filter Teks deskripsi Transaksi")
    kategori_terpilih = st.sidebar.pills("Pilih Kategori Transaksi:", 
                                         options=df_eda['category'].unique(), 
                                         default=df_eda['category'].unique(),
                                         selection_mode="multi")
    
    top_n_words = st.sidebar.slider("Jumlah Kata Terpopuler (N-Gram):", min_value=10, max_value=50, value=30, step=5)

    # Filter Data berdasarkan kategori
    if kategori_terpilih:
        df_filtered_eda = df_eda[df_eda['category'].isin(kategori_terpilih)]
    else:
        df_filtered_eda = pd.DataFrame(columns=df_eda.columns)

    if df_filtered_eda.empty:
        st.warning("⚠️ Tidak ada data untuk kategori yang dipilih. Silakan ubah filter Anda.")
        st.stop()

    # --- Grafik 1: Distribusi Kategori (Count Plot) ---
    st.subheader("Distribusi Jumlah Transaksi Per Kategori")
    cat_counts = df_filtered_eda['category'].value_counts()
    
    fig_cat, ax_cat = plt.subplots(figsize=(12, 6))
    
    # Menggunakan palet Blues_r dan hue_order agar urutan gradien biru terkunci 
    sns.countplot(
        data=df_filtered_eda, 
        y='category', 
        order=cat_counts.index, 
        palette=sns.color_palette("Blues_r", n_colors=len(cat_counts)), 
        hue='category', 
        hue_order=cat_counts.index,
        legend=False, 
        ax=ax_cat
    )
    ax_cat.set_xlabel('Jumlah Transaksi', fontweight='bold')
    ax_cat.set_ylabel('Kategori', fontweight='bold')
    sns.despine()
    st.pyplot(fig_cat)

    st.markdown("---")

    # --- Grafik 2: Statistik Panjang Teks ---
    st.subheader("Karakteristik Teks Deskripsi")
    col_text1, col_text2 = st.columns(2)

    with col_text1:
        st.write("**Distribusi Panjang Karakter Deskripsi**")
        fig_char, ax_char = plt.subplots(figsize=(8, 5))
        sns.histplot(df_filtered_eda['char_length'], bins=30, kde=True, color='orange', ax=ax_char)
        ax_char.set_xlabel('Jumlah Karakter', fontweight='bold')
        ax_char.set_ylabel('Frekuensi', fontweight='bold')
        sns.despine()
        st.pyplot(fig_char)

    with col_text2:
        st.write("**Distribusi Jumlah Kata Deskripsi**")
        fig_word, ax_word = plt.subplots(figsize=(8, 5))
        sns.histplot(df_filtered_eda['word_count'], bins=10, kde=False, color='salmon', ax=ax_word)
        ax_word.set_xlabel('Jumlah Kata', fontweight='bold')
        ax_word.set_ylabel('Frekuensi', fontweight='bold')
        sns.despine()
        st.pyplot(fig_word)

    st.markdown("---")

    # --- Grafik 3: Analisis N-Gram ---
    st.subheader(f"{top_n_words} Kata Terpopuler (Unigram)")
    
    # Ekstraksi kata-kata secara interaktif
    all_words = []
    for text in df_filtered_eda['description'].dropna().astype(str):
        words = text.lower().split()
        all_words.extend(words)

    word_freq = Counter(all_words).most_common(top_n_words)
    words_df = pd.DataFrame(word_freq, columns=['Word', 'Frequency'])

    fig_ngram, ax_ngram = plt.subplots(figsize=(12, 8))
    sns.barplot(data=words_df, x='Frequency', y='Word', palette='mako', hue='Word', legend=False, ax=ax_ngram)
    ax_ngram.set_xlabel('Frekuensi Kemunculan', fontweight='bold')
    ax_ngram.set_ylabel('Kata', fontweight='bold')
    
    for container in ax_ngram.containers:
        ax_ngram.bar_label(container, padding=5, color='#333333', fontsize=10)
        
    sns.despine()
    ax_ngram.margins(x=0.1)
    st.pyplot(fig_ngram)