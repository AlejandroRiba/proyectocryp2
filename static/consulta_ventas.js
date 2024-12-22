function inicio_consultaVentas(status){
    Swal.fire({
        title: 'Sensitive Information',
        text: 'You are about to view sensitive information. Please confirm your password.',
        input: 'password',
        inputPlaceholder: 'Enter your password',
        inputAttributes: {
            autocapitalize: 'off',
            autocorrect: 'off'
        },
        showCancelButton: true,
        confirmButtonText: 'Send',
        cancelfirmButtonText: 'Cancel',
        customClass: {
            confirmButton: 'loading send_btn', // Clase personalizada para el botón de Confirmar
            cancelButton: 'loading cancel_btn', // Clase personalizada para el botón de Cancelar
            actions: 'button-actions',// Clase personalizada para el contenedor de botones
            popup: 'swal_popup'
        },
        buttonsStyling: false, // Desactiva los estilos predeterminados de SweetAlert
        showLoaderOnConfirm: true,
        backdrop: 'rgba(0, 0, 0, 0.7)', // Fondo con efecto difuminado
        allowOutsideClick: false, // Evita que se cierre al hacer clic fuera
        preConfirm: (password) => {
            return fetch('/consulta_venta', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ password: password })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(response.statusText);
                }
                return response.json();
            })
            .then(data => {
                if (!data.success) {
                    throw new Error(data.message || 'Incorrect password');
                }
                return data;
            })
            .catch(error => {
                Swal.showValidationMessage(
                    `Error: ${error.message}`
                );
            });
        }
    }).then((result) => {
        if (result.isConfirmed && result.value.success) {
            const transacciones = result.value.transacciones; // Transacciones devueltas
            if (transacciones) {
                Swal.fire({
                    title: 'Access granted',
                    icon: 'success',
                    customClass: {
                        confirmButton: 'loading send_btn', // Clase personalizada para el botón de Confirmar
                        actions: 'button-actions',// Clase personalizada para el contenedor de botones
                        popup: 'swal_popup'
                        
                    },
                    backdrop: 'rgba(0, 0, 0, 0.5)', // Fondo con efecto difuminado
                    allowOutsideClick: false // Evita que se cierre al hacer clic fuera
                }).then((result) => {
                    if (result.isConfirmed) {
                        insertarVentas(transacciones, status);
                    }
                });
            }
        } else if (result.dismiss === Swal.DismissReason.cancel) {
            window.history.back();
        }
    });
}

function insertarVentas(transacciones, status){
    const tabla = document.querySelector('#ventasTable tbody');
    tabla.innerHTML = "";
    if(!transacciones || transacciones.length === 0){
        const fila = document.createElement("tr");
                fila.innerHTML = `
                    <td colspan="10" style="text-align: center; color: var(--color-warning); border-left: none; border-right: none">
                        No sales found.
                    </td>
                `;
                tabla.appendChild(fila);
    }else{
        // Inserta cada transacción en la tabla
        transacciones.forEach(transaccion => {
            const fila = document.createElement('tr');

            // Si el status es "admin", muestra el empleado_id
            if (status === 'admin') {
                const celdaEmpleadoId = document.createElement('td');
                celdaEmpleadoId.textContent = transaccion.empleado_id || '';
                fila.appendChild(celdaEmpleadoId);
            }

            // Celda de fecha
            const celdaFecha = document.createElement('td');
            celdaFecha.textContent = `${transaccion.fecha}` || '';
            fila.appendChild(celdaFecha);

            // Celda de monto
            const celdaMonto = document.createElement('td');
            celdaMonto.textContent = `$${transaccion.monto || 0}`;
            fila.appendChild(celdaMonto);

            // Celda de cliente nombre y apellido
            const celdaClienteNombre = document.createElement('td');
            celdaClienteNombre.textContent = `${transaccion.cliente || ''}`;
            fila.appendChild(celdaClienteNombre);

            // Celda de tarjeta
            const celdaTarjeta = document.createElement('td');
            if (status === 'admin') {
                celdaTarjeta.textContent = transaccion.tarjeta || '';
            } else {
                celdaTarjeta.textContent = '****************';
            }
            fila.appendChild(celdaTarjeta);

            // Agrega la fila completa a la tabla
            tabla.appendChild(fila);
        });
    }
}