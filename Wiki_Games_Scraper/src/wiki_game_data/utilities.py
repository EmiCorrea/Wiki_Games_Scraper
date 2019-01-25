# Este archivo contiene funciones auxiliares utilizadas a lo largo del programa
import re
import dateutil.parser as dparser

# Función para obtener el texto alojado en un elemento
def get_text(value):
    text = value.xpath('..').xpath('following-sibling::*').xpath('.//text()').extract()
    if text:
        return text
    else:
        return "N/A"

# Función genérica de limpieza de datos
def clean(value):
    v = list(filter(lambda x: x, map(lambda x: re.sub('[\(\[].*?[\)\]]', '', x), value)))
    v2 = list(filter(lambda x: x, map(lambda x: re.sub('[^A-Za-z0-9, :/-]+', '', x), v)))
    return v2

# Función para encontrar y formatear fechas
def format_dates(dates):
    fixed_dates = []
    for d in dates:
        i = dparser.parse(d, fuzzy=True)
        fixed_date = i.strftime("%d %B, %Y")
        fixed_dates.append(fixed_date)
    return fixed_dates

# Función que elimina espacios en blanco
def clear_blanks(value):
    while True:
        try:
            value.remove(' ')
        except ValueError:
            break

# Función de fusión y limpieza de strings
def clean_merge(value, array):
    v = [' '.join(value)]
    v2 = (str(v)).replace('[', '').replace(']', '').replace("'", '').replace(' :', ':').replace('and', '').replace('citation needed', '').replace('  ', ' ').strip()
    array.append(v2)

# Función para limpiar texto
def clean_data(value):
    v = list(filter(lambda x: x, map(lambda x: re.sub('[\(\[].*?[\)\]]', '', x), value)))
    v2 = list(filter(lambda x:x, map(lambda x:re.sub(r'[^A-Za-z0-9 \-\'?Æ®º$%&:]', '', x), v)))
    clear_blanks(v2)
    clear_data = []
    for i in v2:
        d = (str(i)).replace('[', '').replace(']', '').replace("'", '').replace(' :', ':').replace('  ', ' ').strip()
        clear_data.append(d)
    clear_data = [x for x in clear_data if x]
    if "1" and "2" and "players" in clear_data:
        cd = clear_data[0:len(clear_data)]
        clear_data = [' '.join(cd)]
    return clear_data

#Función para limpiar los distribuidores
def clean_publisher(value):
    pub = clean_data(value)
    if ":" in pub:
        indices = [i for i, item in enumerate(pub) if re.search(":", item)]
        publishers = []
        for i in range(len(indices)):
            if i == 0 and len(indices) == 1:
                clean_merge(pub, publishers)
            elif i == 0:
                p = pub[0:(indices[i + 1] - 1)]
                clean_merge(p, publishers)
            elif i == (len(indices) - 1):
                p = pub[(indices[i] - 1):(len(pub))]
                clean_merge(p, publishers)
            else:
                p = pub[(indices[i] - 1):(indices[i + 1] - 1)]
                clean_merge(p, publishers)
        return publishers
    else:
        pub = [x for x in pub if x]
        return pub

#Función para limpiar las fechas
def clean_release_date(date):
    date_ok = clean(date)
    if len(date) == 1:
        return date_ok
    elif len(date) == 2:
        for d in date_ok:
            if d[:1] == '1' or d[:1] == '2':
                return date_ok
            else:
                date_ok = [': '.join(date_ok[0:2])]
                return date_ok
    else:
        indices = [i for i, item in enumerate(date_ok) if re.search(r'[0-9]{4}', item)]
        dates = []
        for i in range(len(indices)):
            if i == 0:
                d = date_ok[0:(indices[i] + 1)]
                clean_merge(d, dates)
            else:
                d = date_ok[(indices[i - 1] + 1):(indices[i] + 1)]
                clean_merge(d, dates)
        return dates