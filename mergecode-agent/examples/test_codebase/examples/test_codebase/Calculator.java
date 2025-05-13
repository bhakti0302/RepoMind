/**
 * A simple calculator class with basic arithmetic operations.
 */
public class Calculator {
    /**
     * Add two numbers.
     * @param a first number
     * @param b second number
     * @return sum of a and b
     */
    public static int add(int a, int b) {
        return a + b;
    }
    
    /**
     * Subtract two numbers.
     * @param a first number
     * @param b second number
     * @return difference of a and b
     */
    public static int subtract(int a, int b) {
        return a - b;
    }
    
    /**
     * Multiply two numbers.
     * @param a first number
     * @param b second number
     * @return product of a and b
     */
    public static int multiply(int a, int b) {
        return a * b;
    }
    
    /**
     * Divide two numbers.
     * @param a first number
     * @param b second number
     * @return quotient of a and b
     * @throws ArithmeticException if b is zero
     */
    public static int divide(int a, int b) {
        if (b == 0) {
            throw new ArithmeticException("Division by zero");
        }
        return a / b;
    }
}
