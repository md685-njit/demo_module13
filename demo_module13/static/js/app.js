const registerForm = document.getElementById("registerForm");

if (registerForm) {
  registerForm.addEventListener("submit", async function (event) {
    event.preventDefault(); // Stops browser refresh so JS can send JSON.

    const formData = {
      username: registerForm.username.value,
      email: registerForm.email.value,
      password: registerForm.password.value,
    };

    const response = await fetch("/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formData), // Sends form data as JSON to FastAPI.
    });

    const data = await response.json();
    registerMessage.textContent = response.ok ? data.message : data.detail;
  });
}


const loginForm = document.getElementById("loginForm");

if (loginForm) {
  loginForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const formData = {
      username: loginForm.username.value,
      password: loginForm.password.value,
    };

    const response = await fetch("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formData),
    });

    const data = await response.json();

    if (response.ok) {
      localStorage.setItem("access_token", data.access_token); // Saves token for later requests.
      window.location.href = "/dashboard"; // Moves user to calculator page.
    } else {
      loginMessage.textContent = data.detail;
    }
  });
}


const calculationForm = document.getElementById("calculationForm");

if (calculationForm) {
  calculationForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const token = localStorage.getItem("access_token"); // Gets saved login token.

    const inputs = calculationForm.numbers.value
      .split(",")
      .map((number) => Number(number.trim())); // Converts "10, 5, 2" into [10, 5, 2].

    const response = await fetch("/calculations", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`, // Proves user is logged in.
      },
      body: JSON.stringify({
        type: calculationForm.type.value,
        inputs: inputs,
      }),
    });

    const data = await response.json();
    calculationResult.textContent = response.ok ? `Result: ${data.result}` : data.detail;
  });
}
