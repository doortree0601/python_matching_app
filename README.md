# The Matchi App

## Section 1 - Database Structure

A relational database was developed for this project. The scheme can be accessed here: https://app.quickdatabasediagrams.com/#/d/QvkzNp

The basic design principle is to minimize interactions with the database unless absolutely necessary. This is designed with real-world applications in mind, where connections to databases can be expensive. We work primarily with objects in our program. 

The decision to work with relational database is rooted in the design decision to minimize string manipulation, thus speeding up querying and database updates. For example, if a user removes a liked user, that row will be deleted from the database. No further database updates will need to be made. 

Each user's basic information is stored in the *user* table. This table has one-to-many relationships with the rest of the tables in the database, where a user can have multiple interests, liked users, matches, etc. 

The program will interact with the database when:
  1. A user is created;
  2. User information is updated;
  3. A user likes or dislikes another user;
  4. A match is made; and
  5. A user views their own profile.

### Sample Database

A sample database with fake names, created using the *faker* library, is available in this repo for testing purpose.
