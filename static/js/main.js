// Escucha cambios en las casillas de verificación
document.querySelectorAll('input[CheckboxMantenimiento="fecha_mantenimiento"], input[CheckboxMantenimiento="fecha_calibracion"]').forEach(function(checkbox) {
    checkbox.addEventListener('change', function() {
        console.log('Checkbox clickeado');
        const productoId = this.getAttribute('data-producto-id');
        const estadoInicial = this.getAttribute('data-estado-inicial');
        const CheckboxMantenimiento = this.getAttribute('CheckboxMantenimiento');
        const periodicidadMantenimiento = this.getAttribute('data-periodicidad-mantenimiento');
        const fechaMantenimiento = this.getAttribute('data-fecha-mantenimiento');
        const vencimientoMantenimiento = this.getAttribute('data-vencimiento-mantenimiento');
        const periodicidadCalibracion = this.getAttribute('data-periodicidad-calibracion');
        const fechaCalibracion = this.getAttribute('data-fecha-calibracion');
        const vencimientoCalibracion = this.getAttribute('data-vencimiento-calibracion');
        const nuevoEstado = this.checked ? 'Activo' : 'Inactivo';

        // Confirmar con el usuario antes de enviar la solicitud
        if (confirm(`¿Cambiar el estado del equipo ${productoId} a ${nuevoEstado}?`)) {
            // Enviar solicitud POST para actualizar el estado y guardar en el historial
            fetch('/checkbox_programacionMantenimiento', {
                method: "POST",
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrf_token
                },
                body: JSON.stringify({
                    productoId: productoId,
                    nuevoEstado: nuevoEstado,
                    CheckboxMantenimiento: CheckboxMantenimiento,
                    periodicidadMantenimiento: periodicidadMantenimiento,
                    fechaMantenimiento: fechaMantenimiento,
                    vencimientoMantenimiento: vencimientoMantenimiento,
                    periodicidadCalibracion: periodicidadCalibracion,
                    fechaCalibracion: fechaCalibracion,
                    vencimientoCalibracion: vencimientoCalibracion
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    console.log(`Estado de ${CheckboxMantenimiento} del equipo ${productoId} actualizado a ${nuevoEstado}`);
                    if (nuevoEstado === 'Activo') {
                        alert("Fechas guardadas en el historial.");
                    }
                } else {

                    if (data.message && data.message.includes("Faltan menos de 30 días")) {
                        alert(data.message);
                        this.checked = false;
                    } else {
                        alert(data.message || "Error al actualizar el estado o guardar en el historial.");
                    }
                    this.checked = estadoInicial === 'Activo';
                }
            })
            .catch(error => {
                console.error('Error en la solicitud:', error);
                this.checked = estadoInicial === 'Activo';
            });
        } else {
            // Si el usuario cancela, restaura el estado inicial
            this.checked = estadoInicial === 'Activo';
        }
    });
});