// Create a function with type annotations
function greet(person) {
    return "Hello, ".concat(person.firstName, " ").concat(person.lastName, "! You are ").concat(person.age, " years old.");
}
// Use the function with an object
var user = {
    firstName: "John",
    lastName: "Doe",
    age: 30
};
// Log the result
console.log(greet(user));
