import random
import re
import spacy

# Load spaCy NLP model
nlp = spacy.load("en_core_web_sm")

# ------------------------------
# 1. LOAD TEXT FILE
# ------------------------------
def load_text(filename="sample.txt"):
    with open(filename, "r", encoding="utf8") as f:
        return f.read()

# ------------------------------
# 2. SPLIT TEXT INTO SENTENCES
# ------------------------------
def get_sentences(text):
    doc = nlp(text)
    return [sent.text.strip() for sent in doc.sents if len(sent.text.strip()) > 30]

# ------------------------------
# 3. EXTRACT ENTITIES FOR QUESTIONS
# ------------------------------
def extract_entities(text):
    doc = nlp(text)
    entities = [(ent.text.strip(), ent.label_) for ent in doc.ents if len(ent.text.strip()) > 2]
    return entities

# ------------------------------
# 4. CREATE CLOZE (FILL-IN-THE-BLANK) QUESTIONS
# ------------------------------
def create_cloze_questions(sentences, entities, limit=10):
    questions = []
    used = set()
    for sent in sentences:
        for ent, label in entities:
            if ent in sent and ent not in used:
                question_text = re.sub(re.escape(ent), "______", sent, count=1)
                questions.append({
                    "type": "cloze",
                    "question": question_text,
                    "answer": ent
                })
                used.add(ent)
                if len(questions) >= limit:
                    return questions
    return questions

# ------------------------------
# 5. CREATE TRUE/FALSE QUESTIONS
# ------------------------------
def create_true_false(sentences, limit=8):
    questions = []
    for s in sentences:
        year_match = re.search(r"\b(19|20)\d{2}\b", s)
        if year_match:
            year = int(year_match.group(0))
            fake_year = year + random.choice([-5, -10, +5, +10])
            false_stmt = s.replace(str(year), str(fake_year))
            if false_stmt != s:
                questions.append({
                    "type": "truefalse",
                    "question": random.choice([s, false_stmt]),
                    "answer": "True" if s == random.choice([s, false_stmt]) else "False"
                })
        if len(questions) >= limit:
            break
    return questions

# ------------------------------
# 6. CREATE MULTIPLE CHOICE QUESTIONS
# ------------------------------
def create_mcqs(sentences, entities, limit=7):
    questions = []
    random.shuffle(entities)
    for ent, label in entities:
        context = next((s for s in sentences if ent in s), None)
        if not context:
            continue
        # Generate distractors (same label if possible)
        same_label_ents = [e for e, l in entities if l == label and e != ent]
        distractors = random.sample(same_label_ents, min(3, len(same_label_ents))) if same_label_ents else []
        options = distractors + [ent]
        random.shuffle(options)
        q = {
            "type": "mcq",
            "question": f"{context}\n\nChoose the correct answer:",
            "options": options,
            "answer": ent
        }
        questions.append(q)
        if len(questions) >= limit:
            break
    return questions

# ------------------------------
# 7. RUN INTERACTIVE QUIZ
# ------------------------------
def run_quiz(questions):
    print("\n🤖 Intelligent Quiz Generator — Interactive Mode")
    print("--------------------------------------------------\n")
    score = 0
    for i, q in enumerate(questions, start=1):
        print(f"\nQuestion {i}/{len(questions)}:")
        if q["type"] == "cloze":
            print(f"Fill in the blank:\n{q['question']}")
            user = input("Your answer: ").strip()
            if user.lower() == q["answer"].lower():
                print("✅ Correct!")
                score += 1
            else:
                print(f"❌ Incorrect. Correct answer: {q['answer']}")

        elif q["type"] == "mcq":
            print(q["question"])
            for idx, opt in enumerate(q["options"], start=1):
                print(f"{idx}. {opt}")
            user_choice = input("Your choice (1-4): ").strip()
            try:
                user_answer = q["options"][int(user_choice) - 1]
                if user_answer.lower() == q["answer"].lower():
                    print("✅ Correct!")
                    score += 1
                else:
                    print(f"❌ Wrong. Correct answer: {q['answer']}")
            except:
                print(f"⚠️ Invalid input. Correct answer: {q['answer']}")

        elif q["type"] == "truefalse":
            print(f"True or False:\n{q['question']}")
            user = input("Your answer (True/False): ").strip().capitalize()
            if user == q["answer"]:
                print("✅ Correct!")
                score += 1
            else:
                print(f"❌ Incorrect. Correct answer: {q['answer']}")
    print("\n----------------------------------------")
    print(f"🎯 Quiz Complete! Your Score: {score}/{len(questions)}")
    print("----------------------------------------\n")

# ------------------------------
# 8. MAIN FUNCTION
# ------------------------------
def main():
    text = load_text("sample.txt")
    sentences = get_sentences(text)
    entities = extract_entities(text)

    cloze_q = create_cloze_questions(sentences, entities, limit=10)
    mcq_q = create_mcqs(sentences, entities, limit=7)
    tf_q = create_true_false(sentences, limit=8)

    all_q = cloze_q + mcq_q + tf_q
    random.shuffle(all_q)
    run_quiz(all_q[:25])

if __name__ == "__main__":
    main()
