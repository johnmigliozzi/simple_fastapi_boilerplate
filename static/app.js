// Authenticate
async function token(username,password) {
    fetch('/token', {
        method: 'POST',
        headers: {
            'accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: `&username=${username}&password=${password}`
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