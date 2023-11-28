require('dotenv').config();
const express = require('express');
const passport = require('passport');
const flash = require('express-flash');
const session = require('express-session');
const multer = require('multer');
const path = require('path');
const mongoose = require('mongoose');
const User = require('./models/user');
const LocalStrategy = require('passport-local').Strategy;
const fetch = require('node-fetch');
const fs = require('fs');
const FormData = require('form-data');

const app = express();
app.use(express.json());

const db_URI = process.env.MONGODB_URI;
mongoose.connect(db_URI);

const storage = multer.memoryStorage();
const upload = multer({ storage: storage });

// Functionality to support HTML pages to test the program
app.set('view-engine', 'ejs');
app.use(express.urlencoded({ extended: false}));

app.use(flash());
app.use(session({
    secret: 'secret',
    resave: false,
    saveUninitialized: false
}));

app.use(passport.initialize());
app.use(passport.session());

passport.use(new LocalStrategy({ usernameField: 'email' }, User.authenticate()));
passport.serializeUser(User.serializeUser());
passport.deserializeUser(User.deserializeUser());


// GET home route, must be logged in to view
app.get('/', checkAuthenticated, (req, res) => {
    res.render('index.ejs', { name: req.user.name, uploadedImage: false});
});

// POST home route to save an user-uploaded image
app.post('/', checkAuthenticated, upload.single('image'), async (req, res) => {
    const formData = new FormData();
    formData.append('file', req.file.buffer, {
        filename: req.file.originalname,
        contentType: req.file.mimetype
    });
    const response = await fetch('http://54.163.41.212:5000/predict', {
        method: 'POST',
        body: formData,
    });
    const data = await response.json();
    console.log(data.prediction);
    res.render('index.ejs', { name: req.user.name, uploadedImage: true});
});

// GET register route to view register form
app.get('/register', checkNotAuthenticated, (req, res) => {
    res.render('register.ejs');
});

// GET login route to view login form
app.get('/login', checkNotAuthenticated, (req, res) => {
    res.render('login.ejs');
});

// POST register route to create new user (password is  hashed using bcrypt)
app.post('/register', checkNotAuthenticated, (req, res) => {
    User.register(
        new User({
            name: req.body.name,
            email: req.body.email
        }), 
        req.body.password,
        (err, user) => {
            if (err) {
                console.log(err);
                res.redirect('/register');
            } else {
                res.redirect('/login');
            }
        }
    );
});

// POST login route to login existing user, passport.js handles this using sessions
app.post('/login', checkNotAuthenticated, passport.authenticate('local', {
    successRedirect: '/',
    failureRedirect: '/login',
    failureFlash: true,
}));

// POST logout route to logout existing user, passport.js handles this (like above)
app.post('/logout', checkAuthenticated, (req, res, next) => {
    req.logout(function(err) {
        if (err) { return next(err); }
        res.redirect('/');
    });
});

// Check if a user is already authenticated (limits which pages a user can view)
function checkAuthenticated(req, res, next) {
    if (req.isAuthenticated()) {
        return next();
    }

    res.redirect('/login');
}

// Check if a user is not authenticated (limits which pages a user can view)
function checkNotAuthenticated(req, res, next) {
    if (req.isAuthenticated()) {
        return res.redirect('/');
    }

    next();
}

const port = process.env.PORT || 3000;
app.listen(port, () => console.log(`Listening on port ${port}...`));