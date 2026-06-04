function validateForm() {
    var x = document.forms["demo"]["NAME"].value;
    if (x == "" || x == null) {
        alert("Name must be filled out");
        return false;
    }
}