CREATE DATABASE IF NOT EXISTS files_database;
CREATE DATABASE IF NOT EXISTS user_database;
CREATE DATABASE IF NOT EXISTS group_database;

# ------ FILES DATABASE ----- #
CREATE USER IF NOT EXISTS 'files'@'%' IDENTIFIED BY 'Files123!';
GRANT ALL PRIVILEGES ON files_database.* TO 'files'@'%';

# ------ USER DATABASE ----- #
CREATE USER IF NOT EXISTS 'user'@'%' IDENTIFIED BY 'User123!';
GRANT ALL PRIVILEGES ON user_database.* TO 'user'@'%';

# ------ GROUP DATABASE ----- #
CREATE USER IF NOT EXISTS 'group'@'%' IDENTIFIED BY 'Group123!';
GRANT ALL PRIVILEGES ON group_database.* TO 'group'@'%';

FLUSH PRIVILEGES;