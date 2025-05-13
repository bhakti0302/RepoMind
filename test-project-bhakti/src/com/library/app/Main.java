package com.library.app;

import com.library.model.Librarian;
import com.library.model.Member;
import com.library.item.Book;

public class Main {
    public static void main(String[] args) {
        Librarian librarian = new Librarian(1, "Alice", "Science");
        Member member = new Member(2, "Bob", 3);
        Book book = new Book("1984", "George Orwell");

        System.out.println(librarian.getDetails());
        System.out.println(member.getDetails());
        System.out.println(book);

        book.issueBook();
        System.out.println("After issuing: " + book);

        book.returnBook();
        System.out.println("After returning: " + book);
    }
}