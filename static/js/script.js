// Seleccionamos los formularios
const registerForm = document.getElementById("register-form");
const loginForm = document.getElementById("login-form");

// Evento para el formulario de registro
if (registerForm) {
    registerForm.addEventListener("submit", (event) => {
        event.preventDefault();

        // Obtener los datos del formulario de registro
        const username = document.getElementById("username").value;
        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;
        const confirmPassword = document.getElementById("confirm-password").value;

        // Verificar que las contraseñas coincidan
        if (password !== confirmPassword) {
            alert("Las contraseñas no coinciden");
            return;
        }

        // Guardar los datos en localStorage
        localStorage.setItem("username", username);
        localStorage.setItem("email", email);
        localStorage.setItem("password", password);

        alert("Registro exitoso. Ahora puedes iniciar sesión.");
        window.location.href = "/Login/Login.html"; // Redirige al login
    });
}

// Evento para el formulario de inicio de sesión
if (loginForm) {
    loginForm.addEventListener("submit", (event) => {
        event.preventDefault();

        // Obtener los datos del formulario de inicio de sesión
        const loginUsername = document.getElementById("login-username").value;
        const loginPassword = document.getElementById("login-password").value;

        // Recuperar los datos guardados en localStorage
        const storedUsername = localStorage.getItem("username");
        const storedPassword = localStorage.getItem("password");

        // Verificar las credenciales
        if (loginUsername === storedUsername && loginPassword === storedPassword) {
            alert("Inicio de sesión exitoso.");
            // Aquí podrías redirigir a otra página o realizar alguna acción adicional
        } else {
            alert("Nombre de usuario o contraseña incorrectos.");
        }
    });
}
