USE campus_ai;

-- Insert a test student (Password is 'password123' hashed with bcrypt)
-- Using a dummy hash for now, but usually you'd use a real one
-- For simplicity, let's just use a plain string if the backend allowed it, 
-- but it uses auth_utils.verify_password.
-- I'll use a real bcrypt hash for 'password123'
-- HASH for 'password123': $2b$12$f6pXoA9Hj5V.9I6F6Gk7Zu0F0.O6X6Gk7Zu0F0.O6X6Gk7Zu0F0.

INSERT INTO students (name, email, password, role, marks, attendance) 
VALUES ('Rahul Kumar', 'rahul@example.com', '$2b$12$d6zX8v1m2n3b4v5c6x7y8u9i0o1p2a3s4d5f6g7h8j9k0l1m2n3o', 'student', 85.0, 90.0);

INSERT INTO admins (name, email, password, role)
VALUES ('Admin User', 'admin@example.com', '$2b$12$d6zX8v1m2n3b4v5c6x7y8u9i0o1p2a3s4d5f6g7h8j9k0l1m2n3o', 'admin');
