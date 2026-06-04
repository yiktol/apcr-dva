function sendData() {

    var saleid = Math.random().toString(36).substring(2, 16);
    // (A) GET FORM DATA
    var timestamp = Date.now();
    var data = new FormData(document.getElementById("demo"));
    data.append("customer", document.getElementById("name").value);
    data.append("coffee", document.getElementById("coffee").value);
    data.append("milk", document.getElementById("milk").value);
    data.append("size", document.getElementById("size").value);
    data.append("qty", document.getElementById("qty").value);
    data.append("timestamp", timestamp);
    data.append("saleid", saleid);
    //document.write(data);
    // (B) INIT FETCH POST
    var url = 'https://serverless.aws.yikyakyuk.com/cashier';

    fetch(url, {
        method: "POST",
        redirect: 'follow',
        headers: new Headers({ 'content-type': 'application/json' }),
        mode: 'no-cors',
        body: JSON.stringify(Object.fromEntries(data))
    })
        // (C) RETURN SERVER RESPONSE AS TEXT
        .then(res => {
            if (res.status != 200) { throw new Error("Bad Server Response"); };
            if (res.status == 200) { window.location.href = '/orderhere.html' };
            return res.text();
        })

        // (D) SERVER RESPONSE
        .then(res => {
            window.location.href = '/orderhere.html';
            console.log(res)
        })

        // (E) HANDLE ERRORS - OPTIONAL
        .catch(err => console.error(err));

    // (F) PREVENT FORM SUBMIT
    return false;
}