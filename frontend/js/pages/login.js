const btn_view_password = document.getElementById("btn-view-password");
const input_password = document.getElementById("password")


// Evento para exibir a senha quando clicar no icones do olho;
btn_view_password.addEventListener("click", () => {
    if(input_password.type === "password"){
        input_password.type = "text";
        btn_view_password.textContent = "visibility_off";
    }else{
        input_password.type = "password";
        btn_view_password.textContent = "visibility";
    }
})