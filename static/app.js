const realFileBtn = document.getElementById('pemFile');
const customBtn = document.getElementById('customButton');
const customTxt = document.getElementById('customText');

customBtn.addEventListener('click', function() {
    realFileBtn.click();
});

realFileBtn.addEventListener('change', function() {
    if (realFileBtn.files.length > 0) {
        customTxt.textContent = realFileBtn.files[0].name;
    } else {
        customTxt.textContent = "No file selected";
    }
});

function redireccion(paginaDest){
    location.href=paginaDest
}