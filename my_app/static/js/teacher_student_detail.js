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


function filterFeedback() {
    const selected = document.getElementById("teammate-select").value;
    const blocks = document.querySelectorAll(".feedback-block");

    blocks.forEach(block => {
        if (selected === "all") {
            block.style.display = "block";
        } else {
            block.style.display = block.id === selected ? "block" : "none";
        }
    });
}