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

INSERT INTO user (username, email, password_hash) VALUES
    ('user1', 'user1@example.com', 'hashed_password'),
    ('user2', 'user2@example.com', 'hashed_password'),
    ('user3', 'user3@example.com', 'hashed_password'),
    ('user4', 'user4@example.com', 'hashed_password'),
    ('user5', 'user5@example.com', 'hashed_password');

INSERT INTO challenge (title, description, creator_id) VALUES
    ('Challenge 1', 'This is challenge 1', 1),
    ('Challenge 2', 'This is challenge 2', 2),
    ('Challenge 3', 'This is challenge 3', 3),
    ('Challenge 4', 'This is challenge 4', 4),
    ('Challenge 5', 'This is challenge 5', 5);

INSERT INTO challenge_goal (challenge_id, description) VALUES
    (1, 'Goal 1 for Challenge 1'),
    (2, 'Goal 1 for Challenge 2'),
    (3, 'Goal 1 for Challenge 3'),
    (4, 'Goal 1 for Challenge 4'),
    (5, 'Goal 1 for Challenge 5');

INSERT INTO challenge_participation (user_id, challenge_id, joined_date, is_completed) VALUES
    (1, 2, CURRENT_TIMESTAMP, 0), (2, 3, CURRENT_TIMESTAMP, 0),
    (3, 4, CURRENT_TIMESTAMP, 1), (4, 5, CURRENT_TIMESTAMP, 1),
    (5, 1, CURRENT_TIMESTAMP, 0);

INSERT INTO badge (name, description) VALUES
    ('Badge 1', 'Description for badge 1'),
    ('Badge 2', 'Description for badge 2'),
    ('Badge 3', 'Description for badge 3');

INSERT INTO tag (name) VALUES
    ('Tag 1'), ('Tag 2'), ('Tag 3');

INSERT INTO chat (challenge_id, user_id, message, timestamp) VALUES
    (1, 1, 'Hello everyone!', CURRENT_TIMESTAMP),
    (2, 2, 'Excited for this challenge!', CURRENT_TIMESTAMP),
    (3, 3, 'Good luck everyone!', CURRENT_TIMESTAMP);

INSERT INTO user_badges (user_id, badge_id) VALUES
    (1, 1), (2, 2), (3, 3);

INSERT INTO challenge_badges (challenge_id, badge_id) VALUES
    (1, 1), (2, 2), (3, 3);

INSERT INTO challenge_tags (challenge_id, tag_id) VALUES
    (1, 1), (2, 2), (3, 3);
