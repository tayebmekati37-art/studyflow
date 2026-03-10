CREATE DATABASE studyflow CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'studyflow_user'@'localhost' IDENTIFIED BY 'strongpassword';
GRANT ALL PRIVILEGES ON studyflow.* TO 'studyflow_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;