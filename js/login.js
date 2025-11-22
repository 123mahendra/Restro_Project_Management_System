// Password confirmation check for the registration form
document.getElementById('register-form')?.addEventListener('submit', function(event) {
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm-password').value;

    if (password !== confirmPassword) {
        alert('Passwords do not match!');
        event.preventDefault();  // Prevent form submission
    }
});