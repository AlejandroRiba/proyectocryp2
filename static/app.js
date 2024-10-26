function redireccion(paginaDest){
    location.href=paginaDest
}

let varianteCount = 1; // Contador para asignar IDs únicos a cada variante

function cambiarTipoProducto() {
    const tipoProducto = document.querySelector('input[name="tipo_producto"]:checked').value;
    const varianteDivs = document.querySelectorAll('.variante');
    const div = document.getElementById('formulario');
    if (tipoProducto != null){
        if (div.style.display === 'none' || div.style.display === '') {
            div.style.display = 'block'; // Cambia a block
        }
    }
    // Actualizar las tallas de todas las variantes existentes
    varianteDivs.forEach((varianteDiv) => {
        const tallaSelect = varianteDiv.querySelector('select[name="talla"]');
        actualizarOpcionesTalla(tallaSelect, tipoProducto);
    });
}

function actualizarOpcionesTalla(tallaSelect, tipoProducto) {
    // Limpiar las opciones actuales
    tallaSelect.innerHTML = '';
    const defaultOption = document.createElement('option');
    defaultOption.value = '';
    defaultOption.disabled = true;
    defaultOption.selected = true;
    defaultOption.textContent = 'Selecciona una talla';
    tallaSelect.appendChild(defaultOption);

    // Agregar opciones según el tipo de producto
    if (tipoProducto === 'calzado') {
        const tallasUS = ['5', '6', '7', '8', '9', '10']; //agregar equivalencias MX

        tallasUS.forEach(talla => {
            const option = document.createElement('option');
            option.value = `US ${talla}`;
            option.textContent = `US ${talla}`;
            tallaSelect.appendChild(option);
        });

    } else if (tipoProducto === 'ropa') {
        const tallasRopa = ['Unitalla', 'XS', 'S', 'M', 'L', 'XL', 'XXL', 'XXXL'];

        tallasRopa.forEach(talla => {
            const option = document.createElement('option');
            option.value = talla;
            option.textContent = talla;
            tallaSelect.appendChild(option);
        });
    }
}

function agregarVariante() {
    const varianteDiv = document.createElement('div');
    varianteDiv.className = 'variante';
    varianteDiv.id = `variante-${varianteCount}`;

    varianteDiv.innerHTML = `
        <label for="talla-${varianteCount}">Talla:</label>
        <select id="talla-${varianteCount}" name="talla" required>
            <option value="" disabled selected>Selecciona una talla</option>
        </select>
        <label for="stock-${varianteCount}">Stock:</label>
        <input type="number" id="stock-${varianteCount}" name="stock" required>
        <button type="button" onclick="eliminarVariante('variante-${varianteCount}')">Eliminar</button>
        <br><br>
    `;

    // Agregar la nueva variante al DOM
    document.getElementById('variantes').appendChild(varianteDiv);

    // Actualizar opciones de talla para la nueva variante
    const tipoProducto = document.querySelector('input[name="tipo_producto"]:checked').value;
    const tallaSelect = varianteDiv.querySelector(`select[name="talla"]`);
    actualizarOpcionesTalla(tallaSelect, tipoProducto);

    varianteCount++; // Incrementar el contador para el próximo ID único
}

function eliminarVariante(varianteId) {
    const varianteDiv = document.getElementById(varianteId);
    if (varianteDiv) {
        varianteDiv.remove(); // Eliminar el div de variante del DOM
    }
}
