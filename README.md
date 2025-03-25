# A-Team




## **Basic Configurations**
1. `cd A-TEAM`
2. `python3 -m venv venv`
3. `source venv/bin/activate`
4. `pip install requests google-auth google-auth-oauthlib google-auth-httplib2`
5. `pip install django-widget-tweaks`






## **API Endpoints**

### **1. Authentication**

| **Endpoint**         | **Method** | **Request Body**  | **Description**                                                                                     | **Response**                                    |
|----------------------|------------|--------------------------------|-------------------------------------------------------------------------------------------------------|-------------------------------------------------|
| `/api/login/`        | `POST`     | - Possibly OAuth callback data | **Google OAuth** login. After a successful login, the server should create or verify a user record.   | Returns user info (e.g., `{id, name, role}`)    |
| `/api/logout/`       | `POST`     | *None*                         | Logs out the user. Frontend should also clear any session/cookie.                                    | 200 OK or 204 No Content                       |
| `/api/current-user/` | `GET`      | *None*                         | Retrieves the currently logged-in user's data (e.g., from session).                                  | `{id, email, name, role, ...}`                 |

---

### **2. User / Profile**


| **Endpoint**            | **Method** | **Request Body**  | **Description**                                                 | **Response**                          |
|-------------------------|------------|----------------------------------------------|-----------------------------------------------------------------|---------------------------------------|
| `/api/users/`           | `GET`      | *None*                                       | **(Admin/Teacher only)**: Retrieve all users (for admin, etc.). | List of users: `[{id, name, role}, ...]` |
| `/api/users/{user_id}`  | `GET`      | *None*                                       | Fetch a specific user.                                          | `{id, name, email, role, ...}`       |
| `/api/users/{user_id}`  | `PUT`      | e.g. `{"name": "...", "role": "teacher"}`    | Update a user’s info (optional).                                | Updated user data                     |

---

### **3. Course Management (Teacher)**

#### 3.1 **Courses**

| **Endpoint**                   | **Method** | **Request Body**   | **Description**                                                                                     | **Response**                                                                       |
|--------------------------------|------------|------------------------------------------------------|------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------|
| `/api/teacher/courses/`        | `GET`      | *None*                                               | **Teacher**: Get list of courses created by this teacher.                                      | `[{ "id": 1, "course_number": "...", "course_name": "...", "teacher_id": 2 }, ...]` |
| `/api/teacher/courses/`        | `POST`     | `{"course_number": "CS101", "course_name": "Intro to CS"}` | **Teacher**: Create a new course.                                                               | Newly created course object                                                       |
| `/api/teacher/courses/{id}/`   | `GET`      | *None*                                               | **Teacher**: Get details of a single course (with or without team/assessment info).            | `{"id":..., "course_number":"...", "course_name":"...", ...}`                      |
| `/api/teacher/courses/{id}/`   | `PUT`      | `{"course_number": "...", "course_name": "..."}`     | **Teacher**: Update course details (optional endpoint).                                        | Updated course object                                                             |
| `/api/teacher/courses/{id}/`   | `DELETE`   | *None*                                               | **Teacher**: Delete a course. (Caution: might need to handle cascade delete for teams, etc.)    | 200 OK or 204 No Content                                                          |

---

#### 3.2 **Teams**

| **Endpoint**                                     | **Method** | **Request Body**  | **Description**                                                                                                | **Response**                                                                                                                    |
|---------------------------------------------------|------------|----------------------------------------------------|------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------|
| `/api/teacher/courses/{course_id}/teams/`         | `GET`      | *None*                                             | **Teacher**: List all teams under a specific course.                                                       | `[{ "id":1, "team_name": "...", "course_id": 10}, ...]`                                                                       |
| `/api/teacher/courses/{course_id}/teams/`         | `POST`     | `{"team_name": "Team A"}`                         | **Teacher**: Create a new team under the given course.                                                     | Newly created team object                                                                                                      |
| `/api/teacher/teams/{team_id}/`                   | `GET`      | *None*                                             | **Teacher**: Get details of a specific team (optionally with members).                                    | `{"id":1, "team_name":"Team A", "course_id":10, "members":[...]} `                                                            |
| `/api/teacher/teams/{team_id}/`                   | `PUT`      | `{"team_name": "Team A++"}` (for rename)          | **Teacher**: Update team info (e.g., rename).                                                              | Updated team object                                                                                                            |
| `/api/teacher/teams/{team_id}/`                   | `DELETE`   | *None*                                             | **Teacher**: Delete a team.                                                                                | 200 OK / 204 No Content                                                                                                        |
| `/api/teacher/teams/{team_id}/members/`           | `GET`      | *None*                                             | **Teacher**: List members of a team.                                                                       | e.g. `[ { "user_id": 7, "name": "Alice" }, { "user_id":8, "name": "Bob" } ]`                                                    |
| `/api/teacher/teams/{team_id}/members/`           | `POST`     | `{"user_id": 8}`                                   | **Teacher**: Add a user (student) to the team.                                                              | 201 Created or the added membership object                                                                                     |
| `/api/teacher/teams/{team_id}/members/{user_id}`  | `DELETE`   | *None*                                             | **Teacher**: Remove a user (student) from the team.                                                         | 200 OK / 204 No Content                                                                                                        |

---

### **4. Assessment Management (Teacher)**

#### 4.1 **Assessments**

| **Endpoint**                                     | **Method** | **Request Body**     | **Description**                                                                                                                               | **Response**                                                                                                                  |
|--------------------------------------------------|-----------|---------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------|
| `/api/teacher/courses/{course_id}/assessments/`  | `GET`      | *None*                                                                                | **Teacher**: Get a list of all assessments for this course (whether draft, published, or finished).                                           | `[{"id":1,"title":"...", "status":"draft","publish_date":null,"due_date":null}, ...]`                                        |
| `/api/teacher/courses/{course_id}/assessments/`  | `POST`     | `{"title":"Exam 1","status":"draft"}`                                                | **Teacher**: Create a new assessment (initially as a draft).                                                                                  | Newly created assessment object                                                                                              |
| `/api/teacher/assessments/{assessment_id}/`      | `GET`      | *None*                                                                                | **Teacher**: Get details of a specific assessment (including questions, possibly).                                                            | `{"id":1,"title":"Exam 1","status":"draft","questions":[...], ...}`                                                          |
| `/api/teacher/assessments/{assessment_id}/`      | `PUT`      | e.g. `{"title":"Exam 1 Revisited","status":"draft"}`                                  | **Teacher**: Update assessment info (title, dates, status, etc.).                                                                             | Updated assessment object                                                                                                    |
| `/api/teacher/assessments/{assessment_id}/`      | `DELETE`   | *None*                                                                                | **Teacher**: Delete an assessment (caution with existing responses).                                                                          | 200 OK / 204 No Content                                                                                                      |
| `/api/teacher/assessments/{assessment_id}/publish` | `POST`   | `{"publish_date":"2025-03-01T08:00Z","due_date":"2025-03-07T23:59Z"}` (example)       | **Teacher**: Publish a draft assessment (set status = published, sets publish_date/due_date, etc.).                                           | Updated assessment object with `status:"published"`                                                                          |
| `/api/teacher/assessments/{assessment_id}/finish`  | `POST`   | *None*                                                                                | Optionally, if finishing early. Sets status = finished.                                                                                       | Updated assessment object with `status:"finished"`                                                                           |
| `/api/teacher/assessments/{assessment_id}/release-results` | `POST` | *None*                                          | **Teacher**: Mark results as released to students (`results_released = true`).                                                                | 200 OK or updated object showing `results_released:true`                                                                     |


#### 4.2 **Assessment Questions**

| **Endpoint**                                                 | **Method** | **Request Body**     | **Description**                                                                                                            | **Response**                                                                                |
|--------------------------------------------------------------|-----------|----------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------|
| `/api/teacher/assessments/{assessment_id}/questions/`        | `GET`      | *None*                                                                           | **Teacher**: Get list of questions for this assessment.                                                                    | `[{"id":1,"question_type":"likert","content":"Rate X","order":1}, ...]`                    |
| `/api/teacher/assessments/{assessment_id}/questions/`        | `POST`     | e.g. `{"question_type":"likert","content":"Rate your teammate","order":1}`       | **Teacher**: Create a new question under this assessment.                                                                  | Newly created question object                                                               |
| `/api/teacher/questions/{question_id}/`                      | `GET`      | *None*                                                                           | **Teacher**: Get details of a single question.                                                                             | `{"id":1,"assessment_id":2,"question_type":"likert","content":"Rate your teammate"}`        |
| `/api/teacher/questions/{question_id}/`                      | `PUT`      | e.g. `{"content":"Rate your teammate's contribution","order":2}`                 | **Teacher**: Update the question's content / order.                                                                        | Updated question object                                                                    |
| `/api/teacher/questions/{question_id}/`                      | `DELETE`   | *None*                                                                           | **Teacher**: Delete a question.                                                                                            | 200 OK / 204 No Content                                                                    |

---

### **5. Student Endpoints**

#### 5.1 **Student’s Courses**

| **Endpoint**                  | **Method** | **Request Body** | **Description**                                                                        | **Response**                                                      |
|-------------------------------|-----------|-----------------|----------------------------------------------------------------------------------------|-------------------------------------------------------------------|
| `/api/student/courses/`       | `GET`      | *None*          | **Student**: Get all courses the student is enrolled in (through teams or direct link). | `[{"id":10,"course_number":"CS101","course_name":"Intro",...},...]` |


#### 5.2 **Assessments (Student)**

| **Endpoint**                                         | **Method** | **Request Body**  | **Description**                                                                                                                     | **Response**                                                                                                                         |
|------------------------------------------------------|-----------|----------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------|
| `/api/student/courses/{course_id}/assessments/`      | `GET`      | *None*                                                                     | **Student**: Get all **published or finished** assessments for this course.                                   | `[{"id":1,"title":"Exam 1","status":"published","due_date":"...","results_released":false},...]`                                     |
| `/api/student/assessments/{assessment_id}/`          | `GET`      | *None*                                                                     | **Student**: Get detail of a single assessment, including whether they can still submit or see results.       | `{"id":1,"title":"Exam 1","status":"published","results_released":false, "questions":[...]}`                                          |
| `/api/student/assessments/{assessment_id}/responses` | `GET`      | *None*                                                                     | **Student**: Get a summary of which teammates they still need to evaluate, or their last-saved answers.       | e.g. `{"to_evaluate":[ {"user_id":8,"name":"Bob","last_saved":"2025-02-28T12:00Z"}, ... ], "due_date":"...", "can_edit":true }`       |
| `/api/student/assessments/{assessment_id}/responses` | `POST`     | e.g. `{"to_user_id":8,"answers":{"Q1":4,"Q2":"Good job"}}`                 | **Student**: Save/update the evaluation responses for a single teammate (or themselves if self-assessment).   | 200 OK with updated response object.                                                                                                 |
| `/api/student/assessments/{assessment_id}/submit-all` (optional) | `POST` | *None* or `{"confirm":true}`                                              | **Student**: Indicate they have finalized all responses. Some designs let them edit until `due_date`, so this may be optional.         | 200 OK.                                                                                                                              |

#### 5.3 **View Results (Student)**

| **Endpoint**                                          | **Method** | **Request Body** | **Description**                                                                                         | **Response**                                                                                                                                 |
|-------------------------------------------------------|-----------|------------------|---------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------|
| `/api/student/assessments/{assessment_id}/results`    | `GET`      | *None*           | **Student**: View their own results for a finished assessment, **only** if `results_released == true`.  | e.g. `{"likert_averages":[{"question_id":1,"mean":4.2,"high":5,"low":3}, ...], "open_feedback":["Good job!","Needs improvement",...]} `       |
|                                                       |           |                  | If `results_released == false`, returns an error or `{"detail":"Results not released."}`.               |                                                                                                                                               |


---

### **6. Teacher Reviewing / Moderating Responses**  

| **Endpoint**                                                                   | **Method** | **Request Body**    | **Description**                                                                                                                    | **Response**                                                                                        |
|--------------------------------------------------------------------------------|-----------|------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------|
| `/api/teacher/assessments/{assessment_id}/responses/`                          | `GET`      | *None*                                                           | **Teacher**: List or search all responses for that assessment (e.g., by team, by student).                                         | Could return a structured JSON with each `from_user -> to_user -> answers`.                         |
| `/api/teacher/assessments/{assessment_id}/responses/{response_id}/moderate`    | `PUT`      | `{"edited_answers":{"Q2":"Rewritten feedback"}}`                | **Teacher**: Modify open-ended answers to remove offensive content.                                                                | Updated response object, storing `edited_answer_open` or equivalent field.                         |
| `/api/teacher/assessments/{assessment_id}/publish-results` (alternative name)  | `POST`     | *None*                                                           | **Teacher**: Final step to make all responses visible to students. (Same concept as `release-results` above, naming is flexible.)  | 200 OK, sets `results_released=true`.                                                               |

---









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


---

### **3. Team Table**

| Field         | Data Type   | PK?  | Not Null? | Description                                 |
|---------------|------------|------|-----------|---------------------------------------------|
| **id**        | UUID / INT | PK   | YES        | Primary key (team ID).                      |
| **course_id** | UUID / INT | FK → Course.id  | YES        | Foreign key referencing **Course**.         |
| **team_name** | VARCHAR    |      | YES        | Name of the team.                           |
| **created_at**| TIMESTAMP  |      | YES (default) | Timestamp when the team was created.    |

---

### **4. CourseMember Table**  
| Field        | Data Type   | PK?  | Not Null? | Description                                     |
|-------------|------------|------|-----------|-------------------------------------------------|
| **id**      | UUID / INT | PK   | YES       | Primary key (course-member ID).                 |
| **course_id** | UUID / INT | FK  | YES       | Foreign key referencing **Course**.             |
| **user_id** | UUID / INT | FK   | YES       | Foreign key referencing **User**.               |
| **role**    | ENUM/VARCHAR |    | YES       | `student` or `teacher`, indicating the role in the course. |
| **joined_at** | TIMESTAMP  |    | YES (default) | Timestamp when the user joined the course. |

---

### **5. TeamMember Table**  
| Field       | Data Type   | PK?  | Not Null? | Description                                     |
|------------|------------|------|-----------|-------------------------------------------------|
| **id**     | UUID / INT | PK   | YES       | Primary key (team-member ID).                   |
| **team_id** | UUID / INT | FK  | YES       | Foreign key referencing **Team**.               |
| **user_id** | UUID / INT | FK  | YES       | Foreign key referencing **User**.               |
| **joined_at** | TIMESTAMP  |    | YES (default) | Timestamp when the student joined the team. |
---

### **6. Assessment Table**

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

---

### **7. AssessmentQuestion Table**

| Field            | Data Type        | PK?  | Not Null? | Description                                                                               |
|------------------|------------------|------|-----------|-------------------------------------------------------------------------------------------|
| **id**           | UUID / INT       | PK   | YES        | Primary key (question ID).                                                                |
| **assessment_id**| UUID / INT       | FK → Assessment.id  | YES        | Foreign key referencing **Assessment**.                                                   |
| **question_type**| ENUM / VARCHAR   |      | YES        | Type of question, e.g., `likert` or `open`.                                              |
| **content**      | TEXT             |      | YES        | The actual question prompt.                                                               |
| **order** (opt.) | INT              |      | NO         | Optional field to specify display order within the assessment.                            |


---

### **8. AssessmentResponse Table**

| Field              | Data Type   | PK?  | Not Null? | Description                                                                                            |
|--------------------|------------|------|-----------|--------------------------------------------------------------------------------------------------------|
| **id**             | UUID / INT | PK   | YES        | Primary key (response ID).                                                                             |
| **assessment_id**  | UUID / INT | FK → Assessment.id  | YES        | Foreign key referencing **Assessment**.                                                                |
| **from_user_id**   | UUID / INT | FK → User.id  | YES        | The user who is giving the feedback (student).                                                         |
| **to_user_id**     | UUID / INT | FK → User.id  | YES        | The user who is being evaluated (student). If self-assessment is allowed, this can be the same as from_user_id. |
| **answers**        | JSON / TEXT|      | YES        | Stores all question responses in a JSON object (e.g., `{"Q1":4,"Q2":"Open-ended text..."}`).           |
| **last_saved**     | DATETIME   |      | YES        | When the response was last saved.                                                                      |
| **submitted** (opt.) | BOOLEAN  |      | NO         | Indicates if the response was fully submitted (versus a draft).                                        |


---






