function validatePasswords() {
    // Obtén los valores de los dos campos de contraseña
    const password = document.getElementById('newpassword');
    const password2 = document.getElementById('newpassword2');
    const message = document.getElementById('password-match-message');

    // Comprueba si las contraseñas coinciden y muestra u oculta el mensaje
    if (password && password2) {
        if (password.value === password2.value) {
            message.style.display = 'none';
            return true;
        } else {
            message.textContent = 'Passwords do not match.';
            message.style.display = 'block';
            return false;
        }
    } else {
        if(message){
            message.style.display = 'none';
        }
        return true; //permite el envío si no hay contraseñas
    }
}

function validarCorreo(input) {
    var valCorreo = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
    const error = document.getElementById('message');
    input.setCustomValidity('')
    error.style.display = 'none';
    if (input.value != ''){
        if (!valCorreo.test(input.value)) {
            error.textContent = 'Invalid Email.';
            error.style.display = 'block';
            return false;
        } else {
            error.style.display = 'none';
            return true;
        }
    }
    
}

function validarTelefono(input) {
    const regex = /^\d{8,10}$/; // Solo permite 10 dígitos numéricos
    const error = document.getElementById('message1');
    input.setCustomValidity('');
    error.style.display = 'none';
    if (input.value != ''){
        if (!regex.test(input.value)) {
            error.textContent = 'Invalid Phone.';
            error.style.display = 'block';
            return false;
        } else {
            error.style.display = 'none';
            return true;
        }
    }
}

function validarLetras(input) {
    // Elimina cualquier carácter que no sea una letra
    input.value = input.value.replace(/[^a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]/g, '');
}

function validarNumeros(input){
    input.value = input.value.replace(/\D/g, '');
}

function validateForm() {
    // Realiza las validaciones de los campos
    const correo = document.getElementById('email');
    const phone = document.getElementById('number');
    if (!validatePasswords()) {
        return false; // No permite el envío del formulario
    }else if(!validarTelefono(phone)){
        return false;
    }else if(!validarCorreo(correo)){
        return false;
    }
    activarIdinput('id') //si todo sale bien se activa el campo id 
    return true;
}

function mostrarLogoTarjeta(tipoTarjeta) {
    const contenedor = document.querySelector('.logoContainer');
    contenedor.innerHTML = ''; // Limpia el contenido actual

    let svg;
    if (tipoTarjeta === 'amex') {
        svg = `
                <svg
            fill="#000000"
            xml:space="preserve"
            viewBox="0 0 512 512"
            xmlns:xlink="http://www.w3.org/1999/xlink"
            xmlns="http://www.w3.org/2000/svg"
            id="Capa_1"
            version="1.1"
            class="svgLogo"
            >
            <g stroke-width="0" id="SVGRepo_bgCarrier"></g>
            <g
                stroke-linejoin="round"
                stroke-linecap="round"
                id="SVGRepo_tracerCarrier"
            ></g>
            <g id="SVGRepo_iconCarrier">
                <path
                d="M512,402.281c0,16.716-13.55,30.267-30.265,30.267H30.265C13.55,432.549,0,418.997,0,402.281V109.717 c0-16.715,13.55-30.266,30.265-30.266h451.47c16.716,0,30.265,13.551,30.265,30.266V402.281L512,402.281z"
                style="fill:#306FC5;"
                ></path>
                <path
                d="M21.517,402.281V109.717 c0-16.715,13.552-30.266,30.267-30.266h-21.52C13.55,79.451,0,93.001,0,109.717v292.565c0,16.716,13.55,30.267,30.265,30.267h21.52 C35.07,432.549,21.517,418.997,21.517,402.281z"
                style="opacity:0.15;fill:#202121;enable-background:new ;"
                ></path>
                <g>
                <polygon
                    points="74.59,220.748 89.888,220.748 82.241,201.278"
                    style="fill:#FFFFFF;"
                ></polygon>
                <polygon
                    points="155.946,286.107 155.946,295.148 181.675,295.148 181.675,304.885 155.946,304.885 155.946,315.318 184.455,315.318 197.666,300.712 185.151,286.107"
                    style="fill:#FFFFFF;"
                ></polygon>
                <polygon
                    points="356.898,201.278 348.553,220.748 364.548,220.748"
                    style="fill:#FFFFFF;"
                ></polygon>
                <polygon
                    points="230.348,320.875 230.348,281.241 212.268,300.712"
                    style="fill:#FFFFFF;"
                ></polygon>
                <path
                    d="M264.42,292.368c-0.696-4.172-3.48-6.261-7.654-6.261h-14.599v12.516h15.299 C261.637,298.624,264.42,296.539,264.42,292.368z"
                    style="fill:#FFFFFF;"
                ></path>
                <path
                    d="M313.09,297.236c1.391-0.697,2.089-2.785,2.089-4.867c0.696-2.779-0.698-4.172-2.089-4.868 c-1.387-0.696-3.476-0.696-5.559-0.696h-13.91v11.127h13.909C309.613,297.932,311.702,297.932,313.09,297.236z"
                    style="fill:#FFFFFF;"
                ></path>
                <path
                    d="M413.217,183.198v8.344l-4.169-8.344H376.37v8.344l-4.174-8.344h-44.502 c-7.648,0-13.909,1.392-19.469,4.173v-4.173h-31.289v0.696v3.477c-3.476-2.78-7.648-4.173-13.211-4.173h-111.95l-7.652,17.384 l-7.647-17.384h-25.031h-10.431v8.344l-3.477-8.344h-0.696H66.942l-13.909,32.68L37.042,251.34l-0.294,0.697h0.294h35.463h0.444 l0.252-0.697l4.174-10.428h9.039l4.172,11.125h40.326v-0.697v-7.647l3.479,8.343h20.163l3.475-8.343v7.647v0.697h15.993h79.965 h0.696v-18.08h1.394c1.389,0,1.389,0,1.389,2.087v15.297h50.065v-4.172c4.172,2.089,10.426,4.172,18.771,4.172h20.863l4.172-11.123 h9.732l4.172,11.123h40.328v-6.952v-3.476l6.261,10.428h1.387h0.698h30.595v-68.143h-31.291l0,0H413.217z M177.501,241.609h-6.955 h-4.171v-4.169v-34.076l-0.696,1.595v-0.019l-16.176,36.669h-0.512h-3.719h-6.017l-16.687-38.245v38.245h-23.64l-4.867-10.43 H70.417l-4.868,10.43H53.326l20.57-48.675h17.382l19.469,46.587v-46.587h4.171h14.251l0.328,0.697h0.024l8.773,19.094l6.3,14.306 l0.223-0.721l13.906-33.375H177.5v48.674H177.501L177.501,241.609z M225.481,203.364h-27.119v9.039h26.423v9.734h-26.423v9.738 h27.119v10.427h-38.939v-49.367h38.939V203.364L225.481,203.364z M275.076,221.294c0.018,0.016,0.041,0.027,0.063,0.042 c0.263,0.278,0.488,0.557,0.68,0.824c1.332,1.746,2.409,4.343,2.463,8.151c0.004,0.066,0.007,0.131,0.011,0.197 c0,0.038,0.007,0.071,0.007,0.11c0,0.022-0.002,0.039-0.002,0.06c0.016,0.383,0.026,0.774,0.026,1.197v9.735h-10.428v-5.565 c0-2.781,0-6.954-2.089-9.735c-0.657-0.657-1.322-1.09-2.046-1.398c-1.042-0.675-3.017-0.686-6.295-0.686h-12.52v17.384h-11.818 v-48.675h26.425c6.254,0,10.428,0,13.906,2.086c3.407,2.046,5.465,5.439,5.543,10.812c-0.161,7.4-4.911,11.46-8.326,12.829 C270.676,218.662,272.996,219.129,275.076,221.294z M298.491,241.609h-11.822v-48.675h11.822V241.609z M434.083,241.609h-15.3 l-22.25-36.855v30.595l-0.073-0.072v6.362h-11.747v-0.029h-11.822l-4.172-10.43H344.38l-4.172,11.123h-13.211 c-5.559,0-12.517-1.389-16.687-5.561c-4.172-4.172-6.256-9.735-6.256-18.773c0-6.953,1.389-13.911,6.256-19.472 c3.474-4.175,9.735-5.562,17.382-5.562h11.128v10.429h-11.128c-4.172,0-6.254,0.693-9.041,2.783 c-2.082,2.085-3.474,6.256-3.474,11.123c0,5.564,0.696,9.04,3.474,11.821c2.091,2.089,4.87,2.785,8.346,2.785h4.867l15.991-38.243 h6.957h10.428l19.472,46.587v-2.376v-15.705v-1.389v-27.116h17.382l20.161,34.07v-34.07h11.826v47.977h0.002L434.083,241.609 L434.083,241.609z"
                    style="fill:#FFFFFF;"
                ></path>
                <path
                    d="M265.161,213.207c0.203-0.217,0.387-0.463,0.543-0.745c0.63-0.997,1.352-2.793,0.963-5.244 c-0.016-0.225-0.057-0.433-0.105-0.634c-0.013-0.056-0.011-0.105-0.026-0.161l-0.007,0.001c-0.346-1.191-1.229-1.923-2.11-2.367 c-1.394-0.693-3.48-0.693-5.565-0.693h-13.909v11.127h13.909c2.085,0,4.172,0,5.565-0.697c0.209-0.106,0.395-0.25,0.574-0.413 l0.002,0.009C264.996,213.389,265.067,213.315,265.161,213.207z"
                    style="fill:#FFFFFF;"
                ></path>
                <path
                    d="M475.105,311.144c0-4.867-1.389-9.736-3.474-13.212v-31.289h-0.032v-2.089c0,0-29.145,0-33.483,0 c-4.336,0-9.598,4.171-9.598,4.171v-4.171h-31.984c-4.87,0-11.124,1.392-13.909,4.171v-4.171h-57.016v2.089v2.081 c-4.169-3.474-11.824-4.171-15.298-4.171h-37.549v2.089v2.081c-3.476-3.474-11.824-4.171-15.998-4.171H215.05l-9.737,10.431 l-9.04-10.431h-2.911h-4.737h-54.93v2.089v5.493v62.651h61.19l10.054-10.057l8.715,10.057h0.698h35.258h1.598h0.696h0.692v-6.953 v-9.039h3.479c4.863,0,11.124,0,15.991-2.089v17.382v1.394h31.291v-1.394V317.4h1.387c2.089,0,2.089,0,2.089,2.086v14.6v1.394 h94.563c6.263,0,12.517-1.394,15.993-4.175v2.781v1.394h29.902c6.254,0,12.517-0.695,16.689-3.478 c6.402-3.841,10.437-10.64,11.037-18.749c0.028-0.24,0.063-0.48,0.085-0.721l-0.041-0.039 C475.087,312.043,475.105,311.598,475.105,311.144z M256.076,306.973h-13.91v2.081v4.174v4.173v7.649h-22.855l-13.302-15.299 l-0.046,0.051l-0.65-0.748l-15.297,15.996h-44.501v-48.673h45.197l12.348,13.525l2.596,2.832l0.352-0.365l14.604-15.991h36.852 c7.152,0,15.161,1.765,18.196,9.042c0.365,1.441,0.577,3.043,0.577,4.863C276.237,304.189,266.502,306.973,256.076,306.973z M325.609,306.276c1.389,2.081,2.085,4.867,2.085,9.041v9.732h-11.819v-6.256c0-2.786,0-7.65-2.089-9.739 c-1.387-2.081-4.172-2.081-8.341-2.081H292.93v18.077h-11.82v-49.369h26.421c5.559,0,10.426,0,13.909,2.084 c3.474,2.088,6.254,5.565,6.254,11.128c0,7.647-4.865,11.819-8.343,13.212C322.829,303.49,324.914,304.885,325.609,306.276z M373.589,286.107h-27.122v9.04h26.424v9.737h-26.424v9.736h27.122v10.429H334.65V275.68h38.939V286.107z M402.791,325.05h-22.252 v-10.429h22.252c2.082,0,3.476,0,4.87-1.392c0.696-0.697,1.387-2.085,1.387-3.477c0-1.394-0.691-2.778-1.387-3.475 c-0.698-0.695-2.091-1.391-4.176-1.391c-11.126-0.696-24.337,0-24.337-15.296c0-6.954,4.172-14.604,16.689-14.604h22.945v11.819 h-21.554c-2.085,0-3.478,0-4.87,0.696c-1.387,0.697-1.387,2.089-1.387,3.478c0,2.087,1.387,2.783,2.778,3.473 c1.394,0.697,2.783,0.697,4.172,0.697h6.259c6.259,0,10.43,1.391,13.211,4.173c2.087,2.087,3.478,5.564,3.478,10.43 C420.869,320.179,414.611,325.05,402.791,325.05z M462.59,320.179c-2.778,2.785-7.648,4.871-14.604,4.871H425.74v-10.429h22.245 c2.087,0,3.481,0,4.87-1.392c0.693-0.697,1.391-2.085,1.391-3.477c0-1.394-0.698-2.778-1.391-3.475 c-0.696-0.695-2.085-1.391-4.172-1.391c-11.122-0.696-24.337,0-24.337-15.295c0-6.609,3.781-12.579,13.106-14.352 c1.115-0.154,2.293-0.253,3.583-0.253h22.948v11.819h-15.3h-5.561h-0.696c-2.087,0-3.476,0-4.865,0.696 c-0.7,0.697-1.396,2.089-1.396,3.478c0,2.087,0.696,2.783,2.785,3.473c1.389,0.697,2.78,0.697,4.172,0.697h0.691h5.565 c3.039,0,5.337,0.375,7.44,1.114c1.926,0.697,8.302,3.549,9.728,10.994c0.124,0.78,0.215,1.594,0.215,2.495 C466.761,313.925,465.37,317.401,462.59,320.179z"
                    style="fill:#FFFFFF;"
                ></path>
                </g>
            </g>
            </svg>
         `; // SVG de Visa
    } else if (tipoTarjeta === 'visa') {
        svg =  `
                <br><br><br><svg viewBox="0 0 256 83" width="70" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <linearGradient
                x="0px"
                y="0px"
                id="logosVisa0"
                class="svgLogo"
                >
                <stop stop-color="#222357" offset="0%"></stop>
                <stop stop-color="#254AA5" offset="100%"></stop>
                </linearGradient>
            </defs>
            <path
                transform="matrix(1 0 0 -1 0 82.668)"
                d="M132.397 56.24c-.146-11.516 10.263-17.942 18.104-21.763c8.056-3.92 10.762-6.434 10.73-9.94c-.06-5.365-6.426-7.733-12.383-7.825c-10.393-.161-16.436 2.806-21.24 5.05l-3.744-17.519c4.82-2.221 13.745-4.158 23-4.243c21.725 0 35.938 10.724 36.015 27.351c.085 21.102-29.188 22.27-28.988 31.702c.069 2.86 2.798 5.912 8.778 6.688c2.96.392 11.131.692 20.395-3.574l3.636 16.95c-4.982 1.814-11.385 3.551-19.357 3.551c-20.448 0-34.83-10.87-34.946-26.428m89.241 24.968c-3.967 0-7.31-2.314-8.802-5.865L181.803 1.245h21.709l4.32 11.939h26.528l2.506-11.939H256l-16.697 79.963zm3.037-21.601l6.265-30.027h-17.158zm-118.599 21.6L88.964 1.246h20.687l17.104 79.963zm-30.603 0L53.941 26.782l-8.71 46.277c-1.022 5.166-5.058 8.149-9.54 8.149H.493L0 78.886c7.226-1.568 15.436-4.097 20.41-6.803c3.044-1.653 3.912-3.098 4.912-7.026L41.819 1.245H63.68l33.516 79.963z"
                fill="url(#logosVisa0)"
            ></path>
            </svg>
         `; // SVG de Amex
    } else if(tipoTarjeta === 'master'){
        svg = `
              <svg
                            xmlns="http://www.w3.org/2000/svg"
                            x="0px"
                            y="0px"
                            width="30"
                            height="30"
                            viewBox="0 0 48 48"
                            class="svgLogo"
                          >
                            <path
                              fill="#ff9800"
                              d="M32 10A14 14 0 1 0 32 38A14 14 0 1 0 32 10Z"
                            ></path>
                            <path
                              fill="#d50000"
                              d="M16 10A14 14 0 1 0 16 38A14 14 0 1 0 16 10Z"
                            ></path>
                            <path
                              fill="#ff3d00"
                              d="M18,24c0,4.755,2.376,8.95,6,11.48c3.624-2.53,6-6.725,6-11.48s-2.376-8.95-6-11.48 C20.376,15.05,18,19.245,18,24z"
                            ></path>
                          </svg>
        `;
    } else{
        svg = `
        <svg class="w-6 h-6 text-gray-800 dark:text-white" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" viewBox="0 0 24 24">
        <path fill-rule="evenodd" d="M2 12C2 6.477 6.477 2 12 2s10 4.477 10 10-4.477 10-10 10S2 17.523 2 12Zm11-4a1 1 0 1 0-2 0v5a1 1 0 1 0 2 0V8Zm-1 7a1 1 0 1 0 0 2h.01a1 1 0 1 0 0-2H12Z" clip-rule="evenodd"/>
      </svg>`;
    }

    if (svg) {
        contenedor.innerHTML = svg; 
    }
}

function detectarTipoTarjeta(input) {
    const numeroTarjeta = input.value;
    if (numeroTarjeta != ''){
        if (/^4/.test(numeroTarjeta)) {
            mostrarLogoTarjeta('visa');
        } else if (/^3[47]/.test(numeroTarjeta)) {
            mostrarLogoTarjeta('amex');
        } else if (/^5[12345]/.test(numeroTarjeta)) {
            mostrarLogoTarjeta('master');
        }else {
            mostrarLogoTarjeta(null); // Limpia el logo si no coincide con ninguna
        }
    }
}

function espacios(input){
    input.value = input.value.replace(/\D/g, ''); //Elimina cualquier cosa que no sea una letra
    let value = input.value.replace(/\s/g, ''); //Quita los espacios actuales interpuestos
    // Separar en grupos de 4 dígitos y unir con un espacio
    let formattedValue = value.replace(/(.{4})/g, '$1 ').trim();

    // Actualizar el valor del input
    input.value = formattedValue;
}