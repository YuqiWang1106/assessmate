function changeCourse(courseId) {
    // 构造新的 URL 并跳转，让 Django 重新渲染模板
    window.location.href = window.location.pathname + "?selected_course=" + courseId;
}
