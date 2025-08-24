
const displayMsg=(msg, id, colorName)=>{
    document.getElementById(id).innerText=msg
    document.getElementById(id).style.color=colorName

}

const fnameValidation = () =>{
    const first_name = document.getElementById('fname').value
    if(first_name == ""){
        displayMsg("First name is required",'fnameMsg','red')
        return false
    }
    else if(!first_name.match(/^([a-zA-Z])+$/)){
        displayMsg("First name can only be alphabet", 'fnameMsg', 'red')
        return false
    }
    else if(first_name.length<2){
        displayMsg('Firstname must be more thatn or equal to 2', 'fnameMsg', 'red')
        return false
    }
    else{
        displayMsg('FirstName is Valid', 'fnameMsg', 'green')
        return true
    }
}


const lnameValidation = () =>{
    const last_name = document.getElementById('fname').value
    if(last_name == ""){
        displayMsg("Last name is required",'lnameMsg','red')
        return false
    }
    else if(!last_name.match(/^([a-zA-Z])+$/)){
        displayMsg("Last  name can only be alphabet", 'lnameMsg', 'red')
        return false
    }
    else if(last_name.length<2){
        displayMsg('Last name must be more than or equal to 2', 'lnameMsg', 'red')
        return false
    }
    else{
        displayMsg('Last tName is Valid', 'lnameMsg', 'green')
        return true
    }
}

// const emailValidation=()=>{
//     const email = document.getElementById('email').value

//     if(email == ""){
//         displayMsg('Email is mandatory', 'emailMsg', 'red')
//         return false
//     }else if(email.match(/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/)){
//         displayMsg('email Invalid', 'emailMsg', 'red')
//         return false
//     }else if(email.length <2){
//         displayMsg('Email must be more than 2 characters','emailMsg', 'red')
//         return false
//     }else{
//         displayMsg('Email is Valid', 'emailMsg','green')
//         return true
//     }
// }


const emailValidation = () => {
    const email = document.getElementById('email').value.trim();
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

    if (email === "") {
        displayMsg('Email is mandatory', 'emailMsg', 'red');
        return false;
    } else if (!emailRegex.test(email)) {
        displayMsg('Email is invalid', 'emailMsg', 'red');
        return false;
    } else if (email.length < 2) {
        displayMsg('Email must be more than 2 characters', 'emailMsg', 'red');
        return false;
    } else {
        displayMsg('Email is valid', 'emailMsg', 'green');
        return true;
    }
};


const pswValidation=()=>{
    const psw =document.getElementById('psw').value

    if(psw==""){
        displayMsg('Password is mandatory','pswMsg','red')
        return false
    }else if(!psw.match(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]).{8,}$/)){
        displayMsg('Password is weak, and should be at least 8 characters like:Abc#123','pswMsg','red')
        return false
    }else{
        displayMsg('Password is valid','pswMsg','green')
        return true
    }
}

const cpswValidation=()=>{
    const psw= document.getElementById('psw').value
    const cpsw= document.getElementById('cpsw').value

    if(cpsw==""){
        displayMsg('Cpassword is mandatory', 'cpswMsg', 'red')
        return false
    }else if(psw!=cpsw){
        displayMsg('Cpassword and password doesnot match', 'cpsw', 'red')
        return false
    }else{
        displayMsg('Cpassword is confirmed', 'cpswMsg','green')
        return true
    }
}



const validForm=()=>{
    if(fnameValidation() && lnameValidation() && emailValidation() && pswValidation() && cpswValidation()){
        displayMsg('Form submitted successfully!', 'submitMsg', 'green')
    }else{
        return false
    }
}


function hideShow(icon){
    const psw = document.getElementById('psw');
    if(psw.type==="password"){
        psw.type="text";
        icon.classList.remove("fa-eye");
        icon.classList.add("fa-eye-slash");
    }else{
        pswd.type="password"
        icon.classList.remove("fa-eye-slash");
        icon.classList.add("fa-eye");
    }
}


function hideShoww(icon){
    const cpsw = document.getElementById('cpsw');
    if(cpsw.type==="password"){
        cpsw.type="text";
        icon.classList.remove("fa-eye");
        icon.classList.add("fa-eye-slash");
    }else{
        cpsw.type="password"
        icon.classList.remove("fa-eye-slash");
        icon.classList.add("fa-eye");
    }
}