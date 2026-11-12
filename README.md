# Gmail Clone – Email Management System

A web-based email management application developed using Python, Flask, and MongoDB.

## Overview

This project is a Gmail-inspired web application developed as part of the **Database System Implementation** course at university. It was built using Flask and MongoDB and originally connected to a university-hosted MongoDB server.
It provides an interface for managing sent and received emails, viewing email details, tracking unread messages, and generating reports using MongoDB queries and aggregation pipelines.

The main purpose of this project was to gain practical experience with NoSQL databases and backend web development.

## Technologies

- Python
- Flask
- MongoDB
- PyMongo
- HTML
- CSS
- JavaScript
- Jinja2

## Features

### Email Management
- View received emails (Inbox)
- View sent emails
- Compose and save new emails
- View detailed email information
- Delete sent and received emails
- Mark received emails as read

### MongoDB Operations
- CRUD operations using PyMongo
- MongoDB Aggregation Framework
- Sorting email records by date
- Filtering unread emails
- Grouping emails by sender and receiver
- Generating email statistics
- Sorting received emails alphabetically by sender

### Reports
- Number of received emails per sender
- Number of sent emails per receiver
- Alphabetically sorted email reports

## MongoDB Concepts Used

This project demonstrates practical usage of several MongoDB aggregation operators:

| Operator | Purpose |
|---|---|
| `$unwind` | Deconstructing email arrays |
| `$match` | Filtering unread emails |
| `$sort` | Sorting email records |
| `$project` | Selecting required fields |
| `$group` | Grouping emails and generating statistics |
| `$skip` | Implementing pagination |
| `$limit` | Limiting query results |

## Project Structure

```text
Email-Management-System/
│
├── app.py
├── requirements.txt
├── README.md
├── templates/
│   ├── gmail.html
│   ├── inbox.html
│   ├── sent.html
│   ├── new_email.html
│   ├── report.html
│   └── ...
```

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/GolsaCodes/Flask-MongoDB-Email-Management-System.git

cd Flask-MongoDB-Email-Management-System
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate the environment:

Windows:
```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure MongoDB

Install and start a local MongoDB instance.

Set the MongoDB connection string:

Windows PowerShell:
```powershell
$env:MONGO_URI="mongodb://localhost:27017/"
```

Linux / macOS:
```bash
export MONGO_URI="mongodb://localhost:27017/"
```

The application uses a database named `G9` with two collections:

- `sent`
- `received`

The collections must contain documents following the data structure expected by the application.

### 5. Run the application

```bash
python app.py
```

Open your browser:

http://127.0.0.1:5000/

## Note

The original MongoDB database was hosted on a university server, which is no longer available.

The application has been designed to use a configurable MongoDB connection string. To run it, configure your own MongoDB instance and provide the required database collections and documents.

## Author
Developed as a university academic project.
