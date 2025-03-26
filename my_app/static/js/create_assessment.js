document.addEventListener("DOMContentLoaded", function() {
    let questionCount = 0;
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
                <label>Question ${newIndex}:</label>
                <input type="text" name="question_text_${newIndex}" value="${q.content}" style="width: 60%;" ${disabledAttr} />
                <input type="hidden" name="question_type_${newIndex}" value="${q.question_type}" />
            `;
    
            if (!isReadOnly) {
                html += `<button type="button" onclick="removeQuestion('question-${newIndex}')">Delete</button>`;
            }
    
            if (q.question_type === "likert") {
                html += `
                <div>
                    Likert Scale:
                    1 <input type="radio" disabled />
                    2 <input type="radio" disabled />
                    3 <input type="radio" disabled />
                    4 <input type="radio" disabled />
                    5 <input type="radio" disabled />
                </div>`;
            } else if (q.question_type === "open") {
                html += `
                <div>
                    <textarea disabled rows="3" cols="60" placeholder="Student will answer here..."></textarea>
                </div>`;
            }
    
            html += `</div>`;
            questionList.insertAdjacentHTML("beforeend", html);
        });
    
        questionCount = questions.length;
    }
    
    
      renderPreloadedQuestions();

    window.openModal = function() {
      document.getElementById("question-modal").style.display = "block";
    }
  
    window.closeModal = function() {
      document.getElementById("question-modal").style.display = "none";
    }
  
    window.confirmAddQuestion = function() {
      const type = document.getElementById("question-type").value;
  
      let html = `
        <div id="question-temp" class="question-block">
          <label>Question X:</label>
          <input type="text" placeholder="Enter your question text here" style="width: 60%;" />
          <input type="hidden" value="${type}" />
          <button type="button">Delete</button>
      `;
  
      if (type === "likert") {
        html += `
          <div style="margin-top: 10px;">
            <label>Likert Scale: </label>
            1 <input type="radio" disabled />
            2 <input type="radio" disabled />
            3 <input type="radio" disabled />
            4 <input type="radio" disabled />
            5 <input type="radio" disabled />
          </div>
        `;
      } else if (type === "open") {
        html += `
          <div style="margin-top: 10px;">
            <label>Open Response:</label>
            <textarea disabled rows="3" cols="60" placeholder="Student will answer here..."></textarea>
          </div>
        `;
      }
  
      html += `</div>`;
      questionList.insertAdjacentHTML("beforeend", html);
  
      closeModal();
      reIndexQuestions();
    }
  
    window.removeQuestion = function(id) {
      const block = document.getElementById(id);
      if (block) {
        block.remove();
      }
      reIndexQuestions();
    }
  
    function reIndexQuestions() {
      const blocks = document.querySelectorAll('#question-list .question-block');
      blocks.forEach((block, idx) => {
        const newIndex = idx + 1;
        block.id = `question-${newIndex}`;
  
        // label: "Question x:"
        const labelEl = block.querySelector('label');
        if (labelEl) {
          labelEl.innerText = `Question ${newIndex}:`;
        }
  
        // text input: name="question_text_x"
        const textInput = block.querySelector("input[type='text']");
        if (textInput) {
          textInput.name = `question_text_${newIndex}`;
        }
  
        // hidden input: name="question_type_x"
        const hiddenInput = block.querySelector("input[type='hidden']");
        if (hiddenInput) {
          hiddenInput.name = `question_type_${newIndex}`;
        }
  
        // Delete button's onclick
        const removeBtn = block.querySelector("button[type='button']");
        if (removeBtn) {
          removeBtn.setAttribute('onclick', `removeQuestion('question-${newIndex}')`);
        }
      });
  
      questionCount = blocks.length;
    }
  });
  
  window.saveAssessment = function(publish) {
    const form = document.getElementById("assessment-form");
    const input = document.createElement("input");
    input.type = "hidden";
    input.name = "publish";
    input.value = publish ? "true" : "false";
    form.appendChild(input);
    form.submit();
  }

    window.openQuitModal = function() {
    document.getElementById("quit-modal").style.display = "block";
  };

    window.confirmQuitAndSave = function() {
    document.getElementById("quit-modal").style.display = "none";
    saveAssessment(false);
  };
  

    window.quitWithoutSaving = function() {
        const teacherId = document.getElementById("teacher-id").value;
        window.location.href = `/assessment_dashboard/${teacherId}/`;
    };

    window.openDeleteModal = function () {
        document.getElementById("delete-modal").style.display = "block";
    };
    
    window.closeDeleteModal = function () {
        document.getElementById("delete-modal").style.display = "none";
    };
    
    window.confirmDelete = function () {
        const teacherId = document.getElementById("teacher-id").value;
        const assessmentId = document.getElementById("assessment-id").value;
        if (teacherId && assessmentId) {
            window.location.href = `/delete_assessment/${teacherId}/${assessmentId}/`;
        }
    };
    
  
    window.openPublishModal = function() {
        document.getElementById("publish-modal").style.display = "block";
    }
    
    window.closePublishModal = function() {
        document.getElementById("publish-modal").style.display = "none";
    }
    
    window.confirmPublish = function() {
        const dueDate = document.getElementById("due-date").value;
        if (!dueDate) {
        alert("Please select a due date.");
        return;
        }
    
        const form = document.getElementById("assessment-form");
        const dateInput = document.createElement("input");
        dateInput.type = "hidden";
        dateInput.name = "due_date";
        dateInput.value = dueDate;
        form.appendChild(dateInput);
    
        saveAssessment(true);
    }
    