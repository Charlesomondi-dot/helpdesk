# STJTID Institute IT Helpdesk System

A complete IT helpdesk ticketing system built with Flask, designed to run on your local network.

## Features

✅ **User Authentication** - Secure registration and login system
✅ **Ticket Submission** - Users can submit support tickets with categories and priority levels
✅ **Ticket Tracking** - Real-time tracking of ticket status and updates
✅ **Admin Dashboard** - Staff members can manage tickets and monitor system statistics
✅ **Messaging System** - Two-way communication between users and IT support staff
✅ **Responsive Design** - Works on desktop, tablet, and mobile devices
✅ **Local Network Support** - Accessible to any device on your network

## System Requirements

- Python 3.8 or higher
- Windows/Mac/Linux OS
- 500MB of disk space

## Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Initial Setup

Run the Flask app for the first time to create the database:

```bash
python app.py
```

The database file `helpdesk.db` will be created automatically.

### 3. Admin Login

The app creates a default system admin account automatically on startup.

Configure the admin account with environment variables before starting the app.
See [.env.example](.env.example) for the available settings. Never commit your
local `.env` file or real credentials.

- `ADMIN_USERNAME`
- `ADMIN_EMAIL`
- `ADMIN_PASSWORD`

If an account with the same username already exists, the app will mark it as staff.

## Running the Application

### Local Machine
```bash
python app.py
```
Access at: `http://localhost:5000`

### Local Network
The app is configured to run on `0.0.0.0:5000`, making it accessible from any computer on your network.

Find your computer's local IP address:
- **Windows**: Open Command Prompt and run `ipconfig` (look for IPv4 Address)
- **Mac/Linux**: Open Terminal and run `ifconfig` (look for inet)

Then access from another device using: `http://YOUR_IP_ADDRESS:5000`

Example: `http://192.168.1.100:5000`

## Default Structure

```
IT HELPDESK/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── helpdesk.db          # SQLite database (created on first run)
├── templates/           # HTML templates
│   ├── base.html        # Base template
│   ├── index.html       # Homepage
│   ├── login.html       # Login page
│   ├── register.html    # Registration page
│   ├── submit_ticket.html
│   ├── my_tickets.html
│   ├── ticket_detail.html
│   ├── admin_dashboard.html
│   ├── admin_tickets.html
│   └── admin_users.html
└── static/              # Static files
    ├── css/
    │   └── style.css    # Main stylesheet
    └── js/
        └── main.js      # JavaScript utilities
```

## User Roles

### Regular User
- Submit support tickets
- Track ticket status
- Communicate with support staff via messages
- View ticket history

### Staff/Admin
- Access admin dashboard
- View all tickets
- Manage ticket status and priority
- Assign responses to tickets
- Monitor system statistics
- Manage user accounts

## Features Guide

### Submitting a Ticket
1. Register and login with your account
2. Click "Submit Ticket"
3. Fill in the form with:
   - Subject (brief title)
   - Category (type of issue)
   - Priority (low/normal/high)
   - Description (detailed explanation)
4. Click "Submit Ticket"

### Tracking Tickets
1. Login to your account
2. Click "My Tickets" to see all your submissions
3. Click on any ticket to view details and messages

### Admin Tasks
1. Login with staff account
2. Click "Admin Dashboard"
3. View statistics and recent tickets
4. Click "Manage Tickets" to work on open issues
5. Update status, priority, and add responses

## Security Notes

⚠️ **Important for Production:**
- Set `SECRET_KEY` to a long random string
- Use environment variables for sensitive configuration
- Set `debug=False` when running in production
- Use HTTPS instead of HTTP
- Implement rate limiting
- Add proper backup strategy for the database

## Troubleshooting

### Port Already in Use
If port 5000 is already in use, modify the last line in `app.py`:
```python
app.run(host='0.0.0.0', port=8000, debug=True)  # Change 5000 to 8000
```

### Database Issues
If the database gets corrupted, delete `helpdesk.db` and run the app again to recreate it.

### Cannot Access from Other Devices
1. Ensure both devices are on the same network
2. Check Windows Firewall settings (allow Python)
3. Use the correct IP address from `ipconfig`
4. Verify port 5000 is not blocked

## Support Categories

- **Accounts & Passwords** - Login issues, password resets
- **Hardware & Devices** - Computer, printer, phone problems
- **Network & Wi-Fi** - Connectivity issues, VPN problems
- **Learning Systems** - LMS, portal access
- **Printing & Scanning** - Printer and copier issues
- **Software Support** - Application issues, Office 365

## Default Response Time

Standard support requests: **4 hours** during normal campus operating hours

## License

© 2026 STJTID Institute. All rights reserved.

## Contact

For setup assistance or questions, contact your IT department.

---

**Version**: 1.0.0  
**Last Updated**: 2026-06-28
