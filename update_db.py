import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, String
from sqlalchemy.orm import declarative_base, sessionmaker

# Load environment variables from .env
load_dotenv()

# Set up the SQLAlchemy Base
Base = declarative_base()

# Define the Employee model matching your database table
class Employee(Base):
    __tablename__ = 'employees'
    
    # SQLAlchemy needs to know the primary key. Assuming 'username' is the primary key.
    username = Column(String(50), primary_key=True)
    github_username = Column(String(100))
    # You don't need to define every column in the table, just the ones you are interacting with!

def update_employee_github(target_user: str, new_github_handle: str):
    """Updates an employee's GitHub handle using SQLAlchemy."""
    
    # 1. Build the connection string (Using mysql-connector as the underlying driver)
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_name = os.getenv("DB_NAME")
    
    # Format: dialect+driver://username:password@host:port/database
    database_url = f"mysql+mysqlconnector://{db_user}:{db_password}@{db_host}/{db_name}"
    
    try:
        # 2. Create the SQLAlchemy engine
        engine = create_engine(database_url)
        
        # 3. Create a session to interact with the database
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # 4. Query the database for the specific employee
        employee = session.query(Employee).filter(Employee.username == target_user).first()
        
        if employee:
            # 5. Update the attribute (Pythonic way!)
            employee.github_username = new_github_handle
            
            # 6. Commit the transaction to save the changes
            session.commit()
            print(f"✅ Success! Updated '{target_user}' to use GitHub handle: '{new_github_handle}'.")
        else:
            print(f"⚠️ No changes made. Could not find a user named '{target_user}' in the database.")
            
    except Exception as e:
        print(f"❌ Database Error: {e}")
        # If something goes wrong, rollback the transaction so the database isn't corrupted
        if 'session' in locals():
            session.rollback() 
    finally:
        # Always close the session to free up the connection pool
        if 'session' in locals():
            session.close()
            print("Database session safely closed.")

if __name__ == "__main__":
    # Run the update
    update_employee_github(target_user='debbie', new_github_handle='octocat')