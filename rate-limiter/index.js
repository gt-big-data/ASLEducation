const express = require('express');
const app = express();
app.use(express.json());

// Rate limiter functionality (uses IP address)
const rateLimit = require('express-rate-limit');

const limiter = rateLimit({
    windowMs: 1 * 1000,         // 1000 ms = 1 second
    max: 1,                     // 1 request / window 
    message: "You have been rate limited (1 hit / sec).",
    standardHeaders: true,
    legacyHeaders: false,
});

// Makes default path use limiter, can modify path(s)
app.use('/', limiter); 

// Testing endpoint, can add more endpoints as needed
app.get('/', (req, res) => {
    res.send('Hello World!');
}); 

const port = process.env.PORT || 3000;
app.listen(port, () => console.log(`Listening on port ${port}...`));