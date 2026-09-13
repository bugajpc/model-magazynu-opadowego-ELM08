import { SectionShell, P, H2, IC, Callout } from "../components/ui";
import { Code } from "../components/Code";
import { Quiz } from "../components/interactives";
import type { SectionProps } from "./types";

const STAGES = `        source                preprocessed          compiled
main.cpp  ──────────────►   main.cpp.i  ──────────────────►   main.cpp.s
 (your text)               (includes + macros           (assembly,
                           expanded)                     human-readable)

        assembled                    linked                runs
main.cpp.o  ◄──────────────────  main.cpp.o  ──────────────────►   ./main
 (machine code,               (object file:         (final program,
  one .o per file)            machine code,          ready to run)
                              but unresolved)
                              names like std::cout)`;

export default function S02({ go, prev, next }: SectionProps) {
  return (
    <SectionShell
      num="02"
      phase="Getting started"
      title="The toolchain: editor, compiler, linker"
      tagline="What 'compiling' really means, and the commands you will use every single day."
      skills={["Reading compiler errors", "Compiling from the terminal", "Debugging mindset"]}
      prev={prev}
      next={next}
      onNav={go}
    >
      <P>
        C++ code is text. The program you run is machine code. Between the two sits the{" "}
        <strong>toolchain</strong>. Understanding it will save you hours of confusion later —
        almost every "weird" C++ error message traces back to one of these four stages.
      </P>

      <H2>One source file → four stages → executable</H2>
      <Code title="The pipeline (simplified)" code={STAGES} />
      <ul className="clean">
        <li><strong>Preprocessor</strong> — expands <IC>#include</IC> and macros into the source.</li>
        <li><strong>Compiler</strong> — translates to assembly, then machine code; emits an <em>object file</em> (<IC>.o</IC>/<IC>.obj</IC>).</li>
        <li><strong>Assembler</strong> — assembly → raw machine code (often bundled with the compiler).</li>
        <li><strong>Linker</strong> — joins all object files plus libraries (like the C++ standard library) into one executable. Fills in the addresses of things like <IC>std::cout</IC>.</li>
      </ul>

      <Callout kind="warn" title="Two kinds of errors">
        <P>
          <strong>Compile errors</strong> stop the build with messages like <IC>error: expected ';'</IC>.
          <strong>Linker errors</strong> appear only when the linker runs: <IC>undefined reference to 'max3'</IC> —
          you used a function whose definition was never included in the build. You will meet both in this lecture.
        </P>
      </Callout>

      <H2>Your everyday commands</H2>
      <Code
        title="Terminal"
        code={`# compile (g++ = GNU C++ compiler)
g++ main.cpp -o app

# run it
./app        # (Windows: app.exe)

# compile with all warnings — do this always
g++ main.cpp -o app -std=c++17 -Wall -Wextra`}
      />
      <Callout kind="tip" title="g++ vs clang++ vs MSVC">
        <P>
          <IC>g++</IC> (GCC) and <IC>clang++</IC> are free and work on Linux, macOS and Windows; MSVC is
          the standard compiler on Windows. They are ~95% interchangeable for everything in this lecture.
          Your compiler's quality matters: it catches bugs for you and decides how fast your binary runs.
        </P>
      </Callout>

      <H2>Check yourself</H2>
      <Quiz
        id="q1"
        prompt="Put the four stages of building a C++ program in the correct order."
        options={[
          "preprocess → compile → assemble → link",
          "compile → preprocess → link → assemble",
          "assemble → compile → preprocess → link",
          "link → preprocess → compile → assemble",
        ]}
        answer={0}
        explain={
          <>
            The preprocessor cleans the source first, the compiler+assembler turn it into an object
            file, and the linker assembles all object files and libraries into the final program.
          </>
        }
      />
      <Quiz
        id="q2"
        prompt="What does the flag <code className=\"ic\">-Wall</code> do?"
        options={[
          "Makes the program run faster",
          "Turns on most compiler warnings",
          "Writes a wall of logs to a file",
          "Wall-times the program",
        ]}
        answer={1}
        explain={
          <>
            Warnings are the compiler telling you "this compiles, but smells like a bug". Treat
            zero warnings as a goal — unit 15 goes deeper into flags.
          </>
        }
      />
      <Quiz
        id="q3"
        prompt="Which of these tools compiles C++ source code?"
        options={["g++", "pip", "npm", "make (by itself)"]}
        answer={0}
        explain={
          <>
            <IC>g++</IC> is the compiler driver. <IC>pip</IC> and <IC>npm</IC> are package managers for
            Python and JavaScript. <IC>make</IC> is a build orchestrator — it <em>calls</em> the compiler,
            it does not compile anything itself.
          </>
        }
      />
    </SectionShell>
  );
}
