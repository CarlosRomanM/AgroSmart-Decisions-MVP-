import streamlit as st
import pandas as pd
import base64
import numpy as np
import io
from datetime import datetime, timedelta
from pulp import LpProblem, LpMaximize, LpVariable, lpSum, LpStatus, value, LpBinary, PULP_CBC_CMD
import streamlit.components.v1 as components
import plotly.express as px
import plotly.graph_objects as go

# -------------------------------
# Configuración general de la página
# -------------------------------
# Aquí establezco el título y la disposición de la página de mi app para que tenga un diseño ancho y profesional
st.set_page_config(page_title="AgroSmart Decisions", layout="wide")

# -------------------------------
# CSS personalizado para sidebar y expanders
# -------------------------------
# Defino estilos para que el sidebar y las secciones desplegables tengan un aspecto verde y limpio, acorde a la temática agrícola
custom_styles = """
<style>
[data-testid="stSidebar"] > div:first-child {
    background-color: #AABFA4;
    padding: 2rem 1rem 1rem 1rem;
}
.sidebar-logo {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-bottom: 1.5rem;
}
.sidebar-logo img {
    max-width: 280px;
    height: auto;
}
div[data-testid="stExpander"] {
    border: 2px solid #AABFA4;
    border-radius: 10px;
    overflow: hidden;
    margin-bottom: 1em;
}
div[data-testid="stExpander"] > details > summary {
    background-color: #AABFA4 !important;
    color: black !important;
    font-weight: bold;
    padding: 0.75em 1em;
    font-size: 1.05em;
}
div[data-testid="stExpander"] > details > div {
    background-color: #f1f7ef !important;
    padding: 1em;
}
</style>
"""
# Aplico estos estilos a la app
st.markdown(custom_styles, unsafe_allow_html=True)

# -------------------------------
# Función para mostrar el logo en el sidebar
# -------------------------------
# Uso esta función para mostrar un logo codificado en base64, para que el sidebar tenga identidad visual consistente
def mostrar_logo_sidebar(ruta):
    with open(ruta, "rb") as f:
        imagen_base64 = base64.b64encode(f.read()).decode()
    logo_html = f"""
    <div class='sidebar-logo'>
        <img src="data:image/png;base64,{imagen_base64}" 
             alt="Logo AgroSmart"
             style="max-width: 180px; height: auto;">
    </div>
    """
    st.sidebar.markdown(logo_html, unsafe_allow_html=True)

mostrar_logo_sidebar("images/solo_logo1.png")

# -------------------------------
# Cargar equivalencias de provincias y zonas climáticas
# -------------------------------
# Intento cargar un archivo CSV para mapear provincias a zonas climáticas equivalentes.
# Esto me permite ajustar recomendaciones según condiciones regionales reales.
try:
    equivalencias = pd.read_csv("agro/data/equivalencias_provincias_clima.csv")
    equivalencias.columns = equivalencias.columns.str.strip()
    provincias_disponibles = sorted(equivalencias["Provincia_usuario"].dropna().unique().tolist())
    provincia_equivalencias = dict(zip(equivalencias["Provincia_usuario"].str.strip(), equivalencias["Provincia_equivalente"].str.strip()))
    provincia_zonaclimatica = dict(zip(equivalencias["Provincia_usuario"].str.strip(), equivalencias["Zona_climatica"].str.strip().str.lower()))
except Exception as e:
    # En caso de fallo, asigno valores por defecto para evitar que la app falle
    provincias_disponibles = ["Navarra", "Murcia", "Lleida"]
    provincia_equivalencias = {prov: prov for prov in provincias_disponibles}
    provincia_zonaclimatica = {prov: "mediterraneo" for prov in provincias_disponibles}
    st.warning(f"⚠️ No se pudo cargar el archivo de equivalencias. Usando valores por defecto. Detalle: {e}")

# -------------------------------
# Menú lateral para navegación
# -------------------------------
# Permito al usuario elegir entre Inicio, Acerca de y el formulario agrícola
menu = st.sidebar.radio("Navegacion", ["Inicio", "Acerca de", "Formulario Agricola Usuario"])

# -------------------------------
# Mostrar logo principal centrado
# -------------------------------
# Aquí muestro el logo grande en la parte superior central de la app para dar identidad visual
with open("images/logo_transp_verde.png", "rb") as f:
    logo_base64 = base64.b64encode(f.read()).decode()

st.markdown(f"""
    <div style='
        display: flex;
        justify-content: center;
        align-items: center;
        height: 240px;
        margin-top: -4rem;
        margin-bottom: 0.5rem;
    '>
        <img src="data:image/png;base64,{logo_base64}"
             alt="AgroSmart Decisions"
             style="max-width: 500px; height: auto;">
    </div>
""", unsafe_allow_html=True)

# -------------------------------
# Contenido dinámico según menú
# -------------------------------
if menu == "Inicio":
    st.subheader("🌱 ¡Bienvenido agricultor del futuro!")
    st.write("Selecciona una sección en el menú lateral para:")

    # Función para mostrar la imagen portada con marco verde y sombra elegante
    def mostrar_imagen_con_marco_verde(ruta_imagen, caption=""):
        with open(ruta_imagen, "rb") as f:
            img_bytes = f.read()
            encoded = base64.b64encode(img_bytes).decode()

        st.markdown(f"""
        <div style="padding: 1rem; background-color: #AABFA4; border-radius: 16px;
                    box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.1);
                    text-align: center; margin-top: 2rem; margin-bottom: 2rem;">
            <img src="data:image/png;base64,{encoded}" style="max-width: 100%; height: auto; border-radius: 8px;">
            <p style="color: #ffffff; font-size: 1.1em; margin-top: 0.5rem;">{caption}</p>
        </div>
        """, unsafe_allow_html=True)

    # ✅ LLAMADA CORRECTA FUERA DE LA FUNCIÓN
    mostrar_imagen_con_marco_verde("images/PORTADA_AGRO.PNG", caption="Cultivos en campo abierto")

# ==============================  # =============================== 
elif menu == "Acerca de":
    st.subheader("📘 Sobre AgroSmart Decisions")
    # Aquí explico en detalle qué es el proyecto, sus funcionalidades y valores
    st.markdown("""
    <p style='font-size: 1.1em;'>
        <strong>AgroSmart Decisions</strong> es una herramienta innovadora desarrollada con el objetivo de empoderar a agricultores, técnicos y cooperativas a través del análisis inteligente de datos. 
        En un contexto marcado por el cambio climático, la escasez de recursos y la necesidad de producir de manera más eficiente, AgroSmart ofrece un enfoque práctico y accesible para la toma de decisiones agrícolas.
    </p>

    <p style='font-size: 1.1em;'>
        Esta aplicación integra información real y actualizada sobre condiciones climáticas, características del suelo, demanda del mercado y disponibilidad de recursos como el agua y la maquinaria. 
        A través de algoritmos de optimización y análisis de datos, permite a los usuarios recibir recomendaciones de cultivo personalizadas y basadas en evidencia.
    </p>

    <ul style='padding-left: 1.2em; font-size: 1.05em;'>
        <li>📊 <strong>Análisis y procesamiento de datos agrícolas</strong></li>
        <li>🌾 <strong>Recomendaciones personalizadas según condiciones reales</strong></li>
        <li>💧 <strong>Optimización del uso del agua y recursos</strong></li>
        <li>🧠 <strong>Modelos inteligentes para maximizar beneficios</strong></li>
        <li>📥 <strong>Exportación de informes personalizables</strong></li>
    </ul>

    <p style='font-size: 1.05em;'>
        AgroSmart Decisions nace como un proyecto académico con vocación real. Su diseño modular y escalable permite integrarlo en múltiples contextos regionales o productivos.
    </p>

    <hr style='border: 1px solid #AABFA4; margin-top: 2em; margin-bottom: 1em;'>

    <h4 style='color: #4E5B48;'>📬 Contacto</h4>
    <p style='font-size: 1em;'>
        ¿Tienes dudas, sugerencias o deseas colaborar?<br>
        Puedes escribirme a: <strong>c.roman.monje@gmail.com</strong><br>
        También puedes seguir el proyecto en 
        <a href='https://github.com/CarlosRomanM/CarlosRomanM' target='_blank' style='color:#4E5B48; text-decoration: underline;'>GitHub</a>
    </p>
    """, unsafe_allow_html=True)

# ===============================  # =============================== 
if menu == "Formulario Agricola Usuario":
    st.subheader("Formulario del Usuario Agrícola")
    st.markdown("Introduce los siguientes datos para generar recomendaciones:")

    # Pedir superficie y opción de cultivo
    with st.expander("📏 Superficie y tipo de cultivo", expanded=True):
        superficie_ha = st.number_input(
            "Superficie total (ha)",
            min_value=0.1,
            max_value=10.0,
            step=0.1,
            value=0.5
        )
        cultivo_unico = st.radio("¿Preferencia por monocultivo o multicultivo?", ["Monocultivo", "Multicultivo"])

    # Condiciones de agua
    with st.expander("🚰 Condiciones de agua", expanded=True):
        acceso_agua = st.selectbox("Acceso a agua", ["bajo", "medio", "alto"])

    # Ubicación y tipo de suelo
    with st.expander("📍 Ubicación y suelo", expanded=True):
        provincia = st.selectbox("Provincia", provincias_disponibles)
        provincia_equiv = provincia_equivalencias.get(provincia)
        tipo_suelo = st.selectbox("Tipo de suelo", ["franco", "arcilloso", "arenoso", "franco-arcilloso", "franco-arenoso"])

    # Opción para permitir recomendaciones fuera de zona climática
    modo_flexible = st.checkbox("¿Permitir recomendaciones fuera de tu zona climática?", value=False)
    zona_climatica = provincia_zonaclimatica.get(provincia, "mediterraneo")

    # Botón para generar recomendaciones
    if st.button("Generar recomendaciones"):
        st.session_state["recomendaciones_generadas"] = True
        st.success("Datos guardados correctamente. Recomendaciones disponibles más abajo.")

    if st.session_state.get("recomendaciones_generadas"):

        # Muestro resumen de datos de usuario
        st.markdown(f"""
        <div style='
            border: 2px solid #AABFA4;
            border-radius: 12px;
            padding: 1.5em;
            background-color: #f9fdf7;
            margin-bottom: 1.5em;'>
            <h4 style='color: #4E5B48;'>🌿 Parámetros del usuario</h4>
            <ul style='list-style-type: none; padding-left: 0; font-size: 1.1em;'>
                <li><strong>Provincia:</strong> {provincia}</li>
                <li><strong>Tipo de suelo:</strong> {tipo_suelo}</li>
                <li><strong>Superficie:</strong> {superficie_ha} ha</li>
                <li><strong>Opción de cultivo:</strong> {cultivo_unico}</li>
                <li><strong>Zona climática:</strong> {zona_climatica}</li>
                <li><strong>Filtro climático flexible:</strong> {'Sí' if modo_flexible else 'No'}</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        # Cargo los datasets base
        cultivos_df = pd.read_csv("agro/data/cultivos_hortalizas_final.csv")
        demanda_df = pd.read_csv("agro/data/demanda_clientes.csv")
        terreno_df = pd.read_csv("agro/data/terreno_suelo_final.csv")

        # Calculo rendimiento por metro cuadrado para cálculos posteriores
        cultivos_df["Rendimiento_kg_m2"] = cultivos_df["Rendimiento_promedio (kg/ha)"].fillna(0) / 10000

        # Flag para modo debug (mensajes técnicos)
        modo_debug = False


  # ===============================  # ===============================  # ===============================  # ===============================
        
        if cultivo_unico == "Multicultivo":
            # Importo la función principal que ejecuta el modelo de optimización para multicultivo
            from app.multicultivo_module import ejecutar_modelo_multicultivo
            
            # Ejecuto el modelo pasando todos los datos relevantes y condiciones del usuario
            # El modelo me devuelve un DataFrame con resultados, el estado de la optimización y el beneficio total
            df_resultados, estado, beneficio = ejecutar_modelo_multicultivo(
                cultivos_df, demanda_df, terreno_df,
                superficie_ha, tipo_suelo, acceso_agua,
                provincia_equiv, zona_climatica,
                modo_flexible,
                debug=modo_debug  # Pasa flag para activar mensajes técnicos en modo debug
            )
            
            # Verifico si obtuve resultados válidos; si no, aviso al usuario que no hay cultivos que cumplan las condiciones
            if df_resultados is None or df_resultados.empty:
                st.warning("⚠️ No hay cultivos que coincidan con tus condiciones actuales o el modelo no encontró solución óptima.")
            else:
                # Si estoy en modo debug, muestro información técnica sobre la ejecución y resultados
                if modo_debug:
                    st.markdown("🔍 Iniciando modelo multicultivo...")
                    st.markdown(f"🌦️ Zona climática asignada: {zona_climatica}")
                    st.markdown(f"💧 Nivel de agua del usuario: {acceso_agua}")
                    st.markdown(f"📌 Estado del modelo: {estado}")
                    st.markdown(f"💰 Beneficio total anual optimizado: € {beneficio:,.2f}")
                
                # Preparación para mostrar el calendario anual de siembra y cosecha
                st.markdown("### 🗓️ Calendario estimado anual de siembra y cosecha")
                
                # Normalizo nombres de cultivos en ambos DataFrames para asegurar coincidencias
                cultivos_df["Nombre_cultivo"] = cultivos_df["Nombre_cultivo"].str.strip().str.lower()
                df_resultados["Cultivo"] = df_resultados["Cultivo"].str.strip().str.lower()
                
                # Obtengo la duración en días de cada cultivo desde cultivos_df y la asigno a df_resultados
                df_duracion = cultivos_df.set_index("Nombre_cultivo")["Duración_cultivo_días"].to_dict()
                df_resultados["Duracion_dias"] = df_resultados["Cultivo"].map(df_duracion)
                
                # Función para estimar fecha de inicio a partir del mes (usando año fijo 2025)
                def estimar_inicio(mes):
                    try:
                        return datetime(2025, int(mes), 1)
                    except:
                        return pd.NaT
                
                # Calculo fechas de inicio y fin del ciclo para cada cultivo y mes
                df_resultados["Inicio"] = df_resultados["Mes"].apply(estimar_inicio)
                df_resultados["Fin"] = df_resultados.apply(
                    lambda row: row["Inicio"] + timedelta(days=int(row["Duracion_dias"])) if pd.notnull(row["Inicio"]) else pd.NaT,
                    axis=1
                )
                
                # Preparo el DataFrame para mostrar calendario, ordenando y limpiando datos
                calendario_multi = df_resultados.dropna(subset=["Inicio", "Fin"])[["Cultivo", "Inicio", "Fin"]].copy()
                calendario_multi["Cultivo"] = calendario_multi["Cultivo"].str.capitalize()
                calendario_multi = calendario_multi.sort_values("Inicio")
                
                # Si hay datos para mostrar, genero el gráfico timeline con Plotly
                if not calendario_multi.empty:
                    fig2 = px.timeline(
                        calendario_multi,
                        x_start="Inicio",
                        x_end="Fin",
                        y="Cultivo",
                        color="Cultivo",
                        title="Calendario anual Multicultivo"
                    )
                    fig2.update_yaxes(autorange="reversed")
                    fig2.update_layout(height=420, margin=dict(l=0, r=0, t=50, b=0))
                    st.plotly_chart(fig2, use_container_width=True)
                    
                    # También muestro la tabla con fechas en formato legible (dd/mm)
                    calendario_mostrar = calendario_multi.copy()
                    calendario_mostrar["Inicio"] = calendario_mostrar["Inicio"].dt.strftime("%d/%m")
                    calendario_mostrar["Fin"] = calendario_mostrar["Fin"].dt.strftime("%d/%m")
                    
                    st.markdown("### 📅 Fechas de siembra y cosecha ", unsafe_allow_html=True)
                    st.markdown("#####  Recomendación de fechas válidas ", unsafe_allow_html=True)
                    st.markdown("""
                        <style>
                        thead tr th {
                            background-color: #AABFA4;
                            color: #1e1e1e;
                            font-weight: bold;
                            text-align: center;
                        }
                        tbody tr td {
                            text-align: center;
                        }
                        </style>
                    """, unsafe_allow_html=True)
                    st.dataframe(calendario_mostrar, use_container_width=True)
                else:
                    st.warning("⚠️ No se pudieron estimar fechas para los cultivos seleccionados.")
                
                # Visualización del uso del terreno con un treemap para entender la distribución por cultivo
                st.markdown("### 🌾 Visualización de uso del terreno por cultivo")
                superficie_por_cultivo = df_resultados.groupby("Cultivo")["Superficie_ha"].sum().reset_index()
                superficie_por_cultivo["Cultivo"] = superficie_por_cultivo["Cultivo"].str.capitalize()
                
                fig_treemap = px.treemap(
                    superficie_por_cultivo,
                    path=["Cultivo"],
                    values="Superficie_ha",
                    color="Superficie_ha",
                    color_continuous_scale="Greens",
                    title="🧭 Distribución de la superficie total por cultivo."
                )
                fig_treemap.update_traces(textinfo="label+value+percent entry")
                fig_treemap.update_layout(margin=dict(t=50, l=10, r=10, b=10))
                st.plotly_chart(fig_treemap, use_container_width=True, key="grafico_treemap")
                
                # Calculo estimado del número de plantas por cultivo para dimensionar recursos
                unidades_dict = cultivos_df.set_index("Nombre_cultivo")["Unidades_m2"].to_dict()
                df_resultados["Unidades_m2"] = df_resultados["Cultivo"].map(unidades_dict)
                df_resultados["Plantas estimadas"] = (df_resultados["Superficie_ha"] * 10000 * df_resultados["Unidades_m2"]).fillna(0).astype(int)
                
                # Agrupo datos para crear un resumen con producción, beneficio, superficie, duración y plantas estimadas
                resumen = df_resultados.groupby("Cultivo").agg(
                    Total_kg=("Cantidad_kg", "sum"),
                    Total_beneficio=("Beneficio_€", "sum"),
                    Total_superficie_ha=("Superficie_ha", "sum"),
                    Duracion_dias=("Duracion_dias", "mean"),
                    Plantas_estimadas=("Plantas estimadas", "sum")
                ).reset_index()
                
                # Presento recomendaciones visuales para cada cultivo en forma de tarjetas
                st.markdown("### 🪴 Resultados personalizados por cultivo")
                st.markdown("#####  🎋 Tarjetas de cultivo ")
                
                # Diccionario de emojis para darle personalidad visual a cada cultivo
                iconos_por_cultivo = {
                    "Tomate": "🍅", "Lechuga": "🥬", "Zanahoria": "🥕", "Cebolla": "🧅", "Ajo": "🧄", "Pimiento": "🌶️",
                    "Pepino": "🥒", "Calabacín": "🥒", "Berenjena": "🍆", "Espinaca": "🥬", "Repollo": "🥬", "Brócoli": "🥦",
                    "Coliflor": "🥦", "Alcachofa": "🥬", "Guisante": "🌱", "Habas": "🌱", "Nabo": "🌰", "Rábano": "🌰",
                    "Apio": "🥬", "Remolacha": "🫒", "Judía verde": "🌿", "Escarola": "🥬", "Endivia": "🥬", "Acelga": "🥬",
                    "Col rizada": "🥬", "Pepinillo": "🥒", "Puerro": "🧅", "Bledo": "🌿", "Mostaza verde": "🌿", "Berro": "🌿",
                    "Acelga de verano": "🥬", "Achicoria": "🥬", "Berza": "🥬", "Canónigos": "🥬", "Cardo": "🌿",
                    "Coles de Bruselas": "🥬", "Mizuna": "🌿", "Pak Choi": "🥬", "Rúcula": "🌿"
                }
                
                # Identifico el cultivo más rentable para destacarlo con una estrella
                cultivo_top = resumen.loc[resumen["Total_beneficio"].idxmax(), "Cultivo"]
                
                # Organizo las tarjetas en filas de 4 columnas para una presentación ordenada
                n_col = 4
                filas = [resumen[i:i + n_col] for i in range(0, resumen.shape[0], n_col)]
                
                # Itero cada fila y cada cultivo para construir las tarjetas con datos relevantes
                for fila in filas:
                    cols = st.columns(len(fila))
                    for i, (_, row) in enumerate(fila.iterrows()):
                        cultivo = row["Cultivo"].capitalize()
                        icono = iconos_por_cultivo.get(cultivo, "🌿")
                        estrella = " ⭐" if cultivo == cultivo_top else ""
                        duracion = int(row["Duracion_dias"]) if not pd.isna(row["Duracion_dias"]) else 90
                        ciclos = int(365 / duracion)
                        produccion_mensual = row["Total_kg"] / 12
                        beneficio_mensual = row["Total_beneficio"] / 12
                        plantas = row.get("Plantas_estimadas", 0)
                        
                        # Construyo la tarjeta en HTML con estilos para mostrar la información detallada
                        with cols[i]:
                            st.markdown(f"""
                            <div style="background-color: #B0C8B4; border: 3px solid #2f4030; border-radius: 16px; padding: 1.2rem; color: white; text-align: center;
                                        box-shadow: 1px 1px 6px rgba(0,0,0,0.1); height: 660px; font-family: 'Segoe UI', sans-serif;">
                            <div style='font-size: 1.2rem;'>{icono}{estrella}</div>
                            <h4 style="margin: 0.5rem 0 0.8rem;">{cultivo}</h4>
                            <div style="margin-bottom: 0.6rem;">
                                <p style="margin-bottom: 0.2rem; color: #2f4030; font-weight: bold;">Duración del ciclo</p>
                                <p>{duracion} días</p>
                            </div>
                            <div style="margin-bottom: 0.6rem;">
                                <p style="margin-bottom: 0.2rem; color: #2f4030; font-weight: bold;">Ciclos por año</p>
                                <p>{ciclos}</p>
                            </div>
                            <div style="margin-bottom: 0.6rem;">
                                <p style="margin-bottom: 0.2rem; color: #2f4030; font-weight: bold;">Plantas estimadas</p>
                                <p>{plantas:,} unidades</p>
                            </div>
                            <div style="margin-bottom: 0.6rem;">
                                <p style="margin-bottom: 0.2rem; color: #2f4030; font-weight: bold;">Producción mensual</p>
                                <p>{produccion_mensual:,.0f} kg</p>
                            </div>
                            <div style="margin-bottom: 0.6rem;">
                                <p style="margin-bottom: 0.2rem; color: #2f4030; font-weight: bold;">Producción total</p>
                                <p>{row['Total_kg']:,.0f} kg</p>
                            </div>
                            <div style="margin-bottom: 0.6rem;">
                                <p style="margin-bottom: 0.2rem; color: #2f4030; font-weight: bold;">Beneficio mensual</p>
                                <p>€ {beneficio_mensual:,.2f}</p>
                            </div>
                            <div style="margin-bottom: 0.6rem;">
                                <p style="margin-bottom: 0.2rem; color: #2f4030; font-weight: bold;">Beneficio Anual</p>
                                <p>€ {row['Total_beneficio']:,.2f}</p>
                            </div>
                            </div>
                            """, unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
                
                # Muestro un DataFrame con el resumen de datos para consulta tabular
                st.markdown("### 📊 Datos Obtenidos por cultivo")
                st.dataframe(resumen, use_container_width=True)
                
                # Muestro una gráfica de barras para comparar producción y beneficio entre cultivos
                st.markdown("### 📊 Comparativa visual por cultivo")
                resumen_melted = resumen.melt(id_vars="Cultivo", value_vars=["Total_kg", "Total_beneficio"])
                fig_resumen = px.bar(
                    resumen_melted,
                    x="Cultivo",
                    y="value",
                    color="variable",
                    barmode="group",
                    title="Representación por cultivo"
                )
                fig_resumen.update_layout(xaxis_title="Cultivo", yaxis_title="Valor", height=420)
                st.plotly_chart(fig_resumen, use_container_width=True)
                
                # Preparo y ofrezco descarga del resultado completo en un archivo Excel con timestamp
                output = io.BytesIO()
                nombre_archivo = f"recomendacion_multicultivo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                    df_resultados.to_excel(writer, index=False, sheet_name="Multicultivo")
                st.download_button(
                    label="🗓️ Descargar resultados en Excel",
                    data=output.getvalue(),
                    file_name=nombre_archivo,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
                # Finalmente, muestro un recuadro con el beneficio total optimizado para que el usuario lo tenga presente
                st.markdown(f"""
                <div style='
                    background-color: #DCEFD9;
                    border: 2px solid #37572F;
                    border-radius: 10px;
                    padding: 1.2rem;
                    text-align: center;
                    font-size: 1.4em;
                    font-weight: bold;
                    color: #2f4030;
                    box-shadow: 1px 2px 6px rgba(0,0,0,0.1);'>
                💰 Beneficio total anual optimizado: € {beneficio:,.2f}
                </div>
                """, unsafe_allow_html=True)



 # =============================== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== =====                

        elif cultivo_unico == "Monocultivo":
            # Importo la función principal que genera las propuestas de cultivo para monocultivo
            from app.monocultivo_module import generar_propuestas_monocultivo
            
            # Ejecuto la función con los datos de cultivos, demanda, terreno y superficie del usuario
            df_monocultivo = generar_propuestas_monocultivo(
                cultivos_df, demanda_df, terreno_df, superficie_ha
            )
            
            # Muestro un título para la sección de propuestas de monocultivo más rentables
            st.markdown("## 🌾 Propuestas de monocultivo más rentables")
            
            # Si no se obtienen resultados válidos, aviso al usuario con una advertencia
            if df_monocultivo is None or df_monocultivo.empty:
                st.warning("⚠️ No se encontraron cultivos válidos para monocultivo con las condiciones actuales.")
            else:
                # Normalizo los nombres de cultivos para evitar errores por diferencias de tildes o mayúsculas/minúsculas
                import unicodedata
                def quitar_tildes(texto):
                    if isinstance(texto, str):
                        # Utilizo unicodedata para eliminar tildes y otros acentos
                        return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
                    return texto
                
                cultivos_df["Nombre_cultivo"] = cultivos_df["Nombre_cultivo"].str.strip().str.lower().apply(quitar_tildes)
                df_monocultivo["Cultivo"] = df_monocultivo["Cultivo"].str.strip().str.lower().apply(quitar_tildes)
                
                # Compruebo si el DataFrame tiene la columna de duración del ciclo y, si no, la agrego
                if "Duración del ciclo (días)" not in df_monocultivo.columns:
                    if "Duración_cultivo_días" in cultivos_df.columns:
                        duraciones = cultivos_df.set_index("Nombre_cultivo")["Duración_cultivo_días"].to_dict()
                        df_monocultivo["Duración del ciclo (días)"] = df_monocultivo["Cultivo"].map(duraciones)
                    else:
                        # Si no encuentro la columna, asigno 90 días como valor por defecto y aviso
                        st.warning("⚠️ No se encontró la columna 'Duración_cultivo_días'. Se usará 90 días por defecto.")
                        df_monocultivo["Duración del ciclo (días)"] = 90
                    
                    # Calculo métricas derivadas útiles para análisis y visualización
                    df_monocultivo["Ciclos por año"] = (365 / df_monocultivo["Duración del ciclo (días)"]).apply(np.floor).astype(int)
                    df_monocultivo["Producción total anual (kg)"] = df_monocultivo["Producción (kg)"] * df_monocultivo["Ciclos por año"]
                    df_monocultivo["Beneficio total anual (€)"] = df_monocultivo["Beneficio estimado (€)"] * df_monocultivo["Ciclos por año"]
                    df_monocultivo["Producción mensual promedio (kg)"] = df_monocultivo["Producción total anual (kg)"] / 12
                    df_monocultivo["Beneficio mensual promedio (€)"] = df_monocultivo["Beneficio total anual (€)"] / 12
                
                # Calculo el número estimado de plantas a partir de las unidades por metro cuadrado y superficie
                if "Unidades_m2" in cultivos_df.columns:
                    unidades_dict = cultivos_df.set_index("Nombre_cultivo")["Unidades_m2"].to_dict()
                    df_monocultivo["Unidades_m2"] = df_monocultivo["Cultivo"].map(unidades_dict)
                    df_monocultivo["Plantas estimadas"] = (df_monocultivo["Superficie (ha)"] * 10000 * df_monocultivo["Unidades_m2"]).astype(int)
                else:
                    # Si no encuentro la columna necesaria, aviso y asigno cero a plantas estimadas
                    st.warning("⚠️ No se encontró la columna 'Unidades_m2'. No se puede calcular plantas estimadas.")
                    df_monocultivo["Plantas estimadas"] = 0
                
                # =======================
                # Construcción del calendario visual para monocultivo
                # =======================
                st.markdown("### 📅 Fechas de siembra y cosecha")
                
                # Función auxiliar para convertir fechas en texto a objetos datetime con año base fijo
                def convertir_fecha(fecha_texto, año_base=2025):
                    try:
                        if isinstance(fecha_texto, str):
                            fecha_texto = fecha_texto.strip().replace("/", "-")
                            dia, mes = map(int, fecha_texto.split("-"))
                            return datetime(año_base, mes, dia)
                    except:
                        return pd.NaT
                    return pd.NaT
                
                # Normalizo nombres para asegurar coincidencias en ambas tablas
                cultivos_df["Nombre_cultivo"] = cultivos_df["Nombre_cultivo"].str.strip().str.lower()
                df_monocultivo["Cultivo"] = df_monocultivo["Cultivo"].str.strip().str.lower()
                
                # Convierto las columnas de fechas de siembra y cosecha a datetime para visualización
                cultivos_df["Fecha_siembra"] = cultivos_df["Fecha_siembra"].astype(str).str.strip()
                cultivos_df["Fecha_cosecha"] = cultivos_df["Fecha_cosecha"].astype(str).str.strip()
                cultivos_df["Fecha_siembra_dt"] = cultivos_df["Fecha_siembra"].apply(convertir_fecha)
                cultivos_df["Fecha_cosecha_dt"] = cultivos_df["Fecha_cosecha"].apply(convertir_fecha)
                
                # Filtro cultivos usados en la propuesta para construir calendario personalizado
                cultivos_usados = df_monocultivo["Cultivo"].unique()
                df_calendario = cultivos_df[cultivos_df["Nombre_cultivo"].isin(cultivos_usados)].copy()
                df_calendario = df_calendario[["Nombre_cultivo", "Fecha_siembra_dt", "Fecha_cosecha_dt"]]
                df_calendario.columns = ["Cultivo", "Inicio", "Fin"]
                df_calendario = df_calendario.dropna()
                
                # Formateo fechas para mostrar tabla legible con estilos CSS
                df_mostrar = df_calendario.copy()
                df_mostrar["Inicio"] = df_mostrar["Inicio"].dt.strftime("%d/%m")
                df_mostrar["Fin"] = df_mostrar["Fin"].dt.strftime("%d/%m")
                st.markdown("""
                    <style>
                    thead tr th {
                        background-color: #AABFA4;
                        color: #1e1e1e;
                        font-weight: bold;
                        text-align: center;
                    }
                    tbody tr td {
                        text-align: center;
                    }
                    </style>
                """, unsafe_allow_html=True)
                st.dataframe(df_mostrar, use_container_width=True)
                
                # Genero gráfico timeline con fechas de siembra y cosecha por cultivo
                st.markdown("### 📅 Calendario anual de siembra y cosecha")
                if not df_calendario.empty:
                    fig = px.timeline(
                        df_calendario,
                        x_start="Inicio",
                        x_end="Fin",
                        y="Cultivo",
                        color="Cultivo",
                        title="Calendario anual Monocultivo",
                    )
                    fig.update_yaxes(autorange="reversed")
                    fig.update_layout(height=420, margin=dict(l=0, r=0, t=50, b=0))
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("⚠️ No se encontraron cultivos con fechas válidas para mostrar el calendario.")
                
                # Preparación y descarga del archivo Excel con los resultados del monocultivo
                output_mono = io.BytesIO()
                nombre_archivo_mono = f"recomendacion_monocultivo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                with pd.ExcelWriter(output_mono, engine="xlsxwriter") as writer:
                    df_monocultivo.to_excel(writer, index=False, sheet_name="Monocultivo")
                
                st.download_button(
                    label="📥 Descargar resultados en Excel",
                    data=output_mono.getvalue(),
                    file_name=nombre_archivo_mono,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
                # =======================
                # Recomendaciones visuales por cultivo (tarjetas con detalles)
                # =======================
                st.markdown("## 🪴 Recomendaciones visuales por cultivo")
                st.markdown("##### 🎋 Tarjetas de cultivo")
                
                # Diccionario de emojis para representar visualmente cada cultivo
                iconos_por_cultivo = {
                    "Tomate": "🍅", "Lechuga": "🥬", "Zanahoria": "🥕", "Cebolla": "🧅", "Ajo": "🧄", "Pimiento": "🌶️",
                    "Pepino": "🥒", "Calabacín": "🥒", "Berenjena": "🍆", "Espinaca": "🥬", "Repollo": "🥬", "Brócoli": "🥦",
                    "Coliflor": "🥦", "Alcachofa": "🥬", "Guisante": "🌱", "Habas": "🌱", "Nabo": "🌰", "Rábano": "🌰",
                    "Apio": "🥬", "Remolacha": "🫒", "Judía verde": "🌿", "Escarola": "🥬", "Endivia": "🥬", "Acelga": "🥬",
                    "Col rizada": "🥬", "Pepinillo": "🥒", "Puerro": "🧅", "Bledo": "🌿", "Mostaza verde": "🌿", "Berro": "🌿",
                    "Acelga de verano": "🥬", "Achicoria": "🥬", "Berza": "🥬", "Canónigos": "🥬", "Cardo": "🌿",
                    "Coles de Bruselas": "🥬", "Mizuna": "🌿", "Pak Choi": "🥬", "Rúcula": "🌿"
                }
                
                # Identifico el cultivo con mayor beneficio anual para destacarlo con una estrella
                cultivo_top = df_monocultivo.loc[df_monocultivo["Beneficio total anual (€)"].idxmax(), "Cultivo"]
                
                # Organizo los cultivos en filas de 4 columnas para mostrar tarjetas ordenadas
                n_col = 4
                rows = [df_monocultivo[i:i + n_col] for i in range(0, df_monocultivo.shape[0], n_col)]
                
                # Construyo cada tarjeta con información clave para el usuario
                for fila in rows:
                    cols = st.columns(len(fila))
                    for i, (_, row) in enumerate(fila.iterrows()):
                        cultivo = row["Cultivo"]
                        icono = iconos_por_cultivo.get(cultivo, "🌿")
                        estrella = " ⭐" if cultivo == cultivo_top else ""
                        
                        with cols[i]:
                            st.markdown(f"""
                            <div style="background-color: #AABFA4; border: 3px solid #2f4030; border-radius: 16px; padding: 1.2rem; color: white; text-align: center;
                                        box-shadow: 1px 1px 6px rgba(0,0,0,0.1); height: 650px; font-family: 'Segoe UI', sans-serif;">
                            
                            <div style='font-size: 1.2rem;'>{icono}{estrella}</div>
                            <h4 style="margin: 0.5rem 0 0.8rem;">{cultivo}</h4>
                            
                            <div style="margin-bottom: 0.6rem;">
                                <p style="margin-bottom: 0.2rem; color: #2f4030; font-weight: bold;">Duración del ciclo</p>
                                <p>{int(row['Duración del ciclo (días)'])} días</p>
                            </div>
                            <div style="margin-bottom: 0.6rem;">
                                <p style="margin-bottom: 0.2rem; color: #2f4030; font-weight: bold;">Ciclos por año</p>
                                <p>{int(row['Ciclos por año'])}</p>
                            </div>
                            <div style="margin-bottom: 0.6rem;">
                                <p style="margin-bottom: 0.2rem; color: #2f4030; font-weight: bold;">Plantas estimadas</p>
                                <p>{int(row.get('Plantas estimadas', 0)):,} unidades</p>
                            </div>
                            <div style="margin-bottom: 0.6rem;">
                                <p style="margin-bottom: 0.2rem; color: #2f4030; font-weight: bold;">Producción mensual</p>
                                <p>{row['Producción mensual promedio (kg)']:,.0f} kg</p>
                            </div>
                            <div style="margin-bottom: 0.6rem;">
                                <p style="margin-bottom: 0.2rem; color: #2f4030; font-weight: bold;">Producción total</p>
                                <p>{row['Producción total anual (kg)']:,.0f} kg</p>
                            </div>
                            <div style="margin-bottom: 0.6rem;">
                                <p style="margin-bottom: 0.2rem; color: #2f4030; font-weight: bold;">Beneficio mensual</p>
                                <p>€ {row['Beneficio mensual promedio (€)']:,.2f}</p>
                            </div>
                            <div>
                                <p style="margin-bottom: 0.2rem; color: #2f4030; font-weight: bold;">Beneficio Anual</p>
                                <p>€ {row['Beneficio total anual (€)']:,.2f}</p>
                            </div>
                            </div>
                            """, unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
                
                # =======================
                # Gráfico resumen final comparativo
                # =======================
                st.markdown("### 📊 Comparativa visual por cultivo")
                
                resumen_mono = df_monocultivo[[
                    "Cultivo", 
                    "Producción total anual (kg)", 
                    "Beneficio total anual (€)", 
                ]].copy()
                
                resumen_melted = resumen_mono.melt(
                    id_vars="Cultivo", 
                    value_vars=[
                        "Producción total anual (kg)", 
                        "Beneficio total anual (€)", 
                    ],
                    var_name="Variable", 
                    value_name="Valor"
                )
                
                fig_resumen_mono = px.bar(
                    resumen_melted,
                    x="Cultivo",
                    y="Valor",
                    color="Variable",
                    barmode="group",
                    title=" Cultivos monocultivos"
                )
                
                fig_resumen_mono.update_layout(
                    xaxis_title="Cultivo",
                    yaxis_title="Valor",
                    height=420,
                    plot_bgcolor='#F2F7F1',      # Fondo igual que el sidebar
                    paper_bgcolor='#F2F7F1',     # También el lienzo externo
                    font=dict(color="#2f4030"),
                    margin=dict(l=0, r=0, t=50, b=0)
                )
                
                # Finalmente muestro el gráfico en Streamlit
                st.plotly_chart(fig_resumen_mono, use_container_width=True)
