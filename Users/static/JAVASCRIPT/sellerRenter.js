document.querySelector("form").addEventListener("submit", function(event) {
   const userType = document.querySelector("input[name='user_type']").value;

    if (userType === "seller") {
        alert("Seller registration has been carried out successfully");
    } else if (userType === "renter") {
        alert("Renter registration has been carried out successfully");
    } else {
        alert("Registration successful!");
    } 
});
