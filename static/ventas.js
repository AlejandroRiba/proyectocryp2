function aumentarvalor(inputId){
    const input = document.getElementById(inputId);
    const maxValue = parseInt(input.getAttribute('max'));
    console.log(`Input id: ${inputId}`);
    console.log(`Val max: ${maxValue}`);
    if (maxValue > 0){
        if (input.value == '' || input.value < 1){
            input.value = 1;
        }else if(input.value < maxValue){
            input.value = parseInt(input.value) + 1;
        }
    }
}

function maxValor(input){
    const maxValue = parseInt(input.getAttribute('max'));
    if (maxValue > 0){
        if (input.value == '' || input.value < 1){
            input.value = 1;
        }else if(input.value >= maxValue){
            input.value = maxValue;
        }else{
            input.value = 1;
        }
    }else{
        input.value = 0;
    }
}

function disminuirvalor(inputId){
    const input = document.getElementById(inputId);
    const maxValue = parseInt(input.getAttribute('max'));
    if (maxValue > 0){
        if (input.value > 1){
            input.value = parseInt(input.value) - 1;
        } else{
            input.value = 1;
        }
    }
}

function actualizarStock(productoId, talla){
    const selectTalla = document.getElementById(`option_${productoId}_${talla}`);
    const spanStock = document.getElementById(`stock_${productoId}`);

    if (selectTalla) {
        const stock = selectTalla.getAttribute('data-stock');
        spanStock.innerText = stock; //Se actualiza el stock
        const input_cantidad = document.getElementById(`cantidad_${productoId}`);
        input_cantidad.setAttribute('max', stock); //se actualiza el max stock
        document.getElementById(`tooltip_${productoId}`). innerText = "Maximum value: " + stock; //mensaje de alerta
        if (stock === 0 || stock === '0'){
            input_cantidad.value = '0';
        }else{
            input_cantidad.value = '1';
        }
    }
}

let carritolist = [] //varible gobal

function actualizarCompra(productoId, talla, inputId, tipo){
    const input_cantidad = document.getElementById(inputId);
    const index = carritolist.findIndex(item => item.id === productoId && item.talla === talla);
    const cantidadActual = carritolist[index].cantidad;
    const maxValue = parseInt(input_cantidad.getAttribute('max'));
    console.log(maxValue);
    let nueva_cantidad;
    const productoPrecio = document.getElementById(`precio_${productoId}`).innerText;
    const precio_real = parseFloat(productoPrecio.replace('$', ''));
    if (tipo === "menos"){
        nueva_cantidad = parseInt(cantidadActual) - 1;
    }else if (tipo === "mas1"){
        nueva_cantidad = parseInt(cantidadActual) + 1;
    }else if (tipo === "mas"){
        nueva_cantidad = parseInt(cantidadActual) + parseInt(input_cantidad.value);
    }else{
        if (!input_cantidad.value || input_cantidad.value == 0){
            nueva_cantidad = 1;
        }else{
            nueva_cantidad = parseInt(input_cantidad.value);
        }
    }

    if (nueva_cantidad <= maxValue && nueva_cantidad >= 1) {
        carritolist[index] = {
        ...carritolist[index], // Mantiene las propiedades existentes
        cantidad: nueva_cantidad, // Actualiza el valor de cantidad
        };
        document.getElementById(`unidades_${productoId}_${talla}`).value = nueva_cantidad; //Se actualiza el input del carrito, no de la lista, el de la lista de actualiza si mandas el producto desde ahí
        document.getElementById(`total_${productoId}_${talla}`).innerText = "$" + (precio_real * nueva_cantidad).toFixed(2);
        console.log(carritolist)
    } else if(nueva_cantidad > maxValue){ //en caso de que las unidades colocadas superen a la actual
        carritolist[index] = {
            ...carritolist[index], // Mantiene las propiedades existentes
            cantidad: maxValue, // Actualiza el valor de cantidad
        };
        document.getElementById(`unidades_${productoId}_${talla}`).value = maxValue;
        document.getElementById(`total_${productoId}_${talla}`).innerText = "$" + (precio_real * maxValue).toFixed(2);
        console.log(carritolist)
    }
    actualiazartotal();
}

function actualiazartotal(){
    const parrafo = document.getElementById('total_carrito');
    const precios = document.querySelectorAll('.precio');

    // Variable para almacenar el total
    let total = 0;

    // Recorre cada elemento de precios
    precios.forEach(precio => {
        // Obtiene el texto, elimina el símbolo de dólar y convierte a número
        const valor = parseFloat(precio.textContent.replace('$', ''));
        total += valor; // Suma al total
    });

    parrafo.innerText = 'Total: $' + total.toFixed(2);
}

function agregarAlCarrito(productoId) {
    const carrito = document.querySelector("#tablaCarrito tbody");
    const talla = document.querySelector(`input[name="btn_${productoId}"]:checked`).value || document.getElementById(`span_talla_${productoId}`).innerText;
    const input_cantidad = document.getElementById(`cantidad_${productoId}`);
    const maxValue = parseInt(input_cantidad.getAttribute('max'));
    console.log(`El maximo actual es ${maxValue}`);
    if(maxValue != 0){
        let cantidad = parseInt(input_cantidad.value);
        const index = carritolist.findIndex(item => item.id === productoId && item.talla === talla);
        if (index != -1){
            //EL PRODUCTO YA EXISTE
            actualizarCompra(productoId, talla, `cantidad_${productoId}`, "mas");
            input_cantidad.value = '1';
        }else {
            const productoNombre = document.getElementById(`name_${productoId}`).innerText;
            const producto_archivo = document.getElementById(`img_${productoId}`).src;
            const productoPrecio = document.getElementById(`precio_${productoId}`).innerText;
            const precio_total = parseFloat(productoPrecio.replace('$', '')) * cantidad;

            const filaCarrito = document.createElement("tr");
            filaCarrito.id = `carrito_${productoId}_${talla}`; //para que cada producto sea único
            filaCarrito.innerHTML = `
                <td><div class="contenedor-square"><img id="img_${productoId}" src="${producto_archivo}" class="cuadrada"></div></td>
                <td>${productoNombre}</td>
                <td>${talla}</td>
                <td>
                    <div class="tooltip-container">
                        <span class="tooltip">Maximum value: ${maxValue}</span>
                        <div class="number-control">
                            <div class="number-left" onclick='actualizarCompra("${productoId}", "${talla}", "unidades_${productoId}_${talla}", "menos")'></div>
                            <input type="number" name="number" min="1" max="${maxValue}" class="number-quantity" id="unidades_${productoId}_${talla}" autocomplete="off" value="${cantidad}" oninput='actualizarCompra("${productoId}", "${talla}", "unidades_${productoId}_${talla}", "otro")'>
                            <div class="number-right" onclick='actualizarCompra("${productoId}", "${talla}", "unidades_${productoId}_${talla}", "mas1")'></div>
                        </div>
                    </div>
                </td>
                <td class="precio" id='total_${productoId}_${talla}'>$${precio_total.toFixed(2)}</td>
                <td>
                    <button class="button_item" type="button" onclick="eliminarDelCarrito('${productoId}','${talla}')">
                                    <span class="button_item__text">Drop Item</span>
                                    <span class="button_item__icon"><svg class="svg" fill="none" height="24" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" viewBox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg"><line x1="5" y1="5" x2="19" y2="19"></line><line x1="19" y1="5" x2="5" y2="19"></line></svg></span>
                    </button>
                </td>
            `;
            carritolist.push({ id: productoId, cantidad: cantidad, talla: talla });
            console.log(carritolist);
            carrito.appendChild(filaCarrito);
            input_cantidad.value = '1';
            actualiazartotal();
        }
    }
}

function eliminarDelCarrito(productoId, talla) {
    const filaCarrito = document.getElementById(`carrito_${productoId}_${talla}`);
    if (filaCarrito) {
        filaCarrito.remove();
    }
    const indexToRemove = carritolist.findIndex(item => item.id === productoId && item.talla === talla);
    if (indexToRemove !== -1) {
        carritolist.splice(indexToRemove, 1);
    }
    actualiazartotal();
    console.log(carritolist);
}

function vaciarCarrito(){
    if (confirm("¿Estás seguro de que deseas vaciar el carrito?")) {
        const carrito = document.querySelector("#tablaCarrito tbody");
        carrito.innerHTML = ''; 
        carritolist.length = 0;
        actualiazartotal();
        console.log(carritolist);
    }
}

function aplicarFiltros(page = 1) {
    const nombre = document.getElementById("buscador").value;
    const categoria = document.querySelector(`input[name="filtro"]:checked`).value

    fetch(`/filtrar_productos?nombre=${nombre}&categoria=${categoria}&page=${page}`)
        .then(response => response.json())
        .then(data => {
            const tbody = document.querySelector("tbody");
            tbody.innerHTML = "";  // Limpiamos las filas existentes

            if (data.productos.length === 0) {
                const fila = document.createElement("tr");
                fila.innerHTML = `
                    <td colspan="10" style="text-align: center; color: red; border-left: none; border-right: none">
                        No results found for this search.
                    </td>
                `;
                tbody.appendChild(fila);
            } else {
                data.productos.forEach(producto => {
                    const fila = document.createElement("tr");
                    let stock = producto.variantes[0].stock; // Obtiene el valor de stock
                    let cantidadInicial = stock > 0 ? 1 : 0; // Define 1 si el stock es mayor a 0, de lo contrario 0
                    fila.innerHTML = `
                        <td style="border-left: none;">${producto.id}</td>
                        <td><div class="contenedor-square"><img id="img_${producto.id}" src="static/images/products/${producto.archivo}" class="cuadrada"></div></td>
                        <td id="name_${producto.id}">${producto.nombre}</td>
                        <td id="precio_${producto.id}">$${producto.precio}</td>
                        <td>${producto.categoria}</td>
                        <td>
                            ${producto.variantes.length > 1 ? 
                                `<div style="display: flex; padding: 6px 0;">
                                    ${producto.variantes.map((variante, index) => `
                                        ${index % 4 === 0 && index !== 0 ? `</div><div style="display: flex; padding: 6px 0;">` : ""}
                                        <div class="wrapper">
                                            <div class="option" onclick="actualizarStock('${producto.id}', '${variante.talla}')">
                                                <input ${index === 0 ? "checked" : ""} id="option_${producto.id}_${variante.talla}" 
                                                    value="${variante.talla}" data-stock="${variante.stock}" 
                                                    name="btn_${producto.id}" type="radio" class="input"/>
                                                <div class="btn">
                                                    <span class="span">${variante.talla}</span>
                                                </div>
                                            </div>
                                        </div>
                                    `).join('')}
                                </div>`
                                : `<div style="display: flex; padding: 6px 0;">
                                        <div class="wrapper" style="pointer-events: none; cursor: default;">
                                            <div class="option">
                                                <input checked id="option_${producto.id}_${producto.variantes[0].talla}" 
                                                    value="${producto.variantes[0].talla}" data-stock="${producto.variantes[0].stock}" 
                                                    name="btn_${producto.id}" type="radio" class="input"/>
                                                <div class="btn">
                                                    <span class="span">${producto.variantes[0].talla}</span>
                                                </div>
                                            </div>
                                        </div>
                                </div>`
                            }
                        </td>
                        <td>${producto.color}</td>
                        <td><span id="stock_${producto.id}">${producto.variantes[0].stock}</span></td>
                        <td>
                            <div class="tooltip-container">
                                <span class="tooltip" id="tooltip_${producto.id}">Maximum value: ${producto.variantes[0].stock}</span>
                                <div class="number-control">
                                    <div class="number-left" onclick='disminuirvalor("cantidad_${producto.id}")'></div>
                                    <input type="number" name="number" max="${producto.variantes[0].stock}" class="number-quantity" 
                                    id="cantidad_${producto.id}" autocomplete="off" value="${cantidadInicial}" oninput="maxValor(this)">
                                    <div class="number-right" onclick='aumentarvalor("cantidad_${producto.id}")'></div>
                                </div>
                            </div>
                        </td>
                        <td style="border-right: none;">
                            <div>
                                <button class="button_item" type="button" onclick="agregarAlCarrito('${producto.id}')">
                                    <span class="button_item__text">Add Item</span>
                                    <span class="button_item__icon">
                                        <svg class="svg" fill="none" height="24" stroke="currentColor" stroke-linecap="round" 
                                            stroke-linejoin="round" stroke-width="2" viewBox="0 0 24 24" width="24" 
                                            xmlns="http://www.w3.org/2000/svg">
                                            <line x1="12" x2="12" y1="5" y2="19"></line>
                                            <line x1="5" x2="19" y1="12" y2="12"></line>
                                        </svg>
                                    </span>
                                </button>
                            </div>
                        </td>
                    `;
                    tbody.appendChild(fila);
                });
            }

            // Actualizar la paginación
            const pagination = document.querySelector(".pagination");
            pagination.innerHTML = `
                ${data.has_prev ? `<button class="next" onclick="aplicarFiltros(${data.prev_num})">Previous</button>` : ""}
                <span>/ Page ${data.page} of ${data.pages} /</span>
                ${data.has_next ? `<button class="next" onclick="aplicarFiltros(${data.next_num})">Next</button>` : ""}
            `;

        })
        .catch(error => console.error("Error:", error));
}

function luhnCheck(cardNo) {
    let nDigits = cardNo.length;
 
    let nSum = 0;
    let isSecond = false;
    for (let i = nDigits - 1; i >= 0; i--){
 
        let d = cardNo[i].charCodeAt() - '0'.charCodeAt();
 
        if (isSecond == true)
            d = d * 2;
        // We add two digits to handle
        // cases that make two digits
        // after doubling
        nSum += parseInt(d / 10, 10);
        nSum += d % 10;
 
        isSecond = !isSecond;
    }
    console.log(nSum);
    return (nSum % 10 == 0);
}

function prepareSelectedProducts() {  
    const phone = document.getElementById('numero');
    const tarjeta = document.getElementById('card');
    let tarjeta_value = tarjeta.value.replace(/\s/g, '');
    if (carritolist.length === 0) {
        console.log("La lista está vacía.");
        alert('Selecciona al menos un producto.');
        return false;
    } if(!validarTelefono(phone)){
        return false;
    } if (!luhnCheck(tarjeta_value)){ //algoritmo de luhn
        alert('Tarjeta no valida');
        return false;
    }else {
        console.log("La lista tiene elementos.");
        // Crear un campo oculto para enviar el arreglo de seleccionados
        hiddenField = document.createElement("input");
        hiddenField.type = "hidden";
        hiddenField.name = "seleccionados";
        hiddenField.id = "hiddenSeleccionados";
        hiddenField.value = JSON.stringify(carritolist); // Convertir el arreglo a JSON
        document.getElementById("ventaForm").appendChild(hiddenField);
        document.getElementById('svg_loading').style.display = 'inline-block'; //muestra el loading
        document.getElementById('btn_cancel').disabled=true;
        document.getElementById('btn_subir').disabled = true;
        setTimeout(() => {
            document.getElementById('svg_loading').style.display = 'none'; // oculta el loading
            tarjeta.value = tarjeta_value; // se manda el valor de los números de tarjeta sin espacios
            alert('Formulario enviado'); // O puedes eliminar esta línea
            document.getElementById("ventaForm").submit(); // Enviar el formulario
        }, 2000);
        
        return false; // Para prevenir el envío inmediato del formulario
    }
}

function ocultarProductos(input){
    const tabla = document.getElementById('productostabla');
    const tabla1 = document.getElementById('carrito');
    if(tabla && tabla1){
        if(tabla.style.display === 'none' || tabla.style.display === ''){
            tabla.style.display = 'block'; //se muestran los productos
            tabla1.style.display = 'none'; //se oculta el carrito
            document.getElementById('btn_shcart').classList.remove('active');
        }else{
            tabla.style.display = 'none'; //se ocultan los productos, se muestra el carrito
            tabla1.style.display = 'block';
            document.getElementById('btn_shcart').classList.add('active');
        }
    }
    input.classList.toggle('active');
}

function ocultarCarrito(input){
    const tabla = document.getElementById('carrito');
    const tabla1 = document.getElementById('productostabla');
    if(tabla && tabla1){
        if(tabla.style.display === 'block' || tabla.style.display === ''){
            tabla.style.display = 'none';
        }else{
            tabla.style.display = 'block'; //se muestra el carrito
            tabla1.style.display = 'none';//se ocultan los productos si es el caso
            document.getElementById('btn_shproductos').classList.remove('active');
        }
    }
    input.classList.toggle('active');
}

function volverArriba() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth' // Desplazamiento suave
    });
}

function scrollToBottom() {
    window.scrollTo({
        top: document.body.scrollHeight,
        behavior: 'smooth' // Esto proporciona un desplazamiento suave
    });
}