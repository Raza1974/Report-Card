import streamlit as st
import pandas as pd
import base64
from fpdf import FPDF
import tempfile
import os
import io
import numpy as np
import matplotlib.pyplot as plt

# Set page configuration
st.set_page_config(page_title="Class Report Card Generator", layout="wide")

# Initialize session state variables if they don't exist
if 'students' not in st.session_state:
    st.session_state.students = []
if 'show_report' not in st.session_state:
    st.session_state.show_report = False
if 'class_name' not in st.session_state:
    st.session_state.class_name = ""
if 'class_teacher' not in st.session_state:
    st.session_state.class_teacher = ""

# Function to calculate grade based on percentage
def calculate_grade(percentage):
    if percentage >= 80:
        return "A+"
    elif percentage >= 70:
        return "A"
    elif percentage >= 60:
        return "B"
    elif percentage >= 50:
        return "C"
    elif percentage >= 40:
        return "F"
    else:
        return "Fail"

# Function to create PDF report card
def create_pdf(students, class_name="", class_teacher=""):
    pdf = FPDF()
    
    for student in students:
        pdf.add_page()
        
        # Set up the PDF
        pdf.set_font("Arial", "B", 16)
        pdf.cell(190, 10, "Student Report Card", 0, 1, "C")
        
        # Class details if provided
        if class_name:
            pdf.set_font("Arial", "B", 12)
            pdf.cell(190, 10, f"Class: {class_name}", 0, 1, "C")
        if class_teacher:
            pdf.set_font("Arial", "", 12)
            pdf.cell(190, 10, f"Class Teacher: {class_teacher}", 0, 1, "C")
            
        pdf.line(10, pdf.get_y() + 5, 200, pdf.get_y() + 5)
        pdf.cell(190, 10, "", 0, 1)  # Add some space
        
        # Student details
        pdf.set_font("Arial", "B", 12)
        pdf.cell(50, 10, "Name:", 0, 0)
        pdf.set_font("Arial", "", 12)
        pdf.cell(140, 10, student["Name"], 0, 1)
        
        pdf.set_font("Arial", "B", 12)
        pdf.cell(50, 10, "Roll Number:", 0, 0)
        pdf.set_font("Arial", "", 12)
        pdf.cell(140, 10, student["Roll Number"], 0, 1)
        
        # Subject marks
        pdf.set_font("Arial", "B", 12)
        pdf.cell(190, 10, "", 0, 1)
        pdf.cell(190, 10, "Subject Marks", 0, 1)
        
        # Table header
        pdf.set_fill_color(200, 200, 200)
        pdf.cell(95, 10, "Subject", 1, 0, "C", True)
        pdf.cell(95, 10, "Marks", 1, 1, "C", True)
        
        # Table data
        pdf.set_font("Arial", "", 12)
        subjects = ["Math", "Physics", "Urdu", "English", "Computer"]
        for subject in subjects:
            pdf.cell(95, 10, subject, 1, 0)
            pdf.cell(95, 10, str(student[subject]), 1, 1)
        
        # Total
        pdf.set_font("Arial", "B", 12)
        pdf.cell(95, 10, "Total", 1, 0)
        pdf.cell(95, 10, str(student["Total"]), 1, 1)
        
        # Percentage and Grade
        pdf.cell(190, 10, "", 0, 1)
        pdf.cell(50, 10, "Percentage:", 0, 0)
        pdf.set_font("Arial", "", 12)
        pdf.cell(140, 10, f"{student['Percentage']:.2f}%", 0, 1)
        
        pdf.set_font("Arial", "B", 12)
        pdf.cell(50, 10, "Grade:", 0, 0)
        pdf.set_font("Arial", "", 12)
        pdf.cell(140, 10, student["Grade"], 0, 1)
        
        # Class Rank if more than one student
        if len(students) > 1:
            # Sort students by percentage to determine rank
            sorted_students = sorted(students, key=lambda x: x['Percentage'], reverse=True)
            rank = [i+1 for i, s in enumerate(sorted_students) if s['Roll Number'] == student['Roll Number']][0]
            
            pdf.set_font("Arial", "B", 12)
            pdf.cell(50, 10, "Class Rank:", 0, 0)
            pdf.set_font("Arial", "", 12)
            pdf.cell(140, 10, f"{rank} out of {len(students)}", 0, 1)
        
        # Footer
        pdf.set_y(-30)
        pdf.set_font("Arial", "I", 8)
        pdf.cell(0, 10, "This is an automatically generated report card.", 0, 0, "C")
    
    # Save the PDF to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        pdf_path = tmp_file.name
        
    pdf.output(pdf_path)
    return pdf_path

# Function to create a download link for the PDF
def get_pdf_download_link(pdf_path, filename):
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    b64_pdf = base64.b64encode(pdf_bytes).decode()
    href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{filename}">Download PDF</a>'
    return href

# Function to create class performance charts
def create_class_performance_charts(students):
    if not students:
        return None
    
    # Create a DataFrame for analysis
    df = pd.DataFrame(students)
    
    # Create a figure with multiple subplots
    fig, axs = plt.subplots(2, 2, figsize=(12, 10))
    
    # 1. Grade Distribution
    grade_counts = df['Grade'].value_counts().sort_index()
    axs[0, 0].bar(grade_counts.index, grade_counts.values, color='skyblue')
    axs[0, 0].set_title('Grade Distribution')
    axs[0, 0].set_xlabel('Grade')
    axs[0, 0].set_ylabel('Number of Students')
    
    # 2. Subject Performance
    subjects = ['Math', 'Physics', 'Urdu', 'English', 'Computer']
    avg_marks = [df[subject].mean() for subject in subjects]
    axs[0, 1].bar(subjects, avg_marks, color='lightgreen')
    axs[0, 1].set_title('Average Marks by Subject')
    axs[0, 1].set_xlabel('Subject')
    axs[0, 1].set_ylabel('Average Marks')
    axs[0, 1].set_ylim(0, 100)
    
    # 3. Percentage Distribution
    axs[1, 0].hist(df['Percentage'], bins=10, color='salmon', edgecolor='black')
    axs[1, 0].set_title('Percentage Distribution')
    axs[1, 0].set_xlabel('Percentage')
    axs[1, 0].set_ylabel('Number of Students')
    
    # 4. Top 5 Students
    top_students = df.sort_values('Percentage', ascending=False).head(5)
    axs[1, 1].barh(top_students['Name'], top_students['Percentage'], color='gold')
    axs[1, 1].set_title('Top 5 Students')
    axs[1, 1].set_xlabel('Percentage')
    axs[1, 1].set_ylabel('Student Name')
    axs[1, 1].invert_yaxis()  # To have the highest at the top
    
    plt.tight_layout()
    
    # Convert plot to image
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    
    return buf

# Title and description
st.title("Class Report Card Generator")
st.markdown("Generate report cards for an entire class of students.")

# Tabs for different input methods
tab1, tab2, tab3 = st.tabs(["Individual Entry", "Bulk Upload", "Class Analytics"])

# Tab 1: Individual Student Entry
with tab1:
    # Class information
    col1, col2 = st.columns(2)
    with col1:
        class_name = st.text_input("Class Name", value=st.session_state.class_name)
        if class_name != st.session_state.class_name:
            st.session_state.class_name = class_name
    
    with col2:
        class_teacher = st.text_input("Class Teacher", value=st.session_state.class_teacher)
        if class_teacher != st.session_state.class_teacher:
            st.session_state.class_teacher = class_teacher
    
    # Input form
    with st.form("student_form"):
        st.subheader("Enter Student Details")
        
        name = st.text_input("Student Name")
        roll_number = st.text_input("Roll Number")
        
        # Subject marks input with validation
        st.subheader("Enter Marks (0-100)")
        col1, col2 = st.columns(2)
        
        with col1:
            math = st.number_input("Math", min_value=0, max_value=100, step=1)
            physics = st.number_input("Physics", min_value=0, max_value=100, step=1)
            urdu = st.number_input("Urdu", min_value=0, max_value=100, step=1)
        
        with col2:
            english = st.number_input("English", min_value=0, max_value=100, step=1)
            computer = st.number_input("Computer", min_value=0, max_value=100, step=1)
        
        # Submit button
        submitted = st.form_submit_button("Add Student")
        
        if submitted:
            if name and roll_number:
                # Check if roll number already exists
                existing_roll_numbers = [s["Roll Number"] for s in st.session_state.students]
                if roll_number in existing_roll_numbers:
                    st.error(f"Roll Number {roll_number} already exists. Please use a unique roll number.")
                else:
                    # Calculate total and percentage
                    total_marks = math + physics + urdu + english + computer
                    percentage = (total_marks / 500) * 100
                    grade = calculate_grade(percentage)
                    
                    # Create student record
                    student = {
                        "Name": name,
                        "Roll Number": roll_number,
                        "Math": math,
                        "Physics": physics,
                        "Urdu": urdu,
                        "English": english,
                        "Computer": computer,
                        "Total": total_marks,
                        "Percentage": percentage,
                        "Grade": grade
                    }
                    
                    # Add to session state
                    st.session_state.students.append(student)
                    st.success(f"Record of {name} inserted successfully!")
            else:
                st.error("Please enter both Name and Roll Number.")

# Tab 2: Bulk Upload
with tab2:
    st.subheader("Upload Student Data")
    st.markdown("""
    Upload a CSV file with student data. The CSV should have the following columns:
    - Name
    - Roll Number
    - Math
    - Physics
    - Urdu
    - English
    - Computer
    """)
    
    # Sample data download
    sample_data = pd.DataFrame({
        'Name': ['John Doe', 'Jane Smith', 'Bob Johnson'],
        'Roll Number': ['001', '002', '003'],
        'Math': [85, 92, 78],
        'Physics': [76, 88, 65],
        'Urdu': [92, 79, 81],
        'English': [88, 94, 72],
        'Computer': [95, 90, 85]
    })
    
    # Create a download link for sample CSV
    csv_buffer = io.StringIO()
    sample_data.to_csv(csv_buffer, index=False)
    csv_str = csv_buffer.getvalue()
    b64_csv = base64.b64encode(csv_str.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64_csv}" download="sample_student_data.csv">Download Sample CSV</a>'
    st.markdown(href, unsafe_allow_html=True)
    
    # File uploader
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        try:
            # Read the CSV file
            df = pd.read_csv(uploaded_file)
            
            # Validate columns
            required_columns = ['Name', 'Roll Number', 'Math', 'Physics', 'Urdu', 'English', 'Computer']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                st.error(f"Missing columns in CSV: {', '.join(missing_columns)}")
            else:
                # Preview the data
                st.subheader("Data Preview")
                st.dataframe(df.head())
                
                # Process and add students
                if st.button("Import Students"):
                    # Check for duplicate roll numbers
                    existing_roll_numbers = [s["Roll Number"] for s in st.session_state.students]
                    new_roll_numbers = df['Roll Number'].astype(str).tolist()
                    duplicates = [roll for roll in new_roll_numbers if roll in existing_roll_numbers]
                    
                    if duplicates:
                        st.error(f"Duplicate roll numbers found: {', '.join(duplicates)}. Please ensure all roll numbers are unique.")
                    else:
                        # Process each row
                        imported_count = 0
                        for _, row in df.iterrows():
                            # Calculate total and percentage
                            total_marks = row['Math'] + row['Physics'] + row['Urdu'] + row['English'] + row['Computer']
                            percentage = (total_marks / 500) * 100
                            grade = calculate_grade(percentage)
                            
                            # Create student record
                            student = {
                                "Name": row['Name'],
                                "Roll Number": str(row['Roll Number']),
                                "Math": row['Math'],
                                "Physics": row['Physics'],
                                "Urdu": row['Urdu'],
                                "English": row['English'],
                                "Computer": row['Computer'],
                                "Total": total_marks,
                                "Percentage": percentage,
                                "Grade": grade
                            }
                            
                            # Add to session state
                            st.session_state.students.append(student)
                            imported_count += 1
                        
                        st.success(f"Successfully imported {imported_count} students!")
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")

# Tab 3: Class Analytics
with tab3:
    if st.session_state.students:
        st.subheader("Class Performance Analytics")
        
        # Create DataFrame for analysis
        df = pd.DataFrame(st.session_state.students)
        
        # Display class statistics
        st.markdown("### Class Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Students", len(df))
        
        with col2:
            st.metric("Class Average", f"{df['Percentage'].mean():.2f}%")
        
        with col3:
            st.metric("Highest Score", f"{df['Percentage'].max():.2f}%")
        
        with col4:
            st.metric("Lowest Score", f"{df['Percentage'].min():.2f}%")
        
        # Display charts
        st.markdown("### Performance Charts")
        chart_buffer = create_class_performance_charts(st.session_state.students)
        if chart_buffer:
            st.image(chart_buffer, use_column_width=True)
        
        # Display subject-wise statistics
        st.markdown("### Subject-wise Statistics")
        subjects = ['Math', 'Physics', 'Urdu', 'English', 'Computer']
        subject_stats = {}
        
        for subject in subjects:
            subject_stats[subject] = {
                'Average': df[subject].mean(),
                'Highest': df[subject].max(),
                'Lowest': df[subject].min(),
                'Pass Rate': (df[subject] >= 40).mean() * 100  # Assuming 40 is pass mark
            }
        
        subject_df = pd.DataFrame(subject_stats).T
        st.dataframe(subject_df.style.format({
            'Average': '{:.2f}',
            'Pass Rate': '{:.2f}%'
        }))
        
        # Top performers
        st.markdown("### Top Performers")
        top_students = df.sort_values('Percentage', ascending=False).head(5)
        st.dataframe(top_students[['Name', 'Roll Number', 'Total', 'Percentage', 'Grade']])
    else:
        st.info("No student data available. Please add students using Individual Entry or Bulk Upload.")

# Sidebar for student list and actions
with st.sidebar:
    st.header("Student List")
    
    if st.session_state.students:
        # Display student count
        st.info(f"Total Students: {len(st.session_state.students)}")
        
        # Display student list
        for i, student in enumerate(st.session_state.students):
            st.markdown(f"**{i+1}. {student['Name']}** (Roll No: {student['Roll Number']})")
        
        # Actions
        st.header("Actions")
        
        # Generate all report cards
        if st.button("Generate All Report Cards"):
            st.session_state.show_report = True
        
        # Download all report cards as PDF
        if st.button("Download All Report Cards"):
            pdf_path = create_pdf(
                st.session_state.students, 
                class_name=st.session_state.class_name,
                class_teacher=st.session_state.class_teacher
            )
            st.markdown(get_pdf_download_link(pdf_path, "class_report_cards.pdf"), unsafe_allow_html=True)
            st.session_state.temp_pdf_path = pdf_path
        
        # Clear all data
        if st.button("Clear All Data"):
            # Clean up any temporary PDF files
            for key in list(st.session_state.keys()):
                if key.startswith("temp_pdf_path"):
                    try:
                        os.remove(st.session_state[key])
                    except:
                        pass
            
            st.session_state.students = []
            st.session_state.show_report = False
            st.experimental_rerun()
    else:
        st.info("No students added yet.")

# Display report cards if requested
if st.session_state.show_report and st.session_state.students:
    st.header("Student Report Cards")
    
    # Create tabs for each student
    student_tabs = st.tabs([f"{s['Name']} ({s['Roll Number']})" for s in st.session_state.students])
    
    for i, tab in enumerate(student_tabs):
        student = st.session_state.students[i]
        
        with tab:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader(f"Report Card: {student['Name']}")
                
                if st.session_state.class_name:
                    st.markdown(f"**Class:** {st.session_state.class_name}")
                if st.session_state.class_teacher:
                    st.markdown(f"**Class Teacher:** {st.session_state.class_teacher}")
                
                st.markdown(f"**Roll Number:** {student['Roll Number']}")
                
                # Create a table for subject marks
                marks_data = {
                    "Subject": ["Math", "Physics", "Urdu", "English", "Computer", "Total"],
                    "Marks": [
                        student["Math"], 
                        student["Physics"], 
                        student["Urdu"], 
                        student["English"], 
                        student["Computer"],
                        student["Total"]
                    ]
                }
                marks_df = pd.DataFrame(marks_data)
                st.table(marks_df)
                
                # Display percentage and grade
                st.markdown(f"**Percentage:** {student['Percentage']:.2f}%")
                st.markdown(f"**Grade:** {student['Grade']}")
                
                # Class Rank
                sorted_students = sorted(st.session_state.students, key=lambda x: x['Percentage'], reverse=True)
                rank = [i+1 for i, s in enumerate(sorted_students) if s['Roll Number'] == student['Roll Number']][0]
                st.markdown(f"**Class Rank:** {rank} out of {len(st.session_state.students)}")
            
            with col2:
                # Individual PDF download button
                if st.button(f"Download PDF", key=f"pdf_{i}"):
                    pdf_path = create_pdf(
                        [student], 
                        class_name=st.session_state.class_name,
                        class_teacher=st.session_state.class_teacher
                    )
                    st.markdown(get_pdf_download_link(pdf_path, f"{student['Name']}_report_card.pdf"), unsafe_allow_html=True)
                    st.session_state[f"temp_pdf_path_{i}"] = pdf_path
                
                # Subject performance chart
                st.markdown("### Subject Performance")
                
                # Create radar chart for subject performance
                subjects = ["Math", "Physics", "Urdu", "English", "Computer"]
                subject_values = [student[subject] for subject in subjects]
                
                # Create a radar chart
                angles = np.linspace(0, 2*np.pi, len(subjects), endpoint=False).tolist()
                angles += angles[:1]  # Close the loop
                
                subject_values += subject_values[:1]  # Close the loop
                
                fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(polar=True))
                ax.plot(angles, subject_values, 'o-', linewidth=2)
                ax.fill(angles, subject_values, alpha=0.25)
                ax.set_thetagrids(np.degrees(angles[:-1]), subjects)
                ax.set_ylim(0, 100)
                ax.grid(True)
                
                st.pyplot(fig)

# Clean up temporary files when the app is closed
if hasattr(st.session_state, "temp_pdf_path"):
    try:
        os.remove(st.session_state.temp_pdf_path)
    except:
        pass