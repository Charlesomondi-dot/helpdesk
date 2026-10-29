# 🚀 STJTID IT Helpdesk - Quick Start Guide

## ✅ Installation Complete!

Your IT Helpdesk system is ready to use!

## 🌐 Access URLs

### From This Computer
- **http://localhost:5000**
- **http://127.0.0.1:5000**

### From Other Devices on Your Network
- **http://192.168.95.83:5000** ← Use this to access from phones, tablets, or other computers

*Note: Replace `192.168.95.83` with your computer's actual IP if different*

---

## 📋 What's Included

✅ **User Authentication** - Registration and secure login
✅ **Ticket Submission** - Users can submit support requests
✅ **Ticket Tracking** - Real-time status updates
✅ **Admin Dashboard** - Complete management interface
✅ **Messaging System** - Two-way communication
✅ **Responsive Design** - Works on all devices
✅ **SQLite Database** - Automatic data persistence

---

## 🎯 First Steps

### 1. Create a User Account
1. Go to the website
2. Click "Register"
3. Fill in Username, Email, and Password
4. Click "Register"

### 2. Admin Login (for IT Staff)

The app now creates a default system admin automatically.

**Login details:**
- Set `ADMIN_USERNAME`, `ADMIN_EMAIL`, and `ADMIN_PASSWORD` before the first
  startup. Use [.env.example](.env.example) as a template.

Set these environment variables before starting the app:
- `ADMIN_USERNAME`
- `ADMIN_EMAIL`
- `ADMIN_PASSWORD`

### 3. Test the System
1. **User Account**: Submit a test ticket
2. **Admin Account**: Login to admin dashboard and manage the ticket

---

## 🎨 Service Categories

The system includes 6 main support categories:
- 🔐 Accounts & Passwords
- 💻 Hardware & Devices
- 📡 Network & Wi-Fi
- 📚 Learning Systems
- 🖨️ Printing & Scanning
- ⚙️ Software Support

---

## 📊 Ticket Priorities

Users can set ticket priority when submitting:
- **Low** - Not urgent
- **Normal** - Standard (default)
- **High** - Urgent

---

## 🔧 Ticket Statuses

Admin can manage ticket status:
- **Open** - New, unassigned ticket
- **In Progress** - Staff is working on it
- **Resolved** - Issue has been fixed

---

## 👥 User Roles

### Regular User
- Submit tickets
- Track ticket status
- View ticket history
- Add messages to own tickets

### Staff/Admin
- View all tickets
- Update ticket status & priority
- Add responses to tickets
- Monitor system statistics
- Manage user accounts
- See the admin dashboard

---

## 🛑 Stopping the Server

To stop the server, go to the terminal and press:
```
CTRL + C
```

---

## 🔄 Starting the Server Again

From the IT HELPDESK folder:

```bash
.venv\Scripts\python.exe app.py
```

Or just double-click `app.py` if you set it to run with Python.

---

## 📁 Project Files

```
IT HELPDESK/
├── app.py                 ← Main application
├── helpdesk.db           ← Database (auto-created)
├── requirements.txt      ← Python packages
├── README.md            ← Full documentation
├── templates/           ← HTML pages
│   └── [All HTML files]
└── static/              ← CSS & JavaScript
    ├── css/style.css
    └── js/main.js
```

---

## ⚠️ Important Settings to Change (For Production)

**In `app.py` (line 9):**

Change:
```python
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') or secrets.token_hex(32)
```

To something random like:
```python
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') or secrets.token_hex(32)
```

---

## 🐛 Troubleshooting

### Port 5000 Already in Use?
Edit `app.py` and change the last line:
```python
app.run(host='0.0.0.0', port=8000, debug=True)  # Change 5000 to 8000
```

### Cannot Access from Other Devices?
1. Make sure both devices are on the same WiFi network
2. Check Windows Firewall allows Python
3. Use the correct IP from the terminal output

### Database Issues?
Delete `helpdesk.db` and restart the server to recreate it.

---

## 📧 Admin Account Info

Set `ADMIN_USERNAME`, `ADMIN_EMAIL`, and `ADMIN_PASSWORD` before the first
startup. Keep the real values in your local `.env` file and use
[.env.example](.env.example) as the safe template.

---

## 🎓 Features Overview

### For Students/Staff (Regular Users)
- ✅ Register and login securely
- ✅ Submit tickets with descriptions
- ✅ Choose issue category
- ✅ Set priority level
- ✅ Track ticket status in real-time
- ✅ Communicate via messages
- ✅ View ticket history

### For IT Support (Admin Staff)
- ✅ View all open tickets
- ✅ Filter by status (open, in progress, resolved)
- ✅ Update ticket status and priority
- ✅ Add response messages
- ✅ View statistics dashboard
- ✅ Manage user accounts
- ✅ Monitor ticket volume

---

## 📞 Need Help?

1. Check the **README.md** for detailed documentation
2. Review the **How it works** section on the homepage
3. Test with a sample ticket to understand the workflow

---

## 🎉 You're Ready to Go!

Your local network IT Helpdesk is now live and ready to handle support requests!

**Current Status**: ✅ Running on http://192.168.95.83:5000

Happy ticket handling! 🎯
