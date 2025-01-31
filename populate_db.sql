-- Clear existing data
DELETE FROM challenge_tags;
DELETE FROM challenge_badges;
DELETE FROM user_badges;
DELETE FROM chat;
DELETE FROM tag;
DELETE FROM badge;
DELETE FROM challenge_participation;
DELETE FROM challenge_goal;
DELETE FROM challenge;
DELETE FROM user;

-- Insert users
INSERT INTO user (username, email, password_hash) VALUES
    ('user1', 'user1@example.com', 'hashed_password'),
    ('user2', 'user2@example.com', 'hashed_password'),
    ('user3', 'user3@example.com', 'hashed_password'),
    ('user4', 'user4@example.com', 'hashed_password'),
    ('user5', 'user5@example.com', 'hashed_password'),
    ('user6', 'user6@example.com', 'hashed_password'),
    ('user7', 'user7@example.com', 'hashed_password');

-- Insert challenges
INSERT INTO challenge (title, description, creator_id) VALUES
    ('Challenge 1', 'This is challenge 1', 1),
    ('Challenge 2', 'This is challenge 2', 2),
    ('Challenge 3', 'This is challenge 3', 3),
    ('Challenge 4', 'This is challenge 4', 4),
    ('Challenge 5', 'This is challenge 5', 5),
    ('Challenge 6', 'This is challenge 6', 1),
    ('Challenge 7', 'This is challenge 7', 2);


-- Insert challenge goals
INSERT INTO challenge_goal (challenge_id, description) VALUES
    (1, 'Goal 1 for Challenge 1'),
    (2, 'Goal 1 for Challenge 2'),
    (3, 'Goal 1 for Challenge 3'),
    (4, 'Goal 1 for Challenge 4'),
    (5, 'Goal 1 for Challenge 5'),
    (6, 'Goal 1 for Challenge 6'),
    (7, 'Goal 1 for Challenge 7');

-- Insert challenge participations (some completed)
INSERT INTO challenge_participation (user_id, challenge_id, joined_date, is_completed, completed_date) VALUES
    (1, 2, CURRENT_TIMESTAMP, 0, NULL),
    (2, 3, CURRENT_TIMESTAMP, 0, NULL),
    (3, 4, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
    (4, 5, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
    (5, 1, CURRENT_TIMESTAMP, 0, NULL),
    (6, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
    (7, 3, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
    (3, 5, CURRENT_TIMESTAMP, 0, NULL);

-- Insert badges
INSERT INTO badge (name, description) VALUES
    ('Elite Finisher', 'Awarded for completing elite challenges'),
    ('Beginner Warrior', 'Awarded for starting your first challenge'),
    ('Veteran', 'Awarded for completing multiple challenges'),
    ('Community Helper', 'Awarded for engaging in chat'),
    ('Ultimate Champion', 'Given to those who finish all challenges');

-- Insert tags
INSERT INTO tag (name) VALUES
    ('Fitness'), ('Health'), ('Strength'), ('Endurance'), ('Meditation');

-- Insert chat messages
INSERT INTO chat (challenge_id, user_id, message, timestamp) VALUES
    (1, 1, 'Hello everyone!', CURRENT_TIMESTAMP),
    (2, 2, 'Excited for this challenge!', CURRENT_TIMESTAMP),
    (3, 3, 'Good luck everyone!', CURRENT_TIMESTAMP),
    (4, 4, 'Let’s stay motivated!', CURRENT_TIMESTAMP),
    (5, 5, 'Any tips for this challenge?', CURRENT_TIMESTAMP),
    (1, 6, 'Day 1 completed!', CURRENT_TIMESTAMP),
    (3, 7, 'This challenge is tough but rewarding.', CURRENT_TIMESTAMP);

-- Assign badges to users
INSERT INTO user_badges (user_id, badge_id) VALUES
    (1, 1), (2, 2), (3, 3), (3, 5), (4, 2), (5, 4), (6, 3), (7, 1);

-- Assign badges to challenges
INSERT INTO challenge_badges (challenge_id, badge_id) VALUES
    (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 1), (7, 2);

-- Assign tags to challenges
INSERT INTO challenge_tags (challenge_id, tag_id) VALUES
    (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 1), (7, 2);
