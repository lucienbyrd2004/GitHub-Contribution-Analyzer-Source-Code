import sqlalchemy as db
from sqlalchemy import create_engine
from sqlalchemy import insert
from sqlalchemy import delete
from sqlalchemy import update
import os
from connector import *

#Table objects
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
        db.Column('Name', db.String(255))
    )

#Insert row entry into table queries
def createUserQuery(name, githubusername, job):
    stmt = insert(Users).values(Name=name, GitHubUsername=githubusername, Job=job)
    with pool.connect() as connection:
        result = connection.execute(stmt)
        connection.commit()
def createSectionQuery(repourl, sectionname):
    stmt = insert(Section).values(RepoURL=repourl, SectionName = sectionname)
    with pool.connect() as connection:
        result = connection.execute(stmt)
        connection.commit()

#Modify existing information in the table queries
def modifyUserquery():
    print(2)

def modifySectionQuery():
    print(4)

#Search for and display information from the tables queries
def searchUserQuery():
    print(5)

def searchSectionQuery():
    print(6)

#Delete row entries in tables queries
def deleteUser(name, userid):
    stmt = delete(Users).where(Users.c.Name == name, Users.c.UserID == userid)
    with pool.connect() as connection:
        result = connection.execute(stmt)
        connection.commit()
def deleteSection(sectionname, sectionid):
    stmt = delete(Section).where(Section.c.SectionName == sectionname, Section.c.SectionID == sectionid)
    with pool.connect() as connection:
        result = connection.execute(stmt)
        connection.commit()

connecttodatabase()
userInput = -1
print("Welcome user")
while userInput != 0:
    userInput = int(input("\nWhat would you like to do? \n" \
    "1) Create a new user\n" \
    "2) Modify an existing user\n" \
    "3) Create a new section\n" \
    "4) Modify an existing section\n" \
    "5) Search for a user\n" \
    "6) Search for a section\n" \
    "0) Exit Program\n"
    "Please input your action's number: "))
    
    if userInput == 1:
        tempName = input("Input Name: ")
        tempGitHubUsername = input("Input GitHub Username: ")
        tempJob = input("Input Job Title: ")
        
        try:
            print("Creating user...")
            createUserQuery(tempName, tempGitHubUsername, tempJob)
            print("User created")
        except:
            print("Error user not created properly")
    
    elif userInput == 2:
        modifyUserquery()

    elif userInput == 3:
        tempName = input("Input Section Name: ")
        tempGitHubURL = input("Input GitHub URL: ")
        try:
            print("Creating section...")
            createSectionQuery(tempGitHubURL, tempName)
            print("Section created")
        except:
            print("Error section not created properly")
    
    elif userInput == 4:
        modifySectionQuery()
    elif userInput == 5:
        searchUserQuery()
    elif userInput == 6:
        searchSectionQuery()

    elif userInput == 7:
        tempName = input("Input Name: ")
        tempID = input("Input UserID: ")
        try:
            print("Deleting user...")
            deleteUser(tempName, tempID)
            print("User deleted")
        except:
            print("Error user not deleted properly")

    elif userInput == 8:
        tempName = input("Input Section Name: ")
        tempID = input("Input SectionID: ")
        try:
            print("Deleting section...")
            deleteSection(tempName, tempID)
            print("Section deleted")
        except:
            print("Error section not deleted properly")
    
    elif userInput == 0:
        print("Exiting program...")
        break
    
    else:
        print("Invalid Response, please try again")