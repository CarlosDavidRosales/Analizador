import matplotlib.pyplot as plt
import matplotlib
import io
import base64
from django.shortcuts import render
from .forms import FileUploadForm
from pysentimiento.preprocessing import preprocess_tweet
from pysentimiento import create_analyzer
from wordcloud import WordCloud

# Usar el backend 'Agg' que es para archivos y no requiere GUI
matplotlib.use('Agg')

# Crear el analizador de sentimientos para español
analyzer = create_analyzer(task="sentiment", lang="es")

def handle_uploaded_file(f):
    """Lee y decodifica el contenido de un archivo subido."""
    content = f.read().decode('utf-8')
    return content

def analyze_sentiments(data):
    """
    Analiza los sentimientos de los mensajes en los datos proporcionados.
    """
    results = {}
    mensajes_grupo = []
    data = data.split("\n")
    for line in data:
        parts = line.split(" - ", 1)
        if len(parts) > 1:
            author_message = parts[1]
            if ": " in author_message:
                author, message = author_message.split(": ", 1)
                if message and not message.startswith("\u200e") and "<Multimedia omitido>" not in message:
                    sentiment = analyzer.predict(preprocess_tweet(message.lower()))
                    if sentiment.probas['NEG'] > 0.45:
                        sentiment = "NEG"
                    elif sentiment.probas['POS'] > 0.40:
                        sentiment = "POS"
                    else:
                        sentiment = str(sentiment.output)
                    if author not in results:
                        results[author] = []
                    results[author].append((message, sentiment))
                    mensajes_grupo.append((message, sentiment))
    
    results['GRUPO'] = mensajes_grupo
    Grupo = results.pop('GRUPO')
    new_results = {"GRUPO": Grupo}
    new_results.update(results)
    return new_results, mensajes_grupo

def nube_de_palabras_base64(palabras, sentimiento=None):
    """
    Genera una nube de palabras en base64 a partir de las palabras y el sentimiento proporcionados.
    """
    if not palabras:
        return None
    colormap = ''
    if sentimiento == "Positivo":
        colormap = "viridis"
    elif sentimiento == "Negativo":
        colormap = "Reds"
    elif sentimiento == "Neutral":
        colormap = "gray"

    wordcloud = WordCloud(colormap=colormap, width=800, height=400, background_color='white').generate_from_frequencies(palabras)

    buf = io.BytesIO()
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.tight_layout(pad=0)
    if sentimiento:
        plt.title("Nube de palabras " + sentimiento, pad=20)
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
    plt.close()
    
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return image_base64

def contar_palabras_mensajes(mensajes):
    """
    Cuenta las palabras en una lista de mensajes, excluyendo ciertas palabras comunes.
    """
    conteo = {}
    exclusiones = [
        "y", "e", "que", "qué", "como",
        "cuando", "mientras", "para", "hasta",
        "este", "esta", "está", "esto", "estos", "estas",
        "el", "la", "los", "las", "un", "una", "unos", "unas", "pero", "o", "Pero"
    ]
    for mensaje in mensajes:
        palabras = mensaje.split()
        for palabra in palabras:
            if not len(palabra) > 3 or palabra in (['emoji', 'cara'] + exclusiones) or palabra.startswith("@52"):
                if palabra.lower() in ["sí", "si", "no"]:
                    conteo[palabra.lower()] = conteo.get(palabra.lower(), 0) + 1
                continue
            elif palabra not in conteo:
                conteo[palabra.lower()] = 1
            else:
                conteo[palabra.lower()] += 1
    return conteo

def file_analysis(request):
    """
    Maneja la subida y análisis del archivo, generando resultados de sentimientos y nubes de palabras.
    """
    sentiments = None
    sentiments_group = None
    wordclouds = {}
    author_sentiment_count = {}
    grafica_barras = None
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            data = handle_uploaded_file(file)
            sentiments, sentiments_group = analyze_sentiments(data)
            grafica_barras = None
            # Generar las nubes de palabras para cada usuario
            for data in sentiments.keys():
                messages = sentiments[data]
                palabras_pos = contar_palabras_mensajes([msg for msg, sent in messages if sent == "POS"])
                palabras_neg = contar_palabras_mensajes([msg for msg, sent in messages if sent == "NEG"])
                palabras_neu = contar_palabras_mensajes([msg for msg, sent in messages if sent == "NEU"])
                
                Pos = 0
                Neu = 0
                Neg = 0
                for message in messages:
                    if message[1] == "POS":
                        Pos += 1
                    elif message[1] == "NEU":
                        Neu += 1 
                    else:
                        Neg += 1
                    
                author_sentiment_count[data] = {"POS": Pos, "NEU": Neu, "NEG": Neg}
                
                wordclouds[data] = {
                    'POS': nube_de_palabras_base64(palabras_pos, 'Positivo') if palabras_pos else None,
                    'NEG': nube_de_palabras_base64(palabras_neg, 'Negativo') if palabras_neg else None,
                    'NEU': nube_de_palabras_base64(palabras_neu, 'Neutral') if palabras_neu else None
                }
            grafica_barras = generar_grafica_barras(author_sentiment_count)
    else:
        form = FileUploadForm()
    return render(request, 'results.html', {'form': form, 'sentiments': sentiments, "author_sentiment_count": author_sentiment_count, 'sentiments_group': sentiments_group, 'wordclouds': wordclouds, 'grafica_barras': grafica_barras})

def generar_grafica_barras(author_sentiment_count):
    """
    Genera una gráfica de barras horizontal en base64 para los sentimientos de cada autor.
    """
    labels = list(author_sentiment_count.keys())
    pos_counts = [author_sentiment_count[author]['POS'] for author in labels]
    neu_counts = [author_sentiment_count[author]['NEU'] for author in labels]
    neg_counts = [author_sentiment_count[author]['NEG'] for author in labels]

    y = range(len(labels))

    fig, ax = plt.subplots(figsize=(15, 8))

    ax.barh(y, pos_counts, height=0.3, label='Positivos', color='green', align='center')
    ax.barh(y, neu_counts, height=0.3, label='Neutrales', color='gray', align='center', left=pos_counts)
    ax.barh(y, neg_counts, height=0.3, label='Negativos', color='red', align='center', left=[i+j for i, j in zip(pos_counts, neu_counts)])

    ax.set_ylabel('Autores')
    ax.set_xlabel('Cantidad de Mensajes')
    ax.set_title('Sentimientos por Autor')
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.legend()

    plt.subplots_adjust(left=0.25, right=0.95, top=0.95, bottom=0.1)

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return image_base64