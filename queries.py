import sqlalchemy as db
from sqlalchemy import create_engine
import os
from connector import *

def createtables():
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
        db.Column('RepoURL', db.String(255))
    )


    UserSection = db.Table(
        'usersection',
        metadata_obj,
        db.Column('SectionID', db.Integer, db.ForeignKey("section.SectionID"), nullable=False),
        db.Column('UserID', db.Integer, db.ForeignKey("users.UserID"), nullable=False),
        db.Column('Name', db.String(255))
    )
    metadata_obj.create_all(pool)



connecttodatabase()
createtables()