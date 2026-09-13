import { SectionShell, P, H2, IC, Callout } from "../components/ui";
import { Code } from "../components/Code";
import { Quiz } from "../components/interactives";
import type { SectionProps } from "./types";

const CODE = `// A real (very small) console application:
// it asks for a name and greets you.
#include <iostream>
#include <string>

int main() {
    std::string name;
    std::cout << "Who are you? ";
    std::cin >> name;          // read from the keyboard
    std::cout << "Hello, " << name << "! C++ says hi." << std::endl;
    return 0;                  // 0 = "everything worked"
}`;

export default function S01({ go, prev, next }: SectionProps) {
  return (
    <SectionShell
      num="01"
      phase="Getting started"
      title="Why C++? The road ahead"
      tagline="What makes C++ worth learning, and what this lecture will build in you."
      skills={["Mental model of compilation", "Reading real C++ code", "Big-picture roadmap"]}
      prev={prev}
      next={next}
      onNav={go}
    >
      <P>
        C++ is one of the most important languages in the world. Game engines, databases, browsers,
        operating systems, financial trading systems, medical devices and robotics are built with it.
        When you learn C++ well, you understand <em>how computers actually work</em> — memory,
        performance, what happens between you pressing Enter and the result appearing on screen.
      </P>
      <P>
        This lecture is a guided tour from <strong>zero to a confident junior C++ programmer</strong>.
        It focuses on <strong>console applications</strong> (programs that run in the terminal),
        because they are the fastest way to practice every core skill without getting lost in tooling.
      </P>

      <H2>Where C++ shines</H2>
      <ul className="clean">
        <li><strong>Systems software</strong> — operating systems, device drivers, embedded systems.</li>
        <li><strong>Games</strong> — Unreal Engine, most AAA game studios.</li>
        <li><strong>Performance-critical code</strong> — HFT trading, scientific simulation, AI inference.</li>
        <li><strong>Tools &amp; libraries</strong> — Google's infrastructure, the Linux toolchain itself.</li>
      </ul>

      <H2>Your first taste of C++</H2>
      <P>
        Don't worry about understanding every line yet — unit 03 dissects this exact idea line by
        line. Notice the shape of a C++ program: it <IC>#include</IC>s the pieces it needs, and it
        <strong> always starts at</strong> <IC>int main()</IC>.
      </P>
      <Code title="greeting.cpp" code={CODE} />

      <Callout kind="info" title="C vs C++">
        <P>
          C (1972) is a small, close-to-the-metal language. C++ (first standard 1998, major updates
          in 2011, 2017, 2020, 2023) is a superset of C plus object-oriented and "modern" features
          such as classes, templates, <IC>std::vector</IC> and lambdas. You will write C++, but knowing
          its C roots explains many of its quirks.
        </P>
      </Callout>

      <H2>How this lecture works</H2>
      <ul className="clean">
        <li>Each unit = one concept, short explanations, real code, and <strong>check-yourself tasks</strong>.</li>
        <li>Your progress is saved in this browser — come back any time and pick up where you stopped.</li>
        <li>Practice is non-negotiable: type the code, break it, fix it. Reading alone does not build skills.</li>
        <li>Unit 17 is a full capstone project you can add to your portfolio.</li>
      </ul>

      <H2>Check yourself</H2>
      <Quiz
        id="q1"
        prompt="Which domain is C++ <em>especially</em> strong in?"
        options={[
          "Building mobile apps that run only in a web browser",
          "High-performance native software: systems, games, tools",
          "Managing a social media feed",
          "Writing HTML pages",
        ]}
        answer={1}
        explain={
          <>
            C++ compiles to native machine code with almost no runtime in the way, so it gives you
            speed and direct control over hardware. It <em>can</em> be used for other things, but
            performance and systems work are its home turf.
          </>
        }
      />
      <Quiz
        id="q2"
        prompt="C++11 (released in 2011) was a turning point. Which of these was introduced by it?"
        options={["Lambdas, auto and range-for loops", "The first C++ standard", "The #include directive", "Pointers"]}
        answer={0}
        explain={
          <>
            C++11 brought the "modern C++" toolkit: <IC>auto</IC>, lambdas, <IC>constexpr</IC>,
            range-for, <IC>std::unique_ptr</IC>. Units 11+ of this lecture build on those features.
          </>
        }
      />
    </SectionShell>
  );
}
