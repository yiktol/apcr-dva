let i = 0;      // Its a just a counter.

let getData = () => {
    const oXHR = new XMLHttpRequest();

    // Initiate request.
    oXHR.onreadystatechange = reportStatus;
    oXHR.open("GET", "/status", true);
    oXHR.setRequestHeader("Content-Type", "application/json");
    oXHR.send();

    function reportStatus() {
        // Check if request is complete.
        if (oXHR.readyState === XMLHttpRequest.DONE &&
            oXHR.status === 200) {

            let status = JSON.parse(this.responseText);

            // Refresh DIV with new content.
            document.getElementById('refresh').innerHTML =
                '<table>' +
                '<tr><td>Barista (Lambda): </td><td>' + status.ApproximateNumberOfMessagesNotVisible + '</td></tr>' +
                '<tr><td>Cashier-Barista Queue (SQS): </td><td>' + status.ApproximateNumberOfMessagesDelayed + '</td></tr>' +
                '<tr><td>Waiter (Lambda): </td><td>' + status.ApproximateNumberOfMessagesNotVisible + '</td></tr>' +
                '<tr><td>Sales (DynamoDB): </td><td>' + status.dynamoItems + '</td></tr>' +
                '</table>'

            i = i + 1;
            if (i == 5)
                i = 0;
        }
    }
}

getData();

var counter = 5;

// The countdown method.
window.setInterval(function () {
    counter--;
    if (counter >= 0) {
        var span;
        span = document.getElementById("cnt");
        span.innerHTML = counter;
    }
    if (counter === 0) {
        counter = 5;
    }

}, 1000);

let reload = window.setInterval('getData()', 1000);