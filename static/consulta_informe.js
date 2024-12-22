function solicita_permiso(url){
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
            return fetch('/autoriza_descarga', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ password: password, url: url})
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(response.statusText);
                }
                return response.blob(); // Convertir la respuesta a Blob para manejar la descarga
            })
            .then(blob => {
                // Crear una URL para el Blob y descargar el archivo
                const downloadUrl = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = downloadUrl;
                a.download = url; // Usar el nombre del archivo desde la URL proporcionada
                document.body.appendChild(a);
                a.click();
                a.remove();
            })
            .catch(error => {
                Swal.showValidationMessage(
                    `Error: ${error.message}`
                );
            });
        }
    });
}

function reload(){
    location.reload();
}