# RightsPlace

## Overview

RightsPlace is a human rights reporting and case-tracking web application. The platform allows individuals to report human rights violations either anonymously or through registered accounts. Verified lawyers and NGOs can then be assigned to these reports as formal cases by site administrators. Reporters are able to track the status of their reports once they are taken up as cases, while lawyers and NGOs have access to read-only dashboards showing the cases assigned to them.

The system is designed to reflect real-world human rights workflows, where reporting, verification, legal action, and resolution are typically mediated by trusted organizations rather than direct peer-to-peer interaction.

## Distinctiveness and Complexity

RightsPlace is intentionally distinct from all other projects in CS50W. It is not a social network, as there is no user-to-user following, posting, or messaging system. It is also not an e-commerce platform, as it involves no transactions, listings, bidding, or payments of any kind.

Unlike earlier course projects, RightsPlace implements a role-based workflow system with clearly defined user responsibilities and permissions. Users interact with the platform differently depending on whether they are reporters, lawyers, NGOs, or administrators. Reports transition through multiple states (e.g., pending, in progress, resolved), and these transitions are controlled through administrative actions rather than direct user interaction.

The project also introduces a case lifecycle model, where reports may or may not become cases, and where cases are tracked independently of their originating reports. This adds a layer of domain complexity beyond simple CRUD operations. Administrative verification of lawyers and NGOs, restricted case assignment, and automated status updates further increase the application’s complexity.

RightsPlace integrates Django models, views, templates, admin customization, and JavaScript-enhanced form handling, while remaining mobile-responsive through Bootstrap styling. The combination of multi-role access control, real-world domain modeling, and administrative workflows makes this project significantly more complex and distinct than any prior assignment in the course.

Additionally, the project implements multi-file evidence uploads using the django-multipleupload package, combined with custom client-side JavaScript. Users can add evidence files via both traditional file selection and drag-and-drop interactions. Supporting this required managing a client-side file bucket, synchronizing files with Django forms, handling upload progress feedback, and processing multiple files server-side with proper relational mapping between reports and evidence. This functionality is not covered in the course material and significantly increased both the technical complexity and development time of the application.

## Features

* Anonymous and authenticated human rights violation reporting
* User registration and authentication
* Role-based user profiles (Reporter, Lawyer, NGO)
* Admin verification of lawyers and NGOs
* Admin-managed case creation and assignment
* Automatic report status updates when cases are created
* Reporter dashboard to track reports and cases
* Lawyer/NGO dashboard to view assigned cases
* Public-facing verified partners listing (restricted to logged-in users)
* Evidence upload and management
* Mobile-responsive UI using Bootstrap

## File Structure and Description
### Project Root
* **`manage.py`**: Django’s command-line utility for running the server, migrations, and administrative tasks.
* **`requirements.txt`**: Lists Python dependencies required to run the application.
* **`media/`**: A directory which stores uploaded evidence files associated with reports.

### rightsplace_project/ (Project Configuration)
* **`settings.py`**: Contains global Django settings, including installed apps, database configuration, static and media settings.
* **`urls.py`**: Root URL configuration that routes requests to the application URLs.

### rightsplace/ (Main Application)
* **`models.py`**: Defines the core data models: UserProfile, Report, Evidence, and Case, which together represent users, reports, uploaded evidence, and assigned legal cases.
* **`views.py`**: Contains all application logic, including report submission, dashboards for reporters, lawyers, and NGOs, authentication handling, and partner listings.
* **`urls.py`**: Maps application-specific URLs to their corresponding views.
* **`forms.py`**: Defines Django forms for user registration and report creation, including centralized validation and error handling.
* **`admin.py`**: Customizes the Django admin interface, including inline evidence management, role-based filtering, verification controls, and automated report status updates.
* **`apps.py`**: Application configuration file for Django.
* **`migrations/`**: Auto-generated database migration files reflecting changes to the data models.

### Templates (rightsplace/templates/rightsplace/)
* **`layout.html`**: Base template defining the site layout and navigation.
* **`index.html`**: Homepage introducing the platform and its purpose.
* **`login.html`** and register.html: Authentication-related templates.
* **`anonymous_report.html`** and  **`report_create.html`**: Templates for submitting reports anonymously or as a registered user.
* **`reporter_dashboard.html`**: Dashboard showing all reports submitted by a reporter.
* **`reporter_cases.html`**: Dashboard showing only reports that have been converted into active cases for a reporter.
* **`assigned_cases_dashboard.html`**: Read-only dashboard for lawyers and NGOs showing assigned cases.
* **`verified_partners.html`**: Lists verified lawyers and NGOs for authenticated users.

### Static Files (rightsplace/static/rightsplace/)
* **`anonymous_report.js`**: Handles client-side validation and interactivity for anonymous reporting.
* **`report_create.js`**: JavaScript enhancements for report creation forms.
* **`register.js`**: Client-side logic for user registration.

## How to Run the Application

1. Clone the repository.

2. Create and activate a virtual environment.

3. Install dependencies:
    ```
    pip install -r requirements.txt
    ```
    ### Database Setup
    This project uses PostgreSQL as its database. PostgreSQL must be installed and running before the application can be started.

    The following environment variables must be set before running database migrations:
    ```
    PGDATABASE=<database_name>
    PGUSER=<database_user>
    PGPASSWORD=<database_password>
    PGHOST=localhost
    PGPORT=5432
    ```
    These variables are referenced in **`settings.py`** and loaded through **`dotenv`** to configure the database connection.

    So, create a **`.env`** file in the root directory with these variables and proceed to step 4.

4. Run database migrations:
    ```
    python manage.py migrate
    ```

5. Create a superuser:
    ```
    python manage.py createsuperuser
    ```

6. Start the development server:
    ```
    python manage.py runserver
    ```

7. Access the application at http://127.0.0.1:8000 in your web browser.

8. The admin interface can be accessed at http://127.0.0.1:8000/admin/, where adminitsrators can verify lawyers and NGOs and manage cases.


## Additional Notes

* Lawyers and NGOs must be verified by an administrator before they can be assigned cases.
* Case progression and resolution are managed by administrators to reflect real-world workflows.
* Communication between reporters, lawyers, NGOs, and administrators is intentionally indirect to preserve safety and oversight.
* The project was designed with clarity, security, and real-world applicability in mind rather than direct user-to-user interaction.



