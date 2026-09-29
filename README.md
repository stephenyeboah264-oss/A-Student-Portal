# Student Portal

A fullstack Flask web application for registering and managing student records, built as a capstone project for the Fullstack Python Developer track.

## Project Description

This application allows students to register with their personal and academic details through a web form. Submitted data is stored in an SQLite database, and uploaded photos are saved to the server. All registered students are listed in a searchable table, with a details page for each student that includes an asynchronous admission status updater.

## Setup Instructions

1. Install dependencies:
2. Run the application:
3. Open your browser at `http://127.0.0.1:5000`

## How to Test

**Form:**
- Go to the "Get Started" page
- Fill in all fields (image, text fields, email, date of birth, gender, phone, address, state/local government, next of kin, WASSCE aggregate)
- Click Submit — you should be redirected to the Students table with your new entry visible

**Table:**
- View all registered students at `/students`
- Use the search bar and filters (name, admission status, gender, WASSCE aggregate) to narrow results
- Click "View" on any row to open that student's details page

**Status update:**
- On a student's Details page, use the "Change Status" dropdown
- Selecting a new status (Admitted / Rejected / Undecided) updates instantly without reloading the page, via an asynchronous request