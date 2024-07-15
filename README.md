Task Manager: (postman doc: https://www.postman.com/flight-engineer-37345319/workspace/task-manager)

This is a Django-based task management application that allows users to create, manage, and track their tasks.

A)Project Setup

  1. Clone the Repository: git clone https://github.com/siddhant-jain-26/taskmanager.git

  2. Create a Virtual Environment: python -m venv venv (It's highly recommended to use a virtual environment to isolate project dependencies. )

B)Activate the Virtual Environment: source venv/bin/activate  # Linux/macOS
                                    venv\Scripts\activate.bat  # Windows

C)Install Dependencies: pip install -r requirements.txt(Install the required Python packages listed in the requirements.txt file)

D)MongoDB Connection

 1. Create a MongoDB Atlas Cluster: Follow the tutorial here to create a MongoDB Atlas cluster: https://www.youtube.com/watch?v=J61_hiFauNs
 2. Configure Database Settings (in settings.py): Replace the placeholders with your actual MongoDB Atlas credentials:
DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'CLIENT': {
            'host': 'mongodb+srv://<username>:<password>@cluster0.dvgmkyc.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0',
            'port': 27017,
            'username': '<username>',
            'password': '<password>',
            'authSource': 'admin',
        },
        'NAME': 'Cluster0',
    }
}

E)Run the Server

1. Create Migrations: python manage.py makemigrations

2. Apply Migrations: python manage.py migrate

3. Start the Development Server: python manage.py runserver(This will typically start the server on http://127.0.0.1:8000/ by default. You can access your application in your web browser at this URL.)

F)Test the Application

1. Registration: Refer to the documentation for users > accounts > register endpoint to register a user. Obtain an access token upon successful registration.

2. Login:
Use the users > accounts > login endpoint to log in with the registered email and password.
Select "Bearer Token" as the authorization type and provide the obtained access token.
This will return a new set of refresh and access token pairs for further use.

3. Profile: Use the access token in the authorization header to interact with the users > accounts > profile endpoints:
GET: Retrieve user profile information.
PUT: Update user profile information.
DELETE: Delete the user profile (use with caution!)

4. Tasks: Use the access token in the authorization header to interact with the tasks endpoints:
GET: /tasks/ - Fetch all tasks for the logged-in user.

5. Single Task: Use the access token in the authorization header to interact with the tasks endpoints: GET: /tasks/<task_id>/ - Fetch a specific task by its ID.

6. Create Task: Use the POST method on the /tasks/ endpoint with the access token in the authorization header and the following data in the request body:
title (string): The title of the task.
description (string): (Optional) A description of the task.
due_date (datetime string): (Optional) The due date and time of the task.

7. Update Task: Use the PUT method on the /tasks/<task_id>/ endpoint with the access token in the authorization header and the desired changes in the request body.

8. Delete Task: Use the DELETE method on the /tasks/<task_id>/ endpoint with the access token in the authorization header.
