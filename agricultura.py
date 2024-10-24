import io
import os
import time
import warnings
import pandas as pd
import altair as alt
import streamlit as st
from dotenv import load_dotenv
from snowflake.snowpark import Session
from datetime import datetime, timedelta

warnings.filterwarnings("ignore", message="Bad owner or permissions on")

st.set_page_config(page_title="Gross Agricultural Production", page_icon="🌾", layout="wide")

if 'session' not in st.session_state:
    st.session_state.session = None
if 'last_activity_time' not in st.session_state:
    st.session_state.last_activity_time = datetime.now()

SESSION_TIMEOUT = timedelta(minutes=4)

def create_session(retries=3, wait=5):
    load_dotenv()

    private_key_path = os.getenv('SF_PRIVATE_KEY_PATH_1')
    
    if not private_key_path:
        raise ValueError("La ruta de la llave privada del usuario de servicio no está definida o está vacía.")

    with open(private_key_path, "rb") as key_file:
        private_key = key_file.read()

    session_config = {
        "account": os.getenv('SF_ACCOUNT'),
        "user": os.getenv('SF_USER'),
        "private_key": private_key,
        "private_key_passphrase": os.getenv('SF_PRIVATE_KEY_PASSPHRASE_2'),
        "database": os.getenv('SF_DATABASE'),
        "schema": os.getenv('SF_SCHEMA'),
        "warehouse": os.getenv('SF_WAREHOUSE'),
        "role": os.getenv('SF_ROLE'),
        "query_tag": "EXPORTATIONS_APP"
    }

    if any(value is None or value == '' for value in session_config.values()):
        raise ValueError("Una o más variables de entorno están indefinidas o vacías.")

    success = False

    for attempt in range(retries):
        try:
            session = Session.builder.configs(session_config).create()            
            success = True
            break 

        except Exception as e:
            print(f"Intento {attempt + 1} de {retries} fallido: \n{str(e)}")
            
            if attempt < retries - 1:
                time.sleep(wait)  
                
    if success:
        return session
    else:
        print("Todos los intentos de conexión fallaron.")
        return None

def check_session():
    if(datetime.now() - st.session_state.last_activity_time) > SESSION_TIMEOUT:
        st.session_state.session = None

def get_session_id(session):
    query = "SELECT CURRENT_SESSION() AS SESSION_ID;"
    result = session.sql(query).collect()
    session_id = result[0]['SESSION_ID']
    print(f"Session ID: {session_id}")

def fetch_data_for_countries(countries):
    check_session()
    get_session_id(st.session_state.session)
    all_dataframes = []  
    
    for country in countries:
        sql_query = f"""
        SELECT * FROM BASE_AGRICULTURA
        WHERE "Region" = '{country}'
        """
        
        df = st.session_state.session.sql(sql_query).to_pandas()
        all_dataframes.append(df)
    
    final_df = pd.concat(all_dataframes, ignore_index=True) 
    all_dataframes.clear()   
    return final_df.set_index("Region")

def get_list_of_all_countries():
    check_session()
    get_session_id(st.session_state.session)
    sql_query = f"""
    SELECT DISTINCT "Region" FROM BASE_AGRICULTURA
    """
    df = st.session_state.session.sql(sql_query).to_pandas()
    countries_list = df['Region'].tolist()
    return countries_list

def to_csv(df):
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    return buffer.getvalue()

def save_chart_as_png(chart):
    buffer = io.BytesIO()
    chart.save(buffer, format='png')
    buffer.seek(0)
    return buffer

def log_event(event_type, detail, unit):
    check_session()
    get_session_id(st.session_state.session)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    sql_query = f"""
    INSERT INTO SEGUIMIENTO_EVENTOS (TIPO_EVENTO, DETALLE_EVENTO, UNIDAD, FECHA_HORA, TAG)
    VALUES ('{event_type}', '{detail}', '{unit}', '{timestamp}', 'AGRICULTURE_APP')
    """
    st.session_state.session.sql(sql_query).collect()

def download_button(df, filename='data.csv', session=None, countries=None):
    csv = to_csv(df)
    
    def log_csv_download():
        if session and countries:
            log_event('Descarga', 'Archivo csv', ', '.join(countries))

    st.download_button(
        label="Download CSV",
        data=csv,
        file_name=filename,
        mime="text/csv",
        on_click=log_csv_download
    )

def download_chart_button(chart, session=None, countries=None):
    chart_image = save_chart_as_png(chart)
    
    def log_png_download():
        if session and countries:
            log_event('Descarga', 'Archivo png', ', '.join(countries))
    
    st.download_button(
        label="Download Chart as PNG",
        data=chart_image.getvalue(),
        file_name='chart.png',
        mime='image/png',
        on_click=log_png_download
    )

try:
    
    if not st.session_state.session:
            st.session_state.session = create_session()
            st.session_state.last_activity_time = datetime.now()
    
    countries = st.multiselect(
        "Choose countries",
        get_list_of_all_countries()
    )
    
    if not countries:
        st.error("Please select at least one country.")
    else:         
        df = fetch_data_for_countries(countries)
        
        if df.empty:
            st.write("No data available for the selected countries.")
        else:
            data = df
            data /= 1000000.0  
            st.write("### Gross Agricultural Production ($B)", data.sort_index())

            data = data.T.reset_index()
            data = pd.melt(data, id_vars=["index"]).rename(
                columns={"index": "year", "value": "Gross Agricultural Product ($B)"}
            )
            
            chart = (
                alt.Chart(data)
                .mark_area(opacity=0.3)
                .encode(
                    x="year:T",
                    y=alt.Y("Gross Agricultural Product ($B):Q", stack=None),
                    color="Region:N",
                )
            )
            
            st.altair_chart(chart, use_container_width=True)
            
            download_button(df, filename='gross_agricultural_production.csv', session=st.session_state.session, countries=countries)
            download_chart_button(chart, session=st.session_state.session, countries=countries)
            
            while True:
                check_session()

except Exception as e:
    st.error(f"**An error occurred.** Error details: {str(e)}")
