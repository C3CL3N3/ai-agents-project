Block 1, setup (15 minutes)
Create the repository you will use for fourteen weeks. Download project_spine.zip and week01_starter.zip from Moodle into the folder where you will create it, then:

git init ai-agents-project && cd ai-agents-project
unzip ../project_spine.zip                        # project_spine/: README, project/, tests/
cp -r project_spine/project ./project             # the spine
cp project_spine/pyproject.toml .                 # so every script can import it
mkdir -p labs && unzip ../week01_starter.zip -d labs   # labs/week01/

python3 -m venv .venv && source .venv/bin/activate
pip install -e . -r labs/week01/starter/requirements.txt
echo "# Decisions" > DECISIONS.md

python labs/week01/starter/00_preflight.py
The starter archive is the whole lab folder, including its fixtures/ directory. Block 3 reads a recording from it. Every later week ships the same way: unzip ../weekNN_starter.zip -d labs gives you labs/weekNN/.

Push the repository to a remote before you leave today. GitHub or GitLab, private or public, the choice is yours, with one condition: the teaching team must have access to it, read access is enough, from the moment your group registers in week 3 until the grades are published. The group registration on Moodle asks for the URL. A group shares one repository; if you work alone, it is yours. Everything you are graded on is read from this remote, so a commit that never got pushed does not exist.

If a model is still downloading, leave it running and skip to block 3, which needs no model. Fix the environment with a person standing next to you rather than at midnight.

What the repository holds, and why
project/ is course-provided and shared by every week. Read project_spine/README.md once. You are expected to know what is in it.
artifacts/ is what your system writes. From week 4 onward every run appends to artifacts/traces.jsonl, and week 10 builds the evaluation harness on exactly that file.
labs/weekNN/ is that week's scratch work.
DECISIONS.md is one line per decision with the reason. In week 13 it becomes a section of your report that you do not have to write.
Run python -m project.verify before every commit. Today it reports that nothing is written yet, which is correct.

Block 2, the first call (30 minutes)
Complete TODO 1 to 3 in starter/01_first_call.py.

A call that prints only the answer is not finished. Print, and be ready to explain, all four of these:

the answer text
the finish reason, and how your program would tell a deliberate ending from a truncation
the prompt and completion token counts, and which of the two you control
the elapsed time, and which part of it a user would actually feel
Then close the trace. It writes one record to artifacts/traces.jsonl in the shape every later week reads, and python -m project.verify confirms it.

Checkpoint 1. The six items in checklist.md.

Block 3, does the model repeat itself (25 minutes)
Complete TODO 4 to 6 in starter/02_variance.py.

Start with the recording, because it costs nothing and puts the whole room on the same numbers:

python labs/week01/starter/02_variance.py --replay --full
That is ninety-six real runs recorded on the teaching machine: four prompts, two temperatures, twelve runs each. make_fixture.py is what produced it and you can regenerate it yourself.

Then run your own two cells live and compare.

Three things to come out of this block able to say:

what happened at temperature 0, and whether your machine agrees with the recording
which cell still returns one single answer at temperature 1.0, and why that one. "The temperature did not work" is not the answer.
which of these cells a unit test asserting exact string equality would pass on, and what that tells you about testing this system
Checkpoint 2. Be ready to read your numbers out loud, as counts.

Block 4, what it costs (15 minutes)
Complete TODO 7 and 8 in starter/03_cost.py.

Two costs are measured and one is estimated.

Seconds. A short answer against a long one, same model, same settings.
The cold start. The number the recording deliberately leaves out, and the largest one you will see today. It decides something about week 3, so write down what.
Euros, estimated. What a 200-case golden set would cost to run nightly for a semester, on a cheap tier and on an expensive one. Week 10 builds that golden set, so this is not a hypothetical.
What goes into DECISIONS.md today
Five entries. The template is in DECISIONS_week01_section.md.

Your machine: model, RAM, and whether you are on the required or the optional model set.
The four numbers from your first call, with the model name and the date.
Your variance table, and the sentence from TODO 6 that carries into week 10.
Your cold start measurement, and what it implies for a system that uses more than one model.
Your nightly evaluation estimate on both tiers, labeled as an estimate, and which tier you would run when.
Homework
Run the full sweep live on your own machine: python labs/week01/starter/02_variance.py --full. Eight cells rather than two. It takes a few minutes and it is the version of the table you put in DECISIONS.md.
Pull the optional models before week 9: ollama pull qwen2.5:7b and ollama pull qwen3-vl:4b.
Read project_spine/README.md and skim project/contracts.py. Week 4 starts writing to that contract and it is easier if you have seen it.