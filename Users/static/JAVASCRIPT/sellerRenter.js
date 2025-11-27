// bhewa vigneshwar 2411725
document.querySelector("form").addEventListener("submit", function(event) {
    event.preventDefault(); //this will prevent the form from submitting immediately

    const userType = document.querySelector("input[name='user_type']").value;
    const email = document.querySelector("input[name='email']").value.trim();
    const password = document.querySelector("input[name='password']").value.trim();
    const confirmPassword = document.querySelector("input[name='confirm_password']").value.trim();
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        alert("Please enter a valid email address.");
        return;
    }
    //the password validation is as follows:
    if (password.length < 6) {
        alert("Password must be at least 6 characters long.");
        return; // stop submission
    }
    if (password !== confirmPassword) {
        alert("Passwords do not match.");
        return; // stop submission
    }
    //user validation part of the seller or renter form
    if (userType === "seller") {
        alert("Seller registration has been carried out successfully");
        e.preventDefault();
    } else if (userType === "renter") {
        alert("Renter registration has been carried out successfully");
        e.preventDefault();
    } else {
        alert("Registration successful!");
        e.preventDefault();
    }
    this.submit();
});
