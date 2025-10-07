"""
Quick fix for production database - Run this on Railway to create missing table
"""

import os
import sys
from sqlalchemy import create_engine, text

def main():
    """Create the missing student_course_progress table"""
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL not found")
        return
    
    try:
        engine = create_engine(database_url)
        
        # SQL to create the missing table
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS student_course_progress (
            id SERIAL PRIMARY KEY,
            student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
            course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
            lessons_attended INTEGER DEFAULT 0,
            enrollment_date DATE NOT NULL,
            UNIQUE(student_id, course_id)
        );
        """
        
        with engine.connect() as conn:
            # Create the table
            conn.execute(text(create_table_sql))
            conn.commit()
            
            print("✅ student_course_progress table created successfully")
            
            # Insert sample data if needed
            sample_data_sql = """
            INSERT INTO student_course_progress (student_id, course_id, lessons_attended, enrollment_date)
            SELECT s.id, c.id, 
                   CASE WHEN s.id = 1 THEN 12 
                        WHEN s.id = 2 THEN 8 
                        WHEN s.id = 3 THEN 6 
                        ELSE 10 END,
                   CASE WHEN s.id = 1 THEN '2024-09-01'::date
                        WHEN s.id = 2 THEN '2024-09-15'::date
                        WHEN s.id = 3 THEN '2024-10-01'::date
                        ELSE '2024-08-20'::date END
            FROM students s
            CROSS JOIN courses c
            WHERE s.id <= 4 AND c.id <= 4 AND s.id = c.id
            ON CONFLICT (student_id, course_id) DO NOTHING;
            """
            
            result = conn.execute(text(sample_data_sql))
            conn.commit()
            
            print(f"✅ Added sample enrollment data")
            
            # Verify the fix
            check_sql = "SELECT COUNT(*) FROM student_course_progress"
            result = conn.execute(text(check_sql))
            count = result.scalar()
            
            print(f"✅ Table verified: {count} enrollment records")
    
    except Exception as e:
        print(f"ERROR: {e}")
        return

if __name__ == "__main__":
    main()
