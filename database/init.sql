CREATE DATABASE IF NOT EXISTS fb_scraper;
USE fb_scraper;

CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(36) PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS scraping_tasks (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    keywords TEXT NOT NULL,
    locations TEXT NOT NULL,
    max_results INT DEFAULT 50,
    status VARCHAR(20) DEFAULT 'pending',
    results JSON,
    csv_path VARCHAR(255),
    total_whatsapp_links INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_tasks_user_id ON scraping_tasks(user_id);
CREATE INDEX idx_tasks_status ON scraping_tasks(status);