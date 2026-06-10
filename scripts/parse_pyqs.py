import json
import re
from pathlib import Path

content_path = Path("/Users/karanrajan/.gemini/antigravity/brain/ae728968-6b93-450b-9839-85e8b164a9e8/.system_generated/steps/115/content.md")
output_path = Path("/Users/karanrajan/PM/Karan-UPSC-RAG/data/modern_history_pyqs.json")

def parse_md():
    if not content_path.exists():
        print("Scraped content.md does not exist.")
        return

    with open(content_path, "r", encoding="utf-8") as f:
        text = f.read()

    # We want to find years (2024, 2023, etc.) and questions under them
    # Let's split by lines
    lines = text.split("\n")
    
    questions = []
    current_year = None
    current_q_num = None
    current_q_text = []
    current_ans = None
    current_exp = []
    state = "NONE" # NONE, QUESTION, EXPLANATION

    for line in lines:
        line_strip = line.strip()
        # Detect year
        year_match = re.match(r"^(20\d{2})$", line_strip)
        if year_match:
            current_year = year_match.group(1)
            continue
            
        # Detect Question header
        q_match = re.match(r"^Question\s+(\d+)$", line_strip, re.I)
        if q_match:
            # Save previous question if any
            if current_q_num and current_q_text:
                questions.append({
                    "year": current_year,
                    "number": current_q_num,
                    "question": "\n".join(current_q_text).strip(),
                    "answer": current_ans,
                    "explanation": "\n".join(current_exp).strip()
                })
            current_q_num = q_match.group(1)
            current_q_text = []
            current_ans = None
            current_exp = []
            state = "QUESTION"
            continue

        # Check for another section that might stop parsing after we have started parsing
        if current_year and (line_strip.startswith("Books") or line_strip.startswith("UPSC PYQs") or line_strip.startswith("UPSC Notes") or line_strip.startswith("About us") or line_strip.startswith("Contact us")):
            # Stop if we hit footer navigation
            break

        if state == "QUESTION":
            # Check for Answer
            ans_match = re.match(r"^Ans\s*:\s*([a-d])", line_strip, re.I)
            if ans_match:
                current_ans = ans_match.group(1).lower()
                state = "EXPLANATION"
                continue
            current_q_text.append(line)
        elif state == "EXPLANATION":
            # Check if this is the start of explanation text
            if line_strip.startswith("Exp:"):
                line = line.replace("Exp:", "", 1)
            current_exp.append(line)

    # Add the last question
    if current_q_num and current_q_text:
        questions.append({
            "year": current_year,
            "number": current_q_num,
            "question": "\n".join(current_q_text).strip(),
            "answer": current_ans,
            "explanation": "\n".join(current_exp).strip()
        })

    # Let's clean up explanation and question texts
    cleaned_questions = []
    for q in questions:
        # Remove empty lines or markdown links like [Explanation](...)
        q_text = q["question"]
        q_text = re.sub(r"\[Explanation\].*?$", "", q_text, flags=re.M).strip()
        
        q_exp = q["explanation"]
        # Remove [Explanation](...) links inside explanation
        q_exp = re.sub(r"\[Explanation\].*?$", "", q_exp, flags=re.M).strip()
        
        # Only keep valid entries
        if q_text and q["answer"]:
            cleaned_questions.append({
                "year": q["year"],
                "number": q["number"],
                "question": q_text,
                "answer": q["answer"],
                "explanation": q_exp
            })

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(cleaned_questions, f, indent=2, ensure_ascii=False)

    print(f"Successfully parsed {len(cleaned_questions)} questions and saved to {output_path}")

if __name__ == "__main__":
    parse_md()
