/**
 * Example Java class for testing the Merge Code Agent.
 */
public class Example {
    /**
     * Main method to demonstrate the class.
     */
    public static void main(String[] args) {
        System.out.println("Hello, World!");
        
        // Create an array
        int[] numbers = {5, 2, 9, 1, 7, 3};
        
        // Print the array
        System.out.println("Original array:");
        printArray(numbers);
    }
    
    /**
     * Print the elements of an array.
     */
    public static void printArray(int[] array) {
        for (int num : array) {
            System.out.print(num + " ");
        }
        System.out.println();
    }
        /**
         * Calculates the sum of an array of integers.
         */
        public static int calculateSum(int[] array) {
            int sum = 0;
            for (int num : array) {
                sum += num;
            }
            return sum;
        }

/**
* Finds the maximum value in an array of integers.
*/
public static int findMaximum(int[] array) {
    int max = array[0];
    for (int num : array) {
        if (num > max) {
            max = num;
        }
    }
    return max;
}
public static String reverseString(String str) {
    StringBuilder sb = new StringBuilder(str);
    return sb.reverse().toString();
}
public static int countCharacterOccurrences(String str, char c) {
    int count = 0;
    for (char ch : str.toCharArray()) {
        if (ch == c) {
            count++;
        }
    }
    return count;
}
}