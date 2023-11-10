require('dotenv').config();
const express = require('express');
const bcrypt = require('bcrypt');
const passport = require('passport');
const flash = require('express-flash');
const session = require('express-session');
const mongoose = require('mongoose');
const User = require('./models/user');
const LocalStrategy = require('passport-local').Strategy;

const app = express();
app.use(express.json());

const db_URI = process.env.MONGODB_URI;
mongoose.connect(db_URI)
    .then(() => console.log("connected to db"));

// Functionality to support HTML pages to test the program
app.set('view-engine', 'ejs');
app.use(express.urlencoded({ extended: false}));

app.use(flash());
app.use(session({
    secret: process.env.SESSION_SECRET,
    resave: true,
    saveUninitialized: true
}));

app.use(passport.initialize());
app.use(passport.session());

passport.use(new LocalStrategy({ usernameField: 'email' }, User.authenticate()));
passport.serializeUser(User.serializeUser());
passport.deserializeUser(User.deserializeUser());

// GET home route, must be logged in to view
app.get('/', checkAuthenticated, (req, res) => {
    res.render('index.ejs', { name: req.user.name});
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