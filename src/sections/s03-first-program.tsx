import { SectionShell, P, H2, IC, Callout } from "../components/ui";
import { Code } from "../components/Code";
import { Quiz, FillCode, PredictOutput } from "../components/interactives";
import type { SectionProps } from "./types";

export default function S03({ go, prev, next }: SectionProps) {
  return (
    <SectionShell
      num="03"
      phase="Getting started"
      title="Anatomy of a C++ program"
      tagline="Every C++ program has a skeleton. Learn it once, use it forever."
      skills={["Writing a full program", "Console I/O basics", "Exit codes"]}
      prev={prev}
      next={next}
      onNav={go}
    >
      <P>
        Here is the minimal hello-world — and next to it, what each line is <em>for</em>.
      </P>
      <Code
        title="hello.cpp"
        code={`#include <iostream>          // 1. pull in the input/output library

int main() {                  // 2. entry point: the OS calls main()
    std::cout << "Hello, world!" << std::endl;  // 3. print + newline
    return 0;                 // 4. exit status 0 = success
}`}
      />
      <ul className="clean">
        <li><strong>1. <IC>#include &lt;iostream&gt;</IC></strong> — tells the preprocessor to splice in the declaration of the console I/O library.</li>
        <li><strong>2. <IC>int main()</IC></strong> — the function your program starts in. Every C++ program has exactly one.</li>
        <li><strong>3. <IC>std::cout &lt;&lt; …</IC></strong> — <IC>cout</IC> is the console output stream; <IC>&lt;&lt;</IC> ("stream into") sends values to it. <IC>std::</IC> is the namespace that holds the standard library.</li>
        <li><strong>4. <IC>return 0;</IC></strong> — the exit status, reported to the operating system.</li>
      </ul>

      <Callout kind="info" title="using namespace std; — a short cut, not a habit">
        <P>
          You will see <IC>using namespace std;</IC> after the include. It lets you write <IC>cout</IC>{" "}
          instead of <IC>std::cout</IC>. Fine in small homework; in real projects it can cause name
          collisions, so this lecture always writes <IC>std::</IC> explicitly.
        </P>
      </Callout>

      <H2>Exit codes: how your program talks to the OS</H2>
      <P>
        The integer returned by <IC>main</IC> is the <strong>exit code</strong>. By convention{" "}
        <IC>0</IC> means "success"; anything else signals a failure. Scripts, CI systems and other
        programs check it:
      </P>
      <Code title="shell" code={`g++ crash.cpp -o crash
./crash; echo "exit code: $?"     # $? = the last program's exit code`} />

      <H2>Fill in the blanks</H2>
      <FillCode
        id="f1"
        prompt={
          <>
            Complete the program so it prints <IC>Hello, world!</IC> and exits successfully.
          </>
        }
        code={`#include <iostream>

int main() {
    ___
    ___
}`}
        expected={['std::cout << "Hello, world!" << std::endl;', "return 0;"]}
        hint="Line 1: stream a message into std::cout and end the line. Line 2: return 0;"
      />

      <H2>Predict the output</H2>
      <PredictOutput
        id="p1"
        prompt="What does this program print?"
        code={`#include <iostream>
int main() {
    std::cout << "C++" << " rocks!" << std::endl;
    std::cout << 6 * 7 << std::endl;
    return 0;
}`}
        accept={["C++ rocks! 42"]}
        explain={
          <>
            <IC>&lt;&lt;</IC> chains left to right: first the text <IC>"C++"</IC>, then{" "}
            <IC>" rocks!"</IC> (no space in the literal — the two strings just sit side by side),
            then a newline, then the computed value <IC>6 * 7</IC>.
          </>
        }
      />

      <H2>Check yourself</H2>
      <Quiz
        id="q1"
        prompt="What does <code className=\"ic\">return 3;</code> at the end of <code className=\"ic\">main</code> do?"
        options={[
          "Prints the number 3 on the console",
          "Exits the program with status 3 (visible to the OS as a failure)",
          "Loops the program 3 times",
          "Returns to line 3 of the file",
        ]}
        answer={1}
        explain={
          <>
            Exit codes are not printed — they are reported to the operating system.{" "}
            <IC>0</IC> = success, non-zero = "something went wrong". Our error-handling unit (13)
            uses this deliberately.
          </>
        }
      />
    </SectionShell>
  );
}
