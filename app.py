import streamlit as st
import pandas as pd
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool, Slider, FactorRange, Range1d  # Range1d ditambahkan di sini
from bokeh.transform import factor_cmap, dodge
from bokeh.palettes import Category10, Category20c # Menggunakan palet yang lebih besar
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Load dataset
df = pd.read_csv('heart_2020_cleaned.csv')

st.set_page_config(layout="wide")
st.title("Dashboard Interaktif: Visualisasi Penyakit Jantung 2020")

# --- Sidebar Filters ---
st.sidebar.header("Filter Interaktif")

# Filter Jenis Kelamin (Dropdown Menu)
selected_sex = st.sidebar.selectbox("Pilih Jenis Kelamin:", options=['All'] + df['Sex'].unique().tolist())

# Filter Kategori Usia (Multiselect Dropdown)
age_order = ['18-24', '25-29', '30-34', '35-39', '40-44', '45-49', '50-54', '55-59', '60-64', '65-69', '70-74', '75-79', '80 or older']
age_options = sorted(df['AgeCategory'].unique().tolist(), key=lambda x: age_order.index(x) if x in age_order else len(age_order))
selected_age = st.sidebar.multiselect("Pilih Kategori Usia:", options=age_options, default=age_options)

# Filter BMI (Slider)
bmi_min_val = float(df['BMI'].min())
bmi_max_val = float(df['BMI'].max())
bmi_range = st.sidebar.slider("Rentang BMI:", min_value=bmi_min_val, max_value=bmi_max_val, value=(bmi_min_val, bmi_max_val))

# Filter Physical Health (Slider)
physical_health_min_val = float(df['PhysicalHealth'].min())
physical_health_max_val = float(df['PhysicalHealth'].max())
physical_health_range = st.sidebar.slider("Rentang Hari Sakit Fisik:", min_value=physical_health_min_val, max_value=physical_health_max_val, value=(physical_health_min_val, physical_health_max_val))

# Filter Mental Health (Slider)
mental_health_min_val = float(df['MentalHealth'].min())
mental_health_max_val = float(df['MentalHealth'].max())
mental_health_range = st.sidebar.slider("Rentang Hari Sakit Mental:", min_value=mental_health_min_val, max_value=mental_health_max_val, value=(mental_health_min_val, mental_health_max_val))

# Filter Sleep Time (Slider)
sleep_time_min_val = float(df['SleepTime'].min())
sleep_time_max_val = float(df['SleepTime'].max())
sleep_time_range = st.sidebar.slider("Rentang Jam Tidur:", min_value=sleep_time_min_val, max_value=sleep_time_max_val, value=(sleep_time_min_val, sleep_time_max_val))

# --- Apply Filters ---
filtered_df = df.copy()
if selected_sex != 'All':
    filtered_df = filtered_df[filtered_df['Sex'] == selected_sex]
filtered_df = filtered_df[filtered_df['AgeCategory'].isin(selected_age)]
filtered_df = filtered_df[(filtered_df['BMI'] >= bmi_range[0]) & (filtered_df['BMI'] <= bmi_range[1])]
filtered_df = filtered_df[(filtered_df['PhysicalHealth'] >= physical_health_range[0]) & (filtered_df['PhysicalHealth'] <= physical_health_range[1])]
filtered_df = filtered_df[(filtered_df['MentalHealth'] >= mental_health_range[0]) & (filtered_df['MentalHealth'] <= mental_health_range[1])]
filtered_df = filtered_df[(filtered_df['SleepTime'] >= sleep_time_range[0]) & (filtered_df['SleepTime'] <= sleep_time_range[1])]

# --- Helper Function for Bokeh Palettes ---
def get_diverse_palette(n_categories):
    # Use Category20c for up to 20 distinct colors
    if n_categories <= len(Category20c):
        return Category20c[n_categories]
    else:
        # If more than 20 categories, cycle through Category20 (which is 20 colors)
        # or expand by repeating/combining
        return Category20c[20] * ((n_categories // 20) + 1) # Repeat for more categories

# Fungsi untuk menampilkan barplot interaktif Bokeh
def bokeh_barplot(data, x_col, y_col, title, x_label, y_label, x_range_order=None, custom_colors=None):
    if x_range_order:
        x_range = FactorRange(factors=x_range_order)
    else:
        x_range = FactorRange(factors=data[x_col].tolist())

    source = ColumnDataSource(data)
    
    if custom_colors:
        palette = custom_colors
    else:
        palette = get_diverse_palette(len(data[x_col].unique()))
    
    p = figure(x_range=x_range, height=350, title=title,
               tools="hover,pan,wheel_zoom,box_zoom,reset,save")
    
    p.vbar(x=x_col, top=y_col, width=0.5, source=source,
           fill_color=factor_cmap(x_col, palette=palette, factors=data[x_col].tolist()))
    
    p.xaxis.major_label_orientation = 1.2
    p.xaxis.axis_label = x_label
    p.yaxis.axis_label = y_label 
    
    hover = p.select_one(HoverTool)
    hover.tooltips = [(x_col, f"@{x_col}"), (y_col, f"@{y_col}")]
    return p

# --- Visualisasi 1: Proporsi Penderita vs Non-Penderita Penyakit Jantung (Bar Chart) ---
st.subheader("1. Distribusi Status Penyakit Jantung")
if not filtered_df.empty:
    disease_count = filtered_df['HeartDisease'].value_counts()
    
    if not disease_count.empty:
        plot_data = pd.DataFrame({'HeartDisease': disease_count.index.tolist(), 'Count': disease_count.values})
        p1 = bokeh_barplot(plot_data, 'HeartDisease', 'Count', "Distribusi Proporsi Penderita Penyakit Jantung", "Status Penyakit Jantung", "Jumlah Orang", custom_colors=['#4B8BBE', '#E4572E'])
        st.bokeh_chart(p1, use_container_width=True)
    else:
        st.info("Tidak ada data yang tersedia untuk filter yang dipilih.")

# --- Visualisasi 2: Jumlah Kasus Penyakit Jantung Berdasarkan Jenis Kelamin (Bar Plot Bokeh) ---
st.subheader("2. Jumlah Kasus Penyakit Jantung Berdasarkan Jenis Kelamin")
if not filtered_df.empty:
    heart_disease_df = filtered_df[filtered_df['HeartDisease'] == 'Yes']
    gender_counts = heart_disease_df.groupby('Sex')['HeartDisease'].count()
    
    if not gender_counts.empty:
        plot_data_gender = pd.DataFrame({'Sex': gender_counts.index.tolist(), 'Count': gender_counts.values})
        p2 = bokeh_barplot(plot_data_gender, 'Sex', 'Count', "Jumlah Kasus Penyakit Jantung per Jenis Kelamin", "Jenis Kelamin", "Jumlah Kasus", custom_colors=['#FF8C00', '#1E90FF'])
        st.bokeh_chart(p2, use_container_width=True)
    else:
        st.info("Tidak ada kasus penyakit jantung berdasarkan jenis kelamin untuk filter yang dipilih.")
else:
    st.info("Tidak ada data yang tersedia untuk filter yang dipilih.")

# --- Visualisasi 3: Jumlah Orang Terkena dan Tidak Terkena Penyakit Jantung Berdasarkan Umur (Horizontal Bar Plot Bokeh) ---
st.subheader("3. Jumlah Orang Terkena dan Tidak Terkena Penyakit Jantung Berdasarkan Umur")
if not filtered_df.empty:
    age_heart_disease_counts = filtered_df.groupby(['AgeCategory', 'HeartDisease']).size().unstack(fill_value=0)
    
    if not age_heart_disease_counts.empty:
        # Reorder AgeCategory for proper display
        age_heart_disease_counts = age_heart_disease_counts.reindex(age_order).fillna(0)

        # Prepare data for Bokeh
        age_categories = age_heart_disease_counts.index.tolist()
        heart_disease_yes = age_heart_disease_counts['Yes'].tolist()
        heart_disease_no = age_heart_disease_counts['No'].tolist()

        source_data = pd.DataFrame({
            'age_category': age_categories,
            'yes_cases': heart_disease_yes,
            'no_cases': heart_disease_no,
            'total_cases': [y + n for y, n in zip(heart_disease_yes, heart_disease_no)]
        })
        source_bokeh = ColumnDataSource(source_data)

        p3 = figure(y_range=FactorRange(factors=age_categories), 
                    height=400, 
                    title="Jumlah Orang Terkena dan Tidak Terkena Penyakit Jantung Berdasarkan Umur",
                    tools="pan,wheel_zoom,box_zoom,reset,hover,save")

        p3.hbar_stack(['yes_cases', 'no_cases'], 
                      y='age_category', 
                      height=0.8, 
                      color=['#E4572E', '#4B8BBE'], # Warna yang lebih menarik
                      legend_label=["Yes", "No"], 
                      source=source_bokeh)

        p3.x_range.start = 0
        p3.xaxis.axis_label = "Jumlah Orang"
        p3.yaxis.axis_label = "Kelompok Umur"
        p3.legend.location = "top_right"
        p3.y_range.factors = age_categories[::-1] # Reverse order for display

        hover_tool = HoverTool()
        hover_tool.tooltips = [
            ("Kelompok Umur", "@age_category"),
            ("Penyakit Jantung (Ya)", "@yes_cases"),
            ("Penyakit Jantung (Tidak)", "@no_cases"),
            ("Total Kasus", "@total_cases")
        ]
        p3.add_tools(hover_tool)
        st.bokeh_chart(p3, use_container_width=True)
    else:
        st.info("Tidak ada data distribusi penyakit jantung berdasarkan kategori usia untuk filter yang dipilih.")
else:
    st.info("Tidak ada data yang tersedia untuk filter yang dipilih.")

# --- Visualisasi 4: Proporsi Penderita Penyakit Jantung berdasarkan Kebiasaan Merokok (Bar Chart) ---
st.subheader("4. Distribusi Penderita Penyakit Jantung berdasarkan Kebiasaan Merokok")
if not filtered_df.empty:
    heart_disease_df_smoking = filtered_df[filtered_df['HeartDisease'] == 'Yes']
    smoking_heart_disease = heart_disease_df_smoking['Smoking'].value_counts()
    
    if not smoking_heart_disease.empty:
        plot_data_smoking = pd.DataFrame({'Smoking': smoking_heart_disease.index.tolist(), 'Count': smoking_heart_disease.values})
        plot_data_smoking['Smoking'] = plot_data_smoking['Smoking'].replace({'Yes': 'Perokok', 'No': 'Bukan Perokok'})
        
        p4 = bokeh_barplot(plot_data_smoking, 'Smoking', 'Count', "Jumlah Penderita Penyakit Jantung berdasarkan Kebiasaan Merokok", "Status Merokok", "Jumlah Penderita", custom_colors=['#008080', '#FFD700'])
        st.bokeh_chart(p4, use_container_width=True)
    else:
        st.info("Tidak ada penderita penyakit jantung berdasarkan kebiasaan merokok untuk filter yang dipilih.")
else:
    st.info("Tidak ada data yang tersedia untuk filter yang dipilih.")

# --- Visualisasi 5: Proporsi Penderita Penyakit Jantung berdasarkan Kebiasaan Minum Alkohol (Bar Chart) ---
st.subheader("5. Distribusi Penderita Penyakit Jantung berdasarkan Kebiasaan Minum Alkohol")
if not filtered_df.empty:
    heart_disease_df_alcohol = filtered_df[filtered_df['HeartDisease'] == 'Yes']
    alcohol_counts = heart_disease_df_alcohol['AlcoholDrinking'].value_counts()

    if not alcohol_counts.empty:
        plot_data_alcohol = pd.DataFrame({'AlcoholDrinking': alcohol_counts.index.tolist(), 'Count': alcohol_counts.values})
        p5 = bokeh_barplot(plot_data_alcohol, 'AlcoholDrinking', 'Count', "Jumlah Penderita Penyakit Jantung berdasarkan Kebiasaan Minum Alkohol", "Status Minum Alkohol", "Jumlah Penderita", custom_colors=['#6A5ACD', '#DAA520'])
        st.bokeh_chart(p5, use_container_width=True)
    else:
        st.info("Tidak ada penderita penyakit jantung berdasarkan kebiasaan minum alkohol untuk filter yang dipilih.")
else:
    st.info("Tidak ada data yang tersedia untuk filter yang dipilih.")

# --- Visualisasi 6: Rata-rata Hari Sakit Fisik dan Mental berdasarkan Status Penyakit Jantung (Grouped Bar Plot Bokeh) ---
st.subheader("6. Rata-rata Hari Sakit Fisik dan Mental berdasarkan Status Penyakit Jantung")
if not filtered_df.empty:
    avg_health_data = filtered_df.groupby('HeartDisease')[['PhysicalHealth', 'MentalHealth']].mean().reset_index()
    
    if not avg_health_data.empty:
        # Melt the dataframe for Bokeh's grouped bars
        melted_avg_health = avg_health_data.melt(id_vars=['HeartDisease'], var_name='HealthType', value_name='AverageDays')
        
        # Create a combined category column for x-axis in Bokeh
        melted_avg_health['combined_category'] = list(zip(melted_avg_health['HeartDisease'], melted_avg_health['HealthType']))
        
        # Define x_range factors for grouped bars
        heart_disease_statuses = melted_avg_health['HeartDisease'].unique().tolist()
        health_types = ['PhysicalHealth', 'MentalHealth'] # Ensure order for consistent dodging

        x_factors_6 = [(status, h_type) for status in heart_disease_statuses for h_type in health_types]

        source_bokeh_6 = ColumnDataSource(melted_avg_health)

        p6 = figure(x_range=FactorRange(factors=x_factors_6), 
                    height=350, 
                    title="Rata-rata Hari Sakit Fisik dan Mental berdasarkan Status Penyakit Jantung",
                    tools="hover,pan,wheel_zoom,box_zoom,reset,save")

        p6.vbar(x='combined_category', # Use the combined category directly
                top='AverageDays', 
                width=0.7, # Lebar batang
                source=source_bokeh_6,
                legend_field='HealthType',
                fill_color=factor_cmap('HealthType', palette=['#9467bd', '#8c564b'], factors=health_types)) # Custom colors

        p6.x_range.range_padding = 0.1
        p6.xaxis.major_label_orientation = 0 # Label HeartDisease di bawah grup
        p6.xaxis.group_label_orientation = 0 # Label kelompok HealthType
        p6.xaxis.axis_label = "Status Penyakit Jantung"
        p6.yaxis.axis_label = "Rata-rata Jumlah Hari"
        p6.legend.location = "top_left"
        p6.legend.orientation = "horizontal"

        hover_tool_6 = HoverTool()
        hover_tool_6.tooltips = [
            ("Status Penyakit Jantung", "@HeartDisease"),
            ("Jenis Sakit", "@HealthType"),
            ("Rata-rata Hari", "@AverageDays{0.00}") # Format to 2 decimal places
        ]
        p6.add_tools(hover_tool_6)
        st.bokeh_chart(p6, use_container_width=True)
    else:
        st.info("Tidak ada data rata-rata hari sakit fisik dan mental untuk filter yang dipilih.")
else:
    st.info("Tidak ada data yang tersedia untuk filter yang dipilih.")


# --- Visualisasi 11: Distribusi Jam Tidur Berdasarkan Status Penyakit Jantung (Histogram Stacked Bokeh) ---
st.subheader("11. Distribusi Jam Tidur Berdasarkan Status Penyakit Jantung")
if not filtered_df.empty:
    bins_sleep = range(int(filtered_df['SleepTime'].min()), int(filtered_df['SleepTime'].max()) + 2)  # +2 agar bin terakhir masuk
    
    hist_yes, edges = np.histogram(filtered_df[filtered_df['HeartDisease'] == 'Yes']['SleepTime'], bins=bins_sleep)
    hist_no, _ = np.histogram(filtered_df[filtered_df['HeartDisease'] == 'No']['SleepTime'], bins=bins_sleep)
    
    hist_sleep_df = pd.DataFrame({
        'left': edges[:-1],
        'right': edges[1:],
        'yes_hist': hist_yes,
        'no_hist': hist_no
    })
    
    source_sleep_stacked = ColumnDataSource(hist_sleep_df)
    
    p11 = figure(height=350, title="Distribusi Jam Tidur Berdasarkan Status Penyakit Jantung",
                 tools="hover,pan,wheel_zoom,box_zoom,reset,save",
                 x_axis_label="Jam Tidur per Malam", y_axis_label="Jumlah Responden",
                 x_range=Range1d(0, 12))
    
    # Gambar histogram bertumpuk (stacked manually)
    p11.quad(top='no_hist', bottom=0, left='left', right='right',
             source=source_sleep_stacked, fill_color='#8FBC8F', legend_label="Tidak")

    p11.quad(top='yes_hist', bottom='no_hist', left='left', right='right',
             source=source_sleep_stacked, fill_color='#FFA07A', legend_label="Ya")

    p11.xaxis.ticker = list(range(0, 13))
    p11.legend.location = "top_right"
    
    hover_sleep_stacked = HoverTool(tooltips=[
        ("Rentang Jam Tidur", "@left{0} - @right{0} jam"),
        ("Jumlah Responden (Ya)", "@yes_hist"),
        ("Jumlah Responden (Tidak)", "@no_hist"),
        ("Total", "@{yes_hist}{0} + @{no_hist}{0}")
    ])
    p11.add_tools(hover_sleep_stacked)
    
    st.bokeh_chart(p11, use_container_width=True)
else:
    st.info("Tidak ada data yang tersedia untuk filter yang dipilih.")
