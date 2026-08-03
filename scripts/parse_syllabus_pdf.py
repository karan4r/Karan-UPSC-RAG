import json
import re
from pathlib import Path
import pypdf

def parse_upsc_micro_syllabus(pdf_path: str, output_path: str):
    reader = pypdf.PdfReader(pdf_path)
    
    current_paper = "GS Paper 1"
    current_subject = None
    current_topic = None
    
    syllabus = {
        "GS Paper 1": {
            "title": "GS Paper 1: Indian Heritage & Culture, History, Geography & Society",
            "subjects": {}
        },
        "GS Paper 2": {
            "title": "GS Paper 2: Governance, Constitution, Polity, Social Justice & IR",
            "subjects": {}
        },
        "GS Paper 3": {
            "title": "GS Paper 3: Technology, Economic Development, Environment & Security",
            "subjects": {}
        },
        "GS Paper 4": {
            "title": "GS Paper 4: Ethics, Integrity & Aptitude",
            "subjects": {}
        }
    }
    
    # Process pages 2 to 20
    for p_idx in range(1, 20):
        if p_idx >= len(reader.pages):
            break
        text = reader.pages[p_idx].extract_text()
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Check if page explicitly states GS Paper
        page_str = "\n".join(lines[:5])
        if "GS Paper 1" in page_str or "GS Paper-1" in page_str or "GS Paper 1 :" in page_str:
            if current_paper != "GS Paper 1":
                current_paper = "GS Paper 1"
                current_subject = None
                current_topic = None
        elif "GS Paper 2" in page_str or "GS Paper-2" in page_str or "GS Paper 2 :" in page_str:
            if current_paper != "GS Paper 2":
                current_paper = "GS Paper 2"
                current_subject = None
                current_topic = None
        elif "GS Paper 3" in page_str or "GS Paper-3" in page_str or "GS Paper 3 :" in page_str:
            if current_paper != "GS Paper 3":
                current_paper = "GS Paper 3"
                current_subject = None
                current_topic = None
        elif "GS Paper 4" in page_str or "GS Paper-4" in page_str or "GS Paper 4 :" in page_str:
            if current_paper != "GS Paper 4":
                current_paper = "GS Paper 4"
                current_subject = None
                current_topic = None
            
        for line in lines:
            # Skip header / footer lines
            if "GS MAINS" in line or "UnderStand UPSC" in line or "Of/f_icial UPSC Syllabus" in line or "Micro-Syllabus" in line:
                continue
                
            # Check Subject transition e.g., "A. Indian Culture", "B. Executive, Legislature & Judiciary", "A. ETHICS & HUMAN INTERFACE"
            subj_match = re.match(r'^\s*([A-H])[\.\s]+([A-Za-z\s&,\–\-]{3,60})$', line)
            if subj_match and not line.startswith("E. Sreedharan"):
                subj_code = subj_match.group(1).upper()
                subj_name = f"{subj_code}. {subj_match.group(2).strip()}"
                current_subject = subj_name
                if current_subject not in syllabus[current_paper]["subjects"]:
                    syllabus[current_paper]["subjects"][current_subject] = {
                        "title": current_subject,
                        "topics": {}
                    }
                current_topic = None
                continue

            # Check Topic transition e.g., "1. India in the 18th Century", "A1. Nature & Scope", "11. Good Governance"
            topic_match = re.match(r'^\s*([A-Z0-9]{1,3}\.|\d+\.)\s+(.*)', line)
            if topic_match and current_subject and len(line) < 110:
                topic_title = line.strip()
                current_topic = topic_title
                if current_subject not in syllabus[current_paper]["subjects"]:
                    syllabus[current_paper]["subjects"][current_subject] = {
                        "title": current_subject,
                        "topics": {}
                    }
                if current_topic not in syllabus[current_paper]["subjects"][current_subject]["topics"]:
                    syllabus[current_paper]["subjects"][current_subject]["topics"][current_topic] = {
                        "title": current_topic,
                        "microtopics": []
                    }
                continue

            # Microtopics are bullet points or items under topics
            if current_paper and current_subject and current_topic:
                if current_subject in syllabus[current_paper]["subjects"] and current_topic in syllabus[current_paper]["subjects"][current_subject]["topics"]:
                    clean_item = re.sub(r'^[•▶»\-\*]\s*', '', line).strip()
                    if clean_item and len(clean_item) > 2:
                        micro_list = syllabus[current_paper]["subjects"][current_subject]["topics"][current_topic]["microtopics"]
                        if clean_item not in micro_list:
                            micro_list.append(clean_item)

    # Remove subjects with no topics
    for paper in list(syllabus.keys()):
        for subj in list(syllabus[paper]["subjects"].keys()):
            if not syllabus[paper]["subjects"][subj]["topics"]:
                del syllabus[paper]["subjects"][subj]

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(syllabus, f, indent=2, ensure_ascii=False)
        
    print(f"Successfully exported clean syllabus dataset to {output_path}")
    return syllabus

if __name__ == "__main__":
    pdf_p = "data/MicroSyllabus-GS-MAINS-2026-27-merged-1-1.pdf"
    out_p = "data/upsc_syllabus_microtopics.json"
    parse_upsc_micro_syllabus(pdf_p, out_p)
