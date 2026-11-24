"""Beginner track: 14 lessons, from the first program to a small project."""

LESSONS = [
{
 "id": "b01", "level": "beginner", "title": "Your first program", "minutes": 10,
 "tags": ["main", "output", "compiler"],
 "goal": "Write, compile and run the smallest complete C++ program.",
 "explain": [
   "Every C++ program starts at a function called main. The computer looks for it, runs the lines inside its braces, and when main finishes the program is over.",
   "std::cout means the console output. The << is an arrow that pushes whatever is on its right into the stream on its left. \"Hello\" is text; the \\n on the end means move to a new line."
 ],
 "example": {
   "title": "hello.cpp - the whole program",
   "code": r"""#include <iostream>

int main() {
    std::cout << "Hello, everyone!\n";
    return 0;
}""",
   "output": "Hello, everyone!\n",
   "notes": [
     ["#include <iostream>", "brings in the printing tools so cout exists"],
     ["int main()", "the starting point; the int means main gives back a number"],
     ["std::cout << ...", "prints the text that follows it"],
     ["\\n", "moves to the next line, like pressing Enter"],
     ["return 0;", "tells the system the program finished happily"]
   ]
 },
 "predict": {
   "q": "If you delete the \\n but keep everything else, what changes?",
   "options": ["The program will not compile",
               "The text prints, but the next output would sit on the same line",
               "Nothing at all"],
   "answer": 1,
   "why": "\\n is not part of the program's structure, it is just a character that moves the cursor down. Without it your text still prints."
 },
 "quiz": [
   {"q": "Which line is the entry point of every C++ program?",
    "options": ["#include <iostream>", "int main()", "return 0;"],
    "answer": 1,
    "why": "main is where execution begins. #include only pulls in tools, and return 0 is the last thing that happens."},
   {"q": "What does std::cout do?",
    "options": ["Reads typing from the keyboard", "Sends text to the console", "Stores a number in memory"],
    "answer": 1,
    "why": "cout is the output stream. Input is cin, and storage needs a variable."},
   {"q": "Why does main return 0?",
    "options": ["Because C++ requires a number after every line",
                "To report that the program ended successfully",
                "To clear the screen"],
    "answer": 1,
    "why": "The return value is the exit status. 0 means success; anything else signals a problem to whatever started the program."}
 ],
 "activity": {
   "goal": "Make the program introduce YOU: print your name and one thing you like, on two separate lines.",
   "starter": r"""#include <iostream>

int main() {
    // TODO: print your name on the first line
    // TODO: print something you like on the second line
    return 0;
}""",
   "expected": "Ana\nI like robots\n",
   "hints": [
     "Each idea needs its own std::cout line, and each line ends with \\n.",
     "The text you print must sit inside double quotes: std::cout << \"Ana\\n\";",
     "Two statements, in order: std::cout << \"Ana\\n\"; then std::cout << \"I like robots\\n\";"
   ],
   "solution": r"""#include <iostream>

int main() {
    std::cout << "Ana\n";
    std::cout << "I like robots\n";
    return 0;
}"""
 },
 "mistake": "Forgetting the semicolon at the end of a statement. The compiler will point at the next line, which is confusing - when an error looks impossible, check the line above.",
 "recap": "A program is main plus the lines inside it, and cout << prints."
},
{
 "id": "b02", "level": "beginner", "title": "Printing several things", "minutes": 10,
 "tags": ["output", "endl"],
 "goal": "Combine text and numbers in one print, and choose between \\n and endl.",
 "explain": [
   "You can chain as many << as you like. Each one adds another piece to the same line, in the order you write them.",
   "std::endl also starts a new line, but it additionally flushes the buffer, which is slower. For a normal program \\n is the better habit."
 ],
 "example": {
   "title": "Mixing text and numbers",
   "code": r"""#include <iostream>

int main() {
    int day = 3;
    std::cout << "Day " << day << " of the build\n";
    std::cout << "Parts: " << 5 << " | Wheels: " << 0 << "\n";
    std::cout << "Done" << std::endl;
    return 0;
}""",
   "output": "Day 3 of the build\nParts: 5 | Wheels: 0\nDone\n",
   "notes": [
     ["\"Day \" << day", "text first, then the value of day - no space unless you print one"],
     ["<< 5", "you can print a number directly, without a variable"],
     ["std::endl", "new line plus a flush; same visible result as \\n here"]
   ]
 },
 "predict": {
   "q": "What does std::cout << \"a\" << \"b\"; print?",
   "options": ["a b", "ab", "a\\nb"],
   "answer": 1,
   "why": "Nothing is added between pieces, not even a space. You get exactly what you wrote, glued together."
 },
 "quiz": [
   {"q": "How do you print a space between two words?",
    "options": ["C++ adds one automatically", "Put the space inside the quotes", "Use std::space"],
    "answer": 1,
    "why": "Formatting is your job: include the space in the text, like \"hello \" or \" \" between pieces."},
   {"q": "Which is usually faster?",
    "options": ["\\n", "std::endl", "They are identical in every way"],
    "answer": 0,
    "why": "endl flushes the output buffer every time, which costs time in loops. Use \\n and flush only when you need to."},
   {"q": "What is printed by std::cout << 2 + 3 << \"\\n\";",
    "options": ["2 + 3", "5", "23"],
    "answer": 1,
    "why": "The expression is calculated first, then the result is printed - so 5, not the characters."}
 ],
 "activity": {
   "goal": "Print a three-column table row: name, score, and a star rating, using one cout chain.",
   "starter": r"""#include <iostream>

int main() {
    // TODO: print  Ana   95   ***   all on one line
    return 0;
}""",
   "expected": "Ana   95   ***\n",
   "hints": [
     "One cout can carry all three pieces if you chain << operators.",
     "Spaces are just characters: put three of them inside the quotes.",
     "std::cout << \"Ana\" << \"   95   \" << \"***\\n\";"
   ],
   "solution": r"""#include <iostream>

int main() {
    std::cout << "Ana" << "   95   " << "***\n";
    return 0;
}"""
 },
 "mistake": "Expecting a space to appear by itself between two << pieces. It never does - the output is exactly the characters you write.",
 "recap": "Chain << to build a line, and put newlines where you want them."
},
{
 "id": "b03", "level": "beginner", "title": "Variables hold values", "minutes": 12,
 "tags": ["variables", "assignment"],
 "goal": "Store a value in a named box and change it later.",
 "explain": [
   "A variable is a named box in memory. int apples = 5; creates the box, puts 5 in it, and lets you use the name apples from then on.",
   "The = here is not \"equals\" in the maths sense, it means \"put this value into that box\". Running apples = apples - eaten; reads the old value, subtracts, and stores the result back."
 ],
 "example": {
   "title": "Counting apples",
   "code": r"""#include <iostream>

int main() {
    int apples = 5;
    int eaten = 2;

    std::cout << "Start: " << apples << "\n";
    apples = apples - eaten;
    std::cout << "Left: " << apples << "\n";
    apples = 10;
    std::cout << "Refilled: " << apples << "\n";
    return 0;
}""",
   "output": "Start: 5\nLeft: 3\nRefilled: 10\n",
   "notes": [
     ["int apples = 5;", "creates the box and fills it in one line"],
     ["apples = apples - eaten;", "right side is calculated first, then stored back"],
     ["apples = 10;", "the old value is thrown away, not added to"]
   ]
 },
 "predict": {
   "q": "After int x = 4; x = x + 1; x = x * 2; what is x?",
   "options": ["10", "8", "12"],
   "answer": 0,
   "why": "Each line uses the value from the line before: 4 becomes 5, then 5 * 2 is 10."
 },
 "quiz": [
   {"q": "What does x = y mean in C++?",
    "options": ["x and y are the same box", "Copy y's value into x", "Check whether x equals y"],
    "answer": 1,
    "why": "Assignment copies the value. Comparison is ==, with two signs, and it is a completely different operation."},
   {"q": "What happens if you use a variable before giving it a value?",
    "options": ["It starts at 0", "It holds whatever was in memory - unpredictable", "The compiler always refuses"],
    "answer": 1,
    "why": "Uninitialised variables hold junk. Always give a value when you create one; compilers warn about it but do not always stop."},
   {"q": "Which line stores 7 in a box called lucky?",
    "options": ["int lucky = 7;", "lucky == 7;", "int lucky;"],
    "answer": 0,
    "why": "int lucky = 7; declares the type and stores the value. lucky == 7 asks a question and throws the answer away."}
 ],
 "activity": {
   "goal": "Start with 3 lives, lose one, then print how many are left.",
   "starter": r"""#include <iostream>

int main() {
    int lives = 3;
    // TODO: lose one life
    // TODO: print "Lives: " and the number
    return 0;
}""",
   "expected": "Lives: 2\n",
   "hints": [
     "Losing a life means storing a new value: lives = lives - 1;",
     "There is also a shortcut: lives -= 1; or --lives;",
     "std::cout << \"Lives: \" << lives << \"\\n\";"
   ],
   "solution": r"""#include <iostream>

int main() {
    int lives = 3;
    lives = lives - 1;
    std::cout << "Lives: " << lives << "\n";
    return 0;
}"""
 },
 "mistake": "Writing int score = 0; inside a loop when you meant to reset a score that already exists - that creates a brand new box each time and hides the old one.",
 "recap": "A variable is a named box; = puts a value in it."
},
{
 "id": "b04", "level": "beginner", "title": "Types: int, double, char, bool", "minutes": 12,
 "tags": ["types", "numbers", "bool"],
 "goal": "Pick the right type for each kind of value and know what each one prints.",
 "explain": [
   "The type tells the computer how to store the value and what you can do with it. int is a whole number, double is a number with a decimal point, char is a single character in single quotes, bool is true or false.",
   "Text lives in std::string, which needs #include <string>. Mixing them up is the most common beginner error: 'A' is a char, \"A\" is a string."
 ],
 "example": {
   "title": "Four types, one person",
   "code": r"""#include <iostream>
#include <string>

int main() {
    std::string name = "Ana";
    int age = 11;
    double height = 1.42;
    char grade = 'A';
    bool awake = true;

    std::cout << name << " is " << age << "\n";
    std::cout << "height " << height << " m\n";
    std::cout << "grade " << grade << "\n";
    std::cout << "awake " << awake << "\n";
    return 0;
}""",
   "output": "Ana is 11\nheight 1.42 m\ngrade A\nawake 1\n",
   "notes": [
     ["char grade = 'A';", "single quotes for one character"],
     ["bool awake = true;", "true/false, but cout prints 1 and 0 unless you ask for text"],
     ["double height", "needed for 1.42; an int would cut it to 1"]
   ]
 },
 "predict": {
   "q": "What does int half = 1.9; store?",
   "options": ["1.9", "1", "2"],
   "answer": 1,
   "why": "Converting a double to an int throws away the fraction; it does not round. 1.9 becomes 1."
 },
 "quiz": [
   {"q": "Which type holds 3.75?",
    "options": ["int", "double", "char"],
    "answer": 1,
    "why": "int cannot hold fractions, and char holds one character. double is the decimal type."},
   {"q": "How do you write the character A?",
    "options": ["'A'", "\"A\"", "A"],
    "answer": 0,
    "why": "Single quotes make a char, double quotes make a string, and bare A would be read as a variable name."},
   {"q": "Why does bool print as 1?",
    "options": ["It is broken", "cout prints true as 1 unless you use std::boolalpha", "true is stored as the number 1 and printed numerically"],
    "answer": 1,
    "why": "By default the stream prints booleans as 1/0. std::boolalpha switches to the words true/false."}
 ],
 "activity": {
   "goal": "Create one variable of each of the four basic types for a robot, then print them on four lines.",
   "starter": r"""#include <iostream>
#include <string>

int main() {
    std::string robot = "Five Sides";
    // TODO: an int for battery percent (start at 87)
    // TODO: a double for height in metres (0.236)
    // TODO: a char for its mood ('H' for happy)
    // TODO: a bool for whether it is awake (true)
    // TODO: print each one on its own line
    return 0;
}""",
   "expected": "Five Sides\n87\n0.236\nH\n1\n",
   "hints": [
     "One declaration per type: int battery = 87; double height = 0.236;",
     "char needs single quotes: char mood = 'H';",
     "Print each with its own cout line ending in \\n."
   ],
   "solution": r"""#include <iostream>
#include <string>

int main() {
    std::string robot = "Five Sides";
    int battery = 87;
    double height = 0.236;
    char mood = 'H';
    bool awake = true;

    std::cout << robot << "\n";
    std::cout << battery << "\n";
    std::cout << height << "\n";
    std::cout << mood << "\n";
    std::cout << awake << "\n";
    return 0;
}"""
 },
 "mistake": "Using double for money-like values without thinking about precision, or storing a decimal in an int and losing the fraction silently.",
 "recap": "Choose the type from the value you want to store, and remember int cuts fractions off."
},
{
 "id": "b05", "level": "beginner", "title": "Reading what the user types", "minutes": 12,
 "tags": ["input", "cin", "getline"],
 "goal": "Ask a question, read the answer, and use it.",
 "explain": [
   "std::cin reads from the keyboard, and >> pushes the typed value into a variable. The arrows point the opposite way from cout because the data flows the other direction.",
   "cin >> stops at the first space, so names with spaces need std::getline(std::cin, name). Mixing >> and getline needs care: >> leaves the Enter key in the buffer, and getline then reads an empty line."
 ],
 "example": {
   "title": "Name and age",
   "code": r"""#include <iostream>
#include <string>

int main() {
    std::string name;
    int age = 0;

    std::cout << "Your name: ";
    std::getline(std::cin, name);
    std::cout << "Your age: ";
    std::cin >> age;

    std::cout << "Hi " << name << ", next year you are " << age + 1 << ".\n";
    return 0;
}""",
   "output": "Your name: Your age: Hi Ana, next year you are 12.\n",
   "stdin": "Ana\n11\n",
   "notes": [
     ["std::getline(std::cin, name);", "reads a whole line, spaces included"],
     ["std::cin >> age;", "reads one number and skips the Enter key"],
     ["age + 1", "you can calculate inside a print"]
   ]
 },
 "predict": {
   "q": "The user types 11 and presses Enter. What does cin >> age leave behind in the buffer?",
   "options": ["Nothing", "The Enter key (a newline character)", "The number 11 again"],
   "answer": 1,
   "why": ">> reads the digits and stops, leaving the newline. That is why a getline straight afterwards returns an empty string."
 },
 "quiz": [
   {"q": "Which reads a full name with a space in it?",
    "options": ["std::cin >> name;", "std::getline(std::cin, name);", "std::cout << name;"],
    "answer": 1,
    "why": ">> stops at whitespace, so 'Ana Cruz' would only give you 'Ana'. getline takes the whole line."},
   {"q": "What does cin >> do if the user types letters where you expect a number?",
    "options": ["It stores 0", "It fails and leaves the variable unchanged", "It crashes the program"],
    "answer": 1,
    "why": "The stream enters a failed state; the variable keeps its old value and further reads do nothing until you clear it."},
   {"q": "Why print a prompt like \"Your age: \" before reading?",
    "options": ["It is required by cin", "So the person knows what to type", "It makes the read faster"],
    "answer": 1,
    "why": "cin waits silently. Without a prompt the user just sees a blank screen and does not know what is expected."}
 ],
 "activity": {
   "goal": "Ask for a number of steps and print double that number, using input.",
   "starter": r"""#include <iostream>

int main() {
    int steps = 0;
    // TODO: ask "Steps? " and read into steps
    // TODO: print "That is " << steps * 2 << " on the way back"
    return 0;
}""",
   "expected": "Steps? That is 40 on the way back\n",
   "stdin": "20\n",
   "hints": [
     "Reading uses cin with the arrows pointing at the variable: std::cin >> steps;",
     "Print the prompt first, with no newline, so the typing appears after it.",
     "std::cout << \"Steps? \"; std::cin >> steps; std::cout << \"That is \" << steps * 2 << \" on the way back\\n\";"
   ],
   "solution": r"""#include <iostream>

int main() {
    int steps = 0;
    std::cout << "Steps? ";
    std::cin >> steps;
    std::cout << "That is " << steps * 2 << " on the way back\n";
    return 0;
}"""
 },
 "mistake": "Forgetting that cin >> skips whitespace - reading a word then a full line without clearing the leftover newline gives you an empty string.",
 "recap": "cin >> reads one value, getline reads one whole line, and always prompt first."
},
{
 "id": "b06", "level": "beginner", "title": "Arithmetic and the integer trap", "minutes": 12,
 "tags": ["operators", "division", "modulo"],
 "goal": "Calculate with + - * / % and avoid the integer division surprise.",
 "explain": [
   "Five operators cover most school maths: + - * / and % (remainder, called modulo). They follow the usual order: * / % before + -, and brackets win.",
   "The trap: dividing two ints gives an int, and the fraction is thrown away. 7 / 2 is 3, not 3.5. To get the decimal, at least one side must be a double."
 ],
 "example": {
   "title": "Seven and two",
   "code": r"""#include <iostream>

int main() {
    int a = 7;
    int b = 2;

    std::cout << "add " << a + b << "\n";
    std::cout << "sub " << a - b << "\n";
    std::cout << "mul " << a * b << "\n";
    std::cout << "div " << a / b << "\n";
    std::cout << "rem " << a % b << "\n";
    std::cout << "real " << 7.0 / 2 << "\n";
    std::cout << "brackets " << (a + b) * 2 << "\n";
    return 0;
}""",
   "output": "add 9\nsub 5\nmul 14\ndiv 3\nrem 1\nreal 3.5\nbrackets 18\n",
   "notes": [
     ["a / b", "both ints, so the answer is the whole number 3"],
     ["a % b", "what is left over: 7 is 3 twos with 1 left"],
     ["7.0 / 2", "one side is a double, so the division keeps the decimal"]
   ]
 },
 "predict": {
   "q": "What is 9 / 10 in C++ when both are ints?",
   "options": ["0.9", "0", "1"],
   "answer": 1,
   "why": "Both are ints, so the result is an int and everything after the point is dropped. 9/10 is 0, not 1 - it never rounds up."
 },
 "quiz": [
   {"q": "How do you make 9 / 10 give 0.9?",
    "options": ["9.0 / 10", "int(9) / 10", "9 / 10.0f is forbidden"],
    "answer": 0,
    "why": "Making either side a decimal forces decimal division. Casting to int does the opposite of what you want."},
   {"q": "What is 17 % 5?",
    "options": ["3", "2", "3.4"],
    "answer": 1,
    "why": "% gives the remainder: 5 fits into 17 three times (15), leaving 2."},
   {"q": "What is 2 + 3 * 4?",
    "options": ["20", "14", "9"],
    "answer": 1,
    "why": "Multiplication happens before addition, so 3*4 is 12 and 2+12 is 14. Use (2+3)*4 if you want 20."}
 ],
 "activity": {
   "goal": "Split 47 sweets between 5 friends: print how many each gets and how many are left over.",
   "starter": r"""#include <iostream>

int main() {
    int sweets = 47;
    int friends = 5;
    // TODO: print "Each: " and the whole-number share
    // TODO: print "Left: " and the remainder
    return 0;
}""",
   "expected": "Each: 9\nLeft: 2\n",
   "hints": [
     "The whole-number share is sweets / friends - both are ints, so it is already whole.",
     "The remainder is sweets % friends.",
     "std::cout << \"Each: \" << sweets / friends << \"\\n\"; then the % one."
   ],
   "solution": r"""#include <iostream>

int main() {
    int sweets = 47;
    int friends = 5;
    std::cout << "Each: " << sweets / friends << "\n";
    std::cout << "Left: " << sweets % friends << "\n";
    return 0;
}"""
 },
 "mistake": "Writing int average = total / count; when both are ints - you silently lose the fraction. Make one side a double, or store into a double with a cast.",
 "recap": "Same-type division keeps the type, so mix in a double when you need the decimal."
},
{
 "id": "b07", "level": "beginner", "title": "Making decisions with if", "minutes": 12,
 "tags": ["if", "comparison", "boolean"],
 "goal": "Run different code depending on a condition.",
 "explain": [
   "An if runs the lines in its braces only when the condition inside the brackets is true. The else branch runs when it is not.",
   "Comparisons produce a bool: == equal, != not equal, > < >= <=. A very common bug is writing = instead of ==, which stores a value instead of asking a question - modern compilers warn about this, but not always."
 ],
 "example": {
   "title": "Did the score pass?",
   "code": r"""#include <iostream>

int main() {
    int score = 72;

    if (score >= 60) {
        std::cout << "Pass\n";
    } else {
        std::cout << "Try again\n";
    }

    if (score == 100) {
        std::cout << "Perfect\n";
    } else {
        std::cout << "Not perfect yet\n";
    }
    return 0;
}""",
   "output": "Pass\nNot perfect yet\n",
   "notes": [
     ["if (score >= 60)", "the condition is a question with a yes/no answer"],
     ["else", "the other path, taken when the question was false"],
     ["score == 100", "two equals signs compare; one would assign"]
   ]
 },
 "predict": {
   "q": "With score = 60, does the first branch run?",
   "options": ["Yes, because >= includes equality", "No, only scores above 60 pass", "It is a syntax error"],
   "answer": 0,
   "why": ">= means 'greater than or equal', so 60 counts. Using > would exclude it."
 },
 "quiz": [
   {"q": "What does if (x = 5) do?",
    "options": ["Checks whether x is 5", "Stores 5 in x, and the condition is true because 5 is not zero", "Nothing at all"],
    "answer": 1,
    "why": "One = is assignment. The expression's value is 5, which counts as true, so the branch always runs. Use == to compare."},
   {"q": "Which condition is true when age is exactly 13?",
    "options": ["age > 13", "age >= 13", "age != 13"],
    "answer": 1,
    "why": ">= includes the boundary; > and != both exclude 13."},
   {"q": "What runs when the condition is false and there is no else?",
    "options": ["The lines inside the if, once", "Nothing - execution continues after the if block", "The program stops"],
    "answer": 1,
    "why": "Without an else, a false condition simply skips the block and carries on with the next statement."}
 ],
 "activity": {
   "goal": "Print \"Hot\" when the temperature is 30 or more, otherwise print \"Cool\".",
   "starter": r"""#include <iostream>

int main() {
    int temp = 34;
    // TODO: one if/else that prints Hot or Cool
    return 0;
}""",
   "expected": "Hot\n",
   "hints": [
     "Compare with >= 30 so that exactly 30 counts.",
     "The else branch needs no condition of its own.",
     "if (temp >= 30) { std::cout << \"Hot\\n\"; } else { std::cout << \"Cool\\n\"; }"
   ],
   "solution": r"""#include <iostream>

int main() {
    int temp = 34;
    if (temp >= 30) {
        std::cout << "Hot\n";
    } else {
        std::cout << "Cool\n";
    }
    return 0;
}"""
 },
 "mistake": "Using = where you meant ==. if (score = 100) always runs and quietly overwrites the score.",
 "recap": "if asks one yes/no question and chooses a path; == compares, = assigns."
},
{
 "id": "b08", "level": "beginner", "title": "Several choices and combining conditions", "minutes": 13,
 "tags": ["else if", "and", "or"],
 "goal": "Choose between many outcomes and join conditions with && and ||.",
 "explain": [
   "An else if chain checks conditions in order and stops at the first true one. Order matters: put the narrowest test first.",
   "&& means both sides must be true, || means at least one must be. ! flips a bool. C++ stops evaluating as soon as the answer is known, so put the cheap or safe test first."
 ],
 "example": {
   "title": "Robot decides what to do",
   "code": r"""#include <iostream>

int main() {
    int battery = 15;
    bool charging = true;

    if (battery < 10) {
        std::cout << "Shut down\n";
    } else if (battery < 30 && charging) {
        std::cout << "Charging, stay still\n";
    } else if (battery < 30) {
        std::cout << "Low, find a cable\n";
    } else {
        std::cout << "Play\n";
    }

    if (!charging || battery > 90) {
        std::cout << "Ready to go out\n";
    }
    return 0;
}""",
   "output": "Charging, stay still\n",
   "notes": [
     ["else if (battery < 30 && charging)", "both must be true: low battery AND plugged in"],
     ["else if (battery < 30)", "reached only if the version above failed"],
     ["!charging || battery > 90", "true when not charging, or nearly full"]
   ]
 },
 "predict": {
   "q": "With battery = 15 and charging = false, which branch runs?",
   "options": ["Shut down", "Low, find a cable", "Play"],
   "answer": 1,
   "why": "15 is not below 10, and the && branch fails because charging is false, so the third test (battery < 30) catches it."
 },
 "quiz": [
   {"q": "When is a && b true?",
    "options": ["When either side is true", "Only when both sides are true", "When both sides are false"],
    "answer": 1,
    "why": "AND is strict. OR (||) is the one that accepts either side."},
   {"q": "Why does the order of else if branches matter?",
    "options": ["It does not", "Only the first true branch runs, so a broad test can hide a specific one", "C++ sorts them for you"],
    "answer": 1,
    "why": "The chain stops at the first match. Put conditions like >= 90 before >= 60, or the specific case is never reached."},
   {"q": "What is !(true) ?",
    "options": ["true", "false", "0.5"],
    "answer": 1,
    "why": "! negates a bool, so the opposite of true is false."}
 ],
 "activity": {
   "goal": "Grade a score: 90+ is A, 75+ is B, 50+ is C, anything else is D. Print only the letter.",
   "starter": r"""#include <iostream>

int main() {
    int score = 82;
    // TODO: else if chain, highest score first
    return 0;
}""",
   "expected": "B\n",
   "hints": [
     "Start with if (score >= 90) and work downwards.",
     "Each later branch can be simpler because the ones above already failed.",
     "if (score >= 90) ... else if (score >= 75) ... else if (score >= 50) ... else ..."
   ],
   "solution": r"""#include <iostream>

int main() {
    int score = 82;
    if (score >= 90) {
        std::cout << "A\n";
    } else if (score >= 75) {
        std::cout << "B\n";
    } else if (score >= 50) {
        std::cout << "C\n";
    } else {
        std::cout << "D\n";
    }
    return 0;
}"""
 },
 "mistake": "Putting a broad branch before a narrow one, so the narrow one can never run. Always order from most specific to least.",
 "recap": "else if chains pick one path, and && / || combine questions."
},
{
 "id": "b09", "level": "beginner", "title": "Repeating with while", "minutes": 13,
 "tags": ["while", "loops"],
 "goal": "Repeat work until a condition becomes false.",
 "explain": [
   "A while loop checks its condition before every pass. If the condition is true, the body runs and then it checks again.",
   "The body must change something the condition depends on, otherwise the loop never ends. That is the number one cause of a program that hangs."
 ],
 "example": {
   "title": "Battery draining",
   "code": r"""#include <iostream>

int main() {
    int battery = 3;

    while (battery > 0) {
        std::cout << "Battery " << battery << "\n";
        battery = battery - 1;
    }
    std::cout << "Empty\n";
    return 0;
}""",
   "output": "Battery 3\nBattery 2\nBattery 1\nEmpty\n",
   "notes": [
     ["while (battery > 0)", "checked before each pass"],
     ["battery = battery - 1;", "without this line the loop would never end"],
     ["std::cout << \"Empty\\n\";", "runs after the loop, once"]
   ]
 },
 "predict": {
   "q": "What if you delete the line battery = battery - 1; ?",
   "options": ["It prints Battery 3 once", "It prints Battery 3 forever", "It is a compile error"],
   "answer": 1,
   "why": "The condition never changes, so it stays true. This is an infinite loop - the runner will stop it after a few seconds."
 },
 "quiz": [
   {"q": "When is a while loop's body skipped completely?",
    "options": ["Never", "When the condition is false on the first check", "Only when the body is empty"],
    "answer": 1,
    "why": "while checks first, so a false condition means zero passes. A do-while is the version that always runs once."},
   {"q": "Which loop always runs at least once?",
    "options": ["while", "do-while", "for"],
    "answer": 1,
    "why": "do-while checks after the body, so the first pass happens unconditionally."},
   {"q": "What is a sentinel value?",
    "options": ["A value that ends the loop, like -1 for 'stop'", "The first value in an array", "A special compiler keyword"],
    "answer": 0,
    "why": "A sentinel is a value the data itself uses to say 'no more'. The loop tests for it each pass."}
 ],
 "activity": {
   "goal": "Count down from 5 to 1 with a while loop, printing each number, then print \"Liftoff\".",
   "starter": r"""#include <iostream>

int main() {
    int n = 5;
    // TODO: while loop that prints n and counts down
    // TODO: print Liftoff after the loop
    return 0;
}""",
   "expected": "5\n4\n3\n2\n1\nLiftoff\n",
   "hints": [
     "The condition should be n > 0.",
     "Inside the loop, print n then decrease it.",
     "\"Liftoff\" goes after the closing brace of the loop, not inside it."
   ],
   "solution": r"""#include <iostream>

int main() {
    int n = 5;
    while (n > 0) {
        std::cout << n << "\n";
        n = n - 1;
    }
    std::cout << "Liftoff\n";
    return 0;
}"""
 },
 "mistake": "Forgetting to change the loop variable inside the body, which creates an infinite loop that never prints anything new.",
 "recap": "while repeats while its condition stays true, and the body must move that condition toward false."
},
{
 "id": "b10", "level": "beginner", "title": "Counting with for", "minutes": 13,
 "tags": ["for", "loops", "accumulator"],
 "goal": "Use a for loop for a known number of repeats.",
 "explain": [
   "for packs the counter into one line: start, keep-going test, and step. for (int i = 1; i <= 5; ++i) reads as 'start at 1, while i is at most 5, add one each pass'.",
   "Use for when you know how many times you are repeating, and while when you are waiting for something to happen. The counter i is a normal variable - it can count up, down, or by twos."
 ],
 "example": {
   "title": "Summer and countdown",
   "code": r"""#include <iostream>

int main() {
    int total = 0;
    for (int i = 1; i <= 5; ++i) {
        total += i;
    }
    std::cout << "Sum 1..5 = " << total << "\n";

    for (int i = 5; i >= 1; --i) {
        std::cout << i << " ";
    }
    std::cout << "\n";

    for (int i = 0; i <= 10; i += 2) {
        std::cout << i << " ";
    }
    std::cout << "\n";
    return 0;
}""",
   "output": "Sum 1..5 = 15\n5 4 3 2 1 \n0 2 4 6 8 10 \n",
   "notes": [
     ["int i = 1", "the starting value, created once"],
     ["i <= 5", "checked before every pass"],
     ["++i", "adds one after every pass; i += 2 adds two"]
   ]
 },
 "predict": {
   "q": "How many times does for (int i = 0; i < 3; ++i) run?",
   "options": ["2", "3", "4"],
   "answer": 1,
   "why": "i takes 0, 1 and 2 - three passes. The test is < 3, so 3 itself is not included."
 },
 "quiz": [
   {"q": "Which loop suits 'repeat exactly 10 times'?",
    "options": ["while", "for", "do-while"],
    "answer": 1,
    "why": "for keeps the counter and the limit together in one line, which is exactly a known repeat count."},
   {"q": "What does total += i; do?",
    "options": ["Compares total and i", "Adds i to total and stores the result", "Creates a new variable"],
    "answer": 1,
    "why": "It is shorthand for total = total + i; a running total is often called an accumulator."},
   {"q": "How many passes for (int i = 10; i > 0; i -= 3)?",
    "options": ["3", "4", "10"],
    "answer": 1,
    "why": "i goes 10, 7, 4, 1 - four passes; after that i is -2 and the test fails."}
 ],
 "activity": {
   "goal": "Print the 7 times table from 1 to 5, one line each, like \"7 x 1 = 7\".",
   "starter": r"""#include <iostream>

int main() {
    // TODO: for loop from 1 to 5
    // TODO: print 7 x i = 7*i on each line
    return 0;
}""",
   "expected": "7 x 1 = 7\n7 x 2 = 14\n7 x 3 = 21\n7 x 4 = 28\n7 x 5 = 35\n",
   "hints": [
     "Loop from 1 while i <= 5.",
     "Build the line in one cout chain: \"7 x \" << i << \" = \" << 7 * i << \"\\n\"",
     "Everything goes inside the loop braces - nothing after them."
   ],
   "solution": r"""#include <iostream>

int main() {
    for (int i = 1; i <= 5; ++i) {
        std::cout << "7 x " << i << " = " << 7 * i << "\n";
    }
    return 0;
}"""
 },
 "mistake": "Off-by-one: using i <= 5 when you wanted 0..4, or i < 5 when you wanted 1..5. Decide the first and last value before writing the loop.",
 "recap": "for is for a known repeat count; it holds start, limit and step in one line."
},
{
 "id": "b11", "level": "beginner", "title": "Functions: giving code a name", "minutes": 13,
 "tags": ["functions", "void"],
 "goal": "Move repeated code into a function and call it by name.",
 "explain": [
   "A function is a named block of code. You write it once and call it as many times as you like, which makes main short and readable.",
   "void means the function gives nothing back - it just does something. The call is the name plus brackets: cheer(); The brackets are not optional, they are what makes it a call."
 ],
 "example": {
   "title": "A cheer function",
   "code": r"""#include <iostream>

void cheer() {
    std::cout << "Go Ana!\n";
    std::cout << "Go Ben!\n";
}

void line(int length) {
    for (int i = 0; i < length; ++i) {
        std::cout << "-";
    }
    std::cout << "\n";
}

int main() {
    line(20);
    cheer();
    line(20);
    cheer();
    return 0;
}""",
   "output": "--------------------\nGo Ana!\nGo Ben!\n--------------------\nGo Ana!\nGo Ben!\n",
   "notes": [
     ["void cheer()", "no parameters, and void because nothing comes back"],
     ["void line(int length)", "takes one number, so the same function can draw any width"],
     ["cheer();", "the call - brackets required"]
   ]
 },
 "predict": {
   "q": "How many lines of ben are printed in total?",
   "options": ["2", "4", "8"],
   "answer": 1,
   "why": "cheer() is called twice and prints two lines each time, so four lines."
 },
 "quiz": [
   {"q": "What does void mean in a function's signature?",
    "options": ["The function returns nothing", "The function takes no parameters", "The function is empty"],
    "answer": 0,
    "why": "void is the return type. A function with no parameters simply has empty brackets, like cheer()."},
   {"q": "Where must a function be defined if main calls it?",
    "options": ["After main is fine", "Before main, or declared with a prototype above main", "Inside main"],
    "answer": 1,
    "why": "The compiler reads top to bottom, so it must know the function before the call - either the whole body or a one-line prototype."},
   {"q": "Why use a function instead of copying the same lines?",
    "options": ["It runs faster than copying", "One place to change, and main stays readable", "C++ forbids long mains"],
    "answer": 1,
    "why": "Duplicated code drifts apart when you fix one copy and forget the other. A function has a single definition."}
 ],
 "activity": {
   "goal": "Write a function banner() that prints three lines: \"=====\", \"Five Sides\", \"=====\". Call it twice.",
   "starter": r"""#include <iostream>

// TODO: write void banner() above main

int main() {
    // TODO: call banner() twice
    return 0;
}""",
   "expected": "=====\nFive Sides\n=====\n=====\nFive Sides\n=====\n",
   "hints": [
     "The function must be defined before main, or main will not know it.",
     "Three cout lines inside the function body.",
     "Call it exactly as written: banner();"
   ],
   "solution": r"""#include <iostream>

void banner() {
    std::cout << "=====\n";
    std::cout << "Five Sides\n";
    std::cout << "=====\n";
}

int main() {
    banner();
    banner();
    return 0;
}"""
 },
 "mistake": "Writing the call as cheer; without brackets - that mentions the function but never runs it, and usually compiles with a warning.",
 "recap": "A function is a named block you call with brackets; void means it returns nothing."
},
{
 "id": "b12", "level": "beginner", "title": "Functions that return values", "minutes": 14,
 "tags": ["functions", "return", "parameters"],
 "goal": "Pass information in and get an answer back.",
 "explain": [
   "Parameters are the inputs in the brackets; return sends a value back to whoever called. The return type replaces void: int area(int w, int h) gives back a whole number.",
   "Parameters are copies. Changing w inside the function does not change the caller's variable - that separation is what makes functions predictable."
 ],
 "example": {
   "title": "Area and average",
   "code": r"""#include <iostream>

int area(int w, int h) {
    return w * h;
}

double average(int a, int b) {
    return (a + b) / 2.0;
}

bool is_pass(int score) {
    return score >= 60;
}

int main() {
    std::cout << "Area " << area(3, 4) << "\n";
    std::cout << "Average " << average(7, 10) << "\n";
    std::cout << "Pass? " << is_pass(72) << "\n";
    return 0;
}""",
   "output": "Area 12\nAverage 8.5\nPass? 1\n",
   "notes": [
     ["int area(int w, int h)", "two inputs, one int answer"],
     ["return (a + b) / 2.0;", "the 2.0 forces decimal division"],
     ["is_pass(72)", "the returned bool prints as 1"]
   ]
 },
 "predict": {
   "q": "What does area(3, 4) return, and what does main do with it?",
   "options": ["Nothing; it only prints", "It returns 12, and main prints that value", "It returns 3 and 4"],
   "answer": 1,
   "why": "return hands the value back to the call site, so the call area(3, 4) can be used like a number."
 },
 "quiz": [
   {"q": "What happens after a return statement runs?",
    "options": ["The function continues to the next line", "The function ends immediately and hands back the value", "Only loops stop"],
    "answer": 1,
    "why": "return exits the function at once. Any lines after it in that function never run."},
   {"q": "Why is average written with 2.0 rather than 2?",
    "options": ["It looks nicer", "So the division is decimal instead of integer", "Because doubles are faster"],
    "answer": 1,
    "why": "int / int throws away the fraction. Dividing by 2.0 makes the result a double."},
   {"q": "If a function is declared int but has no return, what happens?",
    "options": ["It returns 0 automatically", "Undefined behaviour - the compiler warns", "It becomes void"],
    "answer": 1,
    "why": "The value returned would be whatever was in memory. Always return a value from a non-void function."}
 ],
 "activity": {
   "goal": "Write int square(int n) that returns n*n, then print square(9).",
   "starter": r"""#include <iostream>

// TODO: int square(int n)

int main() {
    // TODO: print square(9)
    return 0;
}""",
   "expected": "81\n",
   "hints": [
     "The return type is int and there is one parameter.",
     "Inside, return n * n;",
     "In main: std::cout << square(9) << \"\\n\";"
   ],
   "solution": r"""#include <iostream>

int square(int n) {
    return n * n;
}

int main() {
    std::cout << square(9) << "\n";
    return 0;
}"""
 },
 "mistake": "Forgetting the return type change: writing void square(...) but then trying to print its result.",
 "recap": "Parameters carry values in, return carries one value out."
},
{
 "id": "b13", "level": "beginner", "title": "Working with text", "minutes": 14,
 "tags": ["string", "size", "index"],
 "goal": "Join, measure and pick apart std::string values.",
 "explain": [
   "std::string holds text of any length and grows as needed. + joins two strings, .size() counts the characters, and square brackets read one character by position.",
   "Positions start at 0, so the first character is [0]. Reading past the end is undefined behaviour, not a friendly error - check size() first."
 ],
 "example": {
   "title": "Building a name",
   "code": r"""#include <iostream>
#include <string>

int main() {
    std::string first = "Ana";
    std::string last = "Cruz";
    std::string full = first + " " + last;

    std::cout << full << "\n";
    std::cout << "letters: " << full.size() << "\n";
    std::cout << "first letter: " << full[0] << "\n";
    std::cout << "last letter: " << full[full.size() - 1] << "\n";

    full += "!";
    std::cout << full << "\n";
    return 0;
}""",
   "output": "Ana Cruz\nletters: 8\nfirst letter: A\nlast letter: z\nAna Cruz!\n",
   "notes": [
     ["first + \" \" + last", "+ joins strings end to end"],
     ["full.size()", "the number of characters, spaces included"],
     ["full[0]", "positions start at zero"]
   ]
 },
 "predict": {
   "q": "What is \"Ana\".size()?",
   "options": ["2", "3", "4"],
   "answer": 1,
   "why": "A-n-a is three characters. There is no hidden terminator counted by size()."
 },
 "quiz": [
   {"q": "How do you read the third character?",
    "options": ["s[3]", "s[2]", "s(2)"],
    "answer": 1,
    "why": "Counting starts at 0, so third means index 2. s(2) would look like a function call."},
   {"q": "What does s += \"x\" do?",
    "options": ["Compares s with x", "Appends x to the end of s", "Creates a new string"],
    "answer": 1,
    "why": "+= on a string is append; the string itself changes."},
   {"q": "Why is std::string better than a char array?",
    "options": ["It is always faster", "It knows its own length and grows automatically", "It can hold numbers too"],
    "answer": 1,
    "why": "Fixed arrays need you to track the length and can overflow. std::string manages both for you."}
 ],
 "activity": {
   "goal": "Print a robot's name in capitals, then its length, then the first and last letters.",
   "starter": r"""#include <iostream>
#include <string>

int main() {
    std::string name = "five sides";
    // TODO: make it uppercase with a loop and <cctype> (std::toupper)
    // TODO: print the name, its size, first and last letter
    return 0;
}""",
   "expected": "FIVE SIDES\n10\nF\nS\n",
   "hints": [
     "Include <cctype> for std::toupper.",
     "A for loop over positions: for (std::size_t i = 0; i < name.size(); ++i)",
     "Replace each character: name[i] = static_cast<char>(std::toupper(name[i]));"
   ],
   "solution": r"""#include <iostream>
#include <string>
#include <cctype>

int main() {
    std::string name = "five sides";

    for (std::size_t i = 0; i < name.size(); ++i) {
        name[i] = static_cast<char>(std::toupper(name[i]));
    }

    std::cout << name << "\n";
    std::cout << name.size() << "\n";
    std::cout << name[0] << "\n";
    std::cout << name[name.size() - 1] << "\n";
    return 0;
}"""
 },
 "mistake": "Using <= in a loop over a string: for (i = 0; i <= s.size(); ++i) reads one character past the end.",
 "recap": "Strings join with +, count with size(), and index from zero."
},
{
 "id": "b14", "level": "beginner", "title": "Project: score tracker", "minutes": 25,
 "tags": ["project", "debugging", "arrays"],
 "goal": "Combine variables, loops, conditions and functions into one small working program.",
 "explain": [
   "This project keeps three scores and reports the best, the average and how many passed. It uses one array, two loops and two functions - everything from the beginner track.",
   "Build it in stages: first print all scores, then find the best, then the average. Run it after each stage. Small steps that work beat one big step that does not."
 ],
 "example": {
   "title": "score_tracker.cpp",
   "code": r"""#include <iostream>
#include <string>

int best_index(const int scores[], int count) {
    int best = 0;
    for (int i = 1; i < count; ++i) {
        if (scores[i] > scores[best]) {
            best = i;
        }
    }
    return best;
}

int total_of(const int scores[], int count) {
    int total = 0;
    for (int i = 0; i < count; ++i) {
        total += scores[i];
    }
    return total;
}

int main() {
    const int COUNT = 3;
    std::string names[COUNT] = {"Ana", "Ben", "Robot"};
    int scores[COUNT] = {88, 95, 70};

    for (int i = 0; i < COUNT; ++i) {
        std::cout << names[i] << ": " << scores[i] << "\n";
    }

    int top = best_index(scores, COUNT);
    std::cout << "Top: " << names[top] << " " << scores[top] << "\n";

    int total = total_of(scores, COUNT);
    std::cout << "Average: " << total / COUNT << "\n";

    int passed = 0;
    for (int i = 0; i < COUNT; ++i) {
        if (scores[i] >= 75) {
            ++passed;
        }
    }
    std::cout << "Passed: " << passed << "\n";
    return 0;
}""",
   "output": "Ana: 88\nBen: 95\nRobot: 70\nTop: Ben 95\nAverage: 84\nPassed: 2\n",
   "notes": [
     ["best_index(...)", "returns a position, not a value - so main can print the name too"],
     ["total / COUNT", "both ints, so the average is whole; use 1.0 * total / COUNT for decimals"],
     ["scores[i] >= 75", "the pass rule lives in exactly one place"]
   ]
 },
 "predict": {
   "q": "If Ben's score dropped to 60, what would the output line Average say?",
   "options": ["Average: 72", "Average: 73", "Average: 72.66"],
   "answer": 0,
   "why": "88 + 60 + 70 = 218, and 218 / 3 is 72 in integer division. The fraction is dropped, not rounded."
 },
 "quiz": [
   {"q": "Why does best_index return a position instead of the score?",
    "options": ["Positions are faster", "So main can print the matching name", "Because ints cannot be returned"],
    "answer": 1,
    "why": "The name and the score are two arrays. Knowing the position lets you read both."},
   {"q": "What does the program print if all three scores are equal?",
    "options": ["Top: Ana with the first score", "Nothing", "A compile error"],
    "answer": 0,
    "why": "The comparison is >, not >=, so the first index stays the best when nothing is greater."},
   {"q": "Where would you change the pass mark from 75 to 80?",
    "options": ["In the array", "In the one if statement that tests it", "In best_index"],
    "answer": 1,
    "why": "The rule exists once, in main's counting loop. That is the benefit of not duplicating logic."}
 ],
 "activity": {
   "goal": "Extend the tracker: add a fourth score (a second robot, 60) and print \"Lowest: \" with the lowest name and score.",
   "starter": r"""#include <iostream>
#include <string>

int main() {
    const int COUNT = 4;
    std::string names[COUNT] = {"Ana", "Ben", "Robot", "Spare"};
    int scores[COUNT] = {88, 95, 70, 60};

    // TODO: print each name and score
    // TODO: find the lowest and print Lowest: name score
    return 0;
}""",
   "expected": "Ana: 88\nBen: 95\nRobot: 70\nSpare: 60\nLowest: Spare 60\n",
   "hints": [
     "Start with low = 0 and compare with < this time.",
     "Loop from i = 1 to COUNT - 1, updating low when scores[i] < scores[low].",
     "Remember to print with names[low] and scores[low], not low itself."
   ],
   "solution": r"""#include <iostream>
#include <string>

int main() {
    const int COUNT = 4;
    std::string names[COUNT] = {"Ana", "Ben", "Robot", "Spare"};
    int scores[COUNT] = {88, 95, 70, 60};

    for (int i = 0; i < COUNT; ++i) {
        std::cout << names[i] << ": " << scores[i] << "\n";
    }

    int low = 0;
    for (int i = 1; i < COUNT; ++i) {
        if (scores[i] < scores[low]) {
            low = i;
        }
    }
    std::cout << "Lowest: " << names[low] << " " << scores[low] << "\n";
    return 0;
}"""
 },
 "mistake": "Building the whole project before running it once. Compile after every small addition so the error is always in the lines you just wrote.",
 "recap": "Small working steps plus one rule in one place is how a real program gets built."
}
]
