const displayMsg = (msg, id, colorName) => {
    const el = document.getElementById(id);
    el.innerText = msg;
    el.style.color = colorName;
};

// Just check if email is not empty
const emailValidation = () => {
    const email = document.getElementById('email').value.trim();
    if (email === "") {
        displayMsg('Email is mandatory', 'emailMsg', 'red');
        return false;
    } else {
        displayMsg('', 'emailMsg', 'green');
        return true;
    }
};

// Just check if password is not empty
const pswValidation = () => {
    const psw = document.getElementById("psw").value.trim();
    if (psw === "") {
        displayMsg("Password is mandatory", "pswMsg", "red");
        return false;
    } else {
        displayMsg('', "pswMsg", "green");
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

// Helper to get CSRF token from cookie (Django default)
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Handle login form submit
document.querySelector("form").addEventListener("submit", async function (e) {
    e.preventDefault();

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("psw").value.trim();

    if (!emailValidation() || !pswValidation()) {
        return;
    }

    const csrftoken = getCookie('csrftoken');

    try {
        const response = await fetch("/login_user/", {  // NOTE: changed URL to match your urls.py path name
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken
            },
            body: JSON.stringify({ email, password })
        });

        const result = await response.json();

        if (response.ok) {
            displayMsg("Login successful! Redirecting...", "submitMsg", "green");
            setTimeout(() => {
                window.location.href = result.redirect || "/userpage/";  // Redirect URL from backend or fallback
            }, 1000);
        } else {
            displayMsg(result.error || "Login failed", "submitMsg", "red");
        }
    } catch (err) {
        console.error("Error during login:", err);
        displayMsg("Something went wrong", "submitMsg", "red");
    }
});
