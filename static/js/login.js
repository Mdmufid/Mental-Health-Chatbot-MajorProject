// Show/Hide Password
function togglePassword() {
    const passwordField = document.getElementById("password");
    passwordField.type = passwordField.type === "password" ? "text" : "password";
}

// Show toast if redirected after account deletion
const params = new URLSearchParams(window.location.search);
if (params.get("deleted") === "true") {
    const toast = document.getElementById("accountDeletedToast");
    if (toast) {
        // Slight delay so page renders first
        setTimeout(() => toast.classList.add("show"), 300);

        // Auto-dismiss after 4 seconds
        setTimeout(() => toast.classList.remove("show"), 4300);

        // Clean up the URL so refreshing doesn't re-show the toast
        const cleanUrl = window.location.pathname;
        window.history.replaceState({}, document.title, cleanUrl);
    }
}