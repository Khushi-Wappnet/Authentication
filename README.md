# Authentication and Project Management API

This project is a Django-based API for managing authentication, project management, resource allocation, and reporting. It includes features like user registration, role-based permissions, project and task management, resource allocation, and report generation in CSV and PDF formats.

---

## **Table of Contents**
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Swagger Documentation](#swagger-documentation)
- [Celery Configuration](#celery-configuration)
- [Testing](#testing)
- [License](#license)

---

## **Features**

### **Authentication**
- User registration with OTP verification.
- Login with token-based authentication.
- Forgot password and reset password functionality.
- Role-based access control.

### **Project Management**
- Create and manage projects, tasks, and milestones.
- Assign team members to projects.
- Task dependency management.

### **Resource Management**
- Manage resources (personnel, budget, equipment).
- Allocate resources to projects and tasks.
- Add comments and file attachments to projects and tasks.

### **Reporting**
- Generate project progress reports.
- Export reports in CSV and PDF formats.
- Dashboard with real-time metrics.

---

## **Installation**

### **1. Clone the Repository**
```bash
git clone <repository-url>
cd Authentication
```

### **2. Set Up a Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### **3. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **4. Set Up Environment Variables**
Create a `.env` file in the root directory and add the following:
```env
SECRET_KEY=your_secret_key
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=localhost
DB_PORT=5432
EMAIL_HOST_USER=your_email@example.com
EMAIL_HOST_PASSWORD=your_email_password
```

### **5. Apply Migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

### **6. Create a Superuser**
```bash
python manage.py createsuperuser
```

### **7. Run the Server**
```bash
python manage.py runserver
```

---

## **Usage**

### **Run the Server**
After completing the installation steps, start the Django development server:
```bash
python manage.py runserver
```

### **Access the API**
- Base URL: `http://127.0.0.1:8000/`
- Swagger Documentation: `http://127.0.0.1:8000/swagger/`
- Example Endpoints:
  - **Authentication**: `/api/auth/`
  - **Project Management**: `/api/project-management/`
  - **Resource Management**: `/api/resource-management/`
  - **Reporting**: `/api/reporting/`

---

## **API Endpoints**

### **Authentication**
- `POST /api/auth/register/`: Register a new user.
- `POST /api/auth/verify-otp/`: Verify OTP for user registration.
- `POST /api/auth/login/`: Login and obtain an authentication token.
- `POST /api/auth/forgot-password/`: Request a password reset.
- `POST /api/auth/reset-password/`: Reset the password.
- `GET /api/auth/roles/`: List all roles.
- `POST /api/auth/roles/`: Create all roles.
- `GET /api/auth/permissions/`:List all permissions.
- `POST /api/auth/permissions/`: Create a new permission.
- `GET /api/auth/users/`: List all users..
- `GET /api/auth/role-permissions/:`: List all role-permission mappings.
- `POST /api/auth/role-permissions/:`: Create a new role-permission mapping.
- `DELETE /api/auth/role-permissions/<int:pk>/`: Delete a specific role-permission mapping.



### **Project Management**
- `GET /api/project-management/projects/`: List all projects.
- `POST /api/project-management/projects/`: Create a new project.
- `GET /api/project-management/projects/<id>/`: Retrieve a specific project.
- `PUT /api/project-management/projects/<id>/`: Update a project.
- `DELETE /api/project-management/projects/<id>/`: Delete a project.
- `GET /api/project-management/milestones/`: List all milestones.
- `POST /api/project-management/milestones/`: Create a new milestone.
- `GET /api/project-management/tasks/`: List all tasks.
- `POST /api/project-management/tasks/`: Create a new task.
- `PUT /api/project-management/tasks/<id>/`: Update a specific task.
- `GET /api/project-management/schedule/`: View the project schedule.

### **Resource Management**
- `GET /api/resource-management/resources/`: List all resources.
- `POST /api/resource-management/resources/`: Add a new resource.
- `GET /api/resource-management/allocations/`: List all resource allocations.
- `POST /api/resource-management/allocations/`: Allocate resources to a project or task.
- `GET /api/resource-management/comments/`: List all comments.
- `POST /api/resource-management/comments/`: Add a comment to a project or task.
- `GET /api/resource-management/attachments/`: List all file attachments.
- `POST /api/resource-management/attachments/`: Add a file attachment to a project or task.

### **Reporting**
- `GET /api/reporting/projects/`: Generate project progress reports.
- `GET /api/reporting/resources/`: Generate resource usage reports.
- `GET /api/reporting/export/csv/`: Export reports in CSV format.
- `GET /api/reporting/export/pdf/`: Export reports in PDF format.
- `GET /api/reporting/dashboard/`: View real-time dashboard metrics.

---

## **Swagger Documentation**

The API is documented using Swagger. You can access the Swagger UI by visiting:
```plaintext
http://127.0.0.1:8000/swagger/
```

The Swagger UI provides an interactive interface to test all available endpoints.

---

## **Celery Configuration**

### **1. Start Redis**
Ensure Redis is running on your system:
```bash
redis-server
```

### **2. Start Celery Worker**
Run the following command to start the Celery worker:
```bash
celery -A Authentication worker --loglevel=info
```

### **3. Start Celery Beat (Optional)**
If you are using periodic tasks, start Celery Beat:
```bash
celery -A Authentication beat --loglevel=info
```

---

## **Testing**

Run the test suite using:
```bash
python manage.py test
```

This will execute all unit tests and integration tests for the project.

---

## **License**

This project is licensed under the BSD License. See the LICENSE file for details.