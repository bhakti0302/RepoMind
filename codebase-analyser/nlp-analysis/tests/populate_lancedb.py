# Navigate to the nlp-analysis/tests directory

#!/usr/bin/env python3

import lancedb
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer

# Sample library management code chunks
code_chunks = [
    {
        "file_path": "library/models/Book.java",
        "content": "public class Book {\n    private String title;\n    private String author;\n    private String isbn;\n    private boolean available;\n\n    public Book(String title, String author, String isbn) {\n        this.title = title;\n        this.author = author;\n        this.isbn = isbn;\n        this.available = true;\n    }\n\n    // Getters and setters\n}"
    },
    {
        "file_path": "library/services/BookService.java",
        "content": "public class BookService {\n    private List<Book> books = new ArrayList<>();\n\n    public List<Book> searchByAuthor(String author) {\n        return books.stream()\n            .filter(book -> book.getAuthor().equalsIgnoreCase(author))\n            .collect(Collectors.toList());\n    }\n\n    public boolean checkAvailability(String isbn) {\n        return books.stream()\n            .filter(book -> book.getIsbn().equals(isbn))\n            .findFirst()\n            .map(Book::isAvailable)\n            .orElse(false);\n    }\n}"
    },
    {
        "file_path": "library/controllers/LibraryController.java",
        "content": "public class LibraryController {\n    private BookService bookService;\n\n    public LibraryController(BookService bookService) {\n        this.bookService = bookService;\n    }\n\n    public void displayBooksByAuthor(String author) {\n        List<Book> books = bookService.searchByAuthor(author);\n        for (Book book : books) {\n            System.out.println(book.getTitle() + \" - \" + (book.isAvailable() ? \"Available\" : \"Checked Out\"));\n        }\n    }\n}"
    },
    {
        "file_path": "library/models/Library.java",
        "content": "public class Library {\n    private List<Book> books;\n    private List<User> users;\n\n    public Library() {\n        this.books = new ArrayList<>();\n        this.users = new ArrayList<>();\n    }\n\n    public void addBook(Book book) {\n        books.add(book);\n    }\n\n    public List<Book> searchBooksByAuthor(String author) {\n        return books.stream()\n            .filter(book -> book.getAuthor().equalsIgnoreCase(author))\n            .collect(Collectors.toList());\n    }\n}"
    },
    {
        "file_path": "library/services/UserService.java",
        "content": "public class UserService {\n    private List<User> users = new ArrayList<>();\n\n    public void borrowBook(User user, Book book) {\n        if (book.isAvailable()) {\n            book.setAvailable(false);\n            user.addBorrowedBook(book);\n        } else {\n            throw new IllegalStateException(\"Book is not available\");\n        }\n    }\n\n    public void returnBook(User user, Book book) {\n        user.removeBorrowedBook(book);\n        book.setAvailable(true);\n    }\n}"
    }
]

# Initialize sentence transformer model
print("Loading sentence transformer model...")
model = SentenceTransformer('all-MiniLM-L6-v2')

# Create embeddings for each code chunk
print("Creating embeddings...")
embeddings = []
for chunk in code_chunks:
    embedding = model.encode(chunk["content"])
    embeddings.append(embedding)

# Create a pandas DataFrame
df = pd.DataFrame({
    "file_path": [chunk["file_path"] for chunk in code_chunks],
    "content": [chunk["content"] for chunk in code_chunks],
    "vector": embeddings
})

# Connect to LanceDB
print("Connecting to LanceDB...")
db = lancedb.connect("../.lancedb")

# Create the code_chunks table
print("Creating code_chunks table...")
db.create_table("code_chunks", data=df, mode="overwrite")

print("Database populated successfully!")

# Verify the table was created
tables = db.table_names()
print(f"Available tables: {tables}")

# Check the data in the table
if "code_chunks" in tables:
    table = db.open_table("code_chunks")
    count = table.count_rows()
    print(f"Table 'code_chunks' has {count} rows")
    
    if count > 0:
        print("\nSample data (first 2 rows):")
        sample = table.to_pandas(limit=2)
        # Don't print the vector column as it's too large
        print(sample[["file_path", "content"]])

# Make the script executable

# Run the script to populate LanceDB
