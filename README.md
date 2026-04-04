# Clinic-Appointment-System--Django


## User Stories

### 1. Patient User Stories
* **Registration & Access:** As a Patient, I want to register and log in so that I can securely use the clinic system. 
* **Profile Management:** As a Patient, I want to view and update my profile so that my personal details are correct. 
* **Booking Open Slots:** As a Patient, I want to book only from the open time slots so that I do not try to see a doctor who is busy. 
* **Prevent Overlap:** As a Patient, I want the system to block me from booking two appointments at the exact same time so that my schedule is clear. 
* **View History:** As a Patient, I want to see my future and past appointments so that I know when I need to visit the clinic. 
* **Cancellation:** As a Patient, I want to cancel my visit if the status is "Requested" or "Confirmed" so that I do not waste the doctor's time. 
* **Reschedule Request:** As a Patient, I want to ask for a new time for my visit so that I can still get care if my plans change. 
* **Read Summary:** As a Patient, I want to read a view-only summary of my visit after it is done so that I remember my treatment and tests. 


### 2. Doctor User Stories
* **Daily View:** As a Doctor, I want to see my schedule and today's list of patients so that I know what my day looks like. 
* **Manage Requests:** As a Doctor, I want to confirm or say no to new booking requests so that I control my work hours. 
* **Status Updates:** As a Doctor, I want to mark a patient as "Checked-In" or "No-Show" so that my records show who actually came. 
* **Medical Notes:** As a Doctor, I want to write down a diagnosis, notes, a drug plan, and requested tests so that the visit is fully recorded. 
* **Finish Visit:** As a Doctor, I want the system to force me to fill out the medical record before marking the visit as "Completed" so that I do not forget any steps. 
* **Buffer Time:** As a Doctor, I want a 5-minute break added automatically before and after a visit so that I can rest or catch up. 


### 3. Receptionist User Stories
* **Doctor Availability:** As a Receptionist, I want to set up the weekly schedule for doctors, including their days off, so that patients see the correct open slots. 
* **Confirm Bookings:** As a Receptionist, I want to approve patient requests so that clinic rules are followed. 
* **Patient Arrival:** As a Receptionist, I want to check patients in and manage the order of the line so that the clinic runs smoothly. 
* **Wait Time:** As a Receptionist, I want to see how long a patient has been waiting since check-in so that I can tell them when the doctor is ready. 
* **Staff Rescheduling:** As a Receptionist, I want to change a patient's appointment time for them so that I can help if they call on the phone. 
* **Data Privacy:** As a Receptionist, I want the system to block me from reading the doctor's medical notes so that patient privacy is kept safe. 
* **Search and Filter:** As a Receptionist, I want to find visits by date, status, doctor, or patient name so that I can answer questions fast. 


### 4. Admin User Stories
* **User Control:** As an Admin, I want to manage all users and their roles so that only the right staff can log in. 
* **Reschedule Help:** As an Admin, I want the power to change patient appointments so that I can fix schedule problems. 
* **Custom Dashboard:** As an Admin, I want to view a custom analytics dashboard so that I can see the clinic's data without using the built-in Django screen. 
* **Export Data:** As an Admin, I want to download clinic data as a CSV file so that I can use it in other programs. 
* **Track Changes (Audit Trail):** As an Admin, I want the system to save a history of all changed appointments (old time, new time, reason, who did it) so that I know exactly what happened. 

------------------------------------------------

## The 12-Day Execution Plan

**Day 1: Setup & Database Schema**
* Create the Django project and set up your database (MySQL is a solid choice).
* Create the core models: `User`, `DoctorSchedule`, `Appointment`, and `ConsultationRecord`.
* *Dependency:* None.

**Day 2: Authentication & Roles**
* Set up Django authentication.
* Create the four user groups: Patient, Doctor, Receptionist, Admin.
* Add permissions to lock down endpoints based on the user's role.
* *Dependency:* Requires models from Day 1.

**Day 3: Schedules & Slot Generation**
* Build the logic to define a doctor's weekly schedule.
* Write a function to generate available slots based on the schedule, session duration, and exceptions (vacations).
* *Risk:* Test this logic heavily. If slots generate wrong, the whole system breaks.

**Day 4: The Booking Engine (Crucial)**
* Build the DRF API for patients to book slots.
* Write database constraints to stop overlapping appointments.
* Add the logic for the 5-minute buffer before and after appointments.

**Day 5: Status Lifecycle & Audit Trail**
* Add endpoints to change appointment status (REQUESTED, CONFIRMED, CHECKED_IN, COMPLETED, CANCELLED/NO_SHOW.
* Build the reschedule feature for patients and staff.
* Create a separate database table to save the audit history (old date, new date, who changed it, reason.
* *Dependency:* Requires the booking engine from Day 4.

**Day 6: EMR, Queue, & Search**
* Build the DRF API for doctors to add medical notes, prescriptions, and requested tests for COMPLETED appointments.
* Create the API for the receptionist to check in patients and calculate wait time.
* Add Django Filter to let staff search by status, date, doctor, or patient name.

**Day 7: Unit Tests**
* Stop building features. Write the required tests.
* Write at least 12 unit tests and generate the coverage report. Focus tests on the booking logic and permissions.

**Day 8: Frontend Setup & Admin Dashboard**
* Set up your React or Next.js project.
* Build the Custom Admin Dashboard to manage users, roles, and view analytics
* Rule Check:* Do not use AI for this specific dashboard. Write the code yourself.

**Day 9: Doctor & Patient Views**
* Build the Patient view: profile update, book slots, view history, read-only consultation summary.
* Build the Doctor view: see today's queue, confirm/decline requests, fill out consultation notes.
* *Dependency:* Requires APIs from Days 2-6.

**Day 10: Receptionist View**
* Build the Receptionist view: manage doctor schedules, check in patients, manage the queue.
* Ensure receptionists cannot see the medical notes.

**Day 11: Design Polish**
* Make the UI beautiful.
* You can use AI tools to help generate CSS and improve the layout here.
* Make sure forms show clear error messages if booking fails.

**Day 12: Documentation & Shipping**
* Write the `README.md` file. Add setup steps, how to run tests, and list the sample users.
* Take screenshots of your test coverage.
* Commit everything to GitHub and send the repo link.
I reviewed the requirements for your clinic system. Here are the user stories written with simple words, grouped by the main roles so your team knows exactly what to build.
 --------------------------------------
