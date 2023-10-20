const LocalStrategy = require('passport-local').Strategy;
const bcrypt = require('bcrypt');

// Handles authentication of user by creating local strategy (username & password)
// Makes use of sessions to remember users across several routes/pages (serializing)
// Uses bcrypt to compare existing hashed password to user input (actual password is never stored)
function initialize(passport, getUserByEmail, getUserById) {
    const authenticateUser = async (email, password, done) => {
        const user = getUserByEmail(email);
        if (user == null) {
            return done(null, false, { message: "No user found with given email." });
        }

        try {
            if (await bcrypt.compare(password, user.password)) {
                return done(null, user, { message: "Logged in successfully."});
            } else {
                return done(null, false, { message: "Incorrect password entered." });
            }
        } catch (e) {
            return done(e);
        }
    };

    passport.use(new LocalStrategy({ usernameField: 'email', passwordField: 'password' }, authenticateUser));
    passport.serializeUser((user, done) => done(null, user.id));
    passport.deserializeUser((id, done) => done(null, getUserById(id)));
}

module.exports = initialize;