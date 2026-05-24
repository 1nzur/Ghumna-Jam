# Ghumna Jam Trek Booking

A small trek booking page with a Python Flask backend and MySQL database.

## 1. Create the MySQL database

Do not run SQL commands directly in Bash, Git Bash, PowerShell, or CMD. They must be run inside MySQL.

If you are using MySQL Workbench, phpMyAdmin, XAMPP, or another SQL editor, paste and run the contents of `schema.sql` directly:

```sql
CREATE DATABASE IF NOT EXISTS `ghumna_jam`
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE `ghumna_jam`;

CREATE TABLE IF NOT EXISTS `bookings` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `full_name` VARCHAR(120) NOT NULL,
  `email` VARCHAR(160) NOT NULL,
  `trek` VARCHAR(80) NOT NULL,
  `preferred_date` DATE NOT NULL,
  `people` INT NOT NULL,
  `message` TEXT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

If you want to use Bash or a terminal, first log in to MySQL:

```bash
mysql -u root -p
```

After you type your MySQL password, your prompt should look like this:

```text
mysql>
```

Only then run this command, and only if your terminal was opened in this project folder:

```sql
SOURCE schema.sql;
```

Another terminal option is to run the file without entering the MySQL prompt:

```bash
mysql -u root -p < schema.sql
```

## 2. Create a virtual environment

```bash
python -m venv .venv
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

## 3. Install Python packages

```bash
pip install -r requirements.txt
```

## 4. Set database details

Create a `.env` file from `.env.example`, then set your MySQL username and password.

PowerShell example:

```powershell
$env:DB_HOST="localhost"
$env:DB_USER="root"
$env:DB_PASSWORD="your_mysql_password"
$env:DB_NAME="ghumna_jam"
```

## 5. Run the project

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

When the form submits, Flask receives the request at `/api/bookings` and stores it in the MySQL `bookings` table.

## 6. Push to GitHub

Create a new empty GitHub repository first. Then run these commands from this project folder:

```bash
git init
git add .
git commit -m "Create trek booking app with MySQL backend"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git
git push -u origin main
```

Do not commit your real `.env` file. It is ignored by `.gitignore`; use `.env.example` to show which settings are needed.
