// Utility function to display messages
const displayMsg = (msg, id, colorName) => {
  const element = document.getElementById(id);
  element.textContent = msg;
  element.style.color = colorName;
};

// Validation functions
const fnameValidation = () => {
  const first_name = document.getElementById('fname').value.trim();
  if (first_name === "") {
    displayMsg("First name is required!", 'fnameMsg', 'red');
    return false;
  } else if (first_name.length < 3) {
    displayMsg("First name should be more than 2 characters", 'fnameMsg', 'red');
    return false;
  } else {
    displayMsg('First Name is valid', 'fnameMsg', 'green');
    return true;
  }
};

const lnameValidation = () => {
  const last_name = document.getElementById('lname').value.trim();
  if (last_name === "") {
    displayMsg("Last name is required!", 'lnameMsg', 'red');
    return false;
  } else if (last_name.length < 3) {
    displayMsg("Last name should be more than 2 characters", 'lnameMsg', 'red');
    return false;
  } else {
    displayMsg('Last name is valid', 'lnameMsg', 'green');
    return true;
  }
};

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

const pswValidation = () => {
  const psw = document.getElementById('psw').value;

  if (psw === "") {
    displayMsg('Password is mandatory', 'pswMsg', 'red');
    return false;
  } else if (!psw.match(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]).{8,}$/)) {
    displayMsg('Password is weak, and should be at least 8 characters like: Abc#123', 'pswMsg', 'red');
    return false;
  } else {
    displayMsg('Password is valid', 'pswMsg', 'green');
    return true;
  }
};

const cpswValidation = () => {
  const psw = document.getElementById('psw').value;
  const cpsw = document.getElementById('cpsw').value;

  if (cpsw === "") {
    displayMsg('Confirm password is required!', 'cpswMsg', 'red');
    return false;
  } else if (psw !== cpsw) {
    displayMsg('Passwords do not match', 'cpswMsg', 'red');
    return false;
  } else {
    displayMsg('Passwords confirmed', 'cpswMsg', 'green');
    return true;
  }
};

// Toggle password visibility with eye icon
function hideShow(icon) {
    const psw = document.getElementById('psw');
    if (psw.type === "password") {
        psw.type = "text";
        icon.classList.remove("fa-eye");
        icon.classList.add("fa-eye-slash");
    } else {
        psw.type = "password";
        icon.classList.remove("fa-eye-slash");
        icon.classList.add("fa-eye");
    }
}

function hideShoww(icon) {
  const cpsw = document.getElementById('cpsw');
  if (cpsw.type === "password") {
    cpsw.type = "text";
    icon.classList.remove("fa-eye");
    icon.classList.add("fa-eye-slash");
  } else {
    cpsw.type = "password";
    icon.classList.remove("fa-eye-slash");
    icon.classList.add("fa-eye");
  }
}

// Form submission handler
async function formSubmit(event) {
  event.preventDefault(); // Prevent page reload

  // Validate all fields
  if (!(fnameValidation() && lnameValidation() && emailValidation() && pswValidation() && cpswValidation())) {
    displayMsg('Please fix errors before submitting.', 'submitMsg', 'red');
    return false;
  }

  // Gather form data
  const data = {
    fname: document.getElementById('fname').value.trim(),
    lname: document.getElementById('lname').value.trim(),
    email: document.getElementById('email').value.trim(),
    password: document.getElementById('psw').value,
  };

  try {
    const response = await fetch('http://127.0.0.1:5000/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    const result = await response.json();

    if (response.ok) {
      displayMsg(result.message || 'Registration successful!', 'submitMsg', 'green');
      // ✅ Redirect to login page after 2 seconds using Flask route
      setTimeout(() => { window.location.href = '/login'; }, 2000);
    } else {
      displayMsg(result.error || result.message || 'Registration failed.', 'submitMsg', 'red');
    }
  } catch (error) {
    console.error('Error:', error);
    displayMsg('Server error. Please try again later.', 'submitMsg', 'red');
  }

  return false;
}

// Add event listeners for real-time validation
document.getElementById('fname').addEventListener('input', fnameValidation);
document.getElementById('lname').addEventListener('input', lnameValidation);
document.getElementById('email').addEventListener('input', emailValidation);
document.getElementById('psw').addEventListener('input', pswValidation);
document.getElementById('cpsw').addEventListener('input', cpswValidation);
