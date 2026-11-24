"""Advanced track: 12 lessons - lifetime, ownership, errors, templates, moves."""

LESSONS = [
{
 "id": "a01", "level": "advanced", "title": "Scope and object lifetime", "minutes": 14,
 "tags": ["scope", "lifetime", "stack"],
 "goal": "Know exactly when an object is created and when it dies.",
 "explain": [
   "Every variable lives inside a scope - the braces it was declared in. It is created when execution reaches the declaration and destroyed when execution leaves that block, always in reverse order of creation.",
   "Returning a local by value is safe because a copy (or a move) leaves the function before the local dies. Returning a reference or pointer to a local is the classic lifetime bug."
 ],
 "example": {
   "title": "Two lifetimes",
   "code": r"""#include <iostream>

int make_value() {
    int local = 5;
    return local;
}

int main() {
    int outer = 1;
    {
        int inner = 2;
        std::cout << "inner " << inner << " outer " << outer << "\n";
    }
    std::cout << "outer " << outer << "\n";
    std::cout << "returned " << make_value() << "\n";
    return 0;
}""",
   "output": "inner 2 outer 1\nouter 1\nreturned 5\n",
   "notes": [
     ["{ ... }", "an inner block; inner exists only inside it"],
     ["return local;", "the value is copied out before local is destroyed"],
     ["outer", "still alive after the block, because it was declared outside"]
   ]
 },
 "predict": {
   "q": "In what order are two objects in the same scope destroyed?",
   "options": ["In the order they were created", "Reverse order of creation", "At random"],
   "answer": 1,
   "why": "Destruction is the mirror of construction, so the last created is the first destroyed."
 },
 "quiz": [
   {"q": "What happens to a local variable when its function returns?",
    "options": ["It stays in memory", "It is destroyed; the memory is free for reuse", "It becomes global"],
    "answer": 1,
    "why": "Its lifetime ends with the scope. Anything still pointing at it is dangling."},
   {"q": "Why is returning a reference to a local a bug?",
    "options": ["References cannot be returned", "The local dies, so the reference points at freed memory", "It copies too much"],
    "answer": 1,
    "why": "The caller receives a dangling reference and reading it is undefined behaviour - often it even looks correct for a while."},
   {"q": "Where do ordinary local variables live?",
    "options": ["On the heap", "On the stack", "In the executable file"],
    "answer": 1,
    "why": "Automatic variables live on the stack and are cleaned up automatically as the scope exits."}
 ],
 "activity": {
   "goal": "Write a function that returns the square of its argument by value, and print result inside an inner scope.",
   "starter": r"""#include <iostream>

// TODO: int square(int n)

int main() {
    {
        int result = 0;
        // TODO: result = square(7); then print it
    }
    // TODO: print "done" after the block
    return 0;
}""",
   "expected": "49\ndone\n",
   "hints": [
     "square returns int and takes one int.",
     "Print result while still inside the braces - outside it no longer exists.",
     "\"done\" goes after the closing brace."
   ],
   "solution": r"""#include <iostream>

int square(int n) {
    return n * n;
}

int main() {
    {
        int result = square(7);
        std::cout << result << "\n";
    }
    std::cout << "done\n";
    return 0;
}"""
 },
 "mistake": "Keeping a pointer or reference to something that has already gone out of scope. If it outlives the object, the pointer is dangling.",
 "recap": "Objects live inside their braces, and die in reverse order when the braces end."
},
{
 "id": "a02", "level": "advanced", "title": "The heap, new and delete", "minutes": 15,
 "tags": ["heap", "new", "delete"],
 "goal": "Create objects whose lifetime you control, and clean them up correctly.",
 "explain": [
   "new creates an object on the heap and returns a pointer to it. That object lives until you delete it - it does not care about braces.",
   "Every new needs exactly one delete, and every new[] needs delete[]. Mixing them is undefined behaviour. Forgetting gives a leak; deleting twice is worse. This is why modern C++ rarely calls new directly."
 ],
 "example": {
   "title": "One object and one array",
   "code": r"""#include <iostream>

int main() {
    int* p = new int(42);
    std::cout << "value " << *p << "\n";
    delete p;
    p = nullptr;

    int* arr = new int[3]{1, 2, 3};
    std::cout << "arr " << arr[1] << "\n";
    delete[] arr;

    std::cout << "cleared " << (p == nullptr) << "\n";
    return 0;
}""",
   "output": "value 42\narr 2\ncleared 1\n",
   "notes": [
     ["new int(42)", "allocates one int on the heap, value 42"],
     ["delete p;", "frees it - the pointer still holds the old address"],
     ["p = nullptr;", "the standard habit: a deleted pointer is set to null"],
     ["delete[] arr;", "array form, matching new[]"]
   ]
 },
 "predict": {
   "q": "What happens if you delete p twice?",
   "options": ["Nothing", "Undefined behaviour - often a crash", "It deletes the next object too"],
   "answer": 1,
   "why": "The second delete touches memory that has already been returned to the allocator. Setting the pointer to nullptr after delete prevents the accident."
 },
 "quiz": [
   {"q": "What does new return?",
    "options": ["The object itself", "A pointer to the object", "A copy of the object"],
    "answer": 1,
    "why": "new allocates and constructs, and hands you the address. Dereference it to use the object."},
   {"q": "Which pair matches?",
    "options": ["new with delete[]", "new[] with delete[]", "new[] with delete"],
    "answer": 1,
    "why": "Arrays must be freed with the array form, because the allocator needs to know how many destructors to run."},
   {"q": "What is a memory leak?",
    "options": ["Memory that is freed twice", "Memory that is allocated and never freed", "A crash on startup"],
    "answer": 1,
    "why": "The program keeps the block reserved until it exits, which matters a lot in a long-running robot or server."}
 ],
 "activity": {
   "goal": "Allocate one int on the heap with value 7, double it through the pointer, print it, then delete it.",
   "starter": r"""#include <iostream>

int main() {
    // TODO: new int(7)
    // TODO: double it through the pointer
    // TODO: print, then delete and set to nullptr
    return 0;
}""",
   "expected": "14\n",
   "hints": [
     "int* p = new int(7);",
     "Doubling through the pointer: *p = *p * 2;",
     "delete p; then p = nullptr;"
   ],
   "solution": r"""#include <iostream>

int main() {
    int* p = new int(7);
    *p = *p * 2;
    std::cout << *p << "\n";
    delete p;
    p = nullptr;
    return 0;
}"""
 },
 "mistake": "Losing the only pointer to a heap object (reassigning it) before deleting it - the object is then unreachable but still allocated.",
 "recap": "new gives you a heap object and the duty to delete it exactly once."
},
{
 "id": "a03", "level": "advanced", "title": "RAII: let the destructor clean up", "minutes": 15,
 "tags": ["raii", "destructor"],
 "goal": "Tie a resource's lifetime to an object so it can never be forgotten.",
 "explain": [
   "RAII means Resource Acquisition Is Initialisation: acquire in the constructor, release in the destructor. Because destructors run on every path out of a scope - including exceptions - cleanup cannot be skipped.",
   "This one idea is behind std::vector, std::string, std::fstream and every smart pointer. Once you see it, most of C++'s automatic behaviour makes sense."
 ],
 "example": {
   "title": "A guard that always closes",
   "code": r"""#include <iostream>

class Guard {
public:
    explicit Guard(const char* name) : name_(name) {
        std::cout << "open " << name_ << "\n";
    }
    ~Guard() {
        std::cout << "close " << name_ << "\n";
    }
private:
    const char* name_;
};

void work() {
    Guard g("file");
    std::cout << "working\n";
}

int main() {
    Guard outer("db");
    work();
    std::cout << "end of main\n";
    return 0;
}""",
   "output": "open db\nopen file\nworking\nclose file\nend of main\nclose db\n",
   "notes": [
     ["explicit Guard(...)", "the constructor acquires the resource"],
     ["~Guard()", "the destructor releases it - automatically, always"],
     ["close file before end of main", "work() ended, so its guard died first"]
   ]
 },
 "predict": {
   "q": "If work() threw an exception after creating g, would close file still print?",
   "options": ["No, the destructor is skipped", "Yes, destructors run while the stack unwinds", "Only if you catch it inside work"],
   "answer": 1,
   "why": "Stack unwinding destroys every fully constructed local object on the way out. That guarantee is exactly why RAII is safe."
 },
 "quiz": [
   {"q": "What does RAII tie together?",
    "options": ["Allocation and freeing", "A resource's lifetime and an object's lifetime", "Two threads"],
    "answer": 1,
    "why": "The object owns the resource, so the resource lives exactly as long as the object."},
   {"q": "Which standard library type is RAII?",
    "options": ["std::vector", "int", "std::cout is not a type"],
    "answer": 0,
    "why": "vector allocates in its constructor and frees in its destructor - the canonical example."},
   {"q": "Why is RAII better than writing cleanup at the end of a function?",
    "options": ["It is faster", "It also runs on early returns and exceptions", "It uses less memory"],
    "answer": 1,
    "why": "Hand-written cleanup is skipped by every early return. The destructor cannot be skipped."}
 ],
 "activity": {
   "goal": "Write a class Timer that prints \"start\" on construction and \"stop\" on destruction. Create one in an inner block, then print \"after\" once the block ends.",
   "starter": r"""#include <iostream>

class Timer {
public:
    // TODO: constructor prints start
    // TODO: destructor prints stop
};

int main() {
    {
        // TODO: create a Timer here
    }
    // TODO: print after
    return 0;
}""",
   "expected": "start\nstop\nafter\n",
   "hints": [
     "The constructor is Timer() and the destructor is ~Timer(), both with a body that prints.",
     "Construct with Timer t; inside the braces.",
     "\"after\" must be printed after the closing brace so the timer has already died."
   ],
   "solution": r"""#include <iostream>

class Timer {
public:
    Timer() { std::cout << "start\n"; }
    ~Timer() { std::cout << "stop\n"; }
};

int main() {
    {
        Timer t;
    }
    std::cout << "after\n";
    return 0;
}"""
 },
 "mistake": "Writing a destructor that can throw, or forgetting to make a resource-owning class non-copyable - two objects then free the same resource.",
 "recap": "Acquire in the constructor, release in the destructor, and cleanup becomes automatic."
},
{
 "id": "a04", "level": "advanced", "title": "unique_ptr: one clear owner", "minutes": 15,
 "tags": ["unique_ptr", "ownership", "make_unique"],
 "goal": "Use heap objects without writing delete anywhere.",
 "explain": [
   "A std::unique_ptr owns its object and deletes it when it goes out of scope. It cannot be copied - only moved - so exactly one pointer owns the object at any time.",
   "Prefer std::make_unique<T>(args). It is exception-safe and you never write new or delete again."
 ],
 "example": {
   "title": "One owner, moved once",
   "code": r"""#include <iostream>
#include <memory>
#include <string>
#include <utility>
#include <vector>

struct Robot {
    std::string name;
    explicit Robot(std::string n) : name(std::move(n)) {
        std::cout << "build " << name << "\n";
    }
    ~Robot() { std::cout << "scrap " << name << "\n"; }
};

int main() {
    auto one = std::make_unique<Robot>("Five Sides");
    std::cout << "using " << one->name << "\n";

    std::vector<std::unique_ptr<Robot>> fleet;
    fleet.push_back(std::make_unique<Robot>("Spare"));

    auto moved = std::move(one);
    std::cout << "given away " << (one == nullptr) << "\n";
    std::cout << "new owner has " << moved->name << "\n";
    return 0;
}""",
   "output": "build Five Sides\nusing Five Sides\nbuild Spare\ngiven away 1\nnew owner has Five Sides\nscrap Five Sides\nscrap Spare\n",
   "notes": [
     ["make_unique<Robot>(...)", "constructs on the heap and wraps it in the owner"],
     ["one->name", "the pointer syntax still works, same as a raw pointer"],
     ["std::move(one)", "ownership transfers; one becomes null"],
     ["scrap lines at the end", "destructors run in reverse declaration order"]
   ]
 },
 "predict": {
   "q": "Which robot is scrapped first, and why?",
   "options": ["Spare, because fleet was created first", "Five Sides, because moved was declared last and locals die in reverse order", "Neither is scrapped"],
   "answer": 1,
   "why": "Destruction mirrors construction. one, fleet and moved were declared in that order, so moved (holding Five Sides) is destroyed first, then fleet with Spare."
 },
 "quiz": [
   {"q": "What can you NOT do with a unique_ptr?",
    "options": ["Move it", "Copy it", "Reset it"],
    "answer": 1,
    "why": "Copying would create two owners. Move transfers ownership and leaves the source empty."},
   {"q": "Why prefer make_unique over new?",
    "options": ["It is shorter", "It is exception-safe and removes a raw new from your code", "new is deprecated"],
    "answer": 1,
    "why": "With new T(...) passed into a function that then throws, the object can leak. make_unique closes that gap."},
   {"q": "What does ptr.reset() do?",
    "options": ["Clears the pointer without deleting", "Deletes the object and makes the pointer empty", "Reallocates the object"],
    "answer": 1,
    "why": "reset destroys what it owns, then leaves the pointer null (or takes a new object if you pass one)."}
 ],
 "activity": {
   "goal": "Create a unique_ptr<int> with 5, add 3 through it, print it, then reset and print whether it is empty.",
   "starter": r"""#include <iostream>
#include <memory>

int main() {
    // TODO: make_unique<int>(5)
    // TODO: add 3 through the pointer and print
    // TODO: reset, then print (ptr == nullptr)
    return 0;
}""",
   "expected": "8\n1\n",
   "hints": [
     "auto p = std::make_unique<int>(5);",
     "Dereference like a raw pointer: *p += 3;",
     "p.reset(); then std::cout << (p == nullptr) << \"\\n\";"
   ],
   "solution": r"""#include <iostream>
#include <memory>

int main() {
    auto p = std::make_unique<int>(5);
    *p += 3;
    std::cout << *p << "\n";
    p.reset();
    std::cout << (p == nullptr) << "\n";
    return 0;
}"""
 },
 "mistake": "Passing a unique_ptr by value to a function that only needs to use the object - that transfers ownership and empties the caller's pointer. Pass a reference or a raw pointer instead.",
 "recap": "unique_ptr is the default way to own a heap object: one owner, automatic delete."
},
{
 "id": "a05", "level": "advanced", "title": "shared_ptr and weak_ptr", "minutes": 15,
 "tags": ["shared_ptr", "weak_ptr", "reference counting"],
 "goal": "Share ownership between several places without deciding who deletes.",
 "explain": [
   "A shared_ptr keeps a reference count. Copies increase it, destruction decreases it, and the object is deleted when the count reaches zero.",
   "weak_ptr observes without owning. It does not change the count, and lock() gives you a shared_ptr only if the object still exists. Use it to break cycles, which would otherwise never be freed."
 ],
 "example": {
   "title": "Watching the count",
   "code": r"""#include <iostream>
#include <memory>

int main() {
    auto a = std::make_shared<int>(7);
    std::cout << "count " << a.use_count() << "\n";

    {
        auto b = a;
        std::cout << "count " << a.use_count() << "\n";
        std::cout << "value " << *b << "\n";
    }

    std::cout << "count " << a.use_count() << "\n";

    std::weak_ptr<int> w = a;
    std::cout << "expired " << w.expired() << "\n";
    a.reset();
    std::cout << "expired " << w.expired() << "\n";
    return 0;
}""",
   "output": "count 1\ncount 2\nvalue 7\ncount 1\nexpired 0\nexpired 1\n",
   "notes": [
     ["auto b = a;", "a copy - the count goes to 2"],
     ["weak_ptr<int> w = a;", "does not change the count"],
     ["w.expired()", "true once the last owner is gone"]
   ]
 },
 "predict": {
   "q": "What would use_count() be after a.reset() if w were the only remaining thing pointing at the object?",
   "options": ["1", "0 - weak pointers do not count", "It would still hold the object"],
   "answer": 1,
   "why": "Weak pointers observe only. The count reaches 0 and the object is destroyed, which is why w.expired() becomes true."
 },
 "quiz": [
   {"q": "When is a shared_ptr's object destroyed?",
    "options": ["When the first pointer goes out of scope", "When the last owning pointer is destroyed", "Only when you call delete"],
    "answer": 1,
    "why": "The reference count controls it, so the object lives as long as any owner remains."},
   {"q": "Why do two shared_ptrs pointing at each other leak?",
    "options": ["They do not", "Each keeps the other's count at 1 forever", "shared_ptr cannot be copied"],
    "answer": 1,
    "why": "A cycle keeps both counts above zero. Making one side a weak_ptr breaks it."},
   {"q": "What does weak_ptr::lock() return?",
    "options": ["A reference", "A shared_ptr that is non-empty only if the object still exists", "A raw pointer"],
    "answer": 1,
    "why": "lock() atomically promotes to a shared_ptr, or returns an empty one if it has expired."}
 ],
 "activity": {
   "goal": "Create a shared_ptr<string>, make a weak_ptr to it, print expired, reset the owner, print expired again.",
   "starter": r"""#include <iostream>
#include <memory>
#include <string>

int main() {
    // TODO: make_shared<std::string>("Five Sides")
    // TODO: weak_ptr, print expired (expect 0)
    // TODO: reset the owner, print expired (expect 1)
    return 0;
}""",
   "expected": "0\n1\n",
   "hints": [
     "auto s = std::make_shared<std::string>(\"Five Sides\");",
     "std::weak_ptr<std::string> w = s;",
     "std::cout << w.expired() << \"\\n\"; before and after s.reset();"
   ],
   "solution": r"""#include <iostream>
#include <memory>
#include <string>

int main() {
    auto s = std::make_shared<std::string>("Five Sides");
    std::weak_ptr<std::string> w = s;

    std::cout << w.expired() << "\n";
    s.reset();
    std::cout << w.expired() << "\n";
    return 0;
}"""
 },
 "mistake": "Using shared_ptr everywhere 'to be safe'. Shared ownership makes lifetime hard to reason about; unique_ptr should be your default.",
 "recap": "shared_ptr shares ownership by counting, weak_ptr watches without owning."
},
{
 "id": "a06", "level": "advanced", "title": "Exceptions: reporting the impossible", "minutes": 16,
 "tags": ["exceptions", "try", "catch", "throw"],
 "goal": "Signal failure up the call stack without returning error codes everywhere.",
 "explain": [
   "throw starts an exception, which unwinds the stack until a matching catch is found. Objects in between are destroyed properly, which is why RAII and exceptions work well together.",
   "Catch by const reference. Catch the specific type first and a base class like std::exception last. Anything not caught ends the program, so main is a good place for a final catch."
 ],
 "example": {
   "title": "Parsing three scores",
   "code": r"""#include <iostream>
#include <stdexcept>
#include <string>

int parse_score(const std::string& text) {
    if (text.empty()) {
        throw std::invalid_argument("empty score");
    }
    int value = std::stoi(text);
    if (value < 0 || value > 100) {
        throw std::out_of_range("score out of range: " + text);
    }
    return value;
}

int main() {
    for (const std::string& text : {"88", "250", ""}) {
        try {
            int score = parse_score(text);
            std::cout << "ok " << score << "\n";
        } catch (const std::exception& e) {
            std::cout << "failed: " << e.what() << "\n";
        }
    }
    std::cout << "still running\n";
    return 0;
}""",
   "output": "ok 88\nfailed: score out of range: 250\nfailed: empty score\nstill running\n",
   "notes": [
     ["throw std::out_of_range(...)", "stops this function immediately - note that nothing after it prints"],
     ["catch (const std::exception& e)", "catches any standard exception by reference"],
     ["e.what()", "the message carried by the exception"]
   ]
 },
 "predict": {
   "q": "What happens to a local RAII object inside parse_score when it throws?",
   "options": ["It leaks", "Its destructor runs during stack unwinding", "It is copied to main"],
   "answer": 1,
   "why": "Unwinding destroys every constructed local on the way out - the guarantee that makes RAII reliable."
 },
 "quiz": [
   {"q": "Why catch by const reference instead of by value?",
    "options": ["It is faster to type", "It avoids slicing and copying the exception object", "C++ requires it"],
    "answer": 1,
    "why": "Catching a base class by value slices off the derived part, so you lose the real type and message."},
   {"q": "What ends the program?",
    "options": ["Any throw", "An exception that reaches main without being caught", "A catch block"],
    "answer": 1,
    "why": "If nothing handles it, std::terminate runs and the process aborts."},
   {"q": "When should you NOT use an exception?",
    "options": ["For a file that fails to open", "For an expected, ordinary outcome you can check cheaply", "For invalid user input"],
    "answer": 1,
    "why": "Exceptions are for exceptional cases. Ordinary branching (does this key exist?) belongs in the normal control flow."}
 ],
 "activity": {
   "goal": "Write int checked_div(int a, int b) that throws std::invalid_argument when b is 0. Test 10/2 and 10/0, printing ok or the message.",
   "starter": r"""#include <iostream>
#include <stdexcept>

// TODO: int checked_div(int a, int b)

int main() {
    // TODO: try 10/2 and 10/0, catching std::exception
    return 0;
}""",
   "expected": "ok 5\nfailed: divide by zero\n",
   "hints": [
     "Throw before dividing: if (b == 0) throw std::invalid_argument(\"divide by zero\");",
     "Two separate try blocks, each with its own catch.",
     "Print e.what() in the catch."
   ],
   "solution": r"""#include <iostream>
#include <stdexcept>

int checked_div(int a, int b) {
    if (b == 0) {
        throw std::invalid_argument("divide by zero");
    }
    return a / b;
}

int main() {
    try {
        int result = checked_div(10, 2);
        std::cout << "ok " << result << "\n";
    } catch (const std::exception& e) {
        std::cout << "failed: " << e.what() << "\n";
    }

    try {
        int result = checked_div(10, 0);
        std::cout << "ok " << result << "\n";
    } catch (const std::exception& e) {
        std::cout << "failed: " << e.what() << "\n";
    }
    return 0;
}"""
 },
 "mistake": "Throwing a raw pointer or a string literal - catch it somewhere far away and the type will not match. Throw a standard exception type.",
 "recap": "throw unwinds to the nearest matching catch, destroying everything on the way."
},
{
 "id": "a07", "level": "advanced", "title": "std::optional and honest returns", "minutes": 14,
 "tags": ["optional", "error handling"],
 "goal": "Return 'a value or nothing' without magic numbers.",
 "explain": [
   "std::optional<T> either holds a T or holds nothing. It replaces the sentinel -1, the empty string, and the out-parameter that says whether the call worked.",
   "Check it with if (auto v = f()) or with has_value(), and read with *v or v.value(). value() throws if empty, which is useful when empty really is a bug."
 ],
 "example": {
   "title": "Looking up a score",
   "code": r"""#include <iostream>
#include <optional>
#include <string>

std::optional<int> find_score(const std::string& name) {
    if (name == "Ana") {
        return 88;
    }
    if (name == "Ben") {
        return 95;
    }
    return std::nullopt;
}

int main() {
    for (const std::string& name : {"Ana", "Robot"}) {
        if (auto score = find_score(name)) {
            std::cout << name << " " << *score << "\n";
        } else {
            std::cout << name << " unknown\n";
        }
    }
    return 0;
}""",
   "output": "Ana 88\nRobot unknown\n",
   "notes": [
     ["std::optional<int>", "an int, or nothing at all"],
     ["return std::nullopt;", "the explicit 'no value'"],
     ["if (auto score = ...)", "the optional converts to bool: has a value or not"],
     ["*score", "unwraps the value once you know it exists"]
   ]
 },
 "predict": {
   "q": "What does *score do if the optional is empty?",
   "options": ["Returns 0", "Undefined behaviour - check first, or use .value_or()", "Throws"],
   "answer": 1,
   "why": "operator* does not check. .value() throws std::bad_optional_access, and .value_or(0) supplies a default."
 },
 "quiz": [
   {"q": "What problem does optional solve?",
    "options": ["Slow copying", "Representing 'no result' without a magic value", "Memory allocation"],
    "answer": 1,
    "why": "It makes absence explicit in the type, so the caller cannot forget it."},
   {"q": "How do you get a value or a fallback in one call?",
    "options": ["opt.get()", "opt.value_or(0)", "opt ? *opt : 0 is forbidden"],
    "answer": 1,
    "why": "value_or returns the stored value when present, otherwise the argument you passed."},
   {"q": "When is optional the wrong tool?",
    "options": ["When 'nothing' is an error you must not ignore", "When the value is a string", "When the function is const"],
    "answer": 0,
    "why": "optional can be ignored silently. If absence is a real failure, throw or return a result type."}
 ],
 "activity": {
   "goal": "Write std::optional<int> half(int n) that returns n/2 only when n is even, otherwise nullopt. Print half(10) and half(7).",
   "starter": r"""#include <iostream>
#include <optional>

// TODO: std::optional<int> half(int n)

int main() {
    // TODO: print half(10) or "odd"
    // TODO: print half(7) or "odd"
    return 0;
}""",
   "expected": "5\nodd\n",
   "hints": [
     "if (n % 2 != 0) return std::nullopt; otherwise return n / 2;",
     "Use if (auto h = half(10)) { std::cout << *h << \"\\n\"; }",
     "The else branch prints \"odd\"."
   ],
   "solution": r"""#include <iostream>
#include <optional>

std::optional<int> half(int n) {
    if (n % 2 != 0) {
        return std::nullopt;
    }
    return n / 2;
}

int main() {
    if (auto h = half(10)) {
        std::cout << *h << "\n";
    } else {
        std::cout << "odd\n";
    }

    if (auto h = half(7)) {
        std::cout << *h << "\n";
    } else {
        std::cout << "odd\n";
    }
    return 0;
}"""
 },
 "mistake": "Unwrapping an optional without checking, which turns a missing value into undefined behaviour instead of a clear error.",
 "recap": "optional makes 'maybe nothing' part of the type, so the caller must decide."
},
{
 "id": "a08", "level": "advanced", "title": "Function templates", "minutes": 16,
 "tags": ["templates", "generics"],
 "goal": "Write one function that works for many types.",
 "explain": [
   "A template is a recipe the compiler fills in. template <typename T> T bigger(T a, T b) works for int, double, std::string - the compiler generates one function per type you actually use.",
   "The code must compile for each type you call it with. If a type does not support >, the error appears at that call, not at the template.",
   "Deduction is automatic: bigger(3, 9) uses T = int. When two arguments disagree, you must say which type you mean."
 ],
 "example": {
   "title": "One bigger, four types",
   "code": r"""#include <iostream>
#include <string>

template <typename T>
T bigger(const T& a, const T& b) {
    return (a > b) ? a : b;
}

int main() {
    std::cout << bigger(3, 9) << "\n";
    std::cout << bigger(2.5, 1.5) << "\n";
    std::cout << bigger(std::string("apple"), std::string("pear")) << "\n";
    std::cout << bigger<int>(3, 9) << "\n";
    return 0;
}""",
   "output": "9\n2.5\npear\n9\n",
   "notes": [
     ["template <typename T>", "T is a placeholder for a type"],
     ["const T& a", "no copying, whatever the type is"],
     ["bigger<int>(3, 9)", "explicit type argument - rarely needed but sometimes clearer"]
   ]
 },
 "predict": {
   "q": "What happens if you call bigger(3, 2.5)?",
   "options": ["It picks double", "It fails to deduce T - the two arguments disagree", "It compiles and returns 3"],
   "answer": 1,
   "why": "Deduction needs one consistent T. You must write bigger<double>(3, 2.5) or cast one argument."
 },
 "quiz": [
   {"q": "When is a template function generated?",
    "options": ["When you write it", "When it is called with a concrete type", "At link time for all types"],
    "answer": 1,
    "why": "Templates are instantiated on use, which is why unused ones cost nothing."},
   {"q": "Why put the template definition in a header?",
    "options": ["For style", "The compiler needs the body to generate code for each type", "Headers are faster"],
    "answer": 1,
    "why": "Unlike normal functions, the template body must be visible where it is instantiated."},
   {"q": "What does a template error usually mean?",
    "options": ["The template is broken for every type", "The body does not work for the type you passed", "You forgot to include it"],
    "answer": 1,
    "why": "Templates are only checked per instantiation, so the error names the type that failed."}
 ],
 "activity": {
   "goal": "Write a template T smallest(T a, T b) and use it on two ints (4, 9) and two strings (\"kiwi\", \"apple\").",
   "starter": r"""#include <iostream>
#include <string>

// TODO: template <typename T> T smallest(const T& a, const T& b)

int main() {
    // TODO: print smallest(4, 9) and smallest of the two strings
    return 0;
}""",
   "expected": "4\napple\n",
   "hints": [
     "Same shape as bigger, but with < instead of >.",
     "Strings compare alphabetically, which is what you want here.",
     "smallest(std::string(\"kiwi\"), std::string(\"apple\")) forces both arguments to be strings."
   ],
   "solution": r"""#include <iostream>
#include <string>

template <typename T>
T smallest(const T& a, const T& b) {
    return (a < b) ? a : b;
}

int main() {
    std::cout << smallest(4, 9) << "\n";
    std::cout << smallest(std::string("kiwi"), std::string("apple")) << "\n";
    return 0;
}"""
 },
 "mistake": "Putting a template's definition in a .cpp file - other files then fail to link because the body was never visible.",
 "recap": "A template is code the compiler stamps out once per type you actually use."
},
{
 "id": "a09", "level": "advanced", "title": "Class templates", "minutes": 16,
 "tags": ["templates", "class", "generics"],
 "goal": "Build a container type that can hold anything.",
 "explain": [
   "A class template makes the type itself generic: Box<int> and Box<std::string> are two different, fully compiled classes produced from one blueprint.",
   "Everything you know about classes still applies - constructors, const methods, encapsulation - the only difference is that T is filled in at the point of use."
 ],
 "example": {
   "title": "A box that holds anything",
   "code": r"""#include <iostream>
#include <string>
#include <utility>

template <typename T>
class Box {
public:
    explicit Box(T value) : value_(std::move(value)) {}

    const T& get() const { return value_; }
    void set(T value) { value_ = std::move(value); }

private:
    T value_;
};

int main() {
    Box<int> count{3};
    Box<std::string> label{"Five Sides"};

    std::cout << count.get() << "\n";
    std::cout << label.get() << "\n";

    count.set(7);
    std::cout << count.get() << "\n";
    return 0;
}""",
   "output": "3\nFive Sides\n7\n",
   "notes": [
     ["template <typename T> class Box", "the class, with T still unknown"],
     ["Box<int> count{3}", "the type is completed at the point of use"],
     ["std::move(value)", "avoids copying the string in"]
   ]
 },
 "predict": {
   "q": "Can Box<int> and Box<std::string> be stored in the same vector?",
   "options": ["Yes, they are the same type", "No, they are unrelated types", "Only with a cast"],
   "answer": 1,
   "why": "Each instantiation is a distinct type, exactly like two hand-written classes."
 },
 "quiz": [
   {"q": "What does the compiler produce for a class template?",
    "options": ["One class for all types", "One class per instantiation you use", "A runtime type table"],
    "answer": 1,
    "why": "Each Box<int>, Box<std::string> is generated separately, which is why unused instantiations cost nothing."},
   {"q": "Why is the definition in the header for class templates?",
    "options": ["Tradition", "Each instantiation needs the body to compile", "Headers are read faster"],
    "answer": 1,
    "why": "The compiler must see the members to generate the class for a new T."},
   {"q": "What is the standard library's most famous class template?",
    "options": ["std::vector", "std::cout", "std::main"],
    "answer": 0,
    "why": "vector<T> is a class template; cout is an object, and main is a function."}
 ],
 "activity": {
   "goal": "Write a template class Pair<T> holding first and second of type T, with a sum() method returning first + second. Use it with two ints (3, 4) and two strings (\"a\", \"b\").",
   "starter": r"""#include <iostream>
#include <string>

// TODO: template <typename T> class Pair with first_, second_, sum()

int main() {
    // TODO: Pair<int>{3,4}.sum() and Pair<std::string>{"a","b"}.sum()
    return 0;
}""",
   "expected": "7\nab\n",
   "hints": [
     "sum() returns T, so first_ + second_ works for numbers and for strings.",
     "Make sum() const.",
     "Construct with Pair<int> p{3, 4}; then print p.sum()."
   ],
   "solution": r"""#include <iostream>
#include <string>

template <typename T>
class Pair {
public:
    Pair(T first, T second) : first_(first), second_(second) {}

    T sum() const { return first_ + second_; }

private:
    T first_;
    T second_;
};

int main() {
    Pair<int> numbers{3, 4};
    Pair<std::string> letters{"a", "b"};

    std::cout << numbers.sum() << "\n";
    std::cout << letters.sum() << "\n";
    return 0;
}"""
 },
 "mistake": "Forgetting the <T> at the point of use - writing Box b{3} only works with class template argument deduction, and fails confusingly when it cannot deduce.",
 "recap": "A class template is a blueprint; each type you use creates a real class."
},
{
 "id": "a10", "level": "advanced", "title": "Lambdas and captures", "minutes": 16,
 "tags": ["lambda", "capture", "algorithm"],
 "goal": "Write small functions where they are used, and control what they can see.",
 "explain": [
   "A lambda is an unnamed function written inline: [](int x) { return x > 3; }. It is perfect for the predicate an algorithm needs and that nobody else will ever call.",
   "The brackets at the front are the capture list. [] sees nothing, [x] copies x, [&x] refers to the original, [=] copies everything used, [&] refers to everything. Prefer naming what you need."
 ],
 "example": {
   "title": "Two useful captures",
   "code": r"""#include <algorithm>
#include <iostream>
#include <vector>

int main() {
    std::vector<int> scores{70, 95, 88, 60};

    int limit = 75;
    auto passes = std::count_if(scores.begin(), scores.end(),
                                [limit](int s) { return s >= limit; });
    std::cout << "pass " << passes << "\n";

    int calls = 0;
    std::count_if(scores.begin(), scores.end(),
                  [&calls](int s) { ++calls; return s > 0; });
    std::cout << "calls " << calls << "\n";
    return 0;
}""",
   "output": "pass 2\ncalls 4\n",
   "notes": [
     ["[limit]", "a copy of limit - safe even if limit later changes"],
     ["[&calls]", "a reference, so the lambda can modify the original"],
     ["[](int s) { ... }", "no capture: it cannot see any local variable"]
   ]
 },
 "predict": {
   "q": "What happens if you change limit after the lambda was created with [limit]?",
   "options": ["The lambda uses the new value", "The lambda keeps the value it copied", "It fails to compile"],
   "answer": 1,
   "why": "Capture by value copies at the moment of creation. Use [&limit] if you need the live value."
 },
 "quiz": [
   {"q": "Which capture lets the lambda modify the original variable?",
    "options": ["[x]", "[&x]", "[=]"],
    "answer": 1,
    "why": "Reference capture reaches the original object; value capture works on a private copy."},
   {"q": "Why avoid [&] in something that outlives the current function?",
    "options": ["It copies too much", "The referenced locals are gone, leaving dangling references", "It is slower to compile"],
    "answer": 1,
    "why": "A lambda stored for later use must own what it needs, so capture by value."},
   {"q": "Can a lambda be stored in a variable?",
    "options": ["No, they are anonymous", "Yes - auto f = [](int x) { return x * 2; };", "Only in a vector"],
    "answer": 1,
    "why": "A lambda is an object with operator(). auto gives it a name, and std::function can hold it generically."}
 ],
 "activity": {
   "goal": "Sort words by length using a lambda comparator, then count how many are longer than 3 letters.",
   "starter": r"""#include <algorithm>
#include <iostream>
#include <string>
#include <vector>

int main() {
    std::vector<std::string> words{"robot", "ai", "battery", "go"};
    // TODO: sort by length using a lambda
    // TODO: print them space separated
    // TODO: count words longer than 3 with a lambda
    return 0;
}""",
   "expected": "ai go robot battery\nlong 2\n",
   "hints": [
     "The comparator takes two const std::string& and compares .size().",
     "std::sort(words.begin(), words.end(), [](const std::string& a, const std::string& b) { return a.size() < b.size(); });",
     "count_if with [](const std::string& w) { return w.size() > 3; }"
   ],
   "solution": r"""#include <algorithm>
#include <iostream>
#include <string>
#include <vector>

int main() {
    std::vector<std::string> words{"robot", "ai", "battery", "go"};

    std::sort(words.begin(), words.end(),
              [](const std::string& a, const std::string& b) {
                  return a.size() < b.size();
              });

    for (const auto& w : words) {
        std::cout << w << " ";
    }
    std::cout << "\n";

    auto long_words = std::count_if(words.begin(), words.end(),
                                    [](const std::string& w) { return w.size() > 3; });
    std::cout << "long " << long_words << "\n";
    return 0;
}"""
 },
 "mistake": "Capturing by reference in a lambda that is stored and called later, after the original variable has gone out of scope.",
 "recap": "A lambda is an inline function; its capture list decides what it can see and whether it owns it."
},
{
 "id": "a11", "level": "advanced", "title": "Move semantics", "minutes": 17,
 "tags": ["move", "rvalue", "std::move"],
 "goal": "Understand what std::move actually does and when it saves work.",
 "explain": [
   "Copying duplicates the contents; moving transfers them and leaves the source empty. For a big vector or string, moving is O(1) instead of O(n).",
   "std::move does not move anything by itself - it is a cast that says 'treat this as disposable', which lets the move constructor run. A moved-from object is valid but unspecified: do not read it."
 ],
 "example": {
   "title": "Counting copies and moves",
   "code": r"""#include <iostream>
#include <utility>

class Tracker {
public:
    Tracker() = default;
    Tracker(const Tracker&) { std::cout << "copy\n"; }
    Tracker(Tracker&&) noexcept { std::cout << "move\n"; }
};

void take_copy(Tracker t) { (void)t; }

int main() {
    Tracker a;
    take_copy(a);

    Tracker b = std::move(a);
    (void)b;

    std::cout << "done\n";
    return 0;
}""",
   "output": "copy\nmove\ndone\n",
   "notes": [
     ["Tracker(const Tracker&)", "the copy constructor - duplicates"],
     ["Tracker(Tracker&&) noexcept", "the move constructor - steals, and must not throw"],
     ["take_copy(a)", "a is still needed, so it copies"],
     ["std::move(a)", "a is disposable here, so it moves"]
   ]
 },
 "predict": {
   "q": "What is the state of a after Tracker b = std::move(a); ?",
   "options": ["Unchanged", "Valid but unspecified - do not read it", "Destroyed"],
   "answer": 1,
   "why": "The move constructor is allowed to leave a in any valid state. For standard types it is usually empty."
 },
 "quiz": [
   {"q": "What does std::move(x) return?",
    "options": ["A copy of x", "An rvalue reference to x", "Nothing"],
    "answer": 1,
    "why": "It is a cast to T&&. The actual moving happens in the constructor or assignment that receives it."},
   {"q": "Why should a move constructor be noexcept?",
    "options": ["Style", "So containers can move instead of copying when they grow", "Because moves cannot fail"],
    "answer": 1,
    "why": "vector only moves elements during reallocation if the move cannot throw - otherwise it copies to keep its strong guarantee."},
   {"q": "When is a move automatically used?",
    "options": ["Never", "When returning a local by value, or passing a temporary", "Only with std::move"],
    "answer": 1,
    "why": "Temporaries and returned locals are already rvalues, so the compiler picks the move constructor itself."}
 ],
 "activity": {
   "goal": "Write a class Tag with a copy constructor printing \"copy\" and a move constructor printing \"move\". Copy one object, move another, and print \"done\".",
   "starter": r"""#include <iostream>
#include <utility>

class Tag {
public:
    Tag() = default;
    // TODO: copy constructor printing copy
    // TODO: move constructor printing move
};

int main() {
    Tag a;
    // TODO: copy a into b
    // TODO: move a into c
    // TODO: print done
    return 0;
}""",
   "expected": "copy\nmove\ndone\n",
   "hints": [
     "The copy constructor takes const Tag&, the move takes Tag&& noexcept.",
     "Tag b = a; copies, Tag c = std::move(a); moves.",
     "The constructors need no members - just a cout each."
   ],
   "solution": r"""#include <iostream>
#include <utility>

class Tag {
public:
    Tag() = default;
    Tag(const Tag&) { std::cout << "copy\n"; }
    Tag(Tag&&) noexcept { std::cout << "move\n"; }
};

int main() {
    Tag a;
    Tag b = a;
    (void)b;
    Tag c = std::move(a);
    (void)c;
    std::cout << "done\n";
    return 0;
}"""
 },
 "mistake": "Using std::move on a variable you still need afterwards - it is not a hint, it is a promise you are finished with it.",
 "recap": "Moving transfers ownership of the contents; std::move is the cast that allows it."
},
{
 "id": "a12", "level": "advanced", "title": "Project: inventory with tests", "minutes": 30,
 "tags": ["project", "assert", "raii", "exceptions"],
 "goal": "Build a small class with rules, then prove the rules hold with tests.",
 "explain": [
   "This project is a stock inventory: it refuses bad quantities, reports totals, and is checked by assertions rather than by printing and eyeballing.",
   "assert is the simplest test: it aborts with a message when the condition is false, and disappears entirely when compiled with NDEBUG. That means tests are free in a release build."
 ],
 "example": {
   "title": "inventory.cpp",
   "code": r"""#include <cassert>
#include <iostream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

class Inventory {
public:
    void add(const std::string& item, int qty) {
        if (qty <= 0) {
            throw std::invalid_argument("quantity must be positive");
        }
        items_.push_back({item, qty});
    }

    int total() const {
        int sum = 0;
        for (const auto& entry : items_) {
            sum += entry.second;
        }
        return sum;
    }

    std::size_t kinds() const { return items_.size(); }

private:
    std::vector<std::pair<std::string, int>> items_;
};

int main() {
    Inventory inv;
    inv.add("wheel", 4);
    inv.add("sensor", 2);

    assert(inv.kinds() == 2);
    assert(inv.total() == 6);

    bool refused = false;
    try {
        inv.add("ghost", 0);
    } catch (const std::invalid_argument&) {
        refused = true;
    }
    assert(refused);

    std::cout << "kinds " << inv.kinds() << "\n";
    std::cout << "total " << inv.total() << "\n";
    std::cout << "refused " << refused << "\n";
    return 0;
}""",
   "output": "kinds 2\ntotal 6\nrefused 1\n",
   "notes": [
     ["assert(condition)", "aborts with file and line if false; vanish with NDEBUG"],
     ["try { ... } catch (const std::invalid_argument&)", "tests the refusal path, not just the happy path"],
     ["items_.push_back({item, qty})", "the pair is built inline"]
   ]
 },
 "predict": {
   "q": "If add() accepted qty == 0 instead of throwing, which assert would fail?",
   "options": ["kinds == 2", "total == 6", "refused"],
   "answer": 2,
   "why": "refused stays false because nothing throws, so assert(refused) aborts. Note the first two asserts would still pass."
 },
 "quiz": [
   {"q": "What happens to an assert in a build with NDEBUG?",
    "options": ["It throws", "It is removed entirely", "It prints a warning"],
    "answer": 1,
    "why": "That is why asserts must not contain side effects - the code inside disappears."},
   {"q": "Why test the refusal path?",
    "options": ["To raise coverage numbers", "Otherwise a bug that silently accepts bad data ships unnoticed", "Because asserts require it"],
    "answer": 1,
    "why": "The guard is the feature. Untested guards are the ones that quietly stop working."},
   {"q": "What makes this class easy to test?",
    "options": ["It prints a lot", "It has no I/O and exposes small queries", "It uses vectors"],
    "answer": 1,
    "why": "Separating logic from output is what lets you assert on results instead of reading text."}
 ],
 "activity": {
   "goal": "Add a remove(item, qty) that throws if the item is missing or the quantity is too large, and assert that a valid removal lowers the total.",
   "starter": r"""#include <cassert>
#include <iostream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

class Inventory {
public:
    void add(const std::string& item, int qty) {
        if (qty <= 0) throw std::invalid_argument("qty");
        items_.push_back({item, qty});
    }
    int total() const {
        int sum = 0;
        for (const auto& e : items_) sum += e.second;
        return sum;
    }
    // TODO: void remove(const std::string& item, int qty)
private:
    std::vector<std::pair<std::string, int>> items_;
};

int main() {
    Inventory inv;
    inv.add("wheel", 4);
    // TODO: remove 1 wheel, assert total == 3, print total
    return 0;
}""",
   "expected": "3\n",
   "hints": [
     "Find the entry with a loop over items_ and compare .first.",
     "Throw std::out_of_range if nothing matches, or if qty > entry.second.",
     "Assert total() == 3 after remove(\"wheel\", 1), then print the total."
   ],
   "solution": r"""#include <cassert>
#include <iostream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

class Inventory {
public:
    void add(const std::string& item, int qty) {
        if (qty <= 0) throw std::invalid_argument("qty");
        items_.push_back({item, qty});
    }
    int total() const {
        int sum = 0;
        for (const auto& e : items_) sum += e.second;
        return sum;
    }

    void remove(const std::string& item, int qty) {
        for (auto& entry : items_) {
            if (entry.first == item) {
                if (qty > entry.second) throw std::out_of_range("too many");
                entry.second -= qty;
                return;
            }
        }
        throw std::out_of_range("no such item");
    }

private:
    std::vector<std::pair<std::string, int>> items_;
};

int main() {
    Inventory inv;
    inv.add("wheel", 4);
    inv.remove("wheel", 1);
    assert(inv.total() == 3);
    std::cout << inv.total() << "\n";
    return 0;
}"""
 },
 "mistake": "Putting a side effect inside an assert - with NDEBUG the call vanishes and the program changes behaviour between builds.",
 "recap": "Small queries plus asserts turn a class into something you can prove works."
}
]
