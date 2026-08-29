from src.database.config import supabase
import bcrypt

def hash_pass(pwd):
    return bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()

def check_pass(pwd, hashed):
    return bcrypt.checkpw(pwd.encode(), hashed.encode())
    
def check_teacher_existance(username):
    response = supabase.table("teachers").select("username").eq("username",username).execute()
    return len(response.data) > 0

def create_teacher(username, password, name):
    data = {"username":username, "password":hash_pass(password), "name": name}
    response = supabase.table("teachers").insert(data).execute()
    return response.data


def teacher_login(username, password):
    response = supabase.table("teachers").select("*").eq("username",username).execute()
    if response.data:
        teacher = response.data[0]
        if check_pass(password, teacher["password"]):
            return teacher
    return  None

def get_all_students():
    response = supabase.table("students").select("*").execute()
    return response.data

def create_student(new_name, face_embeddings=None, voice_embeddings=None):
    data = {"name":new_name, "face_embeddings":face_embeddings, "voice_embeddings":voice_embeddings }
    response = supabase.table("students").insert(data).execute()
    return response.data[0]
    
def create_subject(subject_code, name, section, teacher_id):
    data = {"subject_code":subject_code, "name":name, "section":section, "teacher_id":teacher_id}
    response = supabase.table("subjects").insert(data).execute()
    return response.data
def get_teacher_subject(teacher_id):
    response = supabase.table("subjects").select("*, student_subjects(count), attendence_logs(timestamps)").eq("teacher_id" , teacher_id).execute()
    subjects = response.data
    for sub in subjects :
        sub["total_students"] = sub.get("student_subjects", [{}])[0].get('count', 0) if sub.get("student_subjects") else 0
        attendance = sub.get("attendence_logs")
        unique_sessions = len(set(log["timestamps"] for log in attendance))
        sub["total_classes"] = unique_sessions
        
        sub.pop("student_subjects", None)
        sub.pop("attendence_logs", None)
    return subjects
def enroll_student_to_subject(student_id, subject_id) :
    data = {"student_id":student_id, "sub_id":subject_id }  
    response = supabase.table("student_subjects").insert(data).execute()
    return response.data  
def unenroll_student_to_subject(student_id, subject_id) :
    response = supabase.table("student_subjects").delete().eq("student_id", student_id).eq("sub_id" , subject_id ).execute()
    return response.data 
def get_student_subjects(student_id):
    response = supabase.table("student_subjects").select("*, subjects(*)").eq("student_id",student_id).execute()
    return response.data

def get_student_attendance(student_id):
    response = supabase.table("attendence_logs").select("*, subjects(*)").eq("student_id",student_id).execute()
    return response.data

def create_attendance(logs):
    response = supabase.table('attendence_logs').insert(logs).execute()
    return response.data

def get_attendance_for_teacher(teacher_id):
    res = supabase.table('attendence_logs').select("* , subjects!inner(*)").eq('subjects.teacher_id', teacher_id).execute()
    return res.data