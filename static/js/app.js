async function getData() {

    var selectedDataId = document.getElementById("selected-data-id").value;
    const url = "/get_task/" + selectedDataId;

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