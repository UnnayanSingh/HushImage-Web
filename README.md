# 🖼️ HushImage-Web (with Python + Flask + MySQL)

This is a full-featured web application that lets users securely **hide and reveal messages inside images using steganography**, along with secure login, password encryption, and download/export features.

---

## 🚀 Features
- User authentication (Login/Register)
- AES encryption with image steganography
- Hide messages in PNG images
- Auto-delete original upload for storage security
- Reveal secret message using password
- User history with image previews
- Export history as CSV or PDF
- Change password functionality
- Dark mode toggle for better UX  

---

## 📂 Tech Stack

- **Frontend**: HTML, Bootstrap 5
- **Backend**: Flask (Python)
- **Database**: MySQL
- **Security**: Password Hashing (`werkzeug`), AES (optional in future)
- **Libraries**: 
  - `MySQLdb`
  - `reportlab`
  - `Pillow`
  - `markupsafe`
  - `stegano` (for LSB hiding)

---

## 🖥️ How to Run Locally

1. **Clone the repo** or download files:

```bash
git clone https://github.com/your-username/image-steganography-flask
cd image-steganography-flask
```

2. **Install dependencies:**

```pip install flask mysqlclient pillow reportlab```


3. **Setup MySQL Database:**
```CREATE DATABASE steganography_app;
USE steganography_app;

CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL
);

CREATE TABLE messages (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT,
  encrypted_msg TEXT,
  image_path VARCHAR(500),
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);
```

4. **Set config in config.py:**
```MYSQL_HOST = 'localhost'
  MYSQL_USER = 'root'
  MYSQL_PASSWORD = 'your_mysql_password'
  MYSQL_DB = 'steganography_app'
  SECRET_KEY = 'your_secret_key_here'
```

5. **Run the app:**
  ```
  python app.py

```

---

## 🛡️ Security Notes
- All passwords are securely hashed before storage
- Uploaded images are auto-deleted after use
- Message size should not exceed the capacity of the image
- This project is intended for educational purposes

---

## 👨‍💻 Author
- [![GitHub](https://img.shields.io/badge/GitHub-000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/UnnayanSingh)
- [![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/unnayan-singh-2b9062289)
- [![Gmail](https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:unnayansingh2005@gmail.com)  

---
