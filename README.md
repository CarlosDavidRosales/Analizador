# Analizador de sentimientos

El objetivo principal del proyecto es el desarrollo de una aplicación web avanzada diseñada específicamente para llevar a cabo el análisis de sentimientos de conversaciones obtenidas de la aplicación WhatsApp. La plataforma está capacitada para analizar tanto interacciones individuales como discusiones grupales, permitiendo así evaluar las emociones manifestadas por los usuarios individuales y por los grupos a través de los mensajes intercambiados dentro de WhatsApp. 

## Requisitos previos

Antes de comenzar, asegúrate de tener Python instalado en tu sistema. Este proyecto es compatible con **Python 3.11 y versiones anteriores**. No está garantizado que funcione con versiones posteriores de Python.

## Configuración del entorno

Para configurar y activar un entorno virtual, sigue estos pasos:

```bash
# Instala virtualenv si no está instalado
pip install virtualenv

# Crea un entorno virtual
virtualenv venv

# Activa el entorno virtual
# En Windows
venv\Scripts\activate
# En Unix o MacOS
source venv/bin/activate

# Una vez dentro de tu entorno virtual (puedes instalarlas sin necesidad del entorno virtual, pero no se recomienda)
# instala las librerias necesarias para correr la aplicacion web, mediante el siguiente comando
pip install -r requirements.txt

# Una vez instaladas, ejecutamos el comando de django runserver para levantar nuestra aplicacion en nuestro servidor local
python manage.py runserver

# Entramos en la direccion local que nos da Django desde nuestro navegador
http://127.0.0.1:8000/