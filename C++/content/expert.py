"""Expert track: 8 lessons - C++20 features, concurrency, measurement, capstone."""

LESSONS = [
{
 "id": "e01", "level": "expert", "title": "Concepts: templates that explain themselves", "minutes": 18,
 "tags": ["concepts", "c++20", "templates"],
 "goal": "Constrain a template so bad types fail with a readable error.",
 "explain": [
   "A concept names a requirement on a type. std::integral<T> is true when T is a whole number; you can combine concepts with || and && to make your own.",
   "Writing template <Numeric T> instead of template <typename T> means the compiler checks the requirement at the call site and says 'constraints not satisfied', instead of dumping twenty lines from inside the body."
 ],
 "example": {
   "title": "A numeric-only function",
   "code": r"""#include <concepts>
#include <iostream>
#include <string>

template <typename T>
concept Numeric = std::integral<T> || std::floating_point<T>;

template <Numeric T>
T twice(T value) {
    return value * 2;
}

int main() {
    std::cout << twice(4) << "\n";
    std::cout << twice(2.5) << "\n";

    static_assert(Numeric<int>);
    static_assert(!Numeric<std::string>);

    std::cout << "checked\n";
    return 0;
}""",
   "output": "8\n5\nchecked\n",
   "notes": [
     ["concept Numeric = ...", "names a requirement other code can reuse"],
     ["template <Numeric T>", "the requirement replaces 'typename'"],
     ["static_assert(!Numeric<std::string>)", "checked at compile time, costs nothing at run time"]
   ]
 },
 "predict": {
   "q": "What does twice(std::string(\"ab\")) do?",
   "options": ["Compiles and prints abab", "Fails to compile: constraints not satisfied", "Throws at run time"],
   "answer": 1,
   "why": "std::string is not integral or floating point, so the constraint rejects it before any body is compiled."
 },
 "quiz": [
   {"q": "What is a concept?",
    "options": ["A named compile-time requirement on a type", "A comment", "A run-time check"],
    "answer": 0,
    "why": "It is a predicate on types evaluated during compilation, used to constrain templates."},
   {"q": "Why are constrained templates easier to debug?",
    "options": ["They compile faster", "The error names the unmet requirement instead of the body", "They cannot fail"],
    "answer": 1,
    "why": "The check happens at the call site, so the message points at your argument, not at line 40 of the template."},
   {"q": "What does static_assert do?",
    "options": ["Checks a condition at compile time and stops the build if false", "Prints a message at run time", "Adds a debug breakpoint"],
    "answer": 0,
    "why": "It is evaluated by the compiler and has zero run-time cost."}
 ],
 "activity": {
   "goal": "Write a concept HasSize that is true for anything with a .size() method, and a template T describe(const T&) returning \"big\" when size() > 3, else \"small\".",
   "starter": r"""#include <concepts>
#include <iostream>
#include <string>
#include <vector>

// TODO: concept HasSize

// TODO: template <HasSize T> std::string describe(const T& value)

int main() {
    // TODO: print describe(std::string("robot")) and describe(std::string("ai"))
    return 0;
}""",
   "expected": "big\nsmall\n",
   "hints": [
     "A concept can test an expression: requires(T t) { t.size(); }",
     "The function returns std::string and compares value.size() with 3.",
     "template <HasSize T> std::string describe(const T& value) { return value.size() > 3 ? \"big\" : \"small\"; }"
   ],
   "solution": r"""#include <concepts>
#include <iostream>
#include <string>
#include <vector>

template <typename T>
concept HasSize = requires(T t) {
    t.size();
};

template <HasSize T>
std::string describe(const T& value) {
    return value.size() > 3 ? "big" : "small";
}

int main() {
    std::cout << describe(std::string("robot")) << "\n";
    std::cout << describe(std::string("ai")) << "\n";
    return 0;
}"""
 },
 "mistake": "Writing a concept that is so broad it accepts almost everything - a constraint that never rejects anything gives none of the error-message benefit.",
 "recap": "Concepts turn template requirements into compiled checks with clear messages."
},
{
 "id": "e02", "level": "expert", "title": "Ranges and views", "minutes": 18,
 "tags": ["ranges", "views", "c++20"],
 "goal": "Filter and transform a collection without writing loops or copies.",
 "explain": [
   "A view is a lightweight, lazy description of a sequence: filter, transform, take. Nothing is computed until you iterate, and nothing is copied.",
   "The pipe syntax reads left to right: scores | views::filter(...) | views::transform(...). It replaces the begin/end pairs and the temporary vectors that old algorithms needed."
 ],
 "example": {
   "title": "Grades from scores",
   "code": r"""#include <iostream>
#include <ranges>
#include <vector>

int main() {
    std::vector<int> scores{70, 95, 88, 60, 100};

    auto grades = scores
                | std::views::filter([](int s) { return s >= 75; })
                | std::views::transform([](int s) { return s / 10; });

    for (int g : grades) {
        std::cout << g << " ";
    }
    std::cout << "\n";

    for (int s : scores | std::views::take(3)) {
        std::cout << s << " ";
    }
    std::cout << "\n";
    return 0;
}""",
   "output": "9 8 10 \n70 95 88 \n",
   "notes": [
     ["views::filter(...)", "keeps only elements the predicate accepts"],
     ["views::transform(...)", "maps each remaining element"],
     ["views::take(3)", "the first three, lazily"],
     ["no vector is created", "the pipeline is evaluated during the loop"]
   ]
 },
 "predict": {
   "q": "How many elements are read from scores by the second loop?",
   "options": ["All five", "Three - take stops requesting after the third", "None until the loop ends"],
   "answer": 1,
   "why": "take(3) ends the pipeline after three elements, which is the point of lazy views."
 },
 "quiz": [
   {"q": "What is a view?",
    "options": ["A copy of the data", "A lazy, non-owning description of a sequence", "A new container type"],
    "answer": 1,
    "why": "Views refer to the original range and compute on demand."},
   {"q": "Why must the underlying container outlive the view?",
    "options": ["It does not matter", "The view refers to it and does not own it", "Views copy data on creation"],
    "answer": 1,
    "why": "A view over destroyed data is a dangling range - the same lifetime rule as references."},
   {"q": "Which is equivalent to views::take(n)?",
    "options": ["The first n elements", "The last n elements", "Every nth element"],
    "answer": 0,
    "why": "take keeps the first n; drop would skip the first n."}
 ],
 "activity": {
   "goal": "From a list of words, keep those longer than 3 letters, uppercase them, and print them space separated.",
   "starter": r"""#include <cctype>
#include <iostream>
#include <ranges>
#include <string>
#include <vector>

int main() {
    std::vector<std::string> words{"robot", "ai", "battery", "go", "sensor"};
    // TODO: filter size > 3, transform to uppercase
    // TODO: print them space separated
    return 0;
}""",
   "expected": "ROBOT BATTERY SENSOR \n",
   "hints": [
     "Build a pipeline: words | views::filter(...) | views::transform(...)",
     "The transform lambda takes const std::string& and returns a new uppercase string.",
     "Use a small loop inside the lambda, or std::transform from <algorithm>."
   ],
   "solution": r"""#include <cctype>
#include <iostream>
#include <ranges>
#include <string>
#include <vector>

int main() {
    std::vector<std::string> words{"robot", "ai", "battery", "go", "sensor"};

    auto loud = words
              | std::views::filter([](const std::string& w) { return w.size() > 3; })
              | std::views::transform([](const std::string& w) {
                    std::string out = w;
                    for (char& c : out) {
                        c = static_cast<char>(std::toupper(c));
                    }
                    return out;
                });

    for (const auto& w : loud) {
        std::cout << w << " ";
    }
    std::cout << "\n";
    return 0;
}"""
 },
 "mistake": "Building a view over a temporary container, or storing a view and using it after the underlying vector was resized.",
 "recap": "Ranges describe work lazily; nothing runs until you iterate."
},
{
 "id": "e03", "level": "expert", "title": "Threads and mutexes", "minutes": 18,
 "tags": ["thread", "mutex", "concurrency"],
 "goal": "Run work in parallel without corrupting shared data.",
 "explain": [
   "std::thread starts a function on another core. The program does not wait for it: you must call join() before the thread object is destroyed, or the program terminates.",
   "Two threads writing the same variable at once is a data race - undefined behaviour, even if it usually 'works'. A std::mutex with std::lock_guard serialises the critical section, and the guard releases the lock automatically."
 ],
 "example": {
   "title": "Four threads, one counter",
   "code": r"""#include <iostream>
#include <mutex>
#include <thread>
#include <vector>

int main() {
    int counter = 0;
    std::mutex m;

    auto work = [&]() {
        for (int i = 0; i < 1000; ++i) {
            std::lock_guard<std::mutex> lock(m);
            ++counter;
        }
    };

    std::vector<std::thread> workers;
    for (int i = 0; i < 4; ++i) {
        workers.emplace_back(work);
    }
    for (auto& t : workers) {
        t.join();
    }

    std::cout << "counter " << counter << "\n";
    return 0;
}""",
   "output": "counter 4000\n",
   "notes": [
     ["std::thread t(work)", "starts work on another thread immediately"],
     ["lock_guard lock(m)", "locks at construction, unlocks at the end of the block"],
     ["t.join()", "waits for that thread to finish - required before destruction"],
     ["counter == 4000", "exactly 4000 because every increment is protected"]
   ]
 },
 "predict": {
   "q": "What would counter print if you removed the lock_guard?",
   "options": ["Still 4000 every time", "Usually less than 4000, varying between runs", "Exactly 3000"],
   "answer": 1,
   "why": "Concurrent read-modify-write loses updates. It is undefined behaviour, so any value is legal - and it may even print 4000 by luck."
 },
 "quiz": [
   {"q": "What happens if a std::thread is destroyed without join or detach?",
    "options": ["It is joined automatically", "std::terminate is called", "It keeps running"],
    "answer": 1,
    "why": "The standard refuses to guess: destructing a joinable thread terminates the program."},
   {"q": "Why is lock_guard preferred over manual lock/unlock?",
    "options": ["It is faster", "It unlocks on every exit path, including exceptions", "It allows recursive locking"],
    "answer": 1,
    "why": "It is RAII for mutexes - the unlock cannot be forgotten."},
   {"q": "What is a data race?",
    "options": ["Two threads reading the same constant", "Two threads accessing the same memory with at least one write and no synchronisation", "A thread that runs too fast"],
    "answer": 1,
    "why": "It is undefined behaviour, which is why the result can change between runs and compilers."}
 ],
 "activity": {
   "goal": "Start three threads that each add 10 to a shared total under a mutex, join them, and print the total.",
   "starter": r"""#include <iostream>
#include <mutex>
#include <thread>
#include <vector>

int main() {
    int total = 0;
    std::mutex m;
    // TODO: three threads, each adding 10 under lock_guard
    // TODO: join all, print total
    return 0;
}""",
   "expected": "30\n",
   "hints": [
     "The lambda captures by reference: [&]() { ... }",
     "Inside: std::lock_guard<std::mutex> lock(m); total += 10;",
     "Store the threads in a vector, then join every one before printing."
   ],
   "solution": r"""#include <iostream>
#include <mutex>
#include <thread>
#include <vector>

int main() {
    int total = 0;
    std::mutex m;

    auto work = [&]() {
        std::lock_guard<std::mutex> lock(m);
        total += 10;
    };

    std::vector<std::thread> workers;
    for (int i = 0; i < 3; ++i) {
        workers.emplace_back(work);
    }
    for (auto& t : workers) {
        t.join();
    }

    std::cout << total << "\n";
    return 0;
}"""
 },
 "mistake": "Holding a lock while doing slow work (I/O, sleeping), which serialises everything and removes the benefit of threads.",
 "recap": "Threads run concurrently; a mutex makes the shared part safe."
},
{
 "id": "e04", "level": "expert", "title": "async and future", "minutes": 17,
 "tags": ["async", "future", "concurrency"],
 "goal": "Start work now and collect the result when you need it.",
 "explain": [
   "std::async runs a function asynchronously and hands back a std::future - a placeholder for a result that may not exist yet. Calling get() waits only if the work is still running.",
   "Launch policy matters: std::launch::async guarantees a new thread; without it the implementation may defer the work until get(), which is not what you want when you are trying to overlap tasks."
 ],
 "example": {
   "title": "Two seconds of work, overlapped",
   "code": r"""#include <chrono>
#include <future>
#include <iostream>
#include <thread>

int slow_add(int a, int b) {
    std::this_thread::sleep_for(std::chrono::milliseconds(20));
    return a + b;
}

int main() {
    auto f = std::async(std::launch::async, slow_add, 2, 3);
    std::cout << "started\n";
    const int value = f.get();
    std::cout << "result " << value << "\n";
    std::cout << "kept " << value << " (get returns once)\n";
    return 0;
}""",
   "output": "started\nresult 5\nkept 5 (get returns once)\n",
   "notes": [
     ["std::async(launch::async, f, args)", "starts immediately on a new thread"],
     ["f.get()", "waits for the result, or returns it if ready"],
     ["get() once", "it moves the value out - calling it again throws std::future_error"]
   ]
 },
 "predict": {
   "q": "When does the 20 ms sleep happen?",
   "options": ["When async is called", "Only when get() is called", "After main ends"],
   "answer": 0,
   "why": "With launch::async the work starts right away, so the sleep overlaps with the printing of 'started'."
 },
 "quiz": [
   {"q": "What does future::get() do?",
    "options": ["Checks whether the task finished", "Waits for and returns the result, then invalidates the future", "Starts the task"],
    "answer": 1,
    "why": "get() blocks until the value exists. Calling it twice on the same future is an error; the value must be cached first."},
   {"q": "Why pass std::launch::async explicitly?",
    "options": ["It is required syntax", "Otherwise the work may be deferred until get(), so nothing overlaps", "It uses fewer threads"],
    "answer": 1,
    "why": "The default policy lets the implementation choose, including deferring."},
   {"q": "What is a data race's relationship to async?",
    "options": ["None", "Tasks may run on another thread, so shared data still needs protection", "async prevents races automatically"],
    "answer": 1,
    "why": "async moves work to a thread; it does not add synchronisation to your variables."}
 ],
 "activity": {
   "goal": "Launch two async tasks that return 10 and 32, call get() on both, and print their sum.",
   "starter": r"""#include <future>
#include <iostream>

int value(int n) { return n; }

int main() {
    // TODO: two std::async tasks with std::launch::async
    // TODO: print the sum of both get() results
    return 0;
}""",
   "expected": "42\n",
   "hints": [
     "auto a = std::async(std::launch::async, value, 10);",
     "The second is the same call with 32.",
     "Print a.get() + b.get() - both must be called."
   ],
   "solution": r"""#include <future>
#include <iostream>

int value(int n) { return n; }

int main() {
    auto a = std::async(std::launch::async, value, 10);
    auto b = std::async(std::launch::async, value, 32);

    std::cout << a.get() + b.get() << "\n";
    return 0;
}"""
 },
 "mistake": "Letting a future go out of scope without calling get() - with launch::async the destructor blocks until the task finishes, which can look like a mystery hang.",
 "recap": "async starts work, future carries the result, get() waits only when needed."
},
{
 "id": "e05", "level": "expert", "title": "Measuring performance", "minutes": 17,
 "tags": ["chrono", "benchmark", "performance"],
 "goal": "Measure how long code takes, and avoid believing a single run.",
 "explain": [
   "std::chrono::steady_clock is monotonic, which is what you want for durations: it cannot jump backwards like the wall clock can.",
   "Measure a loop that runs many times, not one call, and run it several times. First runs are slower (cold caches, page faults), and a release build with optimisation can be ten times faster than a debug build."
 ],
 "example": {
   "title": "Timing a vector build",
   "code": r"""#include <chrono>
#include <iostream>
#include <vector>

int main() {
    const int N = 200000;

    auto start = std::chrono::steady_clock::now();
    std::vector<int> data;
    for (int i = 0; i < N; ++i) {
        data.push_back(i);
    }
    auto end = std::chrono::steady_clock::now();

    auto us = std::chrono::duration_cast<std::chrono::microseconds>(end - start).count();

    std::cout << "pushed " << data.size() << "\n";
    std::cout << "measured " << (us >= 0) << "\n";
    std::cout << "under a second " << (us < 1000000) << "\n";
    return 0;
}""",
   "output": "pushed 200000\nmeasured 1\nunder a second 1\n",
   "notes": [
     ["steady_clock::now()", "a monotonic timestamp"],
     ["duration_cast<microseconds>", "converts the difference to a plain number"],
     ["(us < 1000000)", "a stable claim; the exact time would change every run"]
   ]
 },
 "predict": {
   "q": "Why does this example print a comparison instead of the microseconds?",
   "options": ["Printing numbers is hard", "The exact time changes every run, so an exact expected output would be wrong", "Because us is not a number"],
   "answer": 1,
   "why": "A lesson that claims an exact duration would fail on a faster machine - the check must be a property, not a number."
 },
 "quiz": [
   {"q": "Why steady_clock rather than system_clock?",
    "options": ["It is more precise", "It never jumps backwards, so durations are meaningful", "It is the only one that compiles"],
    "answer": 1,
    "why": "system_clock can be adjusted by the operating system, which corrupts a measurement."},
   {"q": "Why run the measured code many times?",
    "options": ["To warm up the CPU", "Timers are noisy and single fast operations are lost in that noise", "Because loops are faster"],
    "answer": 1,
    "why": "Measuring 200000 iterations gives a signal much larger than the timer's resolution."},
   {"q": "What does -O0 versus -O2 change?",
    "options": ["Only file size", "The machine code, often by a large factor", "Nothing for C++"],
    "answer": 1,
    "why": "Optimisation is why you should benchmark a release build - a debug build measures the compiler's generosity, not your algorithm."}
 ],
 "activity": {
   "goal": "Time two loops of 100000 iterations: one appending to a vector without reserve, one with reserve. Print the sizes and whether both finished under a second.",
   "starter": r"""#include <chrono>
#include <iostream>
#include <vector>

int main() {
    const int N = 100000;
    // TODO: time a vector push_back loop (no reserve)
    // TODO: time another with data.reserve(N)
    // TODO: print both sizes and (both under a second)
    return 0;
}""",
   "expected": "sizes 100000 100000\nunder a second 1\n",
   "hints": [
     "Wrap each loop in its own pair of now() calls.",
     "reserve(N) before the loop avoids repeated reallocation.",
     "Convert with duration_cast<microseconds> and compare both with 1000000."
   ],
   "solution": r"""#include <chrono>
#include <iostream>
#include <vector>

int main() {
    const int N = 100000;

    auto t0 = std::chrono::steady_clock::now();
    std::vector<int> a;
    for (int i = 0; i < N; ++i) a.push_back(i);
    auto t1 = std::chrono::steady_clock::now();

    auto t2 = std::chrono::steady_clock::now();
    std::vector<int> b;
    b.reserve(N);
    for (int i = 0; i < N; ++i) b.push_back(i);
    auto t3 = std::chrono::steady_clock::now();

    auto first = std::chrono::duration_cast<std::chrono::microseconds>(t1 - t0).count();
    auto second = std::chrono::duration_cast<std::chrono::microseconds>(t3 - t2).count();

    std::cout << "sizes " << a.size() << " " << b.size() << "\n";
    std::cout << "under a second " << (first < 1000000 && second < 1000000) << "\n";
    return 0;
}"""
 },
 "mistake": "Benchmarking a debug build, or timing a single call and drawing conclusions from noise.",
 "recap": "Measure with steady_clock, measure in bulk, and only trust comparisons."
},
{
 "id": "e06", "level": "expert", "title": "Project organisation and build checks", "minutes": 17,
 "tags": ["cmake", "static_assert", "build"],
 "goal": "Make the build fail loudly when the standard or feature is wrong.",
 "explain": [
   "A real project states its requirements in the build file: the C++ standard, warnings, and the sources. CMake is the common choice; the compiler flags matter more than the tool.",
   "You can also assert requirements in code. static_assert(__cplusplus >= 202002L) turns 'this needs C++20' into a build error with your own message instead of a wall of syntax errors."
 ],
 "example": {
   "title": "Asking the compiler what it supports",
   "code": r"""#include <iostream>
#include <version>

static_assert(__cplusplus >= 202002L, "This course needs C++20 or newer");

int main() {
#if defined(__cpp_concepts) && defined(__cpp_lib_ranges)
    std::cout << "concepts and ranges available\n";
#else
    std::cout << "missing C++20 library features\n";
#endif

    std::cout << "standard " << __cplusplus << "\n";
    return 0;
}""",
   "output": "concepts and ranges available\nstandard 202002\n",
   "notes": [
     ["static_assert(cond, \"message\")", "a compile-time check with your own error text"],
     ["__cplusplus", "202002 for C++20, 201703 for C++17"],
     ["#if defined(...)", "feature macros let you support two standards from one file"]
   ]
 },
 "predict": {
   "q": "What happens if you build this file with -std=c++17?",
   "options": ["It compiles and prints 201703", "It fails on the static_assert with your message", "It runs but crashes"],
   "answer": 1,
   "why": "201703 < 202002, so the assertion fires at compile time and the build stops with 'This course needs C++20 or newer'."
 },
 "quiz": [
   {"q": "Why put the standard in the build file rather than a comment?",
    "options": ["Comments are ugly", "The build then enforces it for every file", "CMake requires it"],
    "answer": 1,
    "why": "A requirement in prose is a suggestion; one in the build is a rule."},
   {"q": "What does __cplusplus report?",
    "options": ["The compiler version", "The standard the compiler is using, as a number", "The build date"],
    "answer": 1,
    "why": "It is the language standard macro: 199711, 201103, 201703, 202002."},
   {"q": "Which is a feature-test macro?",
    "options": ["__cplusplus", "__cpp_lib_ranges", "NDEBUG"],
    "answer": 1,
    "why": "Feature macros like __cpp_lib_ranges exist only when the feature is present, which makes them safe to test with #ifdef."}
 ],
 "activity": {
   "goal": "Add a static_assert that sizeof(int) is 4, then print __cplusplus.",
   "starter": r"""#include <iostream>

// TODO: static_assert about sizeof(int)

int main() {
    // TODO: print __cplusplus
    return 0;
}""",
   "expected": "202002\n",
   "hints": [
     "static_assert(sizeof(int) == 4, \"int must be 4 bytes\");",
     "The macro is printed like any number: std::cout << __cplusplus;",
     "Remember the newline."
   ],
   "solution": r"""#include <iostream>

static_assert(sizeof(int) == 4, "int must be 4 bytes");

int main() {
    std::cout << __cplusplus << "\n";
    return 0;
}"""
 },
 "mistake": "Relying on a compiler default standard. Always state -std=c++20 (or the CMake equivalent) so the code means the same thing everywhere.",
 "recap": "Put requirements in the build and in static_assert, so they cannot be forgotten."
},
{
 "id": "e07", "level": "expert", "title": "Capstone 1: designing the classes", "minutes": 25,
 "tags": ["capstone", "design", "optional"],
 "goal": "Turn a fuzzy requirement into classes with clear responsibilities.",
 "explain": [
   "A mission planner needs a Task (data), a Planner (rules), and a way to ask 'what next?'. Each class does one job, and the Planner owns its tasks - no global state.",
   "next() returns std::optional<Task>: there may genuinely be nothing left to do, and the type says so instead of returning a fake task."
 ],
 "example": {
   "title": "planner.cpp - the core",
   "code": r"""#include <algorithm>
#include <iostream>
#include <optional>
#include <string>
#include <vector>

struct Task {
    std::string title;
    int priority;
    bool done = false;
};

class Planner {
public:
    void add(const std::string& title, int priority) {
        tasks_.push_back({title, priority, false});
    }

    bool complete(const std::string& title) {
        for (auto& t : tasks_) {
            if (t.title == title) {
                t.done = true;
                return true;
            }
        }
        return false;
    }

    std::optional<Task> next() const {
        const Task* best = nullptr;
        for (const auto& t : tasks_) {
            if (t.done) continue;
            if (!best || t.priority > best->priority) best = &t;
        }
        if (!best) return std::nullopt;
        return *best;
    }

    int remaining() const {
        return static_cast<int>(std::count_if(
            tasks_.begin(), tasks_.end(), [](const Task& t) { return !t.done; }));
    }

private:
    std::vector<Task> tasks_;
};

int main() {
    Planner p;
    p.add("charge", 5);
    p.add("say hello", 2);
    p.add("calibrate", 4);

    std::cout << "remaining " << p.remaining() << "\n";
    if (auto t = p.next()) std::cout << "next " << t->title << "\n";

    p.complete("charge");
    if (auto t = p.next()) std::cout << "then " << t->title << "\n";
    std::cout << "left " << p.remaining() << "\n";
    return 0;
}""",
   "output": "remaining 3\nnext charge\nthen calibrate\nleft 2\n",
   "notes": [
     ["struct Task", "plain data, no behaviour - easy to copy and print"],
     ["class Planner", "owns the vector and enforces the rules"],
     ["std::optional<Task> next()", "there may be nothing left, and the type says so"],
     ["const Task* best", "a pointer to the existing task, no copying"]
   ]
 },
 "predict": {
   "q": "What does next() return after all three tasks are completed?",
   "options": ["A Task with an empty title", "std::nullopt", "The last task again"],
   "answer": 1,
   "why": "Every task is done, so no candidate is found and the optional is empty - the caller must handle it."
 },
 "quiz": [
   {"q": "Why is Task a struct rather than a class?",
    "options": ["Structs are faster", "It is passive data with no invariant to protect", "Classes cannot be stored in vectors"],
    "answer": 1,
    "why": "Use a struct for plain bundles and a class when you need to enforce rules."},
   {"q": "Why does Planner own the tasks instead of exposing the vector?",
    "options": ["To save memory", "So nothing outside can break 'done' or bypass the ordering rule", "Because vectors are private by default"],
    "answer": 1,
    "why": "Ownership is what lets the class keep its promises."},
   {"q": "What is the cost of returning std::optional<Task> by value?",
    "options": ["A heap allocation", "One copy of the task, which is small", "Nothing, it is a reference"],
    "answer": 1,
    "why": "The optional holds a Task inline; copying a small struct is cheap and safe."}
 ],
 "activity": {
   "goal": "Add a count_done() method returning how many tasks are finished, and print it after completing two tasks.",
   "starter": r"""#include <algorithm>
#include <iostream>
#include <optional>
#include <string>
#include <vector>

struct Task {
    std::string title;
    int priority;
    bool done = false;
};

class Planner {
public:
    void add(const std::string& title, int priority) {
        tasks_.push_back({title, priority, false});
    }
    bool complete(const std::string& title) {
        for (auto& t : tasks_) {
            if (t.title == title) { t.done = true; return true; }
        }
        return false;
    }
    // TODO: int count_done() const
private:
    std::vector<Task> tasks_;
};

int main() {
    Planner p;
    p.add("charge", 5);
    p.add("calibrate", 4);
    p.add("wave", 1);
    // TODO: complete charge and calibrate, print "done " and count_done()
    return 0;
}""",
   "expected": "done 2\n",
   "hints": [
     "count_done uses std::count_if with [](const Task& t) { return t.done; }.",
     "Cast the result to int if you return int.",
     "Complete both by title, then print \"done \" << p.count_done()."
   ],
   "solution": r"""#include <algorithm>
#include <iostream>
#include <optional>
#include <string>
#include <vector>

struct Task {
    std::string title;
    int priority;
    bool done = false;
};

class Planner {
public:
    void add(const std::string& title, int priority) {
        tasks_.push_back({title, priority, false});
    }
    bool complete(const std::string& title) {
        for (auto& t : tasks_) {
            if (t.title == title) { t.done = true; return true; }
        }
        return false;
    }
    int count_done() const {
        return static_cast<int>(std::count_if(
            tasks_.begin(), tasks_.end(), [](const Task& t) { return t.done; }));
    }
private:
    std::vector<Task> tasks_;
};

int main() {
    Planner p;
    p.add("charge", 5);
    p.add("calibrate", 4);
    p.add("wave", 1);

    p.complete("charge");
    p.complete("calibrate");

    std::cout << "done " << p.count_done() << "\n";
    return 0;
}"""
 },
 "mistake": "Letting the UI, the storage and the rules live in one class. Split by responsibility and each part becomes testable.",
 "recap": "Design is deciding who owns what and what each class promises."
},
{
 "id": "e08", "level": "expert", "title": "Capstone 2: a test harness and the finish", "minutes": 25,
 "tags": ["capstone", "tests", "assert"],
 "goal": "Wire the planner into a tiny test harness so the rules stay true.",
 "explain": [
   "A test harness runs checks and counts failures instead of stopping at the first one, so you see every broken rule in one run. Returning a non-zero exit code lets a script or CI decide pass or fail.",
   "Keep the checks small and named. 'add positive' tells you what broke; 'test 3' does not."
 ],
 "example": {
   "title": "harness.cpp",
   "code": r"""#include <iostream>
#include <string>

int checks = 0;
int failures = 0;

void check(bool ok, const std::string& what) {
    ++checks;
    if (!ok) {
        ++failures;
        std::cout << "FAIL " << what << "\n";
    }
}

int add(int a, int b) { return a + b; }

int main() {
    check(add(2, 3) == 5, "add positive");
    check(add(-1, 1) == 0, "add cancels");
    check(add(0, 0) == 0, "add zeros");

    std::cout << checks << " checks, " << failures << " failures\n";
    return failures == 0 ? 0 : 1;
}""",
   "output": "3 checks, 0 failures\n",
   "notes": [
     ["check(condition, name)", "records the result instead of aborting"],
     ["counts, not asserts", "you see every failure in one run"],
     ["return failures == 0 ? 0 : 1", "the exit code is what a script reads"]
   ]
 },
 "predict": {
   "q": "If add had a bug, what would the program print and return?",
   "options": ["Nothing, it aborts", "A FAIL line, then a summary with failures above zero, and exit code 1", "It would crash"],
   "answer": 1,
   "why": "The harness keeps going: each failing check prints its name, the summary counts them, and main returns 1."
 },
 "quiz": [
   {"q": "Why count failures instead of stopping at the first?",
    "options": ["It is faster", "One run shows every broken rule", "Asserts are deprecated"],
    "answer": 1,
    "why": "Fixing one failure at a time hides the rest; a summary shows the shape of the problem."},
   {"q": "Why does the exit code matter?",
    "options": ["It does not", "Scripts and CI read it to decide whether the build passed", "It is printed to the user"],
    "answer": 1,
    "why": "Exit code 0 means success; anything else fails the pipeline."},
   {"q": "What makes a good test name?",
    "options": ["A number", "A short statement of the rule being checked", "The line number"],
    "answer": 1,
    "why": "The name is the only clue you get when it fails at 2am."}
 ],
 "activity": {
   "goal": "Use the harness to check two rules of a Wallet: withdrawing more than the balance fails, and a valid withdrawal lowers the balance.",
   "starter": r"""#include <iostream>
#include <string>

int checks = 0;
int failures = 0;

void check(bool ok, const std::string& what) {
    ++checks;
    if (!ok) {
        ++failures;
        std::cout << "FAIL " << what << "\n";
    }
}

class Wallet {
public:
    explicit Wallet(int start) : balance_(start) {}
    bool withdraw(int amount) {
        if (amount <= 0 || amount > balance_) return false;
        balance_ -= amount;
        return true;
    }
    int balance() const { return balance_; }
private:
    int balance_;
};

int main() {
    // TODO: two checks - overdraw refused, valid withdrawal lowers balance
    // TODO: print the summary line
    return 0;
}""",
   "expected": "2 checks, 0 failures\n",
   "hints": [
     "Create a Wallet w{100};",
     "check(!w.withdraw(150), \"overdraw refused\");",
     "check(w.withdraw(40) && w.balance() == 60, \"valid withdrawal\");"
   ],
   "solution": r"""#include <iostream>
#include <string>

int checks = 0;
int failures = 0;

void check(bool ok, const std::string& what) {
    ++checks;
    if (!ok) {
        ++failures;
        std::cout << "FAIL " << what << "\n";
    }
}

class Wallet {
public:
    explicit Wallet(int start) : balance_(start) {}
    bool withdraw(int amount) {
        if (amount <= 0 || amount > balance_) return false;
        balance_ -= amount;
        return true;
    }
    int balance() const { return balance_; }
private:
    int balance_;
};

int main() {
    Wallet w{100};

    check(!w.withdraw(150), "overdraw refused");
    check(w.withdraw(40) && w.balance() == 60, "valid withdrawal lowers balance");

    std::cout << checks << " checks, " << failures << " failures\n";
    return failures == 0 ? 0 : 1;
}"""
 },
 "mistake": "Writing tests that only exercise the happy path. The guard you never test is the one that quietly stops working.",
 "recap": "A harness that counts failures is the cheapest safety net a project can have."
}
]
