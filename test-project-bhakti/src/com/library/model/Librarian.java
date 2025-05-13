package com.library.model;

public class Librarian extends User {
    private String department;

    public Librarian(int id, String name, String department) {
        super(id, name);
        this.department = department;
    }

    @Override
    public String getDetails() {
        return super.getDetails() + ", Department: " + department;
    }
}