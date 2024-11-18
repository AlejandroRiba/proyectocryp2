function aplicarFiltros(page = 1) {
    const nombre = document.getElementById("buscador").value;
    const categoria = document.querySelector(`input[name="filtro"]:checked`).value

    fetch(`/filtrar_productos?nombre=${nombre}&categoria=${categoria}&page=${page}&consulta=${consulta}`)
        .then(response => response.json())
        .then(data => {
            const tbody = document.querySelector("tbody");
            tbody.innerHTML = ""; // Limpiamos las filas existentes

            if (data.productos.length === 0) {
                const fila = document.createElement("tr");
                fila.innerHTML = `
                    <td colspan="10" style="text-align: center; color: var(--color-warning); border-left: none; border-right: none">
                        No results found for this search.
                    </td>
                `;
                tbody.appendChild(fila);
            } else {
                data.productos.forEach(producto => {
                    const fila = document.createElement("tr");
                    let stock = producto.variantes[0]?.stock || 0; // Obtén el valor de stock
                    let cantidadInicial = stock > 0 ? 1 : 0; // Define 1 si el stock es mayor a 0, de lo contrario 0

                    // Renderiza las columnas condicionalmente
                    let acciones = "";
                    if (data.consulta === "venta") {
                        acciones = `
                            <td>
                                <div class="tooltip-container">
                                    <span class="tooltip" id="tooltip_${producto.id}">Maximum value: ${stock}</span>
                                    <div class="number-control">
                                        <div class="number-left" onclick='disminuirvalor("cantidad_${producto.id}")'></div>
                                        <input type="number" name="number" max="${stock}" class="number-quantity" 
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
                            </td>`;
                    } else {
                        acciones = `
                            <td><a href="/editar_producto/${producto.id}"><img src="static/images/edit.svg" style="height: 30px;"></a></td>
                            <td style="border-right: none;"><img src="static/images/delete.svg" style="height: 30px; cursor: pointer;" onclick="deleteProduct('${producto.id}')"></td>`;
                    }

                    fila.innerHTML = `
                        <td style="border-left: none;">${producto.id}</td>
                        <td><div class="contenedor-square"><img id="img_${producto.id}" src="static/images/products/${producto.archivo}" class="cuadrada"></div></td>
                        <td id="name_${producto.id}">${producto.nombre}</td>
                        <td id="precio_${producto.id}">$${producto.precio}</td>
                        <td>${producto.categoria}</td>
                        <td>${producto.variantes.length > 1 ? 
                            `<div style="display: flex; padding: 6px 0;">
                                ${producto.variantes.map((variante, index) => 
                                    `${index % 4 === 0 && index !== 0 ? `</div><div style="display: flex; padding: 6px 0;">` : ""}
                                    <div class="wrapper">
                                        <div class="option" onclick="actualizarStock('${producto.id}', '${variante.talla}')">
                                            <input ${index === 0 ? "checked" : ""} id="option_${producto.id}_${variante.talla}" 
                                                value="${variante.talla}" data-stock="${variante.stock}" 
                                                name="btn_${producto.id}" type="radio" class="input"/>
                                            <div class="btn">
                                                <span class="span">${variante.talla}</span>
                                            </div>
                                        </div>
                                    </div>`
                                ).join('')}
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
                        <td><span id="stock_${producto.id}">${stock}</span></td>
                        ${acciones}
                    `;
                    tbody.appendChild(fila);
                });
            }

            // Actualizar la paginación
            const pagination = document.querySelector(".pagination");
            pagination.innerHTML = `
                ${data.has_prev ? `<button class="next" onclick="aplicarFiltros(${data.prev_num}, '${data.consulta}')">Previous</button>` : ""}
                <span>/ Page ${data.page} of ${data.pages} /</span>
                ${data.has_next ? `<button class="next" onclick="aplicarFiltros(${data.next_num}, '${data.consulta}')">Next</button>` : ""}
            `;

        })
        .catch(error => console.error("Error:", error));
}