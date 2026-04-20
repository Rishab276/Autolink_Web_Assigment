// bhewa vigneshwar 2411725
$(document).ready(function () {

    $("form").on("submit", function (event) {
        event.preventDefault();

        const userType = $("input[name='user_type']").val();
        const email = $("input[name='email']").val().trim();
        const password = $("input[name='password']").val().trim();
        const confirmPassword = $("input[name='confirm_password']").val().trim();
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if (!emailRegex.test(email)) {
            alert("Please enter a valid email address.");
            return;
        }

        if (password.length < 6) {
            alert("Password must be at least 6 characters long.");
            return;
        }

        if (password !== confirmPassword) {
            alert("Passwords do not match.");
            return;
        }

        // Collect all form data
        const formData = {
            user_type: userType,
            first_name: $("input[name='first_name']").val().trim(),
            last_name: $("input[name='last_name']").val().trim(),
            email: email,
            password: password,
            confirm_password: confirmPassword,
            address: $("input[name='address']").val().trim(),
            contact_number: $("input[name='contact_number']").val().trim(),
            driverliscence: $("input[name='driverliscence']").val().trim(),
            csrfmiddlewaretoken: $("input[name='csrfmiddlewaretoken']").val()
        };

        $.ajax({
            url: $("form").attr("action"),
            type: "POST",
            data: formData,
            success: function (response) {
                if (userType === "seller") {
                    alert("Seller registration has been carried out successfully");
                } else if (userType === "renter") {
                    alert("Renter registration has been carried out successfully");
                } else {
                    alert("Registration successful!");
                }
                // Redirect to login page after success
                window.location.href = response.redirect_url || "/users/login/";
            },
            error: function (xhr) {
                const errorMsg = xhr.responseJSON?.error || "Registration failed. Please try again.";
                alert(errorMsg);
            }
        });
    });

});