package com.library.model;

public class Member extends User {
    private int booksBorrowed;

    public Member(int id, String name, int booksBorrowed) {
        super(id, name);
        this.booksBorrowed = booksBorrowed;
    }

    @Override
    public String getDetails() {
        return super.getDetails() + ", Books Borrowed: " + booksBorrowed;
    }
}