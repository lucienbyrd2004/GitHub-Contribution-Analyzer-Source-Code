import sqlalchemy as db
from sqlalchemy import insert, delete, update, select, desc
import os
from connector import *

# --- TABLE DEFINITIONS ---
metadata_obj = db.MetaData()

Users = db.Table(
    'users',
    metadata_obj,
    db.Column('UserID', db.Integer, primary_key=True, unique=True, autoincrement=True),
    db.Column('Name', db.String(255)),
    db.Column('GitHubUsername', db.String(255)),
    db.Column('Job', db.String(255), nullable=False)
)

Login = db.Table(
    'login',
    metadata_obj,
    db.Column('UserID', db.Integer, db.ForeignKey("users.UserID"), nullable=False),
    db.Column('Username', db.String(255), nullable=False),
    db.Column('Password', db.String(16), nullable=False)
)

Section = db.Table(
    'section',
    metadata_obj,
    db.Column('SectionID', db.Integer, primary_key=True, unique=True, autoincrement=True),
    db.Column('RepoURL', db.String(255)),
    db.Column('SectionName', db.String(255))
)

UserSection = db.Table(
    'usersection',
    metadata_obj,
    db.Column('SectionID', db.Integer, db.ForeignKey("section.SectionID"), nullable=False),
    db.Column('UserID', db.Integer, db.ForeignKey("users.UserID"), nullable=False),
)

# --- HELPER FUNCTIONS ---
def commitStatement(stmt):
    """Executes a basic statement and commits it to the database."""
    with pool.connect() as connection:
        connection.execute(stmt)
        connection.commit()

# --- AUTHENTICATION & LOGIN ---
def verify_login(username, password):
    """Checks credentials and returns user details formatted for Streamlit session state."""
    stmt = select(Users, Login).join(Login, Users.c.UserID == Login.c.UserID)\
           .where(Login.c.Username == username, Login.c.Password == password)
           
    with pool.connect() as connection:
        result = connection.execute(stmt).fetchone()
        
    if result:
        return {
            "id": str(result.UserID), # Keeping as string to match your frontend logic
            "name": result.Name,
            "github": result.GitHubUsername,
            "role": result.Job.lower() # Matches frontend expectations (e.g., 'manager')
        }
    return None

def createUserLogin(userid, username, password):
    if not userid or not username or not password:
        raise ValueError("Error: Please make sure all inputs have a value.")
    
    stmt = insert(Login).values(UserID=userid, Username=username, Password=password)
    commitStatement(stmt)

# --- USER QUERIES ---
def createUserQuery(name, githubusername, job, username, password):
    """Creates a user and their login simultaneously."""
    # 1. Insert into Users
    stmt = insert(Users).values(Name=name, GitHubUsername=githubusername, Job=job)
    commitStatement(stmt)
    
    # 2. Get the new UserID
    stmt = select(Users).order_by(desc(Users.c.UserID)).limit(1)
    with pool.connect() as connection:
        new_user = connection.execute(stmt).fetchone()
        
    # 3. Insert into Login
    if new_user:
        createUserLogin(new_user.UserID, username, password)
        return True
    return False

def get_all_employees():
    """Fetches all users for the manager dashboard."""
    stmt = select(Users)
    users = []
    with pool.connect() as connection:
        for row in connection.execute(stmt):
            users.append({
                "id": str(row.UserID),
                "name": row.Name,
                "role": row.Job.lower()
            })
    return users

def modifyUserquery(userid, new_name, new_github):
    """Updates a user's details (Used by Employee Dashboard)."""
    stmt = update(Users).where(Users.c.UserID == userid).values(
        Name=new_name, 
        GitHubUsername=new_github
    )
    commitStatement(stmt)

def deleteUser(name, userid):
    # Must delete from Login first due to Foreign Key constraints
    stmt1 = delete(Login).where(Login.c.UserID == userid)
    commitStatement(stmt1)
    
    stmt2 = delete(Users).where(Users.c.Name == name, Users.c.UserID == userid)
    commitStatement(stmt2)

# --- SECTION QUERIES ---
def createSectionQuery(repourl, sectionname):
    stmt = insert(Section).values(RepoURL=repourl, SectionName=sectionname)
    commitStatement(stmt)

def get_all_sections():
    """Fetches all sections for the manager dashboard."""
    stmt = select(Section)
    sections = []
    with pool.connect() as connection:
        for row in connection.execute(stmt):
            sections.append({
                "id": row.SectionID, 
                "name": row.SectionName, 
                "url": row.RepoURL
            })
    return sections

def deleteSection(sectionname, sectionid):
    # Important: Delete mappings in UserSection first to avoid foreign key errors
    stmt1 = delete(UserSection).where(UserSection.c.SectionID == sectionid)
    commitStatement(stmt1)
    
    stmt2 = delete(Section).where(Section.c.SectionName == sectionname, Section.c.SectionID == sectionid)
    commitStatement(stmt2)

# --- USER-SECTION MAPPING QUERIES ---
def addUserToSection(userid, sectionid):
    stmt = insert(UserSection).values(UserID=userid, SectionID=sectionid)
    commitStatement(stmt)

def deleteUserSection(userid, sectionid):
    stmt = delete(UserSection).where(UserSection.c.UserID == userid, UserSection.c.SectionID == sectionid)
    commitStatement(stmt)

def get_section_members(sectionid):
    """Fetches all users assigned to a specific section."""
    stmt = select(Users).join(UserSection, Users.c.UserID == UserSection.c.UserID)\
           .where(UserSection.c.SectionID == sectionid)
    members = []
    with pool.connect() as connection:
        for row in connection.execute(stmt):
            members.append({
                "id": str(row.UserID), 
                "name": row.Name
            })
    return members

def get_employee_sections(userid):
    """Fetches all sections assigned to a specific employee."""
    stmt = select(Section).join(UserSection, Section.c.SectionID == UserSection.c.SectionID)\
           .where(UserSection.c.UserID == userid)
    sections = []
    with pool.connect() as connection:
        for row in connection.execute(stmt):
            sections.append({
                "id": row.SectionID, 
                "name": row.SectionName, 
                "url": row.RepoURL
            })
    return sections