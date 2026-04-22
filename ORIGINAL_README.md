# Clinic-Appointment-System--Django

## User Stories

### 1. Patient User Stories

- **Registration & Access:** As a Patient, I want to register and log in so that I can securely use the clinic system.
- **Profile Management:** As a Patient, I want to view and update my profile so that my personal details are correct.
- **Booking Open Slots:** As a Patient, I want to book only from the open time slots so that I do not try to see a doctor who is busy.
- **Prevent Overlap:** As a Patient, I want the system to block me from booking two appointments at the exact same time so that my schedule is clear.
- **View History:** As a Patient, I want to see my future and past appointments so that I know when I need to visit the clinic.
- **Cancellation:** As a Patient, I want to cancel my visit if the status is "Requested" or "Confirmed" so that I do not waste the doctor's time.
- **Reschedule Request:** As a Patient, I want to ask for a new time for my visit so that I can still get care if my plans change.
- **Read Summary:** As a Patient, I want to read a view-only summary of my visit after it is done so that I remember my treatment and tests.

### 2. Doctor User Stories

- **Daily View:** As a Doctor, I want to see my schedule and today's list of patients so that I know what my day looks like.
- **Manage Requests:** As a Doctor, I want to confirm or say no to new booking requests so that I control my work hours.
- **Status Updates:** As a Doctor, I want to mark a patient as "Checked-In" or "No-Show" so that my records show who actually came.
- **Medical Notes:** As a Doctor, I want to write down a diagnosis, notes, a drug plan, and requested tests so that the visit is fully recorded.
- **Finish Visit:** As a Doctor, I want the system to force me to fill out the medical record before marking the visit as "Completed" so that I do not forget any steps.
- **Buffer Time:** As a Doctor, I want a 5-minute break added automatically before and after a visit so that I can rest or catch up.

### 3. Receptionist User Stories

- **Doctor Availability:** As a Receptionist, I want to set up the weekly schedule for doctors, including their days off, so that patients see the correct open slots.
- **Confirm Bookings:** As a Receptionist, I want to approve patient requests so that clinic rules are followed.
- **Patient Arrival:** As a Receptionist, I want to check patients in and manage the order of the line so that the clinic runs smoothly.
- **Wait Time:** As a Receptionist, I want to see how long a patient has been waiting since check-in so that I can tell them when the doctor is ready.
- **Staff Rescheduling:** As a Receptionist, I want to change a patient's appointment time for them so that I can help if they call on the phone.
- **Data Privacy:** As a Receptionist, I want the system to block me from reading the doctor's medical notes so that patient privacy is kept safe.
- **Search and Filter:** As a Receptionist, I want to find visits by date, status, doctor, or patient name so that I can answer questions fast.

### 4. Admin User Stories

- **User Control:** As an Admin, I want to manage all users and their roles so that only the right staff can log in.
- **Reschedule Help:** As an Admin, I want the power to change patient appointments so that I can fix schedule problems.
- **Custom Dashboard:** As an Admin, I want to view a custom analytics dashboard so that I can see the clinic's data without using the built-in Django screen.
- **Export Data:** As an Admin, I want to download clinic data as a CSV file so that I can use it in other programs.
- **Track Changes (Audit Trail):** As an Admin, I want the system to save a history of all changed appointments (old time, new time, reason, who did it) so that I know exactly what happened.

---

## 📸 Pages & Screenshots Documentation

For a comprehensive visual guide to all pages and interfaces in the system, see [PAGES_DOCUMENTATION.md](PAGES_DOCUMENTATION.md).

This documentation includes:

- **Authentication Pages** - Login, Registration, Password Reset
- **Patient Portal** - Dashboard, Booking, History, Profile, Medical Records
- **Doctor Portal** - Daily Queue, Pending Bookings, Diagnosis Form, Schedule
- **Receptionist Portal** - Queue Management, Appointment Search, Dashboard
- **Admin Dashboard** - User Management, Analytics, Scheduling, Audit Trail

Each section includes page descriptions, key features, and corresponding screenshots.

---
