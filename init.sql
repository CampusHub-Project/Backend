CREATE TABLE Users (
    user_id BIGINT PRIMARY KEY, 
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL, 
    department VARCHAR(100) NOT NULL,
    gender ENUM('Male', 'Female') NOT NULL, 
    role ENUM('admin', 'user', 'club_admin') DEFAULT 'user',
    profile_image VARCHAR(255),
    
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMP NULL DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE Clubs (
    club_id INT AUTO_INCREMENT PRIMARY KEY,
    club_name VARCHAR(150) NOT NULL UNIQUE, 
    description TEXT,
    logo_url VARCHAR(255),
    status ENUM('pending', 'active', 'closed', 'rejected') DEFAULT 'pending',
    president_id BIGINT,
    created_by BIGINT,
    
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMP NULL DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (president_id) REFERENCES Users(user_id) ON DELETE SET NULL,
    FOREIGN KEY (created_by) REFERENCES Users(user_id) ON DELETE SET NULL
);

CREATE TABLE ClubFollowers (
    follow_id INT AUTO_INCREMENT PRIMARY KEY,
    club_id INT NOT NULL,
    user_id BIGINT NOT NULL,
    followed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    is_active BOOLEAN DEFAULT TRUE, 
    
    FOREIGN KEY (club_id) REFERENCES Clubs(club_id), 
    FOREIGN KEY (user_id) REFERENCES Users(user_id), 
    UNIQUE(club_id, user_id)
);

CREATE TABLE Events (
    event_id INT AUTO_INCREMENT PRIMARY KEY,
    club_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    description TEXT,
    image_url VARCHAR(255),
    event_date DATETIME NOT NULL,
    end_time DATETIME,
    location VARCHAR(255),
    quota INT DEFAULT 0,
    created_by BIGINT,
    
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMP NULL DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (club_id) REFERENCES Clubs(club_id),
    FOREIGN KEY (created_by) REFERENCES Users(user_id) ON DELETE SET NULL
);

CREATE TABLE EventParticipants (
    participant_id INT AUTO_INCREMENT PRIMARY KEY,
    event_id INT NOT NULL,
    user_id BIGINT NOT NULL,
    status ENUM('going', 'interested', 'not_going') DEFAULT 'going',
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    is_active BOOLEAN DEFAULT TRUE,
    
    FOREIGN KEY (event_id) REFERENCES Events(event_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    UNIQUE(event_id, user_id)
);

CREATE TABLE EventComments (
    comment_id INT AUTO_INCREMENT PRIMARY KEY,
    event_id INT NOT NULL,
    user_id BIGINT NOT NULL,
    comment TEXT NOT NULL,
    
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMP NULL DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (event_id) REFERENCES Events(event_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

CREATE TABLE Notifications (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    club_id INT,
    event_id INT,
    message VARCHAR(255) NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (club_id) REFERENCES Clubs(club_id),
    FOREIGN KEY (event_id) REFERENCES Events(event_id)
);