document.addEventListener("DOMContentLoaded", function () {
    const questionList = document.getElementById("question-list");
  
    function renderPreloadedQuestions() {
      const preloadedDataTag = document.getElementById("preloaded-questions");
      if (!preloadedDataTag) return;
  
      const questions = JSON.parse(preloadedDataTag.textContent);
      const isReadOnly = READ_ONLY === "true";
      const disabledAttr = isReadOnly ? "disabled" : "";
  
      questions.forEach((q, index) => {
        const newIndex = index + 1;
        let html = `
          <div id="question-${newIndex}" class="question-block">
            <div class="question-header">
              <label>Question ${newIndex}</label>
            </div>
            <input 
              type="text" 
              name="question_text_${newIndex}" 
              value="${q.content}" 
              style="width: 60%;" 
              disabled
            />
            <input type="hidden" name="question_type_${newIndex}" value="${q.question_type}" />
        `;
  
        if (q.question_type === "likert") {
          html += `
            <div class="likert-track-container">
              <div class="likert-line">
                <div class="likert-progress" style="width: 0%;"></div>
              </div>
              <div class="likert-options">
                <label><input type="radio" name="likert_${newIndex}" value="1" ${disabledAttr}><span>Strongly Agree</span></label>
                <label><input type="radio" name="likert_${newIndex}" value="2" ${disabledAttr}><span>Agree</span></label>
                <label><input type="radio" name="likert_${newIndex}" value="3" ${disabledAttr}><span>Neutral</span></label>
                <label><input type="radio" name="likert_${newIndex}" value="4" ${disabledAttr}><span>Disagree</span></label>
                <label><input type="radio" name="likert_${newIndex}" value="5" ${disabledAttr}><span>Strongly Disagree</span></label>
              </div>
            </div>
          `;
        } else if (q.question_type === "open") {
          html += `
            <div style="margin-top: 10px;">
              <textarea 
                name="open_${newIndex}" 
                rows="3" 
                cols="60" 
                placeholder="Your answer here..." 
                ${disabledAttr}></textarea>
            </div>
          `;
        }
  
        html += `</div>`;
        questionList.insertAdjacentHTML("beforeend", html);
      });
    }
  
    renderPreloadedQuestions();

    const submitBtn = document.querySelector("button[type='button']");
    if (submitBtn) {
      submitBtn.addEventListener("click", function () {
        const assessmentId = document.getElementById("assessment-id").value;
        const studentId = document.getElementById("student-id").value;
        const courseId = document.getElementById("course-id").value;
        const targetUserId = document.getElementById("target-user-id").value;
  
        const answers = [];
  
        const blocks = document.querySelectorAll(".question-block");
        blocks.forEach((block, i) => {
          const index = i + 1;
          const type = block.querySelector(`input[name="question_type_${index}"]`).value;
  
          if (type === "likert") {
            const selected = block.querySelector(`input[name="likert_${index}"]:checked`);
            answers.push({
              question_type: "likert",
              answer: selected ? selected.value : null,
            });
          } else if (type === "open") {
            const textarea = block.querySelector(`textarea[name="open_${index}"]`);
            answers.push({
              question_type: "open",
              answer: textarea ? textarea.value.trim() : "",
            });
          }
        });
  
        fetch(`/submit_assessment/`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": document.querySelector("input[name='csrfmiddlewaretoken']").value,
          },
          body: JSON.stringify({
            student_id: studentId,
            target_user_id: targetUserId,
            assessment_id: assessmentId,
            answers: answers,
          }),
        })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            alert("Submitted successfully!");
            window.location.href = `/student_course_detail/${studentId}/${courseId}/`;
          } else {
            alert("Submission failed: " + data.message);
          }
        })
        .catch(err => {
          console.error("Error submitting:", err);
          alert("Error submitting assessment.");
        });
      });
    }
  
  
    // Likert 动画交互
    document.addEventListener("click", function (e) {
      if (e.target.name && e.target.name.startsWith("likert_")) {
        const container = e.target.closest(".likert-track-container");
        if (!container) return;
  
        const progress = container.querySelector(".likert-progress");
        const value = parseInt(e.target.value);
        if (!isNaN(value)) {
          const percentage = (value - 1) * 25;
          progress.style.width = `${percentage}%`;
        }
  
        const radios = container.querySelectorAll('input[type="radio"]');
        radios.forEach(radio => {
          const radioValue = parseInt(radio.value);
          if (!isNaN(radioValue)) {
            if (radioValue <= value) {
              radio.classList.add("filled");
            } else {
              radio.classList.remove("filled");
            }
          }
        });
      }
    });
  });
  