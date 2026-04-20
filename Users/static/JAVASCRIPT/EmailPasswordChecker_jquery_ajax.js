// bhewa vigneshwar 2411725
$(document).ready(function () {

    $("form").on("submit", function (event) {
        event.preventDefault();

        const email = $("input[name='email']").val().trim();
        const password = $("input[name='password']").val().trim();
        const confirmPassword = $("input[name='confirm_password']").val().trim();

        let valid = true;
        let validationMessages = [];

        // Email validation based on regex
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            valid = false;
            validationMessages.push("Please enter a valid email.");
        }

        // Validation of password
        if (password.length < 6) {
            valid = false;
            validationMessages.push("Password has to be at least 6 characters.");
        }

        if (password !== confirmPassword) {
            valid = false;
            validationMessages.push("Passwords do not match.");
        }

        if (!valid) {
            alert(validationMessages.join("\n"));
            return;
        }

        // Collect all form data
        const formData = {
            first_name: $("input[name='first_name']").val().trim(),
            last_name: $("input[name='last_name']").val().trim(),
            email: email,
            password: password,
            confirm_password: confirmPassword,
            address: $("input[name='address']").val().trim(),
            contact_number: $("input[name='contact_number']").val().trim(),
            csrfmiddlewaretoken: $("input[name='csrfmiddlewaretoken']").val()
        };

        $.ajax({
            url: $("form").attr("action"),
            type: "POST",
            data: formData,
            success: function (response) {
                alert("Buyer registration has been carried out successfully");
                window.location.href = response.redirect_url || "/users/login/";
            },
            error: function (xhr) {
                const errorMsg = xhr.responseJSON?.error || "Registration failed. Please try again.";
                alert(errorMsg);
            }
        });
    });

});