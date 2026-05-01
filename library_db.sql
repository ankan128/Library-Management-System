CREATE DATABASE Library_DB;
USE Library_DB;



CREATE TABLE Books(
  book_ID INT PRIMARY KEY,
  title VARCHAR(50),
  author VARCHAR(50),
  quantity INT,
  is_available BOOLEAN
);
INSERT INTO Books VALUES 
(5001, "QUANTITIVE APTITUDE", "R.S.AGARWAL", 10, TRUE),
(5002, "REASONING & VERBAL ABILITY", "R.S.AGARWAL", 10, TRUE),
(5003, "Discrete Mathematics", "KENNETH ROZEN", 1, TRUE),
(5004, "Operating systems", "GALVIN", 10, TRUE),
(5005, "Object Oriented Programming", "Robert Lafore", 10, TRUE),
(5006, "DBMS", "KORTH", 10, TRUE),
(5007, "FORMAL LANGUAGE OF AUTOMATA THEORY", "J.C RICKELTON", 10, TRUE),
(5008, "COMPILER DESIGN", "ROSER CHEF", 10, TRUE),
(5009, "DESIGN ANALYSIS OF ALGORITHMS", "GORKI", 10, TRUE),
(5010, "DATA STRUCTURES AND ALGORITHMS", "NARASIMHA KARUMANCHI", 10, TRUE);



CREATE TABLE Users(
  user_ID INT PRIMARY KEY,
  password VARCHAR(50),
  name VARCHAR(50),
  department VARCHAR(50),
  is_admin BOOLEAN
);
INSERT INTO Users VALUES
(11900221, "anirban@123", "Anirban", "IT", FALSE),
(11900222, "abhishek@123", "Abhishek", "IT", FALSE),
(11900223, "ankan@123", "Ankan", "IT", FALSE),
(11900224, "annesha@123", "Annesha", "IT", FALSE),
(11900225, "ayush@123", "Ayush", "IT", FALSE),
(11900226, "bedarshi@123", "Bedarshi", "IT", FALSE),
(11900227, "harsh@123", "Harsh", "IT", FALSE),
(11900228, "rupkatha@123", "Rupkatha", "IT", FALSE),
(11900229, "masuddar@123", "Masuddar", "IT", FALSE),
(101, "pinaki@123", "Pinaki", "LIBRARY", TRUE);



CREATE TABLE Issue(
  issue_ID INT PRIMARY KEY AUTO_INCREMENT,
  book_id INT,
  user_id INT,
  issue_date DATE,
  return_date DATE,
  FOREIGN KEY (book_id) REFERENCES Books(book_ID),
  FOREIGN KEY (user_id) REFERENCES Users(user_ID)
);
INSERT INTO Issue (book_id, user_id, issue_date, return_date) VALUES 
(5001, 11900221, CURDATE(), NULL),
(5002, 11900223, CURDATE(), NULL),
(5004, 11900222, CURDATE(), NULL),
(5005, 11900224, CURDATE(), NULL),
(5008, 11900225, CURDATE(), NULL),
(5004, 11900225, CURDATE(), NULL),
(5005, 11900227, CURDATE(), NULL);