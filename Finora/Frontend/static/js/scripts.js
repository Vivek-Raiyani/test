const forms = document.querySelector(".forms"),
    pwShowHide = document.querySelectorAll(".eye-icon"),
    links = document.querySelectorAll(".link"),
    forgotLink = document.querySelector(".forgot-link"),
    backLogin = document.querySelector(".back-login");

// Password show/hide
pwShowHide.forEach(eyeIcon => {
    eyeIcon.addEventListener("click", () => {
        let pwFields = eyeIcon.parentElement.parentElement.querySelectorAll(".password");
        pwFields.forEach(password => {
            if (password.type === "password") {
                password.type = "text";
                eyeIcon.classList.replace("bx-hide", "bx-show");
            } else {
                password.type = "password";
                eyeIcon.classList.replace("bx-show", "bx-hide");
            }
        })
    })
})

// Switch login/signup
links.forEach(link => {
    link.addEventListener("click", e => {
        e.preventDefault();
        forms.classList.toggle("show-signup");
    })
})

// Forgot password toggle
forgotLink.addEventListener("click", e => {
    e.preventDefault();
    forms.classList.add("show-forgot");
})

backLogin.addEventListener("click", e => {
    e.preventDefault();
    forms.classList.remove("show-forgot");
})
