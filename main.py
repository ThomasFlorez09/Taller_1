import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import polars as pl
import plotly.express as px  

st.write("**Integrantes:** Thomas Flórez Mendoza - Sergio Vargas Cruz")

st.title("Métricas de evaluación para usuarios de Coink")

st.write("Coink es una plataforma financiera digital colombiana que se enfoca en fomentar el ahorro digital a través de su aplicación y red de cajeros electrónicos. Su objetivo principal es permitir a los usuarios guardar dinero de manera segura sin necesidad de una cuenta bancaria tradicional.")
st.write("Como equipo de IOT y de ciencias de datos, se nos solicita evaluar el desempeño de la compañía y analizar los mejores usuarios de Coink registrados en la base de depósitos correspondientes de la empresa (depositos_oink.csv). Para ello, se generan métrica que evalúe qué tan buenos son los usuarios de Coink, estableciendo criterios que reflejen su comportamiento financiero en la plataforma.")

df = pl.read_csv("depositos_oinks.csv")

st.subheader("Carga de la base de depositos de Coink (dataset)")
st.write("El datset correspondiente cuenta con 5 columnas que corresponden a las variables **user_id** (identificiación del usuario), **operation_value** (valor guardado en la transacción), **operation_date** (día y hora exacta de la operación), **maplocation_name** (ubicación del punto de recolección) y **user_createddate** (fecha y hora exacta de creación de usuario). "
"Por otro lado, se cuenta con 4345 filas que corresponden a transacciones realizadas. Los primeros datos del dataset se evidencian a continuación.")

st.dataframe(df.head(10))
num_users = df.select(pl.col("user_id").n_unique()).item()

st.write("El número de usuarios registrados en la plataforma es de", num_users)

df = df.with_columns(pl.col("operation_date").str.to_datetime("%Y-%m-%d %H:%M:%S"))

st.write("Para entender el panorama en el que se está trabajando, se procede a buscar el valor máximo y mínimo de transacciones que este registrado en la base de datos. Los valores correspondientes se presentan a continuación.")

max_transaction = df.select(pl.max("operation_value"))

# Obtener la transacción más baja
min_transaction = df.select(pl.min("operation_value"))

# Mostrar resultados
st.write("Transacción más alta:", max_transaction)
st.write("El valor máximo que se presenta entre todas las transacción es de 2.595.000")
st.write("Transacción más baja:", min_transaction)
st.write("El valor mínimo que se presenta entre todas las transacción es de 50")

st.write("Con el fin de evidenciar cuantas transacciones fueron realizadas bajo un monto significativo, se filtran las transacciones a aquellas cuyo valor sea mayor al de 100.000")

df_filtered = df.filter(pl.col("operation_value") > 100000)
st.dataframe(df_filtered)
num_users = df_filtered["user_id"].n_unique()
st.write(f"Después de filtrar los datos, fue posible evidenciar que de las 4345 transacciones registradas, unicamente {num_users} corresponde a transacciones cuyo monto es mayor a 100.000, es decir, unicamente el 5.24% de los datos.")

st.subheader("**Métrica de transacciones por usuario**")

st.write("Se realiza un conteo del número de transacciones realizadas para cada uno de los usuarios y se guardar en la variable **num_registros**, esto con el fin de evidenciar cuales son los usuarios que utilizan los servicios de Coink con mayor frecuencia. A continuación, se presenta un listado de los 10 usuarios que más transacciones registran.")

#Conteo de número de transacciones por usuario
user_counts = df.group_by("user_id").agg(pl.col("user_id").count().alias("num_registros"))

# Filtrar solo los usuarios con más de 1 registro
users_multiple_records = user_counts.filter(pl.col("num_registros") > 1).sort("num_registros", descending = True)

st.dataframe(users_multiple_records.head(10))

st.write("A continuación, se evidencia una gráfica de barras que permite evidenciar la información presentada anteriormente. En este caso es posible evidenciar que el usuario"
" 47e76d57-09d3-4ea4-8531-9b839d83069e es el que más a utilizado los registros de Coink con 61 operaciones.")

fig, ax = plt.subplots(figsize=(12, 6))
ax.bar(users_multiple_records["user_id"].cast(str)[:10], users_multiple_records["num_registros"][:10], color="royalblue")
plt.xlabel("User ID")

# Etiquetas y título
ax.set_xlabel("User ID")
ax.set_ylabel("Número de Transacciones")
ax.set_title("Top 10 Usuarios con más Transacciones")
ax.tick_params(axis='x', rotation=45)  # Rotar etiquetas del eje X

# Mostrar en Streamlit
st.pyplot(fig)

st.subheader("Métrica general de transacciones realizadas por usuario en el tiempo")

st.write("La caja que se evidencia en la parte inferior permite introducir el id de un usuario y se presenta de manera inmedita una gráfica que permite evidenciar cada una de las transacciones realizadas por el usuario, junto a la fecha y cantidad depositida correspondiente.")
# Seleccionar un usuario específico desde el dashboard
#user_ids = df["user_id"].unique().to_list()
#selected_user = st.selectbox("Seleccione un usuario:", user_ids)
#selected_user = "47e76d57-09d3-4ea4-8531-9b839d83069e"
selected_user = st.text_input("Ingrese el ID del usuario:")

# Filtrar datos del usuario seleccionado
df_user = df.filter(pl.col("user_id") == selected_user).sort("operation_date")

# Graficar los depósitos en el tiempo
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(df_user["operation_date"], df_user["operation_value"], marker="o", linestyle="-", color="b")
ax.set_xlabel("Fecha")
ax.set_ylabel("Cantidad Depositada")
ax.set_title(f"Depósitos de Usuario {selected_user}")
plt.xticks(rotation=45)

# Mostrar la gráfica en Streamlit
st.pyplot(fig)

#Sumar depositos de usuarios
df_users_savings = df.group_by("user_id").agg(pl.sum("operation_value").alias("total_savings"))
# Ordenar de mayor a menor ahorro
df_users_savings = df_users_savings.sort("total_savings", descending=True)

st.subheader("Métrica de usuarios con Mayor Ahorro")

st.write("Para identificar cuales usuarios son los que tienen los depositos generales con mayor cantidad de dinero ahorrada, por lo cual, se realiza la suma del dinero que ha depositado cada usuario en sus múltiples transacciones. "
"Un usuario con un alto ahorro acumulado podría considerarse más bueno en términos de uso de la plataforma y servicios de la empresa.")
st.write("A continuación se presentan los datos del ahorro total para cada usuario en la columna **total_savings**, así como la gráfica de barras que permite evidenciar los 10 usuarios que tienen un ahorro mayor.")

st.write(df_users_savings)

# Crear gráfico de barras
fig, ax = plt.subplots(figsize=(12, 6))
ax.bar(df_users_savings["user_id"].cast(str)[:10], df_users_savings["total_savings"][:10],  color="green")

# Etiquetas y título
ax.set_xlabel("User ID")
ax.set_ylabel("Total Ahorrado")
ax.set_title("Top 10 Usuarios con Más Ahorro")
ax.tick_params(axis='x', rotation=45)

# Mostrar gráfico en Streamlit
st.pyplot(fig)

st.write("En este caso, el usuario con el id 2df8831e-a37a-4ba7-b8f0-ec7c313d68af, es el presenta el ahorro más grande entre los registrados en la base de datos con un monto total de 7.032.500")

st.subheader("Métrica de usuarios con más tiempo activo en la plataforma")

st.write("Para una empresa es de gran importancia conocer durante cuanto tiempo ha estado activo un usuario en la plataforma y cuantos días han realizado depósitos, debido a que un usuario con mayor antigüedad y actividad podría considerarse muy valioso."
"Para esto, se ubicó la primera operación realizada por el usuario (independientemente de la fecha de registro, para saber el periodo ACTIVO) y la ultima fecha de operación con el fin de identificar la diferencia ente estos y los días únicos en los que este usuario ha realizado operaciones")

# Calcular primera y última transacción por usuario
df_usage = df.group_by("user_id").agg(pl.min("operation_date").alias("first_transaction"), pl.max("operation_date").alias("last_transaction"), pl.n_unique("operation_date").alias("unique_days_used"))

# Calcular el tiempo total de uso en días
df_usage = df_usage.with_columns((df_usage["last_transaction"] - df_usage["first_transaction"]).dt.total_days().alias("days_active"))

# Ordenar por mayor tiempo de uso
df_usage = df_usage.sort("days_active", descending=True)

st.write("A continuación, se presentan los 20 usuarios que presentan más días activos en la plataforma, además se presenta la gráfica de barras correspondiente a los datos que se presentan")

st.write(df_usage.head(20))

# Crear gráfico de barras
fig, ax = plt.subplots(figsize=(12, 6))
ax.bar(df_usage["user_id"].cast(str)[:20], df_usage["days_active"][:20], color="green")

# Etiquetas y título
ax.set_xlabel("User ID")
ax.set_ylabel("Días Activos en la Plataforma")
ax.set_title("Top 10 Usuarios con Mayor Tiempo de Uso")
ax.tick_params(axis='x', rotation=45)

# Mostrar gráfico en Streamlit
st.pyplot(fig)

st.write("Teniendo en cuenta la gráfica anterior, es posible analizar que si bien el usuario con id 1b9ac00c-adbe-431e-83de-5f5e538dca3d es el que lleva más días activo con 89 días, "
"este usuario unicamente a utilizado la plataforma 6 veces. Por otro lado, otros usuarios como el 640e5534-369f-43c3-b271-d3af80be37e5, el cual lleva 88 días activo pero a utilizado la plataforma 61 veces.")

st.write("Lo anterior nos permite identificar que el tiempo de permanencia en la plataforma no es proporcional al uso que el usuario pueda tener del servicio proporcionado.")

st.subheader("Identificación de los mejores usuarios a partir de las métricas establecidas")

st.write("Para establecer los mejores usuarios que se encuentran en la base de datos, se establece un Índice de Buen Usuario (IBU), el cual permite calificar a los usuarios que utilizan los servicios de COink a partir de diferentes parámetros que se han evidenciado anteriormente.")
st.write("Para esto, se realiza una normalización de los datos y se establecen los criterios de evaluación que se presenta a continuación.")
st.markdown("""
* Métrica de mayor ahorro por usuario (40%)
* Métrica de número de transacciones por usuario (30%)
* Métrica de días en los que se han hecho depositos (20%)
* Métrica de de activos por usuario (10%)
""")

st.write("A partir de los criterios de evaluación presentados anteriormente, se obtiene la calificación de IBU para cada uno de los usuarios y se establece en orden descente, esto con el fin de evidenciar los mejor 10 usuarios."
" A continuación, se presentan los datos y la gráfica correspondiente.")

# Combinar métricas clave
df_user_metrics = df_users_savings.join(users_multiple_records, on="user_id", how="inner")
df_user_metrics = df_user_metrics.join(df_usage, on="user_id", how="inner")

# Normalizar valores
df_user_metrics = df_user_metrics.with_columns([
    (pl.col("total_savings") / pl.max("total_savings")).alias("normalized_savings"),
    (pl.col("num_registros") / pl.max("num_registros")).alias("normalized_transactions"),
    (pl.col("unique_days_used") / pl.max("unique_days_used")).alias("normalized_days_active"),
    (pl.col("days_active") / pl.max("days_active")).alias("normalized_duration")
])

# Calcular puntuación final
df_user_metrics = df_user_metrics.with_columns(
    (
        0.4 * pl.col("normalized_savings") +
        0.3 * pl.col("normalized_transactions") +
        0.2 * pl.col("normalized_days_active") +
        0.1 * pl.col("normalized_duration")
    ).alias("user_score")
)

# Ordenar por mejor puntuación
df_user_metrics = df_user_metrics.sort("user_score", descending=True)

# Mostrar resultados
st.write("**Top 10 usuarios más valiosos según la métrica combinada:**", df_user_metrics.head(10))

fig, ax = plt.subplots(figsize=(12, 6))
ax.bar(df_user_metrics["user_id"].cast(str)[:10], df_user_metrics["user_score"][:10], color="purple")

ax.set_xlabel("User ID")
ax.set_ylabel("Puntuación del Usuario")
ax.set_title("Top 10 Mejores Usuarios")
ax.tick_params(axis='x', rotation=45)

st.pyplot(fig)

st.write("Teniendo en cuenta los datos que se presentan anteriormente, es posible identificar que, de acuerdo con la calificación obtenida para cada usuario según los depositos realizados en Coink, el mejor usuario registrado es el de id **2df8831e-a37a-4ba7-b8f0-ec7c313d68af**")

st.title("Métricas de uso de depositos y ubicaciones")

st.write("Como empresa, también es necesario analizar de que forma se distribuye la demanda del servicio en lo diferentes puntos de deposito. Por lo anterior, se establece una métrica que permita contar el número de transacciones en cada uno de los tres puntos, esto con el fin "
"de identificar posibles estrategias a futuro para la instalación de nuevos puntos de ahorro.")

# Contar transacciones por punto de depósito
df_locations = df.group_by("maplocation_name").agg(pl.count("operation_value").alias("num_transacciones")).sort("num_transacciones", descending=True)

# Mostrar las 10 ubicaciones con más transacciones
print(df_locations.head(10))

st.subheader("Puntos de Depósito con Más Transacciones")

# Mostrar tabla en Streamlit
st.write(df_locations.head())

# Crear gráfico circular
fig, ax = plt.subplots(figsize=(8, 8))  # Tamaño del gráfico circular

# Graficar el gráfico circular
ax.pie(
    df_locations["num_transacciones"],  # Valores (número de transacciones)
    labels=df_locations["maplocation_name"],  # Etiquetas (nombres de los puntos de depósito)
    autopct='%1.1f%%',  # Mostrar porcentajes con un decimal
    colors=plt.cm.Paired.colors,  # Paleta de colores
    startangle=90  # Iniciar el gráfico desde el ángulo 90°
)

# Título
ax.set_title("Top Puntos de Depósito con Más Transacciones")

# Mostrar gráfico en Streamlit
st.pyplot(fig)

st.write("Con base a la información presentada anteriormente, es posible evidenciar que el punto en el que se realizan más transacciones es el CC Plaza de las Américas  - Plaza Mariposa, seguido "
"por el CC Los Molinos - Zona Montaña Nivel 2 y la Universidad de los Andes - ML Piso 5, los cuales tienen 1976, 1894 y 475 y transacciones respectivamente")

df_savings = df.group_by("maplocation_name").agg(pl.sum("operation_value").alias("total_ahorrado")).sort("total_ahorrado", descending=True)

st.subheader("Puntos de Depósito con Mayores Ahorros")

st.write("Posteriormente, se establece revisa en que punto se presenta un mayor ahorro total. A continuación, se presentan los datos y la información correspondiente.")

# Crear gráfico de barras
fig, ax = plt.subplots(figsize=(12, 6))
ax.barh(df_savings["maplocation_name"][:10], 
        df_savings["total_ahorrado"][:10], 
        color="seagreen")

# Etiquetas y título
ax.set_xlabel("Total Ahorrado")
ax.set_ylabel("Punto de Depósito")
ax.set_title("Top Puntos de Depósito con Mayores Ahorros")
ax.invert_yaxis()  # Para ordenar de mayor a menor

# Mostrar gráfico en Streamlit
st.pyplot(fig)
st.write("Si bien el comportamiento presentado es similar al de la métrica anterior en cuanto al orden de las ubicaciones, en este caso se presenta una mayor diferencia en cuanto al dinero recaudado entre los dos "
"centros comerciales a pesar de que el número de transacciones realizadas en esto puntos es muy cercano. El CC Plaza de las Américas  - Plaza Mariposa presenta un mayor ahorro con 112.241.000 depositados en este punto.")

st.subheader("Métrica de número de transacciones realizadas por mes")

st.write("Finalmente, con el fin de analizar el comportameinto que tienen los usuarios para el uso de las alcancías en términos temporales, se establece una métrica que permita identificar en que meses se presenta un"
"mayor número de transacciones. La información correspondiente se presenta a continuación.")

df_extract = df.with_columns(df["operation_date"].dt.year().alias("year"), df["operation_date"].dt.month().alias("month"))

# Contar transacciones por mes
df_monthly = df_extract.group_by("month").agg(pl.count("operation_value").alias("transaction_count"))

# Ordenar por mes
df_monthly = df_monthly.sort("month")

st.write(df_monthly.head())

fig, ax = plt.subplots()
ax.pie(df_monthly["transaction_count"], labels=df_monthly["month"], autopct='%1.1f%%', colors=plt.cm.Paired.colors, startangle=90)

# Título
ax.set_title("Distribución de Transacciones por Mes")

# Mostrar en Streamlit
st.pyplot(fig)

st.write("Teniendo en cuenta lo anterior, el dataset únicamente cuenta con transacciones realizadas en Noviembre, Diciembre, Enero y Febrero. Además el mes en el que se presento un mayor número de deposito es en Febrero con 1446 transacciones realizadas en este periodo.")