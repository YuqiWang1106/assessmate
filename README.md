# A-Team


## **Database Schema**

### **1. User Table**

| Field        | Data Type           | PK?  | Not Null? | Description                                                                                  |
|--------------|---------------------|------|-----------|----------------------------------------------------------------------------------------------|
| **id**       | UUID / INT         | PK   | YES        | Primary key (user ID). You can use an auto-increment integer or a UUID field.               |
| **email**    | VARCHAR (unique)   |      | YES        | The user’s email (used for Google OAuth login). Must be unique.                             |
| **name**     | VARCHAR            |      | YES        | The user’s display name.                                                                    |
| **role**     | ENUM / VARCHAR     |      | YES        | User role, e.g. `student` or `teacher`.                                                     |
| **created_at** | TIMESTAMP        |      | YES (default) | Timestamp of when the user was created (default: current time).                           |

---

### **2. Course Table**

| Field           | Data Type   | PK?  | Not Null? | Description                                    |
|-----------------|------------|------|-----------|------------------------------------------------|
| **id**          | UUID / INT | PK   | YES        | Primary key (course ID).                       |
| **course_number** | VARCHAR   |      | YES        | A short course identifier (e.g., "CS101").     |
| **course_name** | VARCHAR    |      | YES        | The course name/title.                         |
| **teacher_id**  | UUID / INT | FK → User.id   | YES        | Foreign key referencing **User** (the teacher).|
| **created_at**  | TIMESTAMP  |      | YES (default) | Timestamp when the course was created.     |

> _If needed, add fields like `semester` or `year` to store additional course info._

---

### **3. Team Table**

| Field         | Data Type   | PK?  | Not Null? | Description                                 |
|---------------|------------|------|-----------|---------------------------------------------|
| **id**        | UUID / INT | PK   | YES        | Primary key (team ID).                      |
| **course_id** | UUID / INT | FK → Course.id  | YES        | Foreign key referencing **Course**.         |
| **team_name** | VARCHAR    |      | YES        | Name of the team.                           |
| **created_at**| TIMESTAMP  |      | YES (default) | Timestamp when the team was created.    |

---

### **4. TeamMember Table**  
_This is a junction table to represent which students belong to which team._

| Field        | Data Type   | PK?  | Not Null? | Description                                     |
|--------------|------------|------|-----------|-------------------------------------------------|
| **id**       | UUID / INT | PK   | YES        | Primary key (team-member ID).                   |
| **team_id**  | UUID / INT | FK → Team.id  | YES        | Foreign key referencing **Team**.               |
| **user_id**  | UUID / INT | FK → User.id  | YES        | Foreign key referencing **User** (the student). |
| **joined_at**| TIMESTAMP  |      | YES (default) | Timestamp when the student joined the team. |

> _Consider adding a **unique constraint** on `(team_id, user_id)` to ensure a user is not added twice to the same team._

---

### **5. Assessment Table**

| Field             | Data Type   | PK?  | Not Null? | Description                                                                      |
|-------------------|------------|------|-----------|----------------------------------------------------------------------------------|
| **id**            | UUID / INT | PK   | YES        | Primary key (assessment ID).                                                     |
| **course_id**     | UUID / INT | FK → Course.id  | YES        | Foreign key referencing **Course**.                                              |
| **title**         | VARCHAR    |      | YES        | Title or name of the assessment.                                                 |
| **status**        | ENUM / VARCHAR |  | YES        | Status of the assessment: e.g., `draft`, `published`, `finished`.                |
| **publish_date**  | DATETIME   |      | NO         | Date/time when the assessment becomes available.                                 |
| **due_date**      | DATETIME   |      | NO         | Date/time when the assessment closes.                                            |
| **results_released** | BOOLEAN |      | YES (default: false) | Indicates whether the assessment results have been published to students. |
| **created_at**    | TIMESTAMP  |      | YES (default) | Timestamp when the assessment was created.                                 |

> _Use `results_released` to control if students can see their results._

---

### **6. AssessmentQuestion Table**

| Field            | Data Type        | PK?  | Not Null? | Description                                                                               |
|------------------|------------------|------|-----------|-------------------------------------------------------------------------------------------|
| **id**           | UUID / INT       | PK   | YES        | Primary key (question ID).                                                                |
| **assessment_id**| UUID / INT       | FK → Assessment.id  | YES        | Foreign key referencing **Assessment**.                                                   |
| **question_type**| ENUM / VARCHAR   |      | YES        | Type of question, e.g., `likert` or `open`.                                              |
| **content**      | TEXT             |      | YES        | The actual question prompt.                                                               |
| **order** (opt.) | INT              |      | NO         | Optional field to specify display order within the assessment.                            |

> _For Likert questions, you might store the scale details in code (e.g., 1-5). For open questions, `content` is just the prompt text._

---

### **7. AssessmentResponse Table**

| Field              | Data Type   | PK?  | Not Null? | Description                                                                                            |
|--------------------|------------|------|-----------|--------------------------------------------------------------------------------------------------------|
| **id**             | UUID / INT | PK   | YES        | Primary key (response ID).                                                                             |
| **assessment_id**  | UUID / INT | FK → Assessment.id  | YES        | Foreign key referencing **Assessment**.                                                                |
| **from_user_id**   | UUID / INT | FK → User.id  | YES        | The user who is giving the feedback (student).                                                         |
| **to_user_id**     | UUID / INT | FK → User.id  | YES        | The user who is being evaluated (student). If self-assessment is allowed, this can be the same as from_user_id. |
| **answers**        | JSON / TEXT|      | YES        | Stores all question responses in a JSON object (e.g., `{"Q1":4,"Q2":"Open-ended text..."}`).           |
| **last_saved**     | DATETIME   |      | YES        | When the response was last saved.                                                                      |
| **submitted** (opt.) | BOOLEAN  |      | NO         | Indicates if the response was fully submitted (versus a draft).                                        |

> _If you need to moderate or modify open-ended answers, you can add a separate field (e.g., `edited_answer`) or store them in a child table. If you want more granular storage (one row per question), consider an additional table **AssessmentResponseDetail**._

---
