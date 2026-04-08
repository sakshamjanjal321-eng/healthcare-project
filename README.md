---
title: Healthcase Project
emoji: 🏃
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 5.20.0
app_file: app.py
pinned: false
---

# HealthCare - Your Wellness Companion

A simple, beautifully designed wellness application built with Flask (Python) and Vanilla HTML/CSS. This project allows users to learn about health tracking (fitness, diet, wellness) and seamlessly book appointments directly from the website.

## Features

- **Dynamic Frontend**: Modern and clean UI with a simple dark-mode toggle for better readability.
- **Appointment Booking**: Users can book an appointment automatically via a smooth JavaScript (AJAX) experience without leaving or refreshing the page.
- **Visitor Tracking**: The backend natively and automatically records visitor information (IP address, browser details, accessed paths) so you can track your audience.
- **Database Architecture**: Runs on a robust SQLite3 database (`visits.db`) storing both visitors and bookings systematically.
- **Protected Admin Panel**: Includes a protected `/admin` endpoint where the administrator can inspect recent incoming bookings and visitor tracking logs.
- **Security Check**: Employs an `/api/auth_status` system utilizing browser fetch seamlessly alongside Flask server-side session cookies.

## Admin Credentials

The administrative interface is heavily guarded by a session-encrypted login page (`/login`). To access the Admin Panel, you must use the following updated credentials:

- **Username**: `Saksham0012`
- **Password**: `Saksham@2006`

## Technologies Used

- **Frontend**: HTML5, Vanilla CSS, JavaScript (Fetch API)
- **Backend**: Python, Flask
- **Database**: SQLite3

## Getting Started

### Prerequisites

You need Python 3 installed on your machine. You can download it from [python.org](https://python.org).

### Installation

1. **Clone or Download the project** to your local machine.
2. **Open a terminal** and navigate to the project directory:
   ```bash
<<<<<<< HEAD
   cd path/to/Health Case
=======
   
>>>>>>> ae7c7d5da59be4ed1e221803e743c769b9e69096
   ```
3. **Install the required dependencies** (assuming you have `flask` in your requirements):
   ```bash
   pip install flask
   ```
   *Note: If you have a `requirements.txt` file, you can run `pip install -r requirements.txt` instead.*

4. **Run the application**:
   ```bash
   python app.py
   ```

5. **View the website**:
   Open your browser and navigate to [http://localhost:5000](http://localhost:5000)

## Project Structure

- `app.py` - The core application file containing all Python Flask routing logic, login security, and database controllers.
- `Index.html` - The primary landing page for the application.
- `login.html` & `admin.html` - System administrative pages handling user verification and internal data tables.
- `style.css` - The master CSS file for handling layout configurations, animations, and the overarching dark mode theme.
- `visits.db` - Automatically generated SQLite system housing all data.
- `*.html` - Additional pages (e.g., `about.html`, `fitness.html`, etc.) for more detailed content.
