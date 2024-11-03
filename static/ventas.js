function aumentarvalor(inputId){
    const input = document.getElementById(inputId);
    const maxValue = input.getAttribute('max');
    if (input.value == '' || input.value < 1){
        input.value = 1;
    }else if(input.value < maxValue){
        input.value = parseInt(input.value) + 1;
    }
}

function disminuirvalor(inputId){
    const input = document.getElementById(inputId);
    if (input.value > 1){
        input.value = parseInt(input.value) - 1;
    }else if(input.value < 1){
        input.value = 1;
    }
}

function actualizarStock(productoId){
    const selectTalla = document.getElementById(`sel_talla_${productoId}`);
    const spanStock = document.getElementById(`stock_${productoId}`);

    if (selectTalla) {
        const selectedOption = selectTalla.options[selectTalla.selectedIndex];
        const stock = selectedOption.getAttribute('data-stock');
        spanStock.innerText = stock;
    }
}

let carritolist = [] //varible gobal

function actualizarCompra(productoId, talla, inputId, tipo){
    const input_cantidad = document.getElementById(inputId);
    const index = carritolist.findIndex(item => item.id === productoId && item.talla === talla);
    const cantidadActual = carritolist[index].cantidad;
    const maxValue = parseInt(input_cantidad.getAttribute('max'));
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
        nueva_cantidad = parseInt(input_cantidad.value);
    }

    if (nueva_cantidad <= maxValue && nueva_cantidad >= 1) {
        carritolist[index] = {
        ...carritolist[index], // Mantiene las propiedades existentes
        cantidad: nueva_cantidad, // Actualiza el valor de cantidad
        };
        document.getElementById(`unidades_${productoId}`).value = nueva_cantidad; //Se actualiza el input del carrito, no de la lista, el de la lista de actualiza si mandas el producto desde ahí
        document.getElementById(`total_${productoId}`).innerText = "$" + (precio_real * nueva_cantidad);
        console.log(carritolist)
    } else if(nueva_cantidad > maxValue){ //en caso de que las unidades colocadas superen a la actual
        carritolist[index] = {
            ...carritolist[index], // Mantiene las propiedades existentes
            cantidad: maxValue, // Actualiza el valor de cantidad
        };
        document.getElementById(`unidades_${productoId}`).value = maxValue;
        document.getElementById(`total_${productoId}`).innerText = "$" + (precio_real * maxValue);
        console.log(carritolist)
    }
    actualiazartotal()
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

    parrafo.innerText = 'Total: $' + total;
}

function agregarAlCarrito(productoId) {
    const carrito = document.querySelector("#tablaCarrito tbody");
    const talla = document.getElementById(`sel_talla_${productoId}`)?.value || document.getElementById(`span_talla_${productoId}`).innerText;
    const input_cantidad = document.getElementById(`cantidad_${productoId}`);
    const maxValue = parseInt(input_cantidad.getAttribute('max'));
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
        filaCarrito.id = `carrito_${productoId}`;
        filaCarrito.innerHTML = `
            <td><div class="contenedor-square" ><img id="img_${productoId}" src="${producto_archivo}" class="cuadrada"></div></td>
            <td>${productoNombre}</td>
            <td>${talla}</td>
            <td>
                <div class="number-control">
                    <div class="number-left" onclick='actualizarCompra("${productoId}", "${talla}", "unidades_${productoId}", "menos")'></div>
                    <input type="number" name="number" min="1" max="${maxValue}" class="number-quantity" id="unidades_${productoId}" autocomplete="off" value="${cantidad}" oninput="actualizarCompra("${productoId}", "${talla}", "unidades_${productoId}", "otro")">
                    <div class="number-right" onclick='actualizarCompra("${productoId}", "${talla}", "unidades_${productoId}", "mas1")'></div>
                </div>
            </td>
            <td class="precio" id='total_${productoId}'>$${precio_total}</td>
            <td><button type="button" onclick="eliminarDelCarrito('${productoId}')">Eliminar</button></td>
        `;
        carritolist.push({ id: productoId, cantidad: cantidad, talla: talla });
        console.log(carritolist);
        carrito.appendChild(filaCarrito);
        input_cantidad.value = '1';
        actualiazartotal();
    }
}

function eliminarDelCarrito(productoId) {
    const filaCarrito = document.getElementById(`carrito_${productoId}`);
    if (filaCarrito) {
        filaCarrito.remove();
    }
    const indexToRemove = carritolist.findIndex(item => item.id === productoId);
    if (indexToRemove !== -1) {
        carritolist.splice(indexToRemove, 1);
    }
    actualiazartotal()
    console.log(carritolist)
}

function aplicarFiltros() {
    const nombre = document.getElementById("buscador").value;
    const categoria = document.getElementById("filtroCategoria").value;

    fetch(`/filtrar_productos?nombre=${nombre}&categoria=${categoria}`)
        .then(response => response.json())
        .then(data => {
            const tbody = document.querySelector("tbody");
            tbody.innerHTML = "";  // Limpiamos las filas existentes

            if (data.productos.length === 0) {
                const fila = document.createElement("tr");
                fila.innerHTML = `
                    <td colspan="9" style="text-align: center; color: red;">
                        No results found for this search. If searching by ID, please make sure to enter the complete ID.
                    </td>
                `;
                tbody.appendChild(fila);
            } else {
                data.productos.forEach(producto => {
                    const fila = document.createElement("tr");
                    fila.innerHTML = `
                        <td>${producto.id}</td>
                        <td><div class="contenedor-square"><img id="img_${producto.id}" src="static/images/products/${producto.archivo}" class="cuadrada"></div></td>
                        <td id="name_${producto.id}">${producto.nombre}</td>
                        <td id="precio_${producto.id}">$${producto.precio}</td>
                        <td>${producto.categoria}</td>
                        <td>
                            ${producto.variantes.length > 1 ? 
                                `<select id="sel_talla_${producto.id}" name="talla_${producto.id}" onchange="actualizarStock('${producto.id}')">
                                    ${producto.variantes.map(variante => 
                                        `<option value="${variante.talla}" data-stock="${variante.stock}">${variante.talla}</option>`).join('')}
                                </select>` 
                                : `<span id="span_talla_${producto.id}" data-stock="${producto.variantes[0].stock}">${producto.variantes[0].talla}</span>`
                            }
                        </td>
                        <td>${producto.color}</td>
                        <td><span id="stock_${producto.id}">${producto.variantes[0].stock}</span></td>
                        <td>
                        <div class="number-control">
                            <div class="number-left" onclick='disminuirvalor("cantidad_${producto.id}")'></div>
                            <input type="number" name="number" min="1" max="${producto.variantes[0].stock}" class="number-quantity" id="cantidad_${producto.id}" autocomplete="off" value="1">
                            <div class="number-right" onclick='aumentarvalor("cantidad_${producto.id}")'></div>
                        </div>
                        </td>
                        <td>
                        <div>
                            <button class="button_item" type="button" onclick="agregarAlCarrito('${producto.id}')">
                                <span class="button_item__text">Add Item</span>
                                <span class="button_item__icon"><svg class="svg" fill="none" height="24" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" viewBox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg"><line x1="12" x2="12" y1="5" y2="19"></line><line x1="5" x2="19" y1="12" y2="12"></line></svg></span>
                            </button>
                        </div>
                        </td>
                    `;
                    tbody.appendChild(fila);
                });
            }

        })
        .catch(error => console.error("Error:", error));
}