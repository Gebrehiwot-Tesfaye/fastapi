from fastapi import FastAPI, Path
from typing import Optional
from pydantic import BaseModel

app = FastAPI() 

# I Want to create CRUD endpoints for a resource called "Item".

students={
    1:{
        "name":"John",
        "age":22,
        "class":"Computer year 12"
    }
}
@app.get("/")
def index():
    return {"message": "Welcome to the Item API"}

@app.get("/students")
def get_students():
    return students

@app.get("/students/{student_id}")
def get_student(student_id: int = Path(..., title="The ID of the student to get", gt=0)):
    if student_id not in students:
        return {"error": "Student not found"}
    return students[student_id]  

# query parameters
@app.get("/get-by-name")
def get_student_by_name(name: Optional[str] = None):
    for student_id in students:
        if students[student_id]["name"] == name:
            return students[student_id]
    return {"error": "Student not found"}


# combined path and query parameters

@app.get("/get-student/{student_id}")
def get_student(student_id: int, name: Optional[str] = None):
    if student_id not in students:
        return {"error": "Student id not found"}
    if students[student_id]["name"] == name:
        return students[student_id]
    return {"error": "Student name not found"}


# request body and the post method
class Student(BaseModel):
    name: str
    age: int
    class_name: str

@app.post("/create-student/{student_id}")
def create_student(student_id: int, student: Student):
    if student_id in students:
        return {"error": "Student already exists"}
    students[student_id] = {
        "name": student.name,
        "age": student.age,
        "class": student.class_name
    }
    return students[student_id]   

# put method to update a student
@app.put("/update-student/{student_id}")
def update_student(student_id: int, student: Student):
    if student_id not in students:
        return {"error": "Student not found"}
    students[student_id] = {
        "name": student.name,
        "age": student.age,
        "class": student.class_name
    }
    return students[student_id]   

# delete method to delete a student
@app.delete("/delete-student/{student_id}")
def delete_student(student_id: int):
    if student_id not in students:
        return {"error": "Student not found"}
    del students[student_id]
    return {"message": "Student deleted successfully"}

@app.get("/about")
def about():
    return {"message": "This is a simple API to manage students."}