CREATE DATABASE library_sys;
USE library_sys ;	
CREATE TABLE Books (
    book_id INT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    is_available BOOLEAN NOT NULL
);
INSERT INTO Books (book_id, title, author, is_available) VALUES
(1, 'To Kill a Mockingbird', 'Harper Lee', TRUE),
(2, '1984', 'George Orwell', TRUE),
(3, 'The Great Gatsby', 'F. Scott Fitzgerald', FALSE),
(4, 'Moby Dick', 'Herman Melville', TRUE),
(5, 'Pride and Prejudice', 'Jane Austen', FALSE),
(6, 'The Catcher in the Rye', 'J.D. Salinger', TRUE),
(7, 'The Hobbit', 'J.R.R. Tolkien', TRUE),
(8, 'Fahrenheit 451', 'Ray Bradbury', FALSE),
(9, 'Brave New World', 'Aldous Huxley', TRUE),
(10, 'One Hundred Years of Solitude', 'Gabriel Garcia Marquez', TRUE),
(11, 'The Lord of the Rings', 'J.R.R. Tolkien', TRUE),
(12, 'The Alchemist', 'Paulo Coelho', FALSE);
CREATE TABLE Members (
    member_id INT PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL
);
INSERT INTO Members (member_id, first_name, last_name, email) VALUES
(1, 'Alice', 'Smith', 'alice.smith@email.com'),
(2, 'Bob', 'Johnson', 'bob.j@email.com'),
(3, 'Charlie', 'Brown', 'charlie.b@email.com'),
(4, 'Diana', 'Prince', 'diana.p@email.com'),
(5, 'Edward', 'Norton', 'edward.n@email.com'),
(6, 'Fiona', 'Gomez', 'fiona.g@email.com'),
(7, 'George', 'Lopez', 'george.l@email.com');
CREATE TABLE BorrowRecords (
    record_id INT PRIMARY KEY,
    book_id INT,
    member_id INT,
    borrow_date DATE NOT NULL,
    return_date DATE,
    FOREIGN KEY (book_id) REFERENCES Books(book_id),
    FOREIGN KEY (member_id) REFERENCES Members(member_id)
);

INSERT INTO BorrowRecords (record_id, book_id, member_id, borrow_date, return_date) VALUES
(1, 3, 1, '2025-08-01', NULL), -- The Great Gatsby, currently checked out
(2, 5, 2, '2025-08-05', NULL), -- Pride and Prejudice, currently checked out
(3, 8, 3, '2025-08-08', NULL), -- Fahrenheit 451, currently checked out
(4, 12, 4, '2025-08-10', NULL), -- The Alchemist, currently checked out
(5, 1, 5, '2025-07-20', '2025-08-05'),
(6, 2, 6, '2025-07-25', '2025-08-15'),
(7, 4, 7, '2025-08-10', '2025-08-20'),
(8, 6, 1, '2025-08-12', '2025-08-25'),
(9, 7, 2, '2025-08-15', '2025-08-28'),
(10, 9, 3, '2025-08-20', '2025-08-29'),
(11, 10, 4, '2025-08-25', NULL), -- One Hundred Years of Solitude, currently checked out
(12, 11, 5, '2025-08-28', NULL);