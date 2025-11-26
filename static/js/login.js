 const loginForm = document.getElementById("login-form");
    const signupForm = document.getElementById("signup-form");
    const formTitle = document.getElementById("form-title");
    const showSignup = document.getElementById("show-signup");
    const showLogin = document.getElementById("show-login");

    showSignup.addEventListener("click", (e) => {
      e.preventDefault();
      loginForm.classList.remove("active");
      signupForm.classList.add("active");
      formTitle.textContent = "Sign Up";
    });

    showLogin.addEventListener("click", (e) => {
      e.preventDefault();
      signupForm.classList.remove("active");
      loginForm.classList.add("active");
      formTitle.textContent = "Login";
    })

setTimeout(() => {
    const popups = document.querySelectorAll('.popup');
    popups.forEach(p => p.remove());
}, 3000);
