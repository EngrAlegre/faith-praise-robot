"""Intermediate track: 12 lessons - collections, your own types, files."""

LESSONS = [
{
 "id": "i01", "level": "intermediate", "title": "Arrays: many values, one name", "minutes": 14,
 "tags": ["arrays", "sizeof"],
 "goal": "Store a row of values and walk through them with a loop.",
 "explain": [
   "An array holds a fixed number of values of the same type, one after another in memory. int temps[4] makes four boxes, reached as temps[0] to temps[3].",
   "The size is fixed at compile time and the array does not know its own length in a useful way - you keep the count in a separate constant. The first index is 0, so the last one is size - 1."
 ],
 "example": {
   "title": "Four days of temperature",
   "code": r"""#include <iostream>

int main() {
    const int SIZE = 4;
    int temps[SIZE] = {28, 31, 30, 33};

    for (int i = 0; i < SIZE; ++i) {
        std::cout << "day " << i + 1 << ": " << temps[i] << "\n";
    }

    int hottest = temps[0];
    for (int i = 1; i < SIZE; ++i) {
        if (temps[i] > hottest) {
            hottest = temps[i];
        }
    }
    std::cout << "hottest " << hottest << "\n";
    std::cout << "bytes " << sizeof(temps) << "\n";
    return 0;
}""",
   "output": "day 1: 28\nday 2: 31\nday 3: 30\nday 4: 33\nhottest 33\nbytes 16\n",
   "notes": [
     ["int temps[SIZE]", "SIZE must be a compile-time constant, not a variable that changes"],
     ["temps[0]", "the first box, not the zeroth - counting starts at zero"],
     ["sizeof(temps)", "four ints of 4 bytes each = 16"]
   ]
 },
 "predict": {
   "q": "What does temps[4] do when the array has 4 elements?",
   "options": ["Returns the last value", "Reads memory past the array - undefined behaviour", "Throws an error you can catch"],
   "answer": 1,
   "why": "Valid indexes are 0..3. There is no bounds check at run time, so index 4 reads whatever follows in memory."
 },
 "quiz": [
   {"q": "How many elements does int a[5] hold?",
    "options": ["4", "5", "6"],
    "answer": 1,
    "why": "The number in the brackets is the count, and valid indexes are 0 to 4."},
   {"q": "Why keep the size in a named constant?",
    "options": ["It runs faster", "One place to change, and loops cannot disagree with the array", "Arrays require it"],
    "answer": 1,
    "why": "If the size lives in one constant, changing it updates the declaration and every loop together."},
   {"q": "What is the last valid index of an array with n elements?",
    "options": ["n", "n - 1", "0"],
    "answer": 1,
    "why": "Starting at 0 shifts everything down by one, so n elements end at n-1."}
 ],
 "activity": {
   "goal": "Given five step counts, print the total and the average using a loop.",
   "starter": r"""#include <iostream>

int main() {
    const int DAYS = 5;
    int steps[DAYS] = {4200, 8100, 5600, 9000, 3100};
    // TODO: total with a loop
    // TODO: print "Total: " and "Average: "
    return 0;
}""",
   "expected": "Total: 30000\nAverage: 6000\n",
   "hints": [
     "Start an int total = 0; before the loop and add each element inside.",
     "Loop with for (int i = 0; i < DAYS; ++i).",
     "The average is total / DAYS - both ints, so it stays whole."
   ],
   "solution": r"""#include <iostream>

int main() {
    const int DAYS = 5;
    int steps[DAYS] = {4200, 8100, 5600, 9000, 3100};

    int total = 0;
    for (int i = 0; i < DAYS; ++i) {
        total += steps[i];
    }
    std::cout << "Total: " << total << "\n";
    std::cout << "Average: " << total / DAYS << "\n";
    return 0;
}"""
 },
 "mistake": "Looping to i <= SIZE, which reads one element past the end. The comparison is always < SIZE.",
 "recap": "An array is a fixed row of values indexed from 0 to size-1."
},
{
 "id": "i02", "level": "intermediate", "title": "Vectors: the array that grows", "minutes": 14,
 "tags": ["vector", "range-for"],
 "goal": "Use std::vector when you do not know the size in advance.",
 "explain": [
   "std::vector is an array that knows its length and can grow. push_back adds to the end, pop_back removes the last, size() tells you how many there are.",
   "The range-for loop for (int s : scores) visits every element without any index arithmetic - use it when you do not need the position."
 ],
 "example": {
   "title": "A growing list of scores",
   "code": r"""#include <iostream>
#include <vector>

int main() {
    std::vector<int> scores;

    scores.push_back(88);
    scores.push_back(95);
    scores.push_back(70);

    std::cout << "count " << scores.size() << "\n";
    for (int s : scores) {
        std::cout << s << " ";
    }
    std::cout << "\n";

    scores.pop_back();
    std::cout << "after pop " << scores.size() << "\n";
    std::cout << "front " << scores.front() << " back " << scores.back() << "\n";
    return 0;
}""",
   "output": "count 3\n88 95 70 \nafter pop 2\nfront 88 back 95\n",
   "notes": [
     ["std::vector<int> scores;", "an empty vector that grows as needed"],
     ["push_back(88)", "adds one element at the end"],
     ["for (int s : scores)", "visits each value in turn"]
   ]
 },
 "predict": {
   "q": "What does scores[10] do on a vector with 3 elements?",
   "options": ["Adds a 10th element", "Undefined behaviour, unlike .at(10) which throws", "Returns 0"],
   "answer": 1,
   "why": "operator[] does not check. .at() does check and throws std::out_of_range, which is why it is the safer choice while learning."
 },
 "quiz": [
   {"q": "Which adds 7 to the end of v?",
    "options": ["v.add(7)", "v.push_back(7)", "v[7] = 0"],
    "answer": 1,
    "why": "push_back appends. v[7] writes at an index that does not exist yet - a serious bug."},
   {"q": "What is the difference between size() and capacity()?",
    "options": ["They are the same", "size is how many you have, capacity is how many fit before it grows", "capacity is the number of bytes"],
    "answer": 1,
    "why": "Vectors over-allocate so push_back is usually cheap; capacity reports that reserved room."},
   {"q": "When is a fixed array a better choice than a vector?",
    "options": ["Never", "When the count is known at compile time and never changes", "When the data is numbers"],
    "answer": 1,
    "why": "A fixed array has no bookkeeping and no allocation, which matters in small embedded code."}
 ],
 "activity": {
   "goal": "Read numbers until the user types -1, store them in a vector, then print the count and the biggest.",
   "starter": r"""#include <iostream>
#include <vector>

int main() {
    std::vector<int> values;
    int n = 0;
    // TODO: while (cin >> n && n != -1) push_back
    // TODO: print "Count: " and "Biggest: "
    return 0;
}""",
   "expected": "Count: 3\nBiggest: 42\n",
   "stdin": "10 42 7 -1\n",
   "hints": [
     "The read itself can be the loop condition: while (std::cin >> n && n != -1)",
     "push_back each n that survives the condition.",
     "Track the biggest as you go with if (n > biggest) biggest = n;"
   ],
   "solution": r"""#include <iostream>
#include <vector>

int main() {
    std::vector<int> values;
    int n = 0;

    while (std::cin >> n && n != -1) {
        values.push_back(n);
    }

    int biggest = 0;
    for (int v : values) {
        if (v > biggest) {
            biggest = v;
        }
    }

    std::cout << "Count: " << values.size() << "\n";
    std::cout << "Biggest: " << biggest << "\n";
    return 0;
}"""
 },
 "mistake": "Using a range-for loop while adding or removing elements. The range is captured once, so the loop can read memory that has moved.",
 "recap": "vector grows, knows its size, and pairs with range-for."
},
{
 "id": "i03", "level": "intermediate", "title": "References: another name for the same box", "minutes": 14,
 "tags": ["references", "parameters"],
 "goal": "Change the caller's variable from inside a function.",
 "explain": [
   "A reference is an alias. int& score means 'score is another name for the caller's variable', so writing to it writes to the original.",
   "Without the &, the parameter is a copy and the caller never sees the change. Use const & when you only want to read a big object without copying it."
 ],
 "example": {
   "title": "By value versus by reference",
   "code": r"""#include <iostream>

void add_points(int& score, int amount) {
    score += amount;
}

void add_points_copy(int score, int amount) {
    score += amount;
}

int main() {
    int ana = 10;

    add_points(ana, 5);
    std::cout << "ana " << ana << "\n";

    add_points_copy(ana, 5);
    std::cout << "after copy " << ana << "\n";
    return 0;
}""",
   "output": "ana 15\nafter copy 15\n",
   "notes": [
     ["int& score", "a reference - no copy is made"],
     ["score += amount;", "this writes to ana itself"],
     ["add_points_copy", "its score is a separate box that dies when the function ends"]
   ]
 },
 "predict": {
   "q": "Why does the second call change nothing?",
   "options": ["Because 5 is too small", "Because the parameter is a copy of ana, not ana itself", "Because void functions cannot change anything"],
   "answer": 1,
   "why": "The copy is modified and then destroyed when the function returns; the original is untouched."
 },
 "quiz": [
   {"q": "What does int& mean in a parameter list?",
    "options": ["An optional parameter", "A reference: the caller's variable, not a copy", "A pointer that can be null"],
    "answer": 1,
    "why": "A reference must be bound to an existing object and cannot be null, unlike a pointer."},
   {"q": "Why use const std::string& as a parameter?",
    "options": ["To prevent the function reading it", "To avoid copying a long string while still forbidding changes", "Because strings must be const"],
    "answer": 1,
    "why": "const & is the standard way to pass something big cheaply and safely."},
   {"q": "Can a reference be re-bound to a different variable later?",
    "options": ["Yes", "No - it is bound for its whole life", "Only inside loops"],
    "answer": 1,
    "why": "Assignment through a reference changes the value it refers to, never which object it refers to."}
 ],
 "activity": {
   "goal": "Write void double_it(int& n) that doubles the caller's number, and use it on 21.",
   "starter": r"""#include <iostream>

// TODO: void double_it(int& n)

int main() {
    int value = 21;
    // TODO: call double_it(value) twice, printing after each call
    return 0;
}""",
   "expected": "42\n84\n",
   "hints": [
     "The parameter must be int& with the ampersand, or the caller sees nothing.",
     "Inside: n = n * 2;",
     "Call it once, print, call again, print."
   ],
   "solution": r"""#include <iostream>

void double_it(int& n) {
    n = n * 2;
}

int main() {
    int value = 21;
    double_it(value);
    std::cout << value << "\n";
    double_it(value);
    std::cout << value << "\n";
    return 0;
}"""
 },
 "mistake": "Returning a reference to a local variable. The local dies at the end of the function and the reference points at nothing.",
 "recap": "& binds a second name to the same object; const & reads without copying."
},
{
 "id": "i04", "level": "intermediate", "title": "Pointers: the address of a value", "minutes": 15,
 "tags": ["pointers", "nullptr"],
 "goal": "Read a pointer, follow it, and know what nullptr means.",
 "explain": [
   "A pointer stores an address. int* p = &battery; puts the address of battery into p, and *p reads the value at that address.",
   "The same * means two things: in a declaration it marks the type as 'pointer to int'; in an expression it dereferences. nullptr means 'points at nothing' and is the correct empty value."
 ],
 "example": {
   "title": "Following an address",
   "code": r"""#include <iostream>

int main() {
    int battery = 87;
    int* p = &battery;

    std::cout << "value " << battery << "\n";
    std::cout << "through pointer " << *p << "\n";

    *p = 50;
    std::cout << "after write " << battery << "\n";

    int* empty = nullptr;
    std::cout << "is null " << (empty == nullptr) << "\n";
    return 0;
}""",
   "output": "value 87\nthrough pointer 87\nafter write 50\nis null 1\n",
   "notes": [
     ["int* p = &battery;", "& takes the address of battery"],
     ["*p", "dereference: go to the address and read what is there"],
     ["*p = 50;", "writing through the pointer writes to battery"],
     ["nullptr", "the empty pointer - always check before dereferencing"]
   ]
 },
 "predict": {
   "q": "What happens if you dereference a nullptr?",
   "options": ["You get 0", "The program crashes - undefined behaviour", "It returns nullptr again"],
   "answer": 1,
   "why": "There is no object at that address. On Windows this is an access violation, which ends the program immediately."
 },
 "quiz": [
   {"q": "What does &x give you?",
    "options": ["The value of x", "The address of x", "A copy of x"],
    "answer": 1,
    "why": "& is the address-of operator. In a declaration it also makes a reference - context decides which meaning."},
   {"q": "Which is the safest empty pointer?",
    "options": ["NULL", "0", "nullptr"],
    "answer": 2,
    "why": "nullptr has its own type and cannot be confused with an integer, so overloads resolve correctly."},
   {"q": "Why are pointers considered risky for beginners?",
    "options": ["They are slow", "An invalid pointer still compiles and crashes later, or silently corrupts memory", "They cannot point at numbers"],
    "answer": 1,
    "why": "Nothing checks that a pointer is valid. That is why modern C++ prefers references and smart pointers."}
 ],
 "activity": {
   "goal": "Write void boost(int* p) that adds 10 through the pointer, and call it on a score of 30.",
   "starter": r"""#include <iostream>

// TODO: void boost(int* p)

int main() {
    int score = 30;
    // TODO: call boost with the address of score
    // TODO: print "Score: " and the value
    return 0;
}""",
   "expected": "Score: 40\n",
   "hints": [
     "The function takes int* and changes *p inside.",
     "Pass the address: boost(&score);",
     "Inside: *p += 10;"
   ],
   "solution": r"""#include <iostream>

void boost(int* p) {
    *p += 10;
}

int main() {
    int score = 30;
    boost(&score);
    std::cout << "Score: " << score << "\n";
    return 0;
}"""
 },
 "mistake": "Confusing & in a declaration (int& r - a reference) with & in an expression (&x - the address). Same symbol, different job.",
 "recap": "A pointer holds an address; * follows it and & takes it."
},
{
 "id": "i05", "level": "intermediate", "title": "Structs: grouping facts together", "minutes": 14,
 "tags": ["struct", "aggregate"],
 "goal": "Bundle related values into one type of your own.",
 "explain": [
   "A struct is your own type made of named parts. Once a Robot has a name, a battery and an awake flag, you can pass one Robot around instead of three separate variables.",
   "Structs are usually written in a header so every file can use them. Members are public by default, which is the main difference from a class."
 ],
 "example": {
   "title": "Two robots",
   "code": r"""#include <iostream>
#include <string>

struct Robot {
    std::string name;
    int battery;
    bool awake;
};

void report(const Robot& r) {
    std::cout << r.name << " battery " << r.battery
              << (r.awake ? " awake" : " asleep") << "\n";
}

int main() {
    Robot five{"Five Sides", 87, true};
    Robot spare{"Spare", 12, false};

    report(five);
    report(spare);

    five.battery -= 30;
    report(five);
    return 0;
}""",
   "output": "Five Sides battery 87 awake\nSpare battery 12 asleep\nFive Sides battery 57 awake\n",
   "notes": [
     ["struct Robot { ... };", "a new type - note the semicolon after the closing brace"],
     ["{\"Five Sides\", 87, true}", "members are filled in the order they are declared"],
     ["const Robot& r", "pass by reference so nothing is copied"]
   ]
 },
 "predict": {
   "q": "What does five.battery -= 30 do to the Robot in main?",
   "options": ["Nothing, because report took a const reference", "It changes five, because five is the object itself", "It creates a copy"],
   "answer": 1,
   "why": "The change happens in main on the real object, before report is ever called. The const& only protects r inside report."
 },
 "quiz": [
   {"q": "What is the difference between a struct and a class in C++?",
    "options": ["None at all", "Struct members are public by default; class members are private by default", "Classes can hold functions, structs cannot"],
    "answer": 1,
    "why": "That is the only language-level difference. Both can have methods, constructors and inheritance."},
   {"q": "Why prefer a vector<Robot> over three parallel arrays?",
    "options": ["It uses less memory", "The pieces of one robot stay together and nothing can drift out of step", "Vectors are always faster"],
    "answer": 1,
    "why": "Parallel arrays break the moment you sort one of them - the name and its score stop matching."},
   {"q": "What does the semicolon after a struct's closing brace do?",
    "options": ["Nothing, it is optional", "It ends the type definition - required", "It creates an instance"],
    "answer": 1,
    "why": "A struct definition is a statement and needs its semicolon. Forgetting it produces confusing errors."}
 ],
 "activity": {
   "goal": "Add a level member (int) to Robot, fill in two robots, and print \"name level battery\" for each.",
   "starter": r"""#include <iostream>
#include <string>

struct Robot {
    std::string name;
    int level;
    int battery;
};

int main() {
    // TODO: two Robots with levels 3 and 1
    // TODO: print each as name level battery
    return 0;
}""",
   "expected": "Five Sides 3 87\nSpare 1 40\n",
   "hints": [
     "Aggregate initialisation follows member order: name, level, battery.",
     "Robot a{\"Five Sides\", 3, 87};",
     "Print with a.name << \" \" << a.level << \" \" << a.battery << \"\\n\"."
   ],
   "solution": r"""#include <iostream>
#include <string>

struct Robot {
    std::string name;
    int level;
    int battery;
};

int main() {
    Robot a{"Five Sides", 3, 87};
    Robot b{"Spare", 1, 40};

    std::cout << a.name << " " << a.level << " " << a.battery << "\n";
    std::cout << b.name << " " << b.level << " " << b.battery << "\n";
    return 0;
}"""
 },
 "mistake": "Declaring a struct with the same name as a variable, or forgetting that aggregate initialisers are positional - add a member in the middle and every initialiser shifts.",
 "recap": "A struct is a named bundle of values you can copy, pass and store."
},
{
 "id": "i06", "level": "intermediate", "title": "Classes: data plus behaviour", "minutes": 16,
 "tags": ["class", "constructor", "methods"],
 "goal": "Attach functions to your type and guarantee it starts in a valid state.",
 "explain": [
   "A class is a struct that also owns its behaviour. The constructor runs when the object is created, so an object can never exist half-built.",
   "Member functions that do not change the object are marked const, which lets them be called on const objects and documents your intent. The trailing _ on member names is a common convention to tell them apart from parameters."
 ],
 "example": {
   "title": "A counter that cannot be uninitialised",
   "code": r"""#include <iostream>
#include <string>

class Counter {
public:
    explicit Counter(std::string name) : name_(std::move(name)), count_(0) {}

    void add(int n) { count_ += n; }

    int value() const { return count_; }
    const std::string& name() const { return name_; }

private:
    std::string name_;
    int count_;
};

int main() {
    Counter jumps{"jumps"};
    jumps.add(3);
    jumps.add(2);

    std::cout << jumps.name() << " " << jumps.value() << "\n";
    return 0;
}""",
   "output": "jumps 5\n",
   "notes": [
     ["Counter(std::string name)", "the constructor - same name as the class, no return type"],
     [": name_(std::move(name)), count_(0)", "initialiser list: members are built directly, in declaration order"],
     ["int value() const", "const promises this function does not change the object"]
   ]
 },
 "predict": {
   "q": "What is printed if you delete count_(0) from the initialiser list?",
   "options": ["It still prints 0", "The count starts at an unpredictable value", "It fails to compile"],
   "answer": 1,
   "why": "An int member is left uninitialised by default. The class would compile and then print junk."
 },
 "quiz": [
   {"q": "When does a constructor run?",
    "options": ["When the object is destroyed", "When the object is created", "Only when you call it by name"],
    "answer": 1,
    "why": "Construction is automatic at the point of creation - that is the whole point of a constructor."},
   {"q": "What does the const at the end of a method signature mean?",
    "options": ["The method returns a constant", "The method does not modify the object", "The method cannot be called twice"],
    "answer": 1,
    "why": "It makes this const, so the compiler enforces that no member is changed inside."},
   {"q": "Why mark a single-argument constructor explicit?",
    "options": ["It runs faster", "It stops the compiler silently converting a value into your type", "It is required for classes"],
    "answer": 1,
    "why": "Without explicit, a function taking Counter could be called with a string and the conversion would happen invisibly."}
 ],
 "activity": {
   "goal": "Write a class Battery with charge_ (int) starting at 100, a use(int) method that subtracts but never goes below 0, and level() const.",
   "starter": r"""#include <iostream>

class Battery {
public:
    Battery() {
        // TODO: start at 100
    }
    void use(int amount) {
        // TODO: subtract, clamped at 0
    }
    int level() const { return charge_; }
private:
    int charge_ = 100;
};

int main() {
    Battery b;
    // TODO: use 30, print level; use 100, print level
    return 0;
}""",
   "expected": "70\n0\n",
   "hints": [
     "charge_ already starts at 100, so the constructor body can stay empty - or use an initialiser list.",
     "Clamp with if (charge_ - amount < 0) charge_ = 0; else charge_ -= amount;",
     "Print b.level() after each use."
   ],
   "solution": r"""#include <iostream>

class Battery {
public:
    Battery() = default;

    void use(int amount) {
        if (amount >= charge_) {
            charge_ = 0;
        } else {
            charge_ -= amount;
        }
    }

    int level() const { return charge_; }

private:
    int charge_ = 100;
};

int main() {
    Battery b;
    b.use(30);
    std::cout << b.level() << "\n";
    b.use(100);
    std::cout << b.level() << "\n";
    return 0;
}"""
 },
 "mistake": "Assigning members inside the constructor body when an initialiser list would do - members are built first anyway, so the body assignment is a second write.",
 "recap": "A class keeps data private and guarantees a valid state through its constructor."
},
{
 "id": "i07", "level": "intermediate", "title": "Encapsulation: protecting the rules", "minutes": 14,
 "tags": ["encapsulation", "private", "invariants"],
 "goal": "Keep an object's rules true by refusing bad changes.",
 "explain": [
   "Encapsulation means the outside world asks your object to do things instead of reaching into its data. The object can then refuse anything that would break its own rules.",
   "A rule that must always hold is called an invariant. Here the invariant is 'the balance is never negative', and withdraw() is the only way to change it."
 ],
 "example": {
   "title": "A wallet that cannot go negative",
   "code": r"""#include <iostream>

class Wallet {
public:
    explicit Wallet(int start) : balance_(start) {}

    bool withdraw(int amount) {
        if (amount <= 0 || amount > balance_) {
            return false;
        }
        balance_ -= amount;
        return true;
    }

    void deposit(int amount) {
        if (amount > 0) {
            balance_ += amount;
        }
    }

    int balance() const { return balance_; }

private:
    int balance_;
};

int main() {
    Wallet w{100};

    std::cout << (w.withdraw(50) ? "ok " : "denied ") << w.balance() << "\n";
    std::cout << (w.withdraw(100) ? "ok " : "denied ") << w.balance() << "\n";
    w.deposit(-5);
    std::cout << "after bad deposit " << w.balance() << "\n";
    return 0;
}""",
   "output": "ok 50\ndenied 50\nafter bad deposit 50\n",
   "notes": [
     ["bool withdraw(...)", "returns whether it worked, so callers can react"],
     ["amount <= 0 || amount > balance_", "both rules checked before touching the data"],
     ["private:", "nothing outside the class can write balance_ directly"]
   ]
 },
 "predict": {
   "q": "Why does the second withdraw print denied?",
   "options": ["Because 100 is not a valid number", "Because it is more than the remaining balance of 50", "Because withdraw can only be called once"],
   "answer": 1,
   "why": "The guard rejects any amount larger than the current balance, so nothing is subtracted."
 },
 "quiz": [
   {"q": "What is an invariant?",
    "options": ["A rule that must always be true for the object", "A variable that never changes", "A function that cannot fail"],
    "answer": 0,
    "why": "Invariants are the promises the class keeps; every public method must preserve them."},
   {"q": "Why return bool from withdraw instead of silently ignoring a bad amount?",
    "options": ["It is faster", "The caller can tell the difference between success and refusal", "bool is required by C++"],
    "answer": 1,
    "why": "Silent failure hides bugs. A return value lets the caller show a message or retry."},
   {"q": "What breaks encapsulation?",
    "options": ["A getter that returns a copy", "A public member the caller can write freely", "A const method"],
    "answer": 1,
    "why": "A public writable member lets anyone break the invariant without the class noticing."}
 ],
 "activity": {
   "goal": "Add a transfer(Wallet& other, int amount) method that moves money between wallets and refuses if the source is short.",
   "starter": r"""#include <iostream>

class Wallet {
public:
    explicit Wallet(int start) : balance_(start) {}

    bool withdraw(int amount) {
        if (amount <= 0 || amount > balance_) return false;
        balance_ -= amount;
        return true;
    }
    void deposit(int amount) {
        if (amount > 0) balance_ += amount;
    }
    int balance() const { return balance_; }

    // TODO: bool transfer(Wallet& other, int amount)

private:
    int balance_;
};

int main() {
    Wallet a{100};
    Wallet b{0};
    // TODO: transfer 30 a->b, print both; transfer 200 a->b, print both
    return 0;
}""",
   "expected": "70 30\ndenied\n70 30\n",
   "hints": [
     "A transfer is withdraw from this, then deposit into other - reuse the existing methods.",
     "Return false immediately if withdraw fails, before depositing.",
     "bool transfer(Wallet& other, int amount) { if (!withdraw(amount)) return false; other.deposit(amount); return true; }"
   ],
   "solution": r"""#include <iostream>

class Wallet {
public:
    explicit Wallet(int start) : balance_(start) {}

    bool withdraw(int amount) {
        if (amount <= 0 || amount > balance_) return false;
        balance_ -= amount;
        return true;
    }
    void deposit(int amount) {
        if (amount > 0) balance_ += amount;
    }
    int balance() const { return balance_; }

    bool transfer(Wallet& other, int amount) {
        if (!withdraw(amount)) {
            return false;
        }
        other.deposit(amount);
        return true;
    }

private:
    int balance_;
};

int main() {
    Wallet a{100};
    Wallet b{0};

    a.transfer(b, 30);
    std::cout << a.balance() << " " << b.balance() << "\n";

    if (!a.transfer(b, 200)) {
        std::cout << "denied\n";
    }
    std::cout << a.balance() << " " << b.balance() << "\n";
    return 0;
}"""
 },
 "mistake": "Adding a setBalance() 'just in case'. It hands the invariant back to the caller and every guarantee you built disappears.",
 "recap": "Private data plus checked methods keeps an object's rules true."
},
{
 "id": "i08", "level": "intermediate", "title": "map and set: looking things up", "minutes": 15,
 "tags": ["map", "set", "lookup"],
 "goal": "Store values by key and keep a collection of unique items.",
 "explain": [
   "std::map<Key, Value> keeps pairs sorted by key and finds them quickly. m[key] creates the entry if it is missing, which is convenient but can hide typos - count() or find() tell you whether a key really exists.",
   "std::set holds unique values in sorted order and drops duplicates automatically. Both are usually implemented as balanced trees, so lookups are logarithmic rather than a scan."
 ],
 "example": {
   "title": "Scores by name",
   "code": r"""#include <iostream>
#include <map>
#include <set>
#include <string>

int main() {
    std::map<std::string, int> scores;
    scores["Ana"] = 88;
    scores["Ben"] = 95;
    scores["Ana"] += 2;

    std::cout << "Ana " << scores["Ana"] << "\n";
    std::cout << "count " << scores.size() << "\n";
    std::cout << "has Robot " << scores.count("Robot") << "\n";

    for (const auto& [name, score] : scores) {
        std::cout << name << "=" << score << " ";
    }
    std::cout << "\n";

    std::set<int> unique{3, 1, 3, 2};
    std::cout << "set size " << unique.size() << "\n";
    for (int v : unique) {
        std::cout << v << " ";
    }
    std::cout << "\n";
    return 0;
}""",
   "output": "Ana 90\ncount 2\nhas Robot 0\nAna=90 Ben=95 \nset size 3\n1 2 3 \n",
   "notes": [
     ["scores[\"Ana\"] += 2;", "creates on first use, then updates"],
     ["scores.count(\"Robot\")", "0 or 1 - a safe existence check"],
     ["const auto& [name, score]", "structured binding: unpacks the pair"]
   ]
 },
 "predict": {
   "q": "What does scores[\"Robot\"] do if Robot was never added?",
   "options": ["Throws an exception", "Creates Robot with value 0 and returns it", "Returns -1"],
   "answer": 1,
   "why": "operator[] default-constructs the missing value. Use .at() to throw instead, or .count() to check first."
 },
 "quiz": [
   {"q": "Which is safe when the key might not exist?",
    "options": ["m[key]", "m.at(key) or m.find(key)", "m.insert(key)"],
    "answer": 1,
    "why": "at() throws std::out_of_range and find() returns end() - both tell you the truth. operator[] invents an entry."},
   {"q": "What does a set remove automatically?",
    "options": ["Empty strings", "Duplicate values", "Negative numbers"],
    "answer": 1,
    "why": "Sets store each value at most once; inserting an existing value is a no-op."},
   {"q": "When would an unordered_map be a better choice?",
    "options": ["When you need sorted order", "When you only need fast lookup and do not care about order", "When keys are integers only"],
    "answer": 1,
    "why": "Hash maps give average constant-time lookup but no ordering - pick based on whether you iterate in order."}
 ],
 "activity": {
   "goal": "Count how many times each word appears in a sentence using a map, then print each word and its count.",
   "starter": r"""#include <iostream>
#include <map>
#include <sstream>
#include <string>

int main() {
    std::string text = "go go robot go robot stop";
    std::map<std::string, int> counts;
    std::istringstream stream(text);
    std::string word;
    // TODO: while (stream >> word) ++counts[word];
    // TODO: print word and count, one per line
    return 0;
}""",
   "expected": "go 3\nrobot 2\nstop 1\n",
   "hints": [
     "The loop is while (stream >> word), which reads one word at a time.",
     "++counts[word] both creates the entry and increments it.",
     "A map iterates in sorted key order, so no extra sorting is needed."
   ],
   "solution": r"""#include <iostream>
#include <map>
#include <sstream>
#include <string>

int main() {
    std::string text = "go go robot go robot stop";
    std::map<std::string, int> counts;
    std::istringstream stream(text);
    std::string word;

    while (stream >> word) {
        ++counts[word];
    }

    for (const auto& [w, c] : counts) {
        std::cout << w << " " << c << "\n";
    }
    return 0;
}"""
 },
 "mistake": "Reading with m[key] inside a loop over the same map - it can insert a new element and invalidate the iteration you are in.",
 "recap": "map is key to value, set is unique values, and both keep order."
},
{
 "id": "i09", "level": "intermediate", "title": "The algorithm library", "minutes": 16,
 "tags": ["algorithm", "sort", "accumulate"],
 "goal": "Replace hand-written loops with tested standard algorithms.",
 "explain": [
   "The standard library already contains the loops you keep writing: sort, find, count_if, max_element, accumulate. They are tested, optimised, and say what they mean.",
   "Most take a pair of iterators (begin and end) and some take a predicate - a function returning bool that decides what counts."
 ],
 "example": {
   "title": "Five scores, four questions",
   "code": r"""#include <algorithm>
#include <iostream>
#include <numeric>
#include <vector>

int main() {
    std::vector<int> scores{70, 95, 88, 60, 95};

    std::sort(scores.begin(), scores.end());
    for (int s : scores) {
        std::cout << s << " ";
    }
    std::cout << "\n";

    int total = std::accumulate(scores.begin(), scores.end(), 0);
    std::cout << "total " << total << "\n";

    auto passes = std::count_if(scores.begin(), scores.end(),
                                [](int s) { return s >= 75; });
    std::cout << "pass " << passes << "\n";

    std::cout << "max " << *std::max_element(scores.begin(), scores.end()) << "\n";
    std::cout << "has 88 " << (std::find(scores.begin(), scores.end(), 88) != scores.end()) << "\n";
    return 0;
}""",
   "output": "60 70 88 95 95 \ntotal 408\npass 3\nmax 95\nhas 88 1\n",
   "notes": [
     ["std::sort(begin, end)", "sorts in place, ascending by default"],
     ["std::accumulate(..., 0)", "the 0 is the starting value - use 0.0 for a decimal sum"],
     ["[](int s) { return s >= 75; }", "a lambda: a small function written where it is used"]
   ]
 },
 "predict": {
   "q": "What does std::find return when the value is missing?",
   "options": ["-1", "The end iterator", "nullptr"],
   "answer": 1,
   "why": "Algorithms work on iterator ranges, so 'not found' is signalled by returning end(). Compare against it before dereferencing."
 },
 "quiz": [
   {"q": "Why prefer std::sort over a hand-written bubble sort?",
    "options": ["It is shorter to type", "It is faster, correct, and already tested", "C++ requires it"],
    "answer": 1,
    "why": "The standard sort is a hybrid algorithm with good worst-case behaviour; a hand-rolled sort is usually both slower and wrong on edge cases."},
   {"q": "What is a predicate?",
    "options": ["A function returning bool used to decide something", "A variable that never changes", "A loop with no body"],
    "answer": 0,
    "why": "count_if, find_if and sort all accept one to decide membership or order."},
   {"q": "What does accumulate need as its third argument?",
    "options": ["The size", "The starting value", "A lambda"],
    "answer": 1,
    "why": "It starts from that value and adds each element - which also sets the result type."}
 ],
 "activity": {
   "goal": "Sort the scores descending, print them, then print how many are below 70.",
   "starter": r"""#include <algorithm>
#include <iostream>
#include <vector>

int main() {
    std::vector<int> scores{70, 95, 88, 60, 95};
    // TODO: sort descending with std::greater<int>{}
    // TODO: print them space separated
    // TODO: print "below70 " and the count below 70
    return 0;
}""",
   "expected": "95 95 88 70 60 \nbelow70 1\n",
   "hints": [
     "Descending is a third argument: std::sort(b.begin(), b.end(), std::greater<int>{});",
     "Include <functional> for std::greater.",
     "count_if with a lambda returning s < 70."
   ],
   "solution": r"""#include <algorithm>
#include <functional>
#include <iostream>
#include <vector>

int main() {
    std::vector<int> scores{70, 95, 88, 60, 95};

    std::sort(scores.begin(), scores.end(), std::greater<int>{});
    for (int s : scores) {
        std::cout << s << " ";
    }
    std::cout << "\n";

    auto low = std::count_if(scores.begin(), scores.end(),
                             [](int s) { return s < 70; });
    std::cout << "below70 " << low << "\n";
    return 0;
}"""
 },
 "mistake": "Calling an algorithm on a range that is being modified, or forgetting that sort changes the order of the original vector.",
 "recap": "Reach for <algorithm> before writing a loop by hand."
},
{
 "id": "i10", "level": "intermediate", "title": "Reading and writing files", "minutes": 16,
 "tags": ["fstream", "files", "persistence"],
 "goal": "Save data between runs and read it back.",
 "explain": [
   "std::ofstream writes, std::ifstream reads, and closing happens automatically when the object goes out of scope. The stream is your handle to the file.",
   "Always test whether the file opened. while (in >> name >> score) is the standard read loop: it stops when the data runs out or the file is malformed."
 ],
 "example": {
   "title": "Write two lines, read them back",
   "code": r"""#include <fstream>
#include <iostream>
#include <string>

int main() {
    {
        std::ofstream out("scores.txt");
        out << "Ana 88\n";
        out << "Ben 95\n";
    }

    std::ifstream in("scores.txt");
    if (!in) {
        std::cout << "could not open\n";
        return 1;
    }

    std::string name;
    int score = 0;
    int total = 0;
    while (in >> name >> score) {
        std::cout << name << " " << score << "\n";
        total += score;
    }
    std::cout << "total " << total << "\n";
    return 0;
}""",
   "output": "Ana 88\nBen 95\ntotal 183\n",
   "notes": [
     ["{ std::ofstream out(...); ... }", "the braces close the file as soon as the block ends"],
     ["if (!in)", "the stream converts to bool: false means the open failed"],
     ["while (in >> name >> score)", "reads until the data runs out"]
   ]
 },
 "predict": {
   "q": "Why does the write happen inside its own { } block?",
   "options": ["For style only", "So the file is closed before anything tries to read it", "Because ofstream must be in a block"],
   "answer": 1,
   "why": "Buffered data is flushed when the stream is destroyed. Closing first guarantees the reader sees the complete file."
 },
 "quiz": [
   {"q": "Which class writes to a file?",
    "options": ["std::ifstream", "std::ofstream", "std::fstream is only for reading"],
    "answer": 1,
    "why": "o stands for output. ifstream reads, and fstream can do both."},
   {"q": "What does while (in >> a >> b) do at end of file?",
    "options": ["Loops forever", "Stops, because the read fails and the condition is false", "Throws an exception"],
    "answer": 1,
    "why": "A failed read makes the stream false, which ends the loop - no explicit check needed."},
   {"q": "Why check if (!in) right after opening?",
    "options": ["To make it faster", "A missing or locked file otherwise silently reads nothing", "It is required syntax"],
    "answer": 1,
    "why": "Without the check you get an empty result and no explanation - the classic 'my data vanished' bug."}
 ],
 "activity": {
   "goal": "Write three high scores to a file, read them back, and print the best one.",
   "starter": r"""#include <fstream>
#include <iostream>

int main() {
    // TODO: write "Ana 120\nBen 90\nCy 150\n" to highs.txt in a block
    // TODO: read them back and track the highest score
    // TODO: print "Best: " name score
    return 0;
}""",
   "expected": "Best: Cy 150\n",
   "hints": [
     "Open the writer in its own { } block so it closes before reading.",
     "Read with while (in >> name >> score) and keep bestName/bestScore.",
     "Compare with > and update both name and score together when a better one appears."
   ],
   "solution": r"""#include <fstream>
#include <iostream>
#include <string>

int main() {
    {
        std::ofstream out("highs.txt");
        out << "Ana 120\n";
        out << "Ben 90\n";
        out << "Cy 150\n";
    }

    std::ifstream in("highs.txt");
    std::string name;
    int score = 0;
    std::string bestName;
    int bestScore = -1;

    while (in >> name >> score) {
        if (score > bestScore) {
            bestScore = score;
            bestName = name;
        }
    }

    std::cout << "Best: " << bestName << " " << bestScore << "\n";
    return 0;
}"""
 },
 "mistake": "Writing and reading the same file in one scope without closing the writer first - the reader can see an empty or half-written file.",
 "recap": "ofstream writes, ifstream reads, and the read loop ends itself."
},
{
 "id": "i11", "level": "intermediate", "title": "Declarations, definitions, and many files", "minutes": 16,
 "tags": ["header", "prototype", "separate compilation"],
 "goal": "Understand what goes in a header and why programs are split up.",
 "explain": [
   "The compiler reads one file at a time. A declaration tells it the shape of something (name, parameters, return type) so it can compile a call; the definition supplies the body, and the linker joins them later.",
   "A header (.hpp) holds declarations and is included by everyone. A source file (.cpp) holds definitions. Include guards or #pragma once stop a header being included twice."
 ],
 "example": {
   "title": "The same idea in one file",
   "code": r"""#include <iostream>
#include <string>

// ---- what a header would contain: declarations only
int points_for(int level);
std::string badge_for(int points);

// ---- main uses them without knowing how they work
int main() {
    int points = points_for(2);
    std::cout << points << " points\n";
    std::cout << badge_for(points) << "\n";
    return 0;
}

// ---- what a .cpp file would contain: the definitions
int points_for(int level) {
    return level * 50;
}

std::string badge_for(int points) {
    if (points >= 150) {
        return "gold";
    }
    if (points >= 100) {
        return "silver";
    }
    return "bronze";
}""",
   "output": "100 points\nsilver\n",
   "notes": [
     ["int points_for(int level);", "a declaration: ends with a semicolon, no body"],
     ["int points_for(int level) { ... }", "the definition: same signature, with a body"],
     ["Order matters", "main only compiles because the declarations come first"]
   ]
 },
 "predict": {
   "q": "What happens if you delete both declaration lines but keep the definitions below main?",
   "options": ["Nothing changes", "main fails to compile - the compiler has not seen the names yet", "The linker complains only"],
   "answer": 1,
   "why": "The compiler works top to bottom. Calls above the first sight of a name are errors, not linker errors."
 },
 "quiz": [
   {"q": "What belongs in a header?",
    "options": ["Function bodies", "Declarations, types, and constants", "Only #include lines"],
    "answer": 1,
    "why": "Headers are copied into every file that includes them, so they hold declarations. Bodies in a header cause duplicate-symbol errors at link time."},
   {"q": "What does #pragma once do?",
    "options": ["Runs the file once", "Stops the same header being included twice in one translation unit", "Makes the code faster"],
    "answer": 1,
    "why": "It is a widely supported include guard. The portable alternative is #ifndef/#define/#endif."},
   {"q": "Which error appears when a function is declared but never defined?",
    "options": ["Compile error", "Linker error", "Run-time crash"],
    "answer": 1,
    "why": "The call compiles fine because the declaration exists; the linker is the one that cannot find the body."}
 ],
 "activity": {
   "goal": "Add a declaration for average(int, int) above main, and define it below main so the program prints 7.5.",
   "starter": r"""#include <iostream>

// TODO: declare double average(int a, int b); above main

int main() {
    // TODO: replace this line with: std::cout << average(5, 10) << "\n";
    std::cout << "ready\n";
    return 0;
}

// TODO: define average below main""",
   "expected": "7.5\n",
   "hints": [
     "A declaration is the signature with a semicolon: double average(int a, int b);",
     "The definition repeats the signature and adds a body returning (a + b) / 2.0.",
     "Replace the placeholder line with the real call once the declaration exists."
     "The 2.0 matters - int division would print 7."
   ],
   "solution": r"""#include <iostream>

double average(int a, int b);

int main() {
    std::cout << average(5, 10) << "\n";
    return 0;
}

double average(int a, int b) {
    return (a + b) / 2.0;
}"""
 },
 "mistake": "Putting a function body in a header that several files include - the linker then sees the same definition many times.",
 "recap": "Declare in headers, define in source files, and let the linker join them."
},
{
 "id": "i12", "level": "intermediate", "title": "Project: robot fleet board", "minutes": 28,
 "tags": ["project", "struct", "sort", "algorithm"],
 "goal": "Combine structs, vectors and algorithms into a small report generator.",
 "explain": [
   "This project keeps a fleet of robots, sorts them by battery, flags the low ones and counts how many are ready. It is the shape of a real status screen.",
   "Notice that the sorting and counting rules are written once, as small lambdas, instead of being spread through the printing loop."
 ],
 "example": {
   "title": "fleet.cpp",
   "code": r"""#include <algorithm>
#include <iostream>
#include <string>
#include <vector>

struct Robot {
    std::string name;
    int battery;
    bool charging;
};

int main() {
    std::vector<Robot> fleet{
        {"Five Sides", 87, false},
        {"Spare", 12, true},
        {"Red-Bot", 45, false},
        {"Blue-Bot", 8, true},
    };

    std::sort(fleet.begin(), fleet.end(),
              [](const Robot& a, const Robot& b) { return a.battery > b.battery; });

    for (const Robot& r : fleet) {
        std::cout << r.name << " " << r.battery;
        if (r.battery < 20) {
            std::cout << " LOW";
        }
        if (r.charging) {
            std::cout << " charging";
        }
        std::cout << "\n";
    }

    auto ready = std::count_if(fleet.begin(), fleet.end(),
                               [](const Robot& r) { return r.battery >= 20 || r.charging; });
    std::cout << "ready " << ready << "\n";
    return 0;
}""",
   "output": "Five Sides 87\nRed-Bot 45\nSpare 12 LOW charging\nBlue-Bot 8 LOW charging\nready 4\n",
   "notes": [
     ["[](const Robot& a, const Robot& b)", "the comparator: true means a comes before b"],
     ["a.battery > b.battery", "greater-than gives a descending sort"],
     ["r.battery >= 20 || r.charging", "the readiness rule, written once"]
   ]
 },
 "predict": {
   "q": "If Five Sides dropped to 10 and stopped charging, what would the last line say?",
   "options": ["ready 4", "ready 3", "ready 0"],
   "answer": 1,
   "why": "It would no longer be >= 20 and it is not charging, so it drops out of the count: three remain."
 },
 "quiz": [
   {"q": "Why sort before printing?",
    "options": ["Sorting is required for printing", "The report reads best highest-first, and it shows the sort in action", "It makes printing faster"],
    "answer": 1,
    "why": "There is no technical need - it is a presentation choice, and exactly the kind of thing a status board does."},
   {"q": "What would happen if the comparator returned a.battery >= b.battery?",
    "options": ["It would sort ascending", "Undefined behaviour - a strict weak ordering is required", "Nothing changes"],
    "answer": 1,
    "why": "A comparator must be a strict ordering: comp(a,a) must be false. Using >= breaks that and can crash the sort."},
   {"q": "How would you print only the robots that are ready?",
    "options": ["Add another loop with the same if", "Use std::copy_if or filter inside the loop", "Sort them differently"],
    "answer": 1,
    "why": "Filtering belongs in the iteration step, either with an if inside the loop or an algorithm that selects."}
 ],
 "activity": {
   "goal": "Add a charge(int amount) step before the report: every charging robot gains the amount (max 100), then print the new total battery across the fleet.",
   "starter": r"""#include <algorithm>
#include <iostream>
#include <numeric>
#include <string>
#include <vector>

struct Robot {
    std::string name;
    int battery;
    bool charging;
};

int main() {
    std::vector<Robot> fleet{
        {"Five Sides", 87, false},
        {"Spare", 12, true},
        {"Red-Bot", 45, false},
        {"Blue-Bot", 8, true},
    };
    // TODO: for each charging robot add 20, clamped to 100
    // TODO: print "total " and the sum of all batteries
    return 0;
}""",
   "expected": "total 192\n",
   "hints": [
     "Only charging robots gain: if (r.charging) r.battery += 20;",
     "Clamp with std::min(100, r.battery + 20).",
     "Sum with std::accumulate over a lambda: [](int sum, const Robot& r) { return sum + r.battery; }"
   ],
   "solution": r"""#include <algorithm>
#include <iostream>
#include <numeric>
#include <string>
#include <vector>

struct Robot {
    std::string name;
    int battery;
    bool charging;
};

int main() {
    std::vector<Robot> fleet{
        {"Five Sides", 87, false},
        {"Spare", 12, true},
        {"Red-Bot", 45, false},
        {"Blue-Bot", 8, true},
    };

    for (Robot& r : fleet) {
        if (r.charging) {
            r.battery = std::min(100, r.battery + 20);
        }
    }

    int total = std::accumulate(fleet.begin(), fleet.end(), 0,
                                [](int sum, const Robot& r) { return sum + r.battery; });
    std::cout << "total " << total << "\n";
    return 0;
}"""
 },
 "mistake": "Forgetting the & in for (Robot& r : fleet), which copies each robot and throws the changes away.",
 "recap": "Struct plus vector plus algorithm is enough for a real report."
}
]
