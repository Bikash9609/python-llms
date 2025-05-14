import os
import json
import requests
import re
from pathlib import Path
import shutil
import re
import textwrap


OLLAMA_MODEL = "llama3"
BASE_URL = "http://localhost:11434/api/generate"
COURSE_DIR = "Generated_Udemy_Course"


def query_ollama(prompt, model=OLLAMA_MODEL, context=None):
    data = {
        "model": model,
        "prompt": prompt,
        "stream": True,
        "context": context,
    }
    resp = requests.post(
        BASE_URL,
        json=data,
        stream=True,
    )
    output = ""
    new_context = context  # Initialize with incoming context
    for line in resp.iter_lines():
        if line:
            try:
                chunk = json.loads(line.decode("utf-8"))
                output += chunk.get("response", "")
                new_context = chunk.get("context", new_context)
            except json.JSONDecodeError:
                continue
    return output, new_context


def sanitize_filename(name):
    return re.sub(r"[^\w\-_\. ]", "_", name)


def generate_lesson_script(title, description, module, lesson, previous_context=None):
    prompt = f"""
You are creating a voiceover script for a coding tutorial video. Follow these rules:

1. Write in natural, conversational English - exactly what the instructor should say
2. Format as plain text (NO markdown, NO headers, NO code blocks)
3. For code steps:
   - First explain what we're doing
   - Then show the full code as it should be typed
   - Add inline comments explaining key parts
   - Finally explain what it does
4. Keep paragraphs short (2-3 sentences)
5. Include verbal guidance like:
   "Let's..." 
   "Now we'll..."
   "Important to note that..."
   "Why we do this:..."
6. For the lesson: {lesson['lesson_title']}
7. Module context: {module['module_title']}
8. Required technical level: Complete beginners

Example format:
---
First we need to set up our project environment. Open VS Code and create a new 
folder called 'resume-analyzer'. Now open the integrated terminal and type:

npm create vite@latest frontend -- --template react

This creates our React frontend using Vite. The --template react flag 
specifies we want a React project...

Now let's install... 
---

Course: {title}
Course Description: {description}

Generate the full script:"""

    content, new_context = query_ollama(prompt, context=previous_context)

    # Post-process to ensure code formatting
    content = re.sub(r"`(.+?)`", r"\1", content)  # Remove code backticks
    return content, new_context


def save_markdown(folder, filename, content):
    """Save as plain text with .txt extension instead of markdown"""
    Path(folder).mkdir(parents=True, exist_ok=True)
    with open(
        os.path.join(folder, filename.replace(".md", ".txt")), "w", encoding="utf-8"
    ) as f:
        f.write(content)


def generate_course_roadmap_json(title, description):
    # notice: no f""" here, just a raw triple-quoted string
    raw_json = textwrap.dedent(
        """
    [
      {
        "module_index": 1,
        "module_title": "Introduction & Environment Setup",
        "lessons": [
          { "lesson_index": 1, "lesson_title": "Course Overview: What You Will Build" },
          { "lesson_index": 2, "lesson_title": "Setting Up Python, Node.js and VS Code (Windows/Linux/macOS)" },
          { "lesson_index": 3, "lesson_title": "Installing Git, Creating GitHub Repo, and Project Structure Overview" }
        ]
      },
      {
        "module_index": 2,
        "module_title": "Frontend Basics - React File Upload",
        "lessons": [
          { "lesson_index": 1, "lesson_title": "Creating React App & Folder Structure" },
          { "lesson_index": 2, "lesson_title": "Building the Resume Upload UI" },
          { "lesson_index": 3, "lesson_title": "Connecting Frontend to Backend via REST API" }
        ]
      },
      {
        "module_index": 3,
        "module_title": "Backend Basics - FastAPI for Resume Upload",
        "lessons": [
          { "lesson_index": 1, "lesson_title": "FastAPI Project Setup and Basic Routing" },
          { "lesson_index": 2, "lesson_title": "Receiving and Saving Uploaded Resume Files" },
          { "lesson_index": 3, "lesson_title": "Handling File Types and Errors Gracefully" }
        ]
      },
      {
        "module_index": 4,
        "module_title": "Resume Parsing & Cleaning",
        "lessons": [
          { "lesson_index": 1, "lesson_title": "Extracting Text from PDF Files using PyPDF2" },
          { "lesson_index": 2, "lesson_title": "Regular Expressions for Cleaning and Structuring Text" },
          { "lesson_index": 3, "lesson_title": "Using Pandas to Organize Resume Data" }
        ]
      },
      {
        "module_index": 5,
        "module_title": "AI-Powered Skill Extraction",
        "lessons": [
          { "lesson_index": 1, "lesson_title": "Introduction to OpenAI API and GPT Models" },
          { "lesson_index": 2, "lesson_title": "Generating Structured Skill Data from Resume Text" },
          { "lesson_index": 3, "lesson_title": "Filtering and Ranking Relevant Skills" }
        ]
      },
      {
        "module_index": 6,
        "module_title": "Job Listing Scraping & Matching",
        "lessons": [
          { "lesson_index": 1, "lesson_title": "Scraping Jobs from Indeed with Playwright" },
          { "lesson_index": 2, "lesson_title": "Parsing Job Descriptions and Extracting Requirements" },
          { "lesson_index": 3, "lesson_title": "Matching Jobs to Resume Skills with FuzzyWuzzy" }
        ]
      },
      {
        "module_index": 7,
        "module_title": "Building the Dashboard",
        "lessons": [
          { "lesson_index": 1, "lesson_title": "Designing the UI to Display Matched Jobs" },
          { "lesson_index": 2, "lesson_title": "Fetching Matched Jobs from API and Displaying in React" },
          { "lesson_index": 3, "lesson_title": "Pagination, Sorting and Improving User Experience" }
        ]
      },
      {
        "module_index": 8,
        "module_title": "Project Deployment & Wrap-Up",
        "lessons": [
          { "lesson_index": 1, "lesson_title": "Using Docker for Cross-Platform Deployment" },
          { "lesson_index": 2, "lesson_title": "Deploying the App to Render / Vercel / Railway" },
          { "lesson_index": 3, "lesson_title": "Final Walkthrough, Improvements, and Learning Resources" }
        ]
      }
    ]
    """
    ).strip()

    # now raw_json is a clean JSON string:
    return raw_json


def roadmap_json_to_markdown(roadmap):
    md = "# Course Roadmap\n\n"
    for m in roadmap:
        md += f"## Module {m['module_index']}: {m['module_title']}\n"
        for l in m["lessons"]:
            md += f"- Lesson {m['module_index']}.{l['lesson_index']}: {l['lesson_title']}\n"
        md += "\n"
    return md


def main():
    title = "Build a Smart Resume Analyzer & Job Matcher for Beginners: React + Python + OpenAI (All Open-Source)"

    description = (
        "Welcome to your step-by-step, beginner-friendly journey where we’ll use freely available open-source tools to build a full-stack AI agent. "
        "In this course, you’ll learn how to:\n"
        "1. **Environment Setup** – Get your dev machine ready on Windows, macOS, or Linux using Node.js, Python, Conda, Git, and VS Code (all free).\n"
        "2. **React Frontend** – Create a simple, intuitive UI for uploading and managing resumes using Create React App and Tailwind CSS.\n"
        "3. **Python Scraping & Parsing** – Harness Requests, BeautifulSoup, and Pandas to extract text and structure from resume files.\n"
        "4. **OpenAI NLP Integration** – Call the OpenAI API to clean, enrich, and rank extracted skills and experiences.\n"
        "5. **Live Job Scraping & Matching** – Use Playwright (or Selenium) to scrape real-time job listings, then employ fuzzy matching (FuzzyWuzzy) to pair candidates to roles.\n"
        "6. **Personalized Recommendations** – Generate actionable resume tips and job suggestions with human-like explanations.\n\n"
        "Every lesson is packed with clear analogies, hands-on examples, and code you can copy-paste. No prior experience required—just a willingness to learn!"
    )

    # Generate course roadmap
    print("Fetching JSON roadmap...")
    raw_json = generate_course_roadmap_json(title, description)
    try:
        roadmap = json.loads(raw_json)
    except json.JSONDecodeError as e:
        print("❌ Failed to parse JSON roadmap:", e)
        print("Raw response:", raw_json)
        return

    # Save roadmap markdown
    md = roadmap_json_to_markdown(roadmap)
    save_markdown(COURSE_DIR, "00 - Course Roadmap.md", md)

    # Generate lessons
    step = 1
    context = None  # Holds the API's context tokens
    for mod in roadmap:
        mod_folder = os.path.join(
            COURSE_DIR,
            f"{mod['module_index']:02d} - {sanitize_filename(mod['module_title'])}",
        )
        for lesson in mod["lessons"]:
            print(
                f"Generating Module {mod['module_index']}, Lesson {lesson['lesson_index']}..."
            )
            content, context = generate_lesson_script(
                title, description, mod, lesson, context
            )
            fn = f"{step:02d} - {sanitize_filename(lesson['lesson_title'])}.md"
            save_markdown(mod_folder, fn, content)
            step += 1

    print("\n✅ Course generation complete!")
    print(f"Check the `{COURSE_DIR}` folder for all markdown files.")


if __name__ == "__main__":
    # ── NEW: delete existing course directory
    if os.path.isdir(COURSE_DIR):
        print(f"Removing old directory `{COURSE_DIR}`…")
        shutil.rmtree(COURSE_DIR)
    os.makedirs(COURSE_DIR, exist_ok=True)
    # ───────────────────────────────────────────
    main()
