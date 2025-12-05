# Library Management System

**Team Members**: Gabriel Unigwe, Ahab Siddiqui, Hakim Rashid, Daniel Ogundare

## What is this?

**_"TheDebuggers Library"_** is a library management system built to help manage book reservations, track overdue items, and handle penalties. Think of it as a system that makes running a library easier - from checking out books to tracking who owes fines.

### What can it do?

- **Track Books**: See what's checked out, what's overdue, and what people have reserved
- **Manage Users**: Add users, delete them, see who's active in the system
- **Handle Penalties**: Automatically flag users with overdue books or unpaid fines
- **See What's Happening**: Dashboard with charts showing popular books, trends, and user activity
- **Admin Dashboard**: One place to manage everything - loans, penalties, users, all the data
- **Checkout System**: Users can confirm their checkouts and get receipts

---

## Before You Start

You'll need:

- **Computer Memory**: At least 8GB RAM (more is better for production)
- **Disk Space**: About 20GB free
- **Internet**: To download things initially
- **Docker**: The containerization tool (we'll show you how to get it)

---

## Getting Started

### Step 1: Install Docker

Docker is a container that holds all our code and dependencies so it runs the same way everywhere.

**For Windows or Mac:**
1. Go to https://www.docker.com/products/docker-desktop
2. Download Docker Desktop
3. Install it and restart your computer
4. Open a terminal and check it worked:
   ```bash
   docker --version
   docker-compose --version
   ```

**For Linux:**
```bash
sudo apt-get update
sudo apt-get install docker.io docker-compose
sudo usermod -aG docker $USER
newgrp docker
```

### Step 2: Get the Code

```bash
git clone https://github.com/UBCDebuggers/COSC310.git
cd COSC310
```

### Step 3: Start Everything

```bash
docker-compose up --build
```

This command builds the Docker images and starts all the services. You'll see a bunch of text scrolling - that's normal.

### Step 4: Open It Up

Once you see "Application startup complete" in the logs, open your browser and go to:

- **Frontend**: http://localhost:3000 (the user-facing website)
- **Backend**: http://localhost:8000 (the API)
- **API Documentation**: http://localhost:8000/docs (helpful reference)

---

## Login Info

Here are the test accounts that come with the system:

| Role  | Email | Password       |
|-------|-------|----------------|
| Admin | admin | check document |
| User  | test  | check document |

---

## Common Commands

### Start the system
```bash
# See all the logs in your terminal
docker-compose up

# Run it in the background
docker-compose up -d

# Rebuild everything from scratch
docker-compose up --build
```

### Stop the system
```bash
# Stop everything
docker-compose down

# Stop and delete everything (this deletes your data!)
docker-compose down -v
```

### Check what's happening
```bash
# See all logs from both backend and frontend
docker-compose logs

# Follow backend logs as they happen
docker-compose logs -f backend

# Follow frontend logs
docker-compose logs -f frontend
```

### Restart things
```bash
# Restart everything
docker-compose restart

# Just restart the backend
docker-compose restart backend
```

---

## What's Under the Hood

**Backend**: FastAPI (Python) running on port 8000
- FastAPI (the web framework)
- Uvicorn (serves the API)
- bcrypt (hashes passwords)
- PyJWT (handles login tokens)

**Frontend**: Next.js (React) running on port 3000
- Next.js 15.5.6
- Chakra UI (makes things look nice)
- Recharts (draws those charts on the dashboard)
- Axios (talks to the backend)

**Data**: We're using CSV files to store everything (users, loans, penalties, etc.)

---

## Where's the Data?

All the data files are in:
```
fullstack_project/backend/app/data/
```

This includes:
- `users.csv` - All the user accounts
- `book_reservations.csv` - Who has what book and when it's due
- `penalties.csv` - Who owes fines or is banned
- `ratings.csv` - Book ratings and reviews
- `analytics.csv` - Historical data about library usage

### Backing Up Your Data

Make a copy of these files regularly:

```bash
# Create a backup folder with today's date
cp -r fullstack_project/backend/app/data/ backup/data_$(date +%Y%m%d)
```

If something goes wrong, you can restore from backup:
```bash
cp backup/data_YYYYMMDD/* fullstack_project/backend/app/data/
docker-compose restart backend
```

---

## User Accounts

### Adding New Admins

1. Log in as the admin user
2. Go to user management
3. Create a new account and make them an admin
4. Once that's done, you can delete or disable the default admin account

### Changing Passwords

1. Log in to your account
2. Click account settings
3. Update your password

Make passwords strong - mix uppercase, lowercase, numbers, and special characters. Aim for at least 12 characters.

---

## Keeping the System Running

### Every Day
- Check the logs for errors: `docker-compose logs`
- Make sure you can access http://localhost:3000
- Make sure the API is responding at http://localhost:8000/docs

### Every Week
- Look at who's using the system
- Check if anyone has penalties that are about to expire
- Make a backup of the data
- Make sure you have enough disk space

### Every Month
- Review who has access to the system
- Look at how the system is performing
- Test that your backups actually work
- Update any dependencies if there are security patches

---

## Troubleshooting

### Port 3000 or 8000 is already in use

Something else is using that port. Find it and kill it:

```bash
# On Windows
netstat -ano | findstr :3000

# On Mac/Linux
lsof -i :3000
```

Then stop that process. If you're on Windows, use `taskkill /PID [number] /F`. On Mac/Linux, use `kill -9 [number]`.

### Docker container won't start

Check what went wrong:
```bash
docker-compose logs backend
```

Usually just rebuild and try again:
```bash
docker-compose down
docker-compose up --build
```

### Backend is running but frontend can't connect

Make sure the backend is actually working:
```bash
curl http://localhost:8000/docs
```

If that works, try restarting the backend:
```bash
docker-compose restart backend
```

### System is using too much memory

- Make sure Docker has at least 8GB RAM allocated (check Docker Desktop settings)
- Close some browser tabs
- Restart the containers

---

## Main API Endpoints

These are the endpoints your frontend hits to get data:

### Logging in
- `POST /auth/login` - Send username and password, get a token back

### Users
- `GET /users/getall` - Get a list of all users (admin only)
- `GET /users/get/{id}` - Get info about a specific user
- `POST /users/create` - Create a new user (admin only)

### Library stuff
- `GET /library/outstandingloans` - What books are currently checked out
- `GET /library/activepenalties?userid={id}` - What penalties a user has
- `GET /library/userloans?userid={id}` - What books a user has checked out
- `POST /library/createpenalty` - Add a penalty for a user (admin only)

### Analytics
- `GET /analytics/genre` - Break down loans by genre
- `GET /analytics/trending` - What books are popular

For the full list, check http://localhost:8000/docs when the system is running.

---

## Project Structure

```
COSC310/
├── docker-compose.yml          # Docker setup file
├── README.md                    # This file
├── LICENSE                      
└── fullstack_project/
    ├── backend/                 # The API code
    │   ├── Dockerfile
    │   ├── requirements.txt      # Python packages we need
    │   ├── app/
    │   │   ├── main.py
    │   │   ├── routers/         # API endpoints
    │   │   ├── services/        # Business logic
    │   │   ├── schemas/         # Data models
    │   │   ├── core/            # Security stuff
    │   │   └── data/            # Where CSV files live
    │   ├── UnitTesting/
    │   └── IntegrationTesting/
    │
    └── frontend/                # The website code
        ├── Dockerfile
        ├── package.json         # Node packages we need
        ├── next.config.mjs
        └── src/app/
            ├── dashboard/       # Regular user dashboard
            ├── admindashboard/  # Admin dashboard
            └── penaltymanagement/ # Where admins manage penalties
```

---

## Helpful Links

- **When the system is running**, check out http://localhost:8000/docs for the full API documentation
- **FastAPI docs**: https://fastapi.tiangolo.com/
- **Next.js docs**: https://nextjs.org/docs
- **Docker docs**: https://docs.docker.com/
- **This project on GitHub**: https://github.com/UBCDebuggers/COSC310

---

## Version & Status

- **Version**: 1.0.0
- **Last Updated**: December 5, 2025
- **Status**: Ready to use
