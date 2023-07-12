"""create a multi choice test on specific topic"""
import os
import openai

openai.api_key = os.getenv('OPENAI_API_KEY')

TOPIC = 'Python programming language'
NUM_QUESTIONS = 4
NUM_POSSIBLE_ANSWERS = 4


def create_test_promt(topic, num_questions, num_possible_answers):
    """creates a prompt """
    prompt = f"""Create a multiple choice quiz on the topic of {topic}
                 consisting of {num_questions} questions. Each question should have
                 {num_possible_answers} options. Also include the correct
                 answer to each question using the starting string 'Correct Answer:' 
                 Dont ask questions that could be andswered by opinion, they
                 must only be answer by a single correct answer, they must be based on facts"""
    return prompt


response = openai.Completion.create(
    engine='text-davinci-003',
    prompt=create_test_promt(TOPIC, NUM_QUESTIONS, NUM_POSSIBLE_ANSWERS),
    max_tokens=256,
    temperature=0.6
)


def extract_questions(test, num_questions):
    """creating a student view of test, out of response"""
    questions = {1: ''}
    question_number = 1
    for line in test.split('\n'):
        if not line.startswith("Correct Answer:"):
            questions[question_number] += line + '\n'
        else:
            if question_number < num_questions:
                question_number += 1
                questions[question_number] = ''

    return questions


def extract_answers(test, num_questions):
    """extracting questions out of response"""
    answers = {1: ''}
    question_number = 1
    for line in test.split('\n'):
        if line.startswith("Correct Answer:"):
            answers[question_number] = line.split(':')[1].split('.')[0].strip()[0]
            question_number += 1
       
    return answers

students_view = extract_questions(response['choices'][0]['text'], NUM_QUESTIONS)
correct_answers = extract_answers(response['choices'][0]['text'], NUM_QUESTIONS)

def take_exam(students_view):
    """Exam simulation"""
    student_answer = dict()
    for idx, question in students_view.items():
        print(question)
        answer = input('Enter your answer:')
        student_answer[idx] = answer
    return student_answer

student_answers = take_exam(students_view)

def evaluate_exam(correct_answers, student_answers):
    """Evaluating the results of an exam"""
    results = 0
    for idx, answer in student_answers.items():
        if answer.lower() == correct_answers[idx].lower():
            results += 1    
    grade = 100 * results / len(student_answers)
    return grade

print(f'\nYour score: {evaluate_exam(correct_answers, student_answers)}')
