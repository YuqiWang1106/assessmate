function replaceWithAI(fromUserId, key, button) {
    const rewrittenText = document.getElementById(`rewritten-${fromUserId}-${key}`).innerText;
    const textarea = document.getElementById(`textarea-${fromUserId}-${key}`);
    if (textarea && rewrittenText) {
        textarea.value = rewrittenText;
        button.textContent = "✅ Replaced!";
        button.disabled = true;
        button.style.opacity = 0.6;
    }
}
