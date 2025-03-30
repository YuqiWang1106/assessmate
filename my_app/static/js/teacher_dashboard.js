function changeCourse(courseId) {

    window.location.href = window.location.pathname + "?selected_course=" + courseId;
}

function getCSRFToken() {
    const name = 'csrftoken';
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith(name + '=')) {
            return decodeURIComponent(cookie.substring(name.length + 1));
        }
    }
    return '';
}

document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('invite-modal');
    const openBtn = document.querySelector('.invite-btn');
    const closeBtn = document.querySelector('.close-btn');
    const form = document.getElementById('invite-form');

    // Open modal
    openBtn.addEventListener('click', () => {
        modal.style.display = 'block';
    });

    // Close modal
    closeBtn.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });

    // Send invitation via AJAX
    form.addEventListener("submit", function (e) {
        e.preventDefault();

        const email = document.getElementById("student-email").value;
        const courseId = document.querySelector(".course-item.active").getAttribute("data-course-id");

        fetch("/invite-student/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),
            },
            body: JSON.stringify({ email: email, course_id: courseId }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(data.message);
                modal.style.display = "none";
                form.reset();
            } else {
                alert("Error: " + data.message);
            }
        })
        .catch(error => {
            console.error("Error:", error);
            alert("Something went wrong.");
        });
    });
});



document.querySelectorAll('.my-courses-box ul li').forEach(item => {
    item.addEventListener('click', function(e) {
        const ripple = document.createElement('span');
        ripple.classList.add('ripple');
        this.appendChild(ripple);
        
        const x = e.clientX - this.getBoundingClientRect().left;
        const y = e.clientY - this.getBoundingClientRect().top;
        
        ripple.style.left = `${x}px`;
        ripple.style.top = `${y}px`;
        
        setTimeout(() => {
            ripple.remove();
        }, 600);
    });
});