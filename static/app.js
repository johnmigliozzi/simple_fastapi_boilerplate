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
    getJsonApiResponse("http://127.0.0.1:8000/users/me")
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

// Accept any URL and return a JS object from a JSON API
async function getJsonApiResponse(url) {
    try {
        const response = await fetch(url);
        if (response.status === 401) {
            uiSetLogout();
        }
        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
        }
        return await response.json();
    }
    catch (error) {
        console.error(error.message);
        return null;
    }
}

async function doStuff() {
    getJsonApiResponse("http://127.0.0.1:8000/api/do_stuff/")
}

async function getData() {

    var selectedDataId = document.getElementById("selected-data-id").value;
    const url = "http://127.0.0.1:8000/get_task/" + selectedDataId;

    getJsonApiResponse(url)
        .then(data => {
            if (data) {
                var contentStringData = "ID:  " + data['id'] + "<br/>";
                contentStringData += "created timestamp:  " + data['created_timestamp'] + "<br/>";
                contentStringData += "override date:  " + data['override_date'] + "<br/>";
                contentStringData += "task name:  " + data['task_name'] + "<br/>";
                contentStringData += "project name:  " + data['project_name'] + "<br/>";

                document.getElementById("data-results").innerHTML = contentStringData;
            }
            else {
                document.getElementById("data-results").innerHTML = "ERROR";
            }
        })
}

checkLoginStatus();