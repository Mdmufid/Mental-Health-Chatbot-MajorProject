// Toggle password visibility
function togglePassword(fieldId) {
    const field = document.getElementById(fieldId);
    field.type = field.type === "password" ? "text" : "password";
}

// Form validation
// document.getElementById("passwordForm").addEventListener("submit", function (event) {
//     event.preventDefault();
//     const currentPassword = document.getElementById("currentPassword").value.trim();
//     const newPassword = document.getElementById("newPassword").value.trim();
//     const confirmPassword = document.getElementById("confirmPassword").value.trim();
//     const confirmation = document.getElementById("confirmationMessage");

//     if (!currentPassword || !newPassword || !confirmPassword) {
//         alert("Please fill in all fields.");
//         return;
//     }

//     if (newPassword.length < 6) {
//         alert("New password must be at least 6 characters long.");
//         return;
//     }

//     if (newPassword !== confirmPassword) {
//         alert("New password and confirmation do not match.");
//         return;
//     }

//     // Simulate successful update
//     confirmation.style.display = "block";
// });