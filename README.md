# 🎨 Rakshak Frontend

## Overview

The Rakshak Frontend provides the user interface for the **AI-Powered Mule Account & Fraud Intelligence Platform** developed for the **Bank of India Hackathon 2026**.

It serves as the primary interaction layer for investigators, analysts, and banking personnel to monitor suspicious activities, explore fraud insights, and navigate the platform.

---

## Frontend Structure

```text
frontend/
└── rakshak/
    ├── app.js
    ├── index.html
    ├── organization.html
    ├── profile.html
    └── styles.css
```

---

## Files Description

### `index.html`

The main entry point of the Rakshak frontend.

**Responsibilities:**

* Landing page of the application
* Navigation between modules
* Displays the primary dashboard interface
* Provides access to organization and profile sections

---

### `app.js`

Contains the application's client-side logic.

**Responsibilities:**

* Handles user interactions
* Controls navigation behavior
* Updates dynamic UI components
* Processes frontend events
* Manages dashboard functionality

---

### `organization.html`

Displays information related to the organization and project.

**Responsibilities:**

* Project overview
* Team information
* Organizational details
* Mission and objectives of Rakshak

---

### `profile.html`

Provides user-specific information.

**Responsibilities:**

* User profile details
* Investigator information
* Account-related views
* Personalized interface elements

---

### `styles.css`

Contains the styling definitions for the entire frontend.

**Responsibilities:**

* Layout and responsiveness
* Typography and color themes
* Component styling
* Navigation design
* Consistent user experience

---

## Features

### Dashboard Interface

* Clean and intuitive layout
* Easy navigation across modules
* Responsive design principles

### User Profile Management

* Dedicated profile page
* Investigator information display

### Organization Module

* Project and team information
* Platform objectives

### Dynamic Interactions

* JavaScript-driven user experience
* Event handling and UI updates

---

## Technologies Used

* HTML5
* CSS3
* JavaScript (ES6)

---

## Running the Frontend

### Option 1: Open Directly

Navigate to the frontend directory and open:

```bash
frontend/rakshak/index.html
```

in your preferred web browser.

---

### Option 2: Run Using Python HTTP Server

From the `frontend/rakshak` directory:

```bash
python -m http.server 5500
```

Open your browser and visit:

```text
http://localhost:5500
```

---

## Navigation Flow

```text
index.html
   ├── organization.html
   └── profile.html
```

The application begins at the dashboard (`index.html`) and allows users to navigate to the organization and profile sections.

---

## Future Enhancements

* Real-time fraud monitoring dashboard
* API integration with FastAPI backend
* Live transaction alerts
* Risk scoring visualizations
* Graph-based mule network visualization
* Explainable AI insights
* Authentication and role-based access control
* Responsive mobile experience

---

## Frontend Team Responsibilities

### Developer A

* Dashboard implementation
* Main navigation
* UI components

### Developer B

* Organization and profile modules
* Styling and user experience improvements
* Frontend enhancements

---

## Rakshak Vision

Rakshak aims to provide an intuitive and powerful interface that enables banking professionals to monitor fraud activity, investigate suspicious behavior, and take informed action through intelligent visual experiences.

**"Visualize. Investigate. Protect."**
