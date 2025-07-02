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