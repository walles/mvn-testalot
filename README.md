# mvn-testalot

Run `mvn test` multiple times and report on slow / flaky tests.

# Example commands

Run `mvn test` 10 times:
```
mvn-testalot.py 10
```

Analyze results:
```
mvn-testalot.py report
```

# Example output

Output is printed as human readable Markdown, for easy GitHub bug reporting.

# Slow tests

| Result |    Duration   | Name |
|--------|---------------|------|
| FAIL   |   9.8s (0.6s) | `org.example.DemoTest.bar()` |
| FAIL   |   9.2s (0.7s) | `org.example.DemoTest.foo()` |
| ok     |   8.5s (0.2s) | `org.example.DemoTest.baz()` |

# Flaky tests

`.` = pass, `x` = fail, `E` = error

| Result | Name |
|--------|------|
| `....x....x` | `org.example.DemoTest.bar()` |
| `x....x....` | `org.example.DemoTest.foo()` |
