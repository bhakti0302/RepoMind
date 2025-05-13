package com.company.app;

import com.company.model.Employee;
import com.company.service.EmployeeService;

public class Main {
    public static void main(String[] args) {
        EmployeeService service = new EmployeeService();
        service.addEmployee(new Employee(1, "Alice", "HR"));
        service.addEmployee(new Employee(2, "Bob", "IT"));

        for (Employee e : service.getAllEmployees()) {
            System.out.println(e);
        }
    }
}