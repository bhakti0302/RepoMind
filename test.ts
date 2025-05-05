// Define a simple interface
interface Person {
    firstName: string;
    lastName: string;
    age: number;
}

// Create a function with type annotations
function greet(person: Person): string {
    return `Hello, ${person.firstName} ${person.lastName}! You are ${person.age} years old.`;
}

// Use the function with an object
const user: Person = {
    firstName: "John",
    lastName: "Doe",
    age: 30
};

// Log the result
console.log(greet(user));