# Starting the Frontend Server on Port 3000

## If Port 3000 is Already in Use

If you see an error that port 3000 is already in use, you have two options:

### Option 1: Stop the Existing Process (Recommended)

1. **Find the process using port 3000:**
   ```powershell
   netstat -ano | findstr :3000
   ```
   Note the PID (Process ID) in the last column.

2. **Kill that process:**
   ```powershell
   taskkill /PID <PID_NUMBER> /F
   ```
   Replace `<PID_NUMBER>` with the actual PID from step 1.

3. **Then start the server:**
   ```powershell
   cd COSC310\fullstack_project\frontend
   npm run dev
   ```

### Option 2: Use a Different Port

If you want to keep the existing process running, you can modify `package.json` to use a different port (e.g., 3001):

```json
"dev": "next dev --turbopack -p 3001"
```

## Starting the Server

The server is configured to run on port 3000. To start it:

```powershell
cd COSC310\fullstack_project\frontend
npm run dev
```

You should see output like:
```
▲ Next.js 15.5.6
- Local:        http://localhost:3000
- Ready in X seconds
```

## Troubleshooting

### Server won't start
- Make sure you're in the `frontend` directory
- Check that `node_modules` exists (run `npm install` if needed)
- Verify Node.js is installed: `node --version`

### Port 3000 is busy
- Follow Option 1 above to stop the existing process
- Or check what's using it: `netstat -ano | findstr :3000`

### Server starts but page won't load
- Check browser console for errors
- Verify the backend is running on port 8000
- Check CORS settings in FastAPI backend

