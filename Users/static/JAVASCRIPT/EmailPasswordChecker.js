// bhewa vigneshwar 2411725
document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector("form");
    const emailInput = form.querySelector("input[name='email']");
    const passwordInput = form.querySelector("input[name='password']");
    const confirmPasswordInput = form.querySelector("input[name='confirm_password']");
    const submitBtn = form.querySelector("button[type='submit']");
    form.addEventListener("submit", (e) => {
        let valid = true;
        let messages = [];
        //email validation based on regex
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(emailInput.value)) {
            valid = false;
            messages.push("Please enter a valid email.");
        }
        //validation of password
        if (passwordInput.value.length < 6) {
            valid = false;
            messages.push("Password must be at least 6 characters.");
        }
        if (passwordInput.value !== confirmPasswordInput.value) {
            valid = false;
            messages.push("Passwords do not match.");
        }
        if (!valid) {
            e.preventDefault(); 
            alert(messages.join("\n")); 
        }else {
            alert("Buyer registration has been carried out successfully");
        }
    });
});

