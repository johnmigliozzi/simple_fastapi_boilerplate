// Authenticate
async function token(username,password) {
    fetch('/token', {
        method: 'POST',
        headers: {
            'accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: `&username=${username}&password=${password}`
    }).then(json => {
        uiSetLoginStatus();
    });
}

// Log Out
async function logout() {
    fetch('/logout', {
        method: 'POST'
    }).then(json => {
        uiSetLoginStatus();
    });    
}

async function uiSetLoginStatus(){
    getJsonApiResponse("http://127.0.0.1:8000/users/me")
        .then(json => {
            try {
                document.getElementById("logged-in-as-user").innerHTML = `Logged in as: ${json["full_name"]}.`
                document.getElementById("login_form").style.display = "none";
                document.getElementById("logout_form").style.display = "block";
            } catch(TypeError) {
                document.getElementById("logged-in-as-user").innerHTML = `Not logged in.`
                document.getElementById("login_form").style.display = "block";
                document.getElementById("logout_form").style.display = "none";
            } finally {
                document.getElementById("username_id").value = "";
                document.getElementById("password_id").value = "";
            }
        });
}

// Accept any URL and return a JS object from a JSON API
async function getJsonApiResponse(url) {
    try {
        const response = await fetch(url);
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

    var selectedDataId = document.getElementById("selected_data_id").value;
    const url = "http://127.0.0.1:8000/get_task/" + selectedDataId;

    getJsonApiResponse(url)
        .then(data => {
            if (data) {
                var contentStringData = "ID:  " + data['id'] + "<br/>";
                contentStringData += "created timestamp:  " + data['created_timestamp'] + "<br/>";
                contentStringData += "override date:  " + data['override_date'] + "<br/>";
                contentStringData += "task name:  " + data['task_name'] + "<br/>";
                contentStringData += "project name:  " + data['project_name'] + "<br/>";

                document.getElementById("data_results").innerHTML = contentStringData;
            }
            else {
                document.getElementById("data_results").innerHTML = "ERROR";
            }
        })
}

uiSetLoginStatus();