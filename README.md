# Shelter & Soul – Real Estate Web Application

## Project Overview

Shelter & Soul is a Django-based real estate web application developed as part of the DA3331 – Business Application Development group project.
The platform allows users to search, view, and list properties for sale or rent, while enabling administrators to manage listings, users, and inquiries efficiently.

## Key Features

### User Features
- User Registration and Login 
- Browse and Search Properties 
- Filter Properties  
- View detailed property information with images 
- Add properties to Wishlist 
- Compare different properties 
- Send inquiries to admin/agents
- Contact Agents through mail
- View recently viewed properties
- Edit profile details
- Add property for selling (approval required)
- Edit or delete user-submitted property listings

### Admin Features
- Managing property listings (add, edit, delete)
- Approving / rejecting sell requests
- Viewing and managing user inquiries
- Managing registered users
- Managing agents
- Viewing wishlist of users
- Monitoring overall system data

### Technologies Used
- Backend: Python, Django 
- Database: SQLite 
- Frontend: HTML, CSS, JavaScript 
- Styling: Bootstrap 
- Version Control: Git & GitHub

## Screenshots

### Homepage

<img width="1900" height="869" alt="image" src="https://github.com/user-attachments/assets/d260fc12-aaa6-4b99-b922-b629e10c0645" />

### Login

<img width="1895" height="862" alt="image" src="https://github.com/user-attachments/assets/9e692174-2693-4b2b-9d0f-a04d0c72fa1b" />

### Property Details Page

<img width="1900" height="864" alt="image" src="https://github.com/user-attachments/assets/b1cdec5c-1856-414b-a510-f6fad7b0c0fc" />

## Add property

<img width="1895" height="867" alt="image" src="https://github.com/user-attachments/assets/71930c04-edfd-4a4f-999c-57ca490b73c8" />

### Agent Page

<img width="1901" height="868" alt="image" src="https://github.com/user-attachments/assets/cda6fec4-3c07-4da7-9357-7e1cb2100b2e" />

### Dashboard

<img width="1902" height="868" alt="image" src="https://github.com/user-attachments/assets/0d152d9c-70bd-4f65-acd1-5e67dd7dab24" />

### My Profile

<img width="1901" height="864" alt="image" src="https://github.com/user-attachments/assets/efe7a17d-03ba-4f2f-9e96-aba78f1ce0f5" />

### My Wishlist

<img width="1901" height="867" alt="image" src="https://github.com/user-attachments/assets/62f6c4ff-96d8-4c46-869e-d8fbdd3b3dbc" />

### My Inquiries

<img width="1892" height="866" alt="image" src="https://github.com/user-attachments/assets/c8ca7282-47c4-40b7-a069-e12b5de5e410" />

### My Sell Requests

<img width="1908" height="866" alt="image" src="https://github.com/user-attachments/assets/e9e14754-44b1-4d0c-b690-bc98785fb62d" />

### Compare Properties

<img width="1903" height="872" alt="image" src="https://github.com/user-attachments/assets/6c31daf6-ad05-4bf4-acdf-f856aef49177" /> 

## Installation & Setup Guide

- ### Follow these steps to run the project locally
git clone https://github.com/pemajo-sudo/real-estate-project.git  
cd real-estate-project

- ### Create virtual environment
python -m venv env

- ### Activate environment
source env/Scripts/activate

- ### Install dependencies
pip install -r requirements.txt

- ### Apply migrations
python manage.py migrate

- ### Run the server
python manage.py runserver

- ### Open in browser
http://127.0.0.1:8000/

## Admin Panel & Database Management

This application uses Django’s built-in administration panel to manage the database efficiently.

- ### Admin panel can be accessed at:
http://127.0.0.1:8000/admin

- ### Login using superuser credentials
Username: user1  
Password: 1234admin  
Email: admin@gmail.com

This project demonstrates a fully functional real estate management system with user interaction, admin control and modern UI design, fulfilling the requirements of the assignment.












