
// Escucha cambios en las casillas de verificación
document.querySelectorAll('input[type="checkbox"]').forEach(function(checkbox) {
    checkbox.addEventListener('change', function() {
        console.log('clickeados')
        const productoId = this.getAttribute('data-producto-id');
        const estadoInicial = this.getAttribute('data-estado-inicial');
        const name = this.getAttribute('name');
        const nuevoEstado = this.checked ? 'Activo' : 'Inactivo';

        // alert(name);

        // Confirmar con el usuario antes de enviar la solicitud
        if (confirm(`¿Cambiar el estado de ${name} ${productoId} a ${nuevoEstado}?`)) {

            // Enviar una solicitud POST al servidor para actualizar el estado
            fetch('/checkbox_programacionMantenimiento', {
                method: "POST",
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrf_token // Adjuntar el token CSRF generado
                },
                body: JSON.stringify({
                    productoId: productoId,
                    nuevoEstado: nuevoEstado,
                    name : name
                })
            })
            .then(response => {
                if (response.ok) {
                    // Actualización exitosa, puedes realizar alguna acción adicional si es necesario
                    console.log(`Estado de producto ${productoId} actualizado a ${nuevoEstado}`);
                } else {
                    // Manejar errores si es necesario
                    console.error('Error al actualizar el estado del producto');
                }
            })
            .catch(error => {
                console.error('Error en la solicitud:', error);
            });
        } else {
            // Si el usuario cancela, restaura el estado inicial
            this.checked = estadoInicial === 'Activo';
        }
    });
    
});