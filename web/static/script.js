document.addEventListener('DOMContentLoaded', function() {
    var form = document.querySelector('form');
    form.onsubmit = function() {
        // Mostrar el spinner
        document.getElementById('loading').style.display = 'block';
    };
});

var currentVisible = null;  // Guardar el id del elemento actualmente visible

function toggleVisibility(author) {
    var elementId = 'messages-' + author;
    var element = document.getElementById(elementId);
    
    if (currentVisible && currentVisible !== elementId) {
        // Si hay algún elemento visible y no es el que queremos mostrar, ocultarlo
        document.getElementById(currentVisible).style.display = 'none';
    }
    
    // Toggle la visibilidad del elemento seleccionado
    if (element.style.display === 'none' || !currentVisible) {
        element.style.display = 'block';
        currentVisible = elementId;  // Actualizar el elemento actualmente visible
    } else {
        element.style.display = 'none';
        currentVisible = null;
    }
}