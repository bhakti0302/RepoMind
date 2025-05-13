package com.library.item;

public class Book {
    private String title;
    private String author;
    private boolean isIssued;

    public Book(String title, String author) {
        this.title = title;
        this.author = author;
        this.isIssued = false;
    }

    public void issueBook() {
        isIssued = true;
    }

    public void returnBook() {
        isIssued = false;
    }

    public String getStatus() {
        return isIssued ? "Issued" : "Available";
    }

    @Override
    public String toString() {
        return "Book: " + title + " by " + author + " [" + getStatus() + "]";
    }
}