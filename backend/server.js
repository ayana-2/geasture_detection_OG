const express = require('express');
const bcrypt = require('bcryptjs');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());
app.use(express.static(__dirname));
app.use(express.urlencoded({ extended: true }));

// Database setup
const db = new sqlite3.Database('./database.db');

// Create users table
db.serialize(() => {
    db.run(`CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )`);
    
    // Insert a demo user (username: demo, password: demo123)
    const demoPassword = bcrypt.hashSync('demo123', 10);
    db.run(`INSERT OR IGNORE INTO users (username, email, password) 
            VALUES (?, ?, ?)`, 
            ['demo', 'demo@example.com', demoPassword]);
});

// Login API endpoint
app.post('/api/login', (req, res) => {
    const { username, password } = req.body;
    
    if (!username || !password) {
        return res.status(400).json({ 
            success: false, 
            message: 'Username and password required' 
        });
    }
    
    // Check if user exists
    db.get('SELECT * FROM users WHERE username = ? OR email = ?', 
           [username, username], (err, user) => {
        if (err) {
            return res.status(500).json({ 
                success: false, 
                message: 'Server error' 
            });
        }
        
        if (!user) {
            return res.status(401).json({ 
                success: false, 
                message: 'Invalid credentials' 
            });
        }
        
        // Compare passwords
        bcrypt.compare(password, user.password, (err, isMatch) => {
            if (err || !isMatch) {
                return res.status(401).json({ 
                    success: false, 
                    message: 'Invalid credentials' 
                });
            }
            
            // Login successful
            res.json({ 
                success: true, 
                message: 'Login successful',
                user: { id: user.id, username: user.username }
            });
        });
    });
});

// Register API endpoint (optional)
app.post('/api/register', (req, res) => {
    const { username, email, password } = req.body;
    
    if (!username || !email || !password) {
        return res.status(400).json({ 
            success: false, 
            message: 'All fields required' 
        });
    }
    
    // Hash password
    bcrypt.hash(password, 10, (err, hashedPassword) => {
        if (err) {
            return res.status(500).json({ 
                success: false, 
                message: 'Server error' 
            });
        }
        
        // Insert new user
        db.run('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
               [username, email, hashedPassword], function(err) {
            if (err) {
                return res.status(400).json({ 
                    success: false, 
                    message: 'Username or email already exists' 
                });
            }
            
            res.json({ 
                success: true, 
                message: 'Registration successful',
                userId: this.lastID 
            });
        });
    });
});

// Serve HTML files
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'login.html'));
});

app.get('/detection', (req, res) => {
    res.sendFile(path.join(__dirname, 'detection.html'));
});

// Start server
app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
    console.log(`Demo credentials: username: demo, password: demo123`);
});