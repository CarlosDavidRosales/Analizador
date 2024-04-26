from django.shortcuts import render
from .forms import FileUploadForm
from pysentimiento import create_analyzer
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Usar el backend 'Agg' que es para archivos y no requiere GUI

from wordcloud import WordCloud
import io
import base64


analyzer = create_analyzer(task="sentiment", lang="es")

def handle_uploaded_file(f):
    content = f.read().decode('utf-8')
    return content

def analyze_sentiments(data):
    results = {}
    data = data.split("\n")
    for line in data:
        parts = line.split(" - ", 1)
        if len(parts) > 1:
            author_message = parts[1]
            if ": " in author_message:
                author, message = author_message.split(": ", 1)
                if message and not message.startswith("\u200e") and "<Multimedia omitido>" not in message:
                    sentiment = analyzer.predict(message).output
                    if author not in results:
                        results[author] = []
                    results[author].append((message, sentiment))
    return results

def nube_de_palabras_base64(palabras, sentimiento=None):
    if not palabras:  # Verificar si el diccionario está vacío
        return None  # Devolver None o manejar de otra manera

    wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(palabras)
    
    buf = io.BytesIO()
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    if sentimiento:
        plt.title("Nube de palabras " + sentimiento)
    plt.savefig(buf, format='png')
    plt.close()
    
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return image_base64

def contar_palabras_mensajes(mensajes):
    conteo = {}
    for mensaje in mensajes:
        palabras = mensaje.split()
        for palabra in palabras:
            if palabra not in conteo:
                conteo[palabra] = 1
            else:
                conteo[palabra] += 1
    return conteo

def file_analysis(request):
    sentiments = None
    wordclouds = {}
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            data = handle_uploaded_file(file)
            sentiments = analyze_sentiments(data)
            # Generar las nubes de palabras para cada usuario
            for _, messages in sentiments.items():
                # Asegurar que 'messages' es una lista de tuplas (mensaje, sentimiento)
                palabras_pos = contar_palabras_mensajes([msg for msg, sent in messages if sent == "POS"])
                palabras_neg = contar_palabras_mensajes([msg for msg, sent in messages if sent == "NEG"])
                palabras_neu = contar_palabras_mensajes([msg for msg, sent in messages if sent == "NEU"])
                
                wordclouds = {
                    'author': {
                        'POS': nube_de_palabras_base64(palabras_pos, 'Positivo') if palabras_pos else None,
                        'NEG': nube_de_palabras_base64(palabras_neg, 'Negativo') if palabras_neg else None,
                        'NEU': nube_de_palabras_base64(palabras_neu, 'Neutral') if palabras_neu else None
                    }
                }
    else:
        form = FileUploadForm()
    return render(request, 'results.html', {'form': form, 'sentiments': sentiments, 'wordclouds': wordclouds})
