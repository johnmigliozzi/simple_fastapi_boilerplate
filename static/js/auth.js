// Log In
async function logIn() {
    const username = document.getElementById('username-id').value;
    const password = document.getElementById('password-id').value;
    fetch('/token', {
        method: 'POST',
        headers: {
            'accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: `&username=${username}&password=${password}`
    }).then(json => {
        checkLoginStatus();
    });
}

// Log Out
async function logOut() {
    fetch('/logout', {
        method: 'POST'
    }).then(json => {
        uiSetLogout();
    });
}

async function checkLoginStatus() {
    getJsonApiResponse("/users/me")
        .then(json => {
            if (json) {
                uiSetLogin(json["full_name"])
            }
        });
}

async function uiSetLogin(name) {
    document.getElementById("logged-in-as-user").innerHTML = `Logged in as: ${name}.`;
    document.getElementById("login-form").style.display = "none";
    document.getElementById("logout-form").style.display = "block";
    uiClearLoginForm();
}

async function uiSetLogout() {
    document.getElementById("logged-in-as-user").innerHTML = `Not logged in.`;
    document.getElementById("login-form").style.display = "block";
    document.getElementById("logout-form").style.display = "none";
    uiClearLoginForm();
}

async function uiClearLoginForm() {
    document.getElementById("username-id").value = "";
    document.getElementById("password-id").value = "";
}

checkLoginStatus();