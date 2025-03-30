document.addEventListener("DOMContentLoaded", function () {
    const semesterSelect = document.getElementById("semester-select");
    const yearSelect = document.getElementById("year-select");

    function updateCourses() {
        const semester = semesterSelect.value;
        const year = yearSelect.value;
        const urlParams = new URLSearchParams(window.location.search);
        urlParams.set('semester', semester);
        urlParams.set('year', year);
        window.location.search = urlParams.toString();
    }

    semesterSelect.addEventListener("change", updateCourses);
    yearSelect.addEventListener("change", updateCourses);
});

function confirmDelete() {
    return confirm("Are you sure you want to delete this course? This action cannot be undone.");
}
