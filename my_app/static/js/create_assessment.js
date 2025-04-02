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
              <div class="question-header">
                <label>Question ${newIndex}</label>
                ${!isReadOnly ? `
                  <button class="ca-delete-button" type="button" onclick="removeQuestion('question-${newIndex}')">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-trash3" viewBox="0 0 16 16">
                      <path d="M6.5 1h3a.5.5 0 0 1 .5.5v1H6v-1a.5.5 0 0 1 .5-.5M11 2.5v-1A1.5 1.5 0 0 0 9.5 0h-3A1.5 1.5 0 0 0 5 1.5v1H1.5a.5.5 0 0 0 0 1h.538l.853 10.66A2 2 0 0 0 4.885 16h6.23a2 2 0 0 0 1.994-1.84l.853-10.66h.538a.5.5 0 0 0 0-1zm1.958 1-.846 10.58a1 1 0 0 1-.997.92h-6.23a1 1 0 0 1-.997-.92L3.042 3.5zm-7.487 1a.5.5 0 0 1 .528.47l.5 8.5a.5.5 0 0 1-.998.06L5 5.03a.5.5 0 0 1 .47-.53Zm5.058 0a.5.5 0 0 1 .47.53l-.5 8.5a.5.5 0 1 1-.998-.06l.5-8.5a.5.5 0 0 1 .528-.47M8 4.5a.5.5 0 0 1 .5.5v8.5a.5.5 0 0 1-1 0V5a.5.5 0 0 1 .5-.5"/>
                    </svg>
                  </button>
                ` : ''}
              </div>
              <input type="text" placeholder="Enter your question text here" name="question_text_${newIndex}" value="${q.content}" style="width: 60%;" ${disabledAttr} />
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
          }
            
            else if (q.question_type === "open") {
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



    window.openModal = function () {
        const modal = document.getElementById("question-modal");
        modal.classList.remove("fade-out"); 
        modal.style.display = "block";
        modal.classList.add("fade-in");
      };
      

    window.closeModal = function () {
        const modal = document.getElementById("question-modal");
        modal.classList.remove("fade-in");
        modal.classList.add("fade-out");
      
        modal.addEventListener("animationend", function handler() {
          modal.classList.remove("fade-out");
          modal.style.display = "none";
          modal.removeEventListener("animationend", handler);
        });
      };
      
      
  
    window.confirmAddQuestion = function() {
      const type = document.getElementById("question-type").value;
      let html = `
        <div id="question-temp" class="question-block">
            <div class="question-header">
            <label>Question X</label>
            <button type="button" class="ca-delete-button">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-trash3" viewBox="0 0 16 16">
                <path d="M6.5 1h3a.5.5 0 0 1 .5.5v1H6v-1a.5.5 0 0 1 .5-.5M11 2.5v-1A1.5 1.5 0 0 0 9.5 0h-3A1.5 1.5 0 0 0 5 1.5v1H1.5a.5.5 0 0 0 0 1h.538l.853 10.66A2 2 0 0 0 4.885 16h6.23a2 2 0 0 0 1.994-1.84l.853-10.66h.538a.5.5 0 0 0 0-1zm1.958 1-.846 10.58a1 1 0 0 1-.997.92h-6.23a1 1 0 0 1-.997-.92L3.042 3.5zm-7.487 1a.5.5 0 0 1 .528.47l.5 8.5a.5.5 0 0 1-.998.06L5 5.03a.5.5 0 0 1 .47-.53Zm5.058 0a.5.5 0 0 1 .47.53l-.5 8.5a.5.5 0 1 1-.998-.06l.5-8.5a.5.5 0 0 1 .528-.47M8 4.5a.5.5 0 0 1 .5.5v8.5a.5.5 0 0 1-1 0V5a.5.5 0 0 1 .5-.5"/>
                </svg>
            </button>
            </div>
            <input type="text" placeholder="Enter your question text here" style="width: 60%;" />
            <input type="hidden" value="${type}" />
        `;

  
      if (type === "likert") {
        html += `
          <div class="likert-track-container">
            <div class="likert-line">
              <div class="likert-progress"></div>
            </div>
            <div class="likert-options">
              <label><input type="radio" name="likert_temp" value="1"><span>Strongly Agree</span></label>
              <label><input type="radio" name="likert_temp" value="2"><span>Agree</span></label>
              <label><input type="radio" name="likert_temp" value="3"><span>Neutral</span></label>
              <label><input type="radio" name="likert_temp" value="4"><span>Disagree</span></label>
              <label><input type="radio" name="likert_temp" value="5"><span>Strongly Disagree</span></label>
            </div>
          </div>
        `;
      }
      
      else if (type === "open") {
        html += `
          <div style="margin-top: 10px;">
            <textarea disabled rows="3" cols="60" placeholder="Student will answer here..."></textarea>
          </div>
        `;
      }
  
      html += `</div>`;
      questionList.insertAdjacentHTML("beforeend", html);


        const newBlock = document.getElementById("question-temp");
        if (newBlock) {
        newBlock.classList.add("animate-slide-in");
        newBlock.id = `question-${questionCount + 1}`; 
        }

  
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
  

    window.quitWithoutSaving = function () {
        const teacherId = document.getElementById("teacher-id").value;
        const courseIdInput = document.getElementById("course-id");
        const courseId = courseIdInput ? courseIdInput.value : null;
    
        if (courseId) {
            window.location.href = `/assessment_dashboard/${teacherId}/?course_id=${courseId}`;
        } else {
            window.location.href = `/assessment_dashboard/${teacherId}/`;
        }
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
        const courseId = document.getElementById("course-id").value;
        if (teacherId && assessmentId && courseId) {
            window.location.href = `/delete_assessment/${teacherId}/${assessmentId}/?course_id=${courseId}`;
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
    
    // document.addEventListener("click", function (e) {
    //   if (e.target.name && e.target.name.startsWith("likert_")) {
    //     const container = e.target.closest(".likert-track-container");
    //     if (!container) return;
    
    //     const progress = container.querySelector(".likert-progress");
    //     const value = parseInt(e.target.value);
    //     if (!isNaN(value)) {
    //       const percentage = (value - 1) * 25;
    //       progress.style.width = `${percentage}%`;
    //     }
    //   }
    // });
    

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
    