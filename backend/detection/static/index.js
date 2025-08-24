  // Show first name from localStorage
  const userFirstName = localStorage.getItem("firstName");
  if (userFirstName) {
    document.getElementById("userFirstName").textContent = userFirstName;
  }


    function logout() {
    localStorage.removeItem("firstName");
    window.location.href = "Login.html";
  }