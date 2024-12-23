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
        cancelButtonText: 'Cancel',
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
            const empleados = result.value.empleados;
            if (transacciones && empleados) {
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
                        if(status == 'admin'){
                            insertarEmpleados(empleados);
                        }
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
    
    if(!transacciones || transacciones.length === 0){
        // Mostrar o esconder la fila "No se encontraron resultados"
        const noResultsRow = document.getElementById("noResultsRow");
        const botonApply = document.getElementById("applyfilters");
        const botonClear = document.getElementById("clearfilters");
        botonClear.diabled = true;
        botonApply.disabled = true;
        noResultsRow.style.display = "";
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

//Función para generar una lista de empleados 
function insertarEmpleados(empleados){
    const dropdown = document.getElementById("dropdown");
    dropdown.innerHTML = ""; // Limpiar el contenido previo

    empleados.forEach(empleado => {
        // Crear un contenedor para cada checkbox
        const label = document.createElement("label");

        // Crear el checkbox
        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.value = empleado.id;
        checkbox.id = `checkbox-${empleado.id}`;
        
        // Añadir el nombre del empleado
        label.appendChild(checkbox);
        label.appendChild(document.createTextNode(empleado.id));

        // Añadir el label al contenedor dropdown
        dropdown.appendChild(label);

        // Agregar el listener de cambio al checkbox
        checkbox.addEventListener("change", function() {
            handleCheckboxChange(empleado.id, checkbox.checked);
        });

    });

}

// Para almacenar los empleados seleccionados
let empleadosSeleccionados = [];


// Función para mostrar/ocultar la lista desplegable
function toggleDropdown() {
    const dropdown = document.getElementById("dropdown");
    const button = document.getElementById("toggleDropdown");
    // Calcular la posición del botón
    const buttonRect = button.getBoundingClientRect();
        
    // Ajustar la posición de la lista desplegable
    dropdown.style.top = `${buttonRect.bottom + window.scrollY + 5}px`;  // Colocar la lista justo debajo del botón
    dropdown.style.left = `${buttonRect.left + window.scrollX}px`;  // Alinear la lista con el botón
    dropdown.style.display = dropdown.style.display === "block" ? "none" : "block";  // Alternar visibilidad
}


// Función para manejar el cambio de estado de los checkboxes
function handleCheckboxChange(empleadoId, isChecked) {
    if (isChecked) {
        empleadosSeleccionados.push(empleadoId);
    } else {
        empleadosSeleccionados = empleadosSeleccionados.filter(id => id !== empleadoId);
    }
    
    // Actualizar el texto del botón
    updateButtonText();
}

// Función para actualizar el texto del botón
function updateButtonText() {
    const button = document.getElementById("toggleDropdown");

    if(button){
        if (empleadosSeleccionados.length > 0) {
            button.innerHTML = `Employees selected <i class="fa fa-caret-down"></i>`;
        } else {
            button.innerHTML = `Select employees <i class="fa fa-caret-down"></i>`;
        }
    }
    }


function limpiarSeleccion() {
    // Obtener todos los checkboxes dentro del dropdown
    const checkboxes = document.querySelectorAll('#dropdown input[type="checkbox"]');

    // Iterar sobre los checkboxes y desmarcarlos
    if(checkboxes){
        checkboxes.forEach(checkbox => {
            checkbox.checked = false;
        });
    }
}

//Función para aplicar los filtros
function aplicarFiltrosVentas(clear, status){
    const dropdown = document.getElementById("dropdown");
    if(dropdown){
        dropdown.style.display = "none";
    }
    const mes = document.querySelector('#mes').value.trim();
    const año = document.querySelector('#año').value.trim();
    const minAmountInput = document.getElementById("minAmount");
    const maxAmountInput = document.getElementById("maxAmount");
    const clientSearchInput = document.getElementById("buscador");
    const clientSearch = clientSearchInput.value.trim().toLowerCase();
    const minAmount = parseFloat(minAmountInput.value) || 0;
    const maxAmount = parseFloat(maxAmountInput.value) || Infinity;
    const rows = document.querySelectorAll("#ventasTable tbody tr");

    let visibleRowCount = 0;

    // Verificar si todos los campos están vacíos
    if(!clear){
        if (empleadosSeleccionados.length === 0 && !mes && !año && !minAmountInput.value && !maxAmountInput.value && !clientSearch) {
            Swal.fire({
                icon: 'info',
                title: 'No filters',
                text: 'Please select at least one filter before applying.',
                timer: 3000,
                showConfirmButton: false,
                customClass: {
                    confirmButton: 'loading send_btn', // Clase personalizada para el botón de Confirmar
                    cancelButton: 'loading cancel_btn', // Clase personalizada para el botón de Cancelar
                    actions: 'button-actions',// Clase personalizada para el contenedor de botones
                    popup: 'swal_popup'
                },
            });
            return; // No hacer nada si no hay filtros seleccionados
        }
    }

    rows.forEach((row, index) => {
        if(index == 0){
            return;
        }
        let match = true;

        // Filtrado por cliente
        let clientCell;
        if(status == 'admin'){
            clientCell = row.querySelector("td:nth-child(4)"); // La celda del cliente está en la columna 4
        }else{
            clientCell = row.querySelector("td:nth-child(3)"); // La celda del cliente está en la columna 3
        }
        const clientName = clientCell ? clientCell.textContent.trim().toLowerCase() : "";
        if (clientSearch && !clientName.includes(clientSearch)) {
            match = false;
        }

        // Filtrado por monto
        let amountCell;
        if(status == 'admin'){
            amountCell = row.querySelector("td:nth-child(3)"); // La celda de monto está en la columna 3
        }else{
            amountCell = row.querySelector("td:nth-child(2)"); // La celda de monto está en la columna 2
        }
        const amount = parseFloat(amountCell.textContent.replace('$', '').replace(',', '')) || 0;
        if (amount < minAmount || amount > maxAmount) {
            match = false;
        }

        // Filtrado por empleados seleccionados
        if (empleadosSeleccionados.length > 0) {
            console.log(empleadosSeleccionados)
            const employeeIdCell = row.querySelector("td:nth-child(1)"); // La celda de Employee ID está en la columna 1 (si es admin)
            const employeeId = employeeIdCell.textContent || 0;
            if (!empleadosSeleccionados.includes(employeeId)) {
                match = false;
            }
        }

        // Filtrado por año y mes
        if (año || mes) {
            let dateCell;
            if(status == 'admin'){
                dateCell = row.querySelector("td:nth-child(2)"); // La celda de fecha está en la columna 2
            }else{
                dateCell = row.querySelector("td:nth-child(1)"); // La celda de fecha está en la columna 1

            }
            const rowDate = dateCell.textContent.trim(); // El formato de la fecha debe ser algo como "YYYY-MM-DD"
            
            // Filtrar por año
            if (año && !rowDate.startsWith(año)) {
                match = false;
            }

            // Filtrar por mes (solo si se seleccionó un mes)
            if (mes && !rowDate.slice(5, 7).includes(mes)) {
                match = false;
            }
        }

        // Mostrar u ocultar fila dependiendo de si coincide con los filtros
        row.style.display = match ? "" : "none";

        // Contar las filas visibles
        if (match) {
            visibleRowCount++;
        }

    });
    // Mostrar o esconder la fila "No se encontraron resultados"
    const noResultsRow = document.getElementById("noResultsRow");
    noResultsRow.style.display = visibleRowCount === 0 ? "" : "none";
}

//Función para limpiar los filtros
function clearFiltros(){
    const mes = document.querySelector('#mes');
    const año = document.querySelector('#año');
    const minAmountInput = document.getElementById("minAmount");
    const maxAmountInput = document.getElementById("maxAmount");
    const clientSearchInput = document.getElementById("buscador");
    clientSearchInput.value = ""
    mes.value = ""
    año.value = ""
    minAmountInput.value = ""
    maxAmountInput.value = ""
    empleadosSeleccionados = [];
    limpiarSeleccion()
    updateButtonText();
    aplicarFiltrosVentas(true);
}
