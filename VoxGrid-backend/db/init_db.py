import mysql.connector

# DB CONNECTION
con = mysql.connector.connect(host="localhost", user="root", password="1234567890")

cursor = con.cursor()

# CREATE DATABASE
cursor.execute("CREATE DATABASE IF NOT EXISTS vox_grid")
cursor.execute("USE vox_grid")

# USERS
cursor.execute("""
CREATE TABLE users (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(100),
  email VARCHAR(100) UNIQUE,
  password VARCHAR(255),
  avatar_url TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# CATEGORIES
cursor.execute("""
CREATE TABLE IF NOT EXISTS categories (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(50)
)
""")

# ISSUES
cursor.execute("""
CREATE TABLE IF NOT EXISTS issues (
  id INT PRIMARY KEY AUTO_INCREMENT,
  title VARCHAR(255),
  summary TEXT,
  category_id INT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  FOREIGN KEY (category_id) REFERENCES categories(id)
)
""")

# DISCUSSIONS
cursor.execute("""
CREATE TABLE IF NOT EXISTS discussions (
  id INT PRIMARY KEY AUTO_INCREMENT,
  issue_id INT,
  user_id INT,
  title VARCHAR(255),
  content TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  FOREIGN KEY (issue_id) REFERENCES issues(id),
  FOREIGN KEY (user_id) REFERENCES users(id)
)
""")

# COMMENTS
cursor.execute("""
CREATE TABLE IF NOT EXISTS comments (
  id INT PRIMARY KEY AUTO_INCREMENT,
  discussion_id INT,
  user_id INT,
  content TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  FOREIGN KEY (discussion_id) REFERENCES discussions(id),
  FOREIGN KEY (user_id) REFERENCES users(id)
)
""")


# POLLS
cursor.execute("""
CREATE TABLE IF NOT EXISTS polls (
  id INT PRIMARY KEY AUTO_INCREMENT,
  issue_id INT,
  question TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  FOREIGN KEY (issue_id) REFERENCES issues(id)
)
""")

# POLL OPTIONS
cursor.execute("""
CREATE TABLE IF NOT EXISTS poll_options (
  id INT PRIMARY KEY AUTO_INCREMENT,
  poll_id INT,
  option_text TEXT,

  FOREIGN KEY (poll_id) REFERENCES polls(id)
)
""")

# POLL VOTES
cursor.execute("""
CREATE TABLE IF NOT EXISTS poll_votes (
  id INT PRIMARY KEY AUTO_INCREMENT,
  poll_id INT,
  option_id INT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  FOREIGN KEY (poll_id) REFERENCES polls(id),
  FOREIGN KEY (option_id) REFERENCES poll_options(id)
)
""")

# VOTES (DISCUSSIONS + COMMENTS)
cursor.execute("""
CREATE TABLE IF NOT EXISTS votes (
  id INT PRIMARY KEY AUTO_INCREMENT,
  target_type ENUM('discussion', 'comment'),
  target_id INT,
  vote_type ENUM('agree', 'disagree')
)
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS blogs (
  id INT PRIMARY KEY AUTO_INCREMENT,

  issue_id INT,
  user_id INT,

  title VARCHAR(255),
  content LONGTEXT,

  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  FOREIGN KEY (issue_id) REFERENCES issues(id),
  FOREIGN KEY (user_id) REFERENCES users(id)
);
""")

con.commit()
cursor.close()
con.close()

print("Done")
