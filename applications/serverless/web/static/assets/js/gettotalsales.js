
let getSales = () => {
    const oXHR = new XMLHttpRequest();
    // Initiate request.
    oXHR.onreadystatechange = reportSales;
    oXHR.open("GET", "/sales", true);
    oXHR.setRequestHeader("Content-Type", "application/json");
    oXHR.send();

    function reportSales() {
        // Check if request is complete.
        if (oXHR.readyState === XMLHttpRequest.DONE &&
            oXHR.status === 200) {

            let status = JSON.parse(this.responseText);
            //document.getElementById('sales').innerHTML = '<p>' + status[0].salesid + '</p>';
            var table = document.createElement('table'), tr, td, th, row;
            tr = document.createElement('tr');
            th = document.createElement('th'); th.innerHTML = 'ID'; tr.appendChild(th);
            th2 = document.createElement('th'); th2.innerHTML = 'NAME'; tr.appendChild(th2);
            th3 = document.createElement('th'); th3.innerHTML = 'COFFEE'; tr.appendChild(th3);
            th4 = document.createElement('th'); th4.innerHTML = 'MILK'; tr.appendChild(th4);
            th5 = document.createElement('th'); th5.innerHTML = 'SIZE'; tr.appendChild(th5);
            th6 = document.createElement('th'); th6.innerHTML = 'QTY'; tr.appendChild(th6);
            table.appendChild(tr);
            for (row = 0; row < Object.keys(status).length; row++) {
                tr = document.createElement('tr');
                td = document.createElement('td'); td.innerHTML = status[row].salesid; tr.appendChild(td);
                td2 = document.createElement('td'); td2.innerHTML = status[row].name; tr.appendChild(td2);
                td3 = document.createElement('td'); td3.innerHTML = status[row].coffee; tr.appendChild(td3);
                td4 = document.createElement('td'); td4.innerHTML = status[row].milk; tr.appendChild(td4);
                td5 = document.createElement('td'); td5.innerHTML = status[row].size; tr.appendChild(td5);
                td6 = document.createElement('td'); td6.innerHTML = status[row].qty; tr.appendChild(td6);
                table.appendChild(tr);
            }
            document.getElementById('sales').appendChild(table);

        }
    }
}

getSales();



