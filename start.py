from flask import Flask, render_template, request
import sqlite3
from datetime import datetime

app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def search():
    if request.method == 'GET':
        return render_template('search_student.html')
    else:
        conn = sqlite3.connect('students.db')
        c = conn.cursor()
        student_name = request.form.get('studentname')
        c.execute(f"""SELECT * FROM info
                    WHERE name LIKE '%{student_name}%'""")
        results = c.fetchall()
        if results == None:
            return render_template('wrong_name.html')
        else:
            column_names = ['Name', 'Student ID', 'Address', 'Gender','Date of Birth']
            conn.close()

            return render_template('search_results.html', headings = column_names, mylist = results)

@app.route('/add_student', methods=['GET','POST'])
def add_student():
    if request.method == 'GET':
        return render_template('add_student.html')
    else:
        conn = sqlite3.connect('students.db')
        c = conn.cursor()

        student_name = request.form.get('studentname')
        student_id = request.form.get('id')
        student_address = request.form.get('address')
        student_gender = request.form.get('gender')
        student_dob = request.form.get('dob')
        student_chem101 = request.form.get('chem101')
        student_math101 = request.form.get('math101')
        student_phys101 = request.form.get('phys101')

        if not student_name or not student_id:
            return "Name and Student ID are mandatory"
        else:
            student_id = int(student_id)
        
        sql_query = f"""INSERT INTO info VALUES(
                        '{student_name}',
                         {student_id},
                        '{student_address}',
                        '{student_gender}',
                        '{student_dob}')"""
        c.execute(sql_query)
        conn.commit()

        scores = {}
        scores['CHEM101'] = float(student_chem101) if student_chem101 else None
        scores['MATH101'] = float(student_math101) if student_math101 else None
        scores['PHYS101'] = float(student_phys101) if student_phys101 else None

        for code,score in scores.items():
            if score != None:
                sql_query = f"""INSERT INTO scores VALUES (
                                {student_id}, '{code}', {score})"""
                c.execute(sql_query)
                conn.commit()
        
        return f"The student {student_name} is created..."

def extract_data(request):
    data_dict = {}
    scores_dict = {}
    data_dict['name'] = request.form.get('studentname')
    data_dict['studentid'] = request.form.get('student_id')
    data_dict['address'] = request.form.get('student_address')
    data_dict['dob'] = request.form.get('dob')
    data_dict['gender'] = request.form.get('student_gender')

    scores_dict['CHEM101'] = float(request.form.get('chem101')) if request.form.get('chem101') else None
    scores_dict['MATH101'] = float(request.form.get('math101')) if request.form.get('math101') else None
    scores_dict['PHYS101'] = float(request.form.get('phys101')) if request.form.get('phys101') else None
    return data_dict, scores_dict
 
@app.route('/edit_student/<int:student_id>', methods = ['GET', 'POST'])
def edit_student(student_id):
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    if request.method == 'GET':
        c.execute(f'SELECT * FROM info WHERE studentid={student_id}')
        info_results = c.fetchall()[0]

        c.execute(f'SELECT * FROM scores WHERE studentid={student_id}')
        scores_results = c.fetchall()
        scores_dict = {'CHEM101': '', 'MATH101': '', 'PHYS101': ''}
        for each_score in scores_results:
            scores_dict[each_score[1]] = each_score[2]
        return render_template('edit_student.html', info_results=info_results, scores_dict = scores_dict)
    
    else:

        student_dict, student_scores_dict = extract_data(request)
        if not student_dict['name']:
            return "Name is a mandatory field"

        sql_query = f"""
                        UPDATE info SET
                        name = '{student_dict['name']}',
                        address = '{student_dict['address']}',
                        gender = '{student_dict['gender']}',
                        dob = '{student_dict['dob']}'
                        WHERE studentid = {student_dict['studentid']}       
                    """
        c.execute(sql_query)
        conn.commit()

        sql_query = f"""DELETE FROM scores WHERE studentid = {student_dict['studentid']}"""
        c.execute(sql_query)
        conn.commit()

        for k, v in student_scores_dict.items():
            if v != None:
                sql_query = f"""INSERT INTO scores VALUES(
                                {student_dict['studentid']},
                                '{k}',
                                {v}
                            )"""
                c.execute(sql_query)
                conn.commit()
        conn.close()
        return f"Records for the Student ID {student_dict['studentid']} have been updated."

@app.route('/courses')
def courses():
    conn = sqlite3.connect('students.db')
    c = conn.cursor()

    c.execute("""SELECT * FROM scores""")
    scores_list = c.fetchall()

    courses_codes = ['CHEM101', 'PHYS101', 'MATH101']
    course_details = []

    for each_course in courses_codes:
        course_dict = {'name': each_course,
                       'average' : 0.0,
                       'num_students' : 0,
                       'passed': 0}
        for each_score in scores_list:
            if each_course == each_score[1]:
                course_dict['num_students'] += 1
                course_dict['average'] += each_score[2]
                if each_score[2] >= 50.0:
                    course_dict['passed'] += 1
        
        course_dict['average'] /= course_dict['num_students']
        course_dict['average'] = round(course_dict['average'], 2)
        course_details.append(course_dict)
    conn.close()
    return render_template('course_details.html', course_details=course_details)



if __name__ == '__main__':
    app.run(debug=True, port = 5000)