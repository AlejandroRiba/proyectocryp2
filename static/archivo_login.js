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


function verificarAdmin(input){
    if(input.value == 'admin'){
        realFileBtn.disabled = true;
        customBtn.style.cursor = "not-allowed";
        customBtn.style.pointerEvents = "none";
        customBtn.classList.add('customButtondisabled');
        customBtn.classList.remove('customButton');
        customTxt.textContent = "Welcome, admin. First time is not necessary the key.\n If you're an employee, please, upload a file or try it and we'll laugh at you LOL.";
    }else{
        customBtn.classList.remove('customButtondisabled');
        customBtn.classList.add('customButton');
        customBtn.style.cursor = "auto";
        customBtn.style.pointerEvents = "auto";
        customTxt.textContent = "No file selected.";
    }
}