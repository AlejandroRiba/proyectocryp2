const realFileBtn = document.getElementById('image');
const customBtn = document.getElementById('customButton');
const customTxt = document.getElementById('customText');
const checkBox = document.getElementById('editimage');
const inputImg = document.getElementById('image');

customBtn.addEventListener('click', function() {
    realFileBtn.click();
});

realFileBtn.addEventListener('change', function() {
    if (realFileBtn.files.length > 0) {
        customBtn.textContent = realFileBtn.files[0].name;
    } else {
        customBtn.textContent = "No image selected";
    }
});


function edit_image(){
    if(checkBox.checked){
        inputImg.disabled = false;
        customBtn.classList.remove('customButtondisabled');
        customBtn.classList.add('customButton');
        customBtn.style.cursor = "auto";
        if (realFileBtn.files.length > 0) {
            customBtn.textContent = realFileBtn.files[0].name;
        } else {
            customBtn.textContent = "No image selected";
        }
    } else{
        inputImg.disabled = true;
        customBtn.style.cursor = "not-allowed";
        customBtn.classList.add('customButtondisabled');
        customBtn.classList.remove('customButton');
    }
}

document.addEventListener('DOMContentLoaded', edit_image);