function validatePasswords() {
    // Obtén los valores de los dos campos de contraseña
    const password = document.getElementById('newpassword').value;
    const password2 = document.getElementById('newpassword2').value;
    const message = document.getElementById('password-match-message');

    // Comprueba si las contraseñas coinciden y muestra u oculta el mensaje
    if (password && password2) {
        if (password === password2) {
            message.style.display = 'none';
            return true;
        } else {
            message.textContent = 'Passwords do not match.';
            message.style.display = 'block';
            return false;
        }
    } else {
        message.style.display = 'none';
        return true; //permite el envío si no hay contraseñas
    }
}

function validarCorreo(input) {
    var valCorreo = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
    const error = document.getElementById('message');
    if (!valCorreo.test(input.value)) {
        error.textContent = 'Invalid Email.';
        error.style.display = 'block';
        return false;
    } else {
        error.style.display = 'none';
        return true;
    }
}

function validarTelefono(input) {
    const regex = /^\d{8,10}$/; // Solo permite 10 dígitos numéricos
    const error = document.getElementById('message1');
    if (!regex.test(input.value)) {
        error.textContent = 'Invalid Phone.';
        error.style.display = 'block';
        return false;
    } else {
        error.style.display = 'none';
        return true;
    }
}

function validarLetras(input) {
    // Elimina cualquier carácter que no sea una letra
    input.value = input.value.replace(/[^a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]/g, '');
}

function validarNumeros(input){
    input.value = input.value.replace(/\D/g, '');
}

function validateForm(event) {
    // Realiza las validaciones de los campos
    const correo = document.getElementById('email');
    const phone = document.getElementById('number');
    if (!validatePasswords()) {
        event.preventDefault(); // Evita el envío del formulario
        return false; // No permite el envío del formulario
    }else if(!validarTelefono(phone)){
        event.preventDefault(); // Evita el envío del formulario
        return false;
    }else if(!validarCorreo(correo)){
        event.preventDefault(); // Evita el envío del formulario
        return false;
    }
    activarIdinput('id') //si todo sale bien se activa el campo id 
    return true;
}
