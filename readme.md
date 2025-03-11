# Netflix Clone (Django + Tailwind CSS)

A fully functional Netflix Clone built using Django, Tailwind CSS, and Django-Allauth for authentication. This project allows users to create accounts, manage multiple profiles, and stream movies/videos.

## Features

- User Authentication (Login, Signup, Logout)  
- Profile Management (Multiple Profiles per Account)  
- Movies & TV Shows (Single & Seasonal Content)  
- Maturity Levels (Kids & All)  
- Video Streaming (Upload & Watch Movies)  
- Responsive UI (Built with Tailwind CSS)  

## Tech Stack

- Backend: Django, Django ORM  
- Frontend: Tailwind CSS, HTML, JavaScript  
- Database: SQLite (default), PostgreSQL (optional)  
- Authentication: Django-Allauth  


## Installation Guide

### Clone the Repository

```bash
git clone https://github.com/shahradf/Netflix
cd Netflix
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
python manage.py migrate
python manage.py createsuperuser 
python manage.py runserver
```