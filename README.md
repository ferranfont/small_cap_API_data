Instalación:

pip install -r requirements.txt



script para descargar datos de Interactive Brokers

main.py

- Le el vector de DATOS ./DATA/smal_caps_bio.csv con las empresas biotechnológicas seleccionadas a fecha Junio de 2025
- Hace una petición a df = get_ibkr_data_loop() ya la almacena en un Dataframe
- Inserta el df en mysql insertar_df_en_mysql(df, ticker=SYMBOL)
- Hace un chart con ese ticker plot_close_and_volume_resample() si bien esta función primero agrupa los datos con un resample 
- Dentro de esta función plot_close_and_volume_resample() llama a plot_close_and_volume() para propiamente hacer el gráfico


Otros métodos:
read_SQL_database.py lee un valor y lo grafica

El fichero CSV endDateTime_Blocks es un fichero auxiliar creado para hacer la petición a Interactive Brokers, 
pues el método que usa no es establecer un rango de fechas, sino un fecha determinada y a partir de esa
fecha pedir un número n de días hacia atrás. Los bloques creados en ese CSV son las fechas en las que hay
que hacer la petición hasta cubrir la fecha inicial.


ESTADÍSTICAS
stat_days_sectors estudia los días que se tardan en alcanzar el máximo así como las pérdidas del 60, 80 y 90%
stat_lost_histogram estudia la distribución del histograma de retronos

en outputs directory, se almacena el fichero bio_summary.csv dónde están registradas las caídas

ESTRATEGIA
strat_time ejecuta una estrategia basada en entrar tras 100 días de la IPO y salir cuando el precio alcanza el 90% de pérdida desde el máximo
