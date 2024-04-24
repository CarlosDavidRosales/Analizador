from django.shortcuts import render
from .forms import FileUploadForm
from pysentimiento import create_analyzer
import matplotlib.pyplot as plt
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
                if message:
                    sentiment = analyzer.predict(message).output
                    if author not in results:
                        results[author] = []
                    results[author].append((message, sentiment))
    return results



def file_analysis(request):
    sentiments = None
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            data = handle_uploaded_file(file)
            sentiments = analyze_sentiments(data)
    else:
        form = FileUploadForm()
    return render(request, 'results.html', {'form': form, 'sentiments': sentiments})


