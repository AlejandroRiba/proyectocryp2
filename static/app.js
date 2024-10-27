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

function actualizarOpcionesTalla(tallaSelect, tipoProducto, option) {
    // Limpiar las opciones actuales
    tallaSelect.innerHTML = '';
    const defaultOption = document.createElement('option');
    if (option != null){
        defaultOption.value = option;
        defaultOption.textContent = option;
        defaultOption.disabled = false;
    } else{
        defaultOption.value = '';
        defaultOption.textContent = 'Selecciona una talla';
        defaultOption.disabled = true;
    }
    console.log(defaultOption.value)
    defaultOption.selected = true;
    tallaSelect.appendChild(defaultOption);

    // Agregar opciones según el tipo de producto
    if (tipoProducto === 'Shoes') {
        const tallasUS = ['3.5','4','4.5','5','5.5','6','6.5', '7', '7.5', '8', '8.5', '9', '9.5','10','10.5','11','11.5','12','13']; //agregar equivalencias MX

        tallasUS.forEach(talla => {
            const option = document.createElement('option');
            option.value = `US ${talla}`;
            option.textContent = `US ${talla}`;
            tallaSelect.appendChild(option);
        });

    } else if (tipoProducto === 'Clothing') {
        const tallasRopa = ['One Size', 'XS', 'S', 'M', 'L', 'XL', 'XXL', 'XXXL', '28', '30', '32', '34', '36', '38', '40', '42'];


        tallasRopa.forEach(talla => {
            const option = document.createElement('option');
            option.value = talla;
            option.textContent = talla;
            tallaSelect.appendChild(option);
        });
    } else if (tipoProducto === 'Accessories') {
        const tallasRopa = ['One Size', 'Adjustable'];

        tallasRopa.forEach(talla => {
            const option = document.createElement('option');
            option.value = talla;
            option.textContent = talla;
            tallaSelect.appendChild(option);
        });
    }
}

function agregarVariante(contador) {
    const varianteDiv = document.createElement('div');
    varianteDiv.className = 'variante';
    console.log(contador)
    if(contador > varianteCount){
        varianteCount = contador + 1;
    }
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
    const tipoProductoElement = document.querySelector('input[name="tipo_producto"]:checked');
    let tipoProducto = null
    if (tipoProductoElement) { //si no existe el input de ese tipo, entonces existe el segundo
        tipoProducto = tipoProductoElement.value;
    } else {
        tipoProducto = document.getElementById('tipo_producto').value;
    }
    const tallaSelect = varianteDiv.querySelector(`select[name="talla"]`);
    actualizarOpcionesTalla(tallaSelect, tipoProducto, null);

    varianteCount++; // Incrementar el contador para el próximo ID único
    
}

function eliminarVariante(varianteId) {
    const varianteDiv = document.getElementById(varianteId);
    if (varianteDiv) {
        varianteDiv.remove(); // Eliminar el div de variante del DOM
    }
}

function activarIdinput(){
    const input = document.getElementById('id_product');
    input.disabled = false;
}
