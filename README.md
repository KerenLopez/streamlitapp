# Miniaplicativos: `agricultura.py` y `exportaciones.py`

Este repositorio contiene dos scripts de Python, `agricultura.py` y `exportaciones.py`, diseñados para interactuar con datos almacenados en Snowflake. Los scripts están destinados a procesar y analizar datos agrícolas y de exportaciones, respectivamente.

## Requisitos Previos

Este proyecto fue creado con la versión 3.8.19 de Python. Antes de ejecutar los scripts, asegúrate de tener instaladas las siguientes dependencias (lo ideal sería que crees un entorno de conda para realizarlo):

- **Snowflake Connector for Python** (`snowflake-connector-python[pandas]`)
- **Snowpark for Python** (`snowflake-snowpark-python`)
- **Pandas** (`pandas`)
- **Streamlit** (`streamlit`) (si utilizas Streamlit para visualización)
- **Altair Saver** (`altair_saver`)
- **VL Convert** (`vl-convert-python`)
- **Python Dotenv** (`python-dotenv`)

Usa pip install con cada una de ellas:

```bash
pip install "snowflake-connector-python[pandas]"
pip install streamlit
pip install pandas
pip install altair_saver
pip install vl-convert-python
pip install python-dotenv
pip install snowflake-snowpark-python
```

## Ejecución del Proyecto
Para ejecutar el script de agricultura.py o exportaciones.py utilizando Streamlit, sigue los siguientes pasos:

1. Navega hasta el directorio donde se encuentran los scripts:
```bash
cd "snowflake/Otros scripts/miniaplicativos"
```
2. Elige el comando según el aplicativo que quieras correr:
```bash
python -m streamlit run agricultura.py
```
```bash
python -m streamlit run exportaciones.py
```

## Referencias
Para la construcción del aplicativo de agricultura se tomó como base el código correspondiente a Dataframe demo, el cual sale al ejecutar el comando *streamlit hello* después de su instalación. Además, los datos utilizados fueron extraídos de este [enlace](https://streamlit-demo-data.s3-us-west-2.amazonaws.com/agri.csv.gz).
