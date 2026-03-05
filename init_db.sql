-- Create the database
CREATE DATABASE IF NOT EXISTS campus_ai;
USE campus_ai;

-- Clear any existing tables for a clean slate
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS admins;
SET FOREIGN_KEY_CHECKS = 1;

-- Correctly formatted students table
CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'student',
    marks FLOAT DEFAULT 0.0,
    attendance FLOAT DEFAULT 0.0,
    INDEX email_idx (email) -- Removed the extra parentheses that caused your error
);

-- Correctly formatted admins table
CREATE TABLE admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'admin',
    INDEX admin_email_idx (email)
);

-- viewing student table
select * from students;

-- viewing admins table
select * from admins;
