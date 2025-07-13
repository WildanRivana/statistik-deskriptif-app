import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import StringIO

# Fungsi untuk menghitung statistik
def calculate_statistics(data):
    stats = {
        'Mean': np.mean(data),
        'Median': np.median(data),
        'Mode': pd.Series(data).mode().tolist(),
        'Variance': np.var(data, ddof=0),  # Population variance
        'Standard Deviation': np.std(data, ddof=0),  # Population std
        'Min': np.min(data),
        'Max': np.max(data),
        'Range': np.max(data) - np.min(data),
        'Q1': np.percentile(data, 25),
        'Q3': np.percentile(data, 75),
        'IQR': np.percentile(data, 75) - np.percentile(data, 25)
    }
    return stats

# Konfigurasi halaman
st.set_page_config(page_title="Simulasi Statistik Deskriptif", page_icon="📊", layout="wide")

# Judul aplikasi
st.title("📊 Aplikasi Simulasi Statistik Deskriptif")
st.markdown("""
Aplikasi ini menghitung berbagai ukuran statistik deskriptif dan menampilkan visualisasi data.
""")

# Sidebar untuk input data
with st.sidebar:
    st.header("Input Data")
    input_method = st.radio("Pilih metode input:", 
                           ("Manual", "Upload CSV"))
    
    if input_method == "Manual":
        st.subheader("Input Data Manual")
        raw_data = st.text_area("Masukkan data (pisahkan dengan koma atau spasi):", 
                               "1, 2, 3, 4, 5, 5, 6, 7, 8, 9")
        # Proses input manual
        try:
            data = np.array([float(x.strip()) for x in raw_data.replace(',', ' ').split()])
        except ValueError:
            st.error("Format data tidak valid. Pastikan hanya angka yang dimasukkan.")
            st.stop()
    else:
        st.subheader("Upload File CSV")
        uploaded_file = st.file_uploader("Pilih file CSV", type=["csv"])
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) == 0:
                    st.error("File CSV tidak mengandung kolom numerik.")
                    st.stop()
                
                selected_col = st.selectbox("Pilih kolom numerik untuk dianalisis:", numeric_cols)
                data = df[selected_col].dropna().values
            except Exception as e:
                st.error(f"Error membaca file: {e}")
                st.stop()
        else:
            st.info("Silakan upload file CSV untuk melanjutkan.")
            st.stop()

# Validasi data
if len(data) < 2:
    st.error("Data harus memiliki setidaknya 2 nilai untuk analisis statistik.")
    st.stop()

# Tampilkan data
st.subheader("Data Input")
col1, col2 = st.columns(2)
with col1:
    st.write("**Data mentah:**", data)
with col2:
    st.write("**Jumlah data points:**", len(data))

# Hitung statistik
try:
    stats = calculate_statistics(data)
except Exception as e:
    st.error(f"Error dalam perhitungan statistik: {e}")
    st.stop()

# Tampilkan hasil statistik
st.subheader("Hasil Statistik Deskriptif")
stats_df = pd.DataFrame.from_dict(stats, orient='index', columns=['Value'])

# Format khusus untuk Mode yang bisa memiliki multiple values
stats_df.loc['Mode', 'Value'] = ', '.join(map(str, stats['Mode'])) if isinstance(stats['Mode'], list) else stats['Mode']

st.dataframe(stats_df.style.format({'Value': '{:.4f}'}), use_container_width=True)

# Visualisasi data
st.subheader("Visualisasi Data")

plot_type = st.selectbox("Pilih jenis plot:", ["Histogram", "Boxplot", "Keduanya"])

fig, ax = plt.subplots(figsize=(10, 6))

if plot_type in ["Histogram", "Keduanya"]:
    if plot_type == "Keduanya":
        ax = plt.subplot(1, 2, 1)
    sns.histplot(data, kde=True, ax=ax if plot_type != "Keduanya" else ax)
    ax.set_title('Histogram dengan KDE')
    ax.axvline(stats['Mean'], color='r', linestyle='--', label=f'Mean: {stats["Mean"]:.2f}')
    ax.axvline(stats['Median'], color='g', linestyle='-', label=f'Median: {stats["Median"]:.2f}')
    ax.legend()

if plot_type in ["Boxplot", "Keduanya"]:
    if plot_type == "Keduanya":
        ax = plt.subplot(1, 2, 2)
    sns.boxplot(x=data, ax=ax if plot_type != "Keduanya" else ax)
    ax.set_title('Boxplot')
    if plot_type != "Keduanya":
        ax.axvline(stats['Mean'], color='r', linestyle='--', label=f'Mean: {stats["Mean"]:.2f}')

st.pyplot(fig)

# Interpretasi hasil
st.subheader("Interpretasi Hasil")
st.markdown(f"""
- **Mean/Rata-rata ({stats['Mean']:.2f})**: Nilai rata-rata dari seluruh data.
- **Median ({stats['Median']:.2f})**: Nilai tengah data ketika diurutkan.
- **Mode ({', '.join(map(str, stats['Mode']))})**: Nilai yang paling sering muncul.
- **Standar Deviasi ({stats['Standard Deviation']:.2f})**: Ukuran sebaran data dari mean.
- **Range ({stats['Range']:.2f})**: Selisih antara nilai maksimum dan minimum.
- **IQR ({stats['IQR']:.2f})**: Rentang interkuartil (Q3-Q1), menunjukkan sebaran 50% data tengah.
""")

# Catatan
st.info("""
**Catatan:**
- Perhitungan varians dan standar deviasi menggunakan formula populasi (N sebagai penyebut).
- Mode bisa memiliki lebih dari satu nilai jika ada beberapa nilai dengan frekuensi maksimum yang sama.
""")
