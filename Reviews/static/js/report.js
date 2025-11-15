/* By humaa */
document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("reportForm");

    form.addEventListener("submit", function (event) {
        event.preventDefault();  // stop default submit

        alert("Your report has been submitted successfully!");

        form.submit();  // now submit to Django
    });
});
