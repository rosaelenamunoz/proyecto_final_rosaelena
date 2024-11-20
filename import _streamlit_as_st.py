import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# Configuración inicial
st.set_page_config(page_title="Dashboard Sakila", layout="wide")

st.title("Dashboard de Alquileres - Base de Datos Sakila")
st.markdown("""
### Proyecto Final
Este dashboard permite analizar y visualizar datos sobre el comportamiento de los alquileres de películas.
""")

# Conexión y carga de datos
ruta_bd = 'sakila_master.db'
conn = sqlite3.connect(ruta_bd)

df_rental = pd.read_sql('SELECT * FROM rental', conn)
df_inventory = pd.read_sql('SELECT * FROM inventory', conn)
df_film = pd.read_sql('SELECT * FROM film', conn)
df_category = pd.read_sql('SELECT * FROM category', conn)
df_payment = pd.read_sql('SELECT * FROM payment', conn)
df_film_category = pd.read_sql('SELECT * FROM film_category', conn)

conn.close()

# Procesamiento inicial de datos
df_rental['rental_date'] = pd.to_datetime(df_rental['rental_date'])
df_rental_by_month = df_rental.groupby(df_rental['rental_date'].dt.to_period('M')).size().reset_index(name='count')
df_rental_by_month['rental_date'] = df_rental_by_month['rental_date'].dt.to_timestamp()

# Sidebar
st.sidebar.header("Filtros del Dashboard")

# Filtro: Rango de fechas
rango_fechas = st.sidebar.date_input(
    "Rango de Fechas",
    value=[df_rental['rental_date'].min(), df_rental['rental_date'].max()]
)

# Filtro: Categorías
categorias = df_category['name'].unique()
categoria_seleccionada = st.sidebar.multiselect(
    "Seleccionar categorías",
    options=categorias,
    default=categorias[:3]
)

# Aplicar filtros
# Aquí puedes personalizar más máscaras para ajustar datos filtrados.
datos_filtrados = df_rental_by_month  # Cambiar según las necesidades.

st.divider()

# Gráfico 1: Alquileres por mes
st.subheader("Número de Alquileres por Mes")
fig1 = px.line(
    df_rental_by_month,
    x='rental_date',
    y='count',
    title="Tendencia de Alquileres"
)
st.plotly_chart(fig1, use_container_width=True)

# Métricas rápidas
st.subheader("Métricas Rápidas")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="Total de Registros",
        value=len(df_rental),
        delta=f"{len(df_rental) - len(datos_filtrados)} menos filtrados"
    )

with col2:
    st.metric(
        label="Promedio de Alquileres Mensuales",
        value=f"{df_rental_by_month['count'].mean():.2f}"
    )

with col3:
    st.metric(
        label="Mes con más Alquileres",
        value=df_rental_by_month.loc[df_rental_by_month['count'].idxmax(), 'rental_date']
    )

st.divider()

# Gráfico 2: Popularidad de Categorías
st.subheader("Popularidad de Categorías de Películas")
df_film_category_merged = pd.merge(df_film_category, df_category, on='category_id')
df_category_popularity = df_film_category_merged.groupby('name').size().reset_index(name='total_rentals')
fig2 = px.bar(
    df_category_popularity,
    x='name',
    y='total_rentals',
    title="Categorías más Populares"
)
st.plotly_chart(fig2, use_container_width=True)

# Gráfico 3: Relación entre duración de películas y alquileres
st.subheader("Duración de Películas vs. Número de Alquileres")
df_inventory_merged = pd.merge(df_inventory, df_film, on='film_id')
df_rental_inventory = pd.merge(df_rental, df_inventory_merged, on='inventory_id')
df_duration_rental = df_rental_inventory.groupby('length').size().reset_index(name='total_rentals')
fig3 = px.scatter(
    df_duration_rental,
    x='length',
    y='total_rentals',
    title="Duración vs. Alquileres"
)
st.plotly_chart(fig3, use_container_width=True)

# Tabla interactiva
st.subheader("Tabla de Datos Filtrados")
st.dataframe(datos_filtrados)

# Efecto de nieve
if st.checkbox("Activar Efecto de Nieve"):
    st.snow()

st.divider()

st.write("Versión de Streamlit:", st.__version__)
