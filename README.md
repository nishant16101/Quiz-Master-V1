## Quiz Master Application


Overview

Quiz Master is an interactive quiz application designed to manage quizzes efficiently. Users can attempt quizzes on various subjects and track their progress. The application supports an admin panel to create and manage quizzes, subjects, and users.

Features

User authentication (Admin & Regular Users)

Quiz creation and management

Subject and chapter categorization

Quiz attempts tracking with scores

Secure password hashing

Installation & Setup

Follow these steps to set up and run the Quiz Master application on your local machine.

1. Clone the Repository

git clone https://github.com/yourusername/QuizMaster.git
cd QuizMaster

2. Create a Virtual Environment

python -m venv venv

3. Activate the Virtual Environment

On Windows:

venv\Scripts\activate

On macOS/Linux:

source venv/bin/activate

4. Install Dependencies

pip install -r requirements.txt



5. Run the Application

python app.py

The application will start running on http://127.0.0.1:5000/.

Usage

Open a web browser and visit http://127.0.0.1:5000/

Sign up or log in as an admin to create quizzes

Users can attempt quizzes and track their scores