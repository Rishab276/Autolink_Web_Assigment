document.querySelector("form").addEventListener("submit", function(event) {
   const userType = document.querySelector("input[name='user_type']").value;

    if (userType === "seller") {
        alert("Seller information registered successfully!");
    } else if (userType === "renter") {
        alert("Renter information registered successfully!");
    } else {
        alert("Registration successful!");
    }
    
});
