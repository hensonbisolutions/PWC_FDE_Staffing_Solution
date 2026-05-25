"""
Generate Sample Data for FDE Staffing Intelligence Platform

This script creates realistic sample datasets for the staffing intelligence application.
It generates:
- Employee profiles with seniority levels and sector experience
- Technical skills with proficiency levels
- Certifications and training records
- Project history with complexity ratings
- Availability and allocation status
- Staffing opportunities
- Self-assessment for career development

The data is generated using Faker for realism and is designed to support
staffing matching algorithms and dashboarding.

Generated files are saved to the data/ directory.
"""

import pandas as pd
from faker import Faker
import random
import os
from datetime import datetime, timedelta


def generate_employees(n_employees=40):
    """
    Generate employee master records with seniority, sector experience,
    and employment status.
    """
    fake = Faker('en_GB')
    random.seed(42)
    
    seniority_levels = ['Junior', 'Mid-Level', 'Senior', 'Lead', 'Principal']
    sectors = ['Healthcare', 'Aviation', 'Transport', 'Banking', 'Retail', 
               'Government', 'Energy', 'Insurance']
    locations = ['London', 'Manchester', 'Birmingham', 'Leeds', 'Edinburgh',
                 'Bristol', 'Cambridge', 'Oxford']
    
    employees = []
    for emp_id in range(1001, 1001 + n_employees):
        emp = {
            'employee_id': emp_id,
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'email': fake.email(),
            'seniority_level': random.choice(seniority_levels),
            'primary_sector': random.choice(sectors),
            'secondary_sector': random.choice(sectors),
            'location': random.choice(locations),
            'years_experience': random.randint(1, 20),
            'employment_status': random.choice(['Active', 'Active', 'On Leave']),
            'join_date': fake.date_between(start_date='-10y'),
            'manager_id': random.choice([None, None, None] + [1001 + i for i in range(5)])
        }
        employees.append(emp)
    
    return pd.DataFrame(employees)


def generate_skills(employees_df):
    """
    Generate technical skills inventory with proficiency levels.
    Links skills to employees with realistic proficiency distributions.
    """
    skills = ['Python', 'SQL', 'Power BI', 'DAX', 'Azure', 'Data Engineering',
              'Machine Learning', 'Automation', 'ETL', 'Stakeholder Management',
              'AI/ML', 'Analytics', 'Data Visualisation', 'VBA', 'Cloud Engineering']
    
    proficiency_levels = ['Beginner', 'Intermediate', 'Advanced', 'Expert']
    
    employee_skills = []
    for _, emp in employees_df.iterrows():
        # Each employee has 3-8 skills
        n_skills = random.randint(3, 8)
        selected_skills = random.sample(skills, min(n_skills, len(skills)))
        
        for skill in selected_skills:
            # Senior employees more likely to have advanced skills
            if emp['seniority_level'] in ['Lead', 'Principal']:
                proficiency = random.choices(
                    proficiency_levels,
                    weights=[5, 15, 35, 45]
                )[0]
            elif emp['seniority_level'] in ['Senior']:
                proficiency = random.choices(
                    proficiency_levels,
                    weights=[10, 25, 40, 25]
                )[0]
            else:
                proficiency = random.choices(
                    proficiency_levels,
                    weights=[20, 40, 30, 10]
                )[0]
            
            employee_skills.append({
                'employee_id': emp['employee_id'],
                'skill_name': skill,
                'proficiency_level': proficiency,
                'years_of_experience': max(1, random.randint(1, emp['years_experience']))
            })
    
    return pd.DataFrame(employee_skills)


def generate_certifications(employees_df):
    """
    Generate professional certifications and training records.
    Certifications are mapped to skills and seniority levels.
    """
    certifications_list = [
        'AWS Certified Solutions Architect',
        'Azure Administrator Certified',
        'Google Cloud Professional',
        'Microsoft Certified: Data Analyst Associate',
        'Tableau Desktop Specialist',
        'Power BI Data Analyst',
        'PMP - Project Management Professional',
        'CISSP - Certified Information Systems Security Professional',
        'Certified Data Science Professional',
        'Google Analytics Certification',
        'Advanced Excel Certification',
        'SQL Server Administration',
        'Oracle Certified Associate',
        'Python Professional Certification',
        'Agile Scrum Master Certification'
    ]
    
    certifications = []
    for _, emp in employees_df.iterrows():
        # More senior employees have more certifications
        n_certs = random.randint(0, 4 if emp['seniority_level'] in ['Lead', 'Principal'] 
                                  else 2 if emp['seniority_level'] in ['Senior']
                                  else 1)
        
        selected_certs = random.sample(certifications_list, min(n_certs, len(certifications_list)))
        
        for cert in selected_certs:
            issue_date = datetime.now() - timedelta(days=random.randint(30, 1095))
            certifications.append({
                'employee_id': emp['employee_id'],
                'certification_name': cert,
                'issue_date': issue_date.date(),
                'expiry_date': (issue_date + timedelta(days=365*3)).date(),
                'issuing_body': random.choice(['AWS', 'Microsoft', 'Google', 'Tableau', 'PMI', 'ISC2']),
                'status': 'Active' if issue_date > datetime.now() - timedelta(days=1095) else 'Expired'
            })
    
    return pd.DataFrame(certifications)


def generate_project_history(employees_df):
    """
    Generate project assignment history with complexity and sector alignment.
    """
    fake = Faker('en_GB')
    project_types = ['Data Migration', 'Analytics Implementation', 'Cloud Infrastructure',
                     'Automation Initiative', 'AI Proof of Concept', 'Process Optimization',
                     'System Integration', 'Risk Assessment', 'Capability Building']
    sectors = ['Healthcare', 'Aviation', 'Transport', 'Banking', 'Retail', 
               'Government', 'Energy', 'Insurance']
    
    project_history = []
    for _, emp in employees_df.iterrows():
        # 2-6 projects per employee
        n_projects = random.randint(2, 6)
        
        for i in range(n_projects):
            end_date = datetime.now() - timedelta(days=random.randint(30, 1095))
            start_date = end_date - timedelta(days=random.randint(90, 365))
            
            project_history.append({
                'employee_id': emp['employee_id'],
                'project_id': f"PROJ_{1001 + i}",
                'project_name': fake.sentence(nb_words=4),
                'sector': random.choice(sectors),
                'complexity': random.choice(['Low', 'Medium', 'High', 'Critical']),
                'role': random.choice(['Analyst', 'Engineer', 'Lead', 'Advisor']),
                'start_date': start_date.date(),
                'end_date': end_date.date(),
                'allocation_percentage': random.randint(50, 100),
                'delivery_status': random.choice(['Completed', 'Completed', 'On Track', 'Delayed'])
            })
    
    return pd.DataFrame(project_history)


def generate_availability(employees_df):
    """
    Generate current availability and allocation status for workforce planning.
    """
    availability = []
    for _, emp in employees_df.iterrows():
        availability.append({
            'employee_id': emp['employee_id'],
            'available_percentage': random.randint(0, 100),
            'current_allocation_percentage': random.randint(0, 100),
            'next_available_date': (datetime.now() + timedelta(days=random.randint(0, 90))).date(),
            'mobility_willing': random.choice([True, True, False]),
            'remote_willing': random.choice([True, True, True, False]),
            'last_updated': datetime.now().date()
        })
    
    return pd.DataFrame(availability)


def generate_opportunities(n_opportunities=15):
    """
    Generate staffing opportunities matching potential employee profiles.
    """
    fake = Faker('en_GB')
    sectors = ['Healthcare', 'Aviation', 'Transport', 'Banking', 'Retail', 
               'Government', 'Energy', 'Insurance']
    skills = ['Python', 'SQL', 'Power BI', 'DAX', 'Azure', 'Data Engineering',
              'Machine Learning', 'Automation', 'ETL', 'Stakeholder Management',
              'AI/ML', 'Analytics', 'Data Visualisation', 'VBA', 'Cloud Engineering']
    
    opportunities = []
    for opp_id in range(2001, 2001 + n_opportunities):
        required_skills = random.sample(skills, random.randint(2, 5))
        opportunity = {
            'opportunity_id': opp_id,
            'opportunity_name': fake.sentence(nb_words=4),
            'client_sector': random.choice(sectors),
            'location': random.choice(['London', 'Manchester', 'Remote', 'Birmingham']),
            'required_seniority': random.choice(['Mid-Level', 'Senior', 'Lead']),
            'required_skills': ', '.join(required_skills),
            'allocation_weeks': random.randint(4, 52),
            'start_date': (datetime.now() + timedelta(days=random.randint(7, 60))).date(),
            'status': random.choice(['Open', 'Open', 'In Progress', 'Filled']),
            'priority': random.choice(['Medium', 'High', 'Critical', 'Low']),
            'description': fake.sentence(nb_words=8)
        }
        opportunities.append(opportunity)
    
    return pd.DataFrame(opportunities)


def generate_self_assessment(employees_df):
    """
    Generate employee self-assessments for career development and capability planning.
    """
    development_areas = ['Technical Leadership', 'Cloud Architecture', 'Data Science',
                        'Stakeholder Management', 'Agile Methodologies',
                        'Industry Knowledge', 'Project Management', 'Team Leadership']
    career_goals = ['Promotion to Senior Role', 'Sector Specialization',
                   'Technical Expertise', 'Management Track', 'Entrepreneurship']
    
    self_assessment = []
    for _, emp in employees_df.iterrows():
        self_assessment.append({
            'employee_id': emp['employee_id'],
            'career_goal': random.choice(career_goals),
            'development_priority': random.choice(development_areas),
            'learning_preference': random.choice(['Online', 'Hands-on', 'Mentoring', 'Certification']),
            'sector_preference': random.choice(['Healthcare', 'Aviation', 'Transport', 'Banking', 
                                               'Retail', 'Government', 'Energy', 'Insurance']),
            'mobility_preference': random.choice(['UK Only', 'Europe', 'Global']),
            'engagement_score': random.randint(60, 100),
            'last_assessment_date': (datetime.now() - timedelta(days=random.randint(0, 180))).date()
        })
    
    return pd.DataFrame(self_assessment)


def create_data_directory():
    """Ensure data directory exists."""
    data_dir = 'data'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    return data_dir


def main():
    """
    Main execution function - generates all datasets and saves to CSV files.
    """
    print("\n" + "="*60)
    print("FDE STAFFING INTELLIGENCE PLATFORM")
    print("Sample Data Generation")
    print("="*60 + "\n")
    
    # Create data directory
    data_dir = create_data_directory()
    
    print("Generating sample datasets...\n")
    
    # Generate employees
    print("  ✓ Generating 40 employee profiles...")
    employees_df = generate_employees(n_employees=40)
    employees_df.to_csv(os.path.join(data_dir, 'employees.csv'), index=False)
    
    # Generate skills
    print("  ✓ Generating technical skills inventory...")
    skills_df = generate_skills(employees_df)
    skills_df.to_csv(os.path.join(data_dir, 'employee_skills.csv'), index=False)
    
    # Generate certifications
    print("  ✓ Generating certifications and training records...")
    certs_df = generate_certifications(employees_df)
    certs_df.to_csv(os.path.join(data_dir, 'certifications.csv'), index=False)
    
    # Generate project history
    print("  ✓ Generating project history...")
    projects_df = generate_project_history(employees_df)
    projects_df.to_csv(os.path.join(data_dir, 'project_history.csv'), index=False)
    
    # Generate availability
    print("  ✓ Generating availability tracking...")
    availability_df = generate_availability(employees_df)
    availability_df.to_csv(os.path.join(data_dir, 'availability.csv'), index=False)
    
    # Generate opportunities
    print("  ✓ Generating staffing opportunities...")
    opportunities_df = generate_opportunities(n_opportunities=15)
    opportunities_df.to_csv(os.path.join(data_dir, 'opportunities.csv'), index=False)
    
    # Generate self-assessment
    print("  ✓ Generating employee self-assessments...")
    assessment_df = generate_self_assessment(employees_df)
    assessment_df.to_csv(os.path.join(data_dir, 'self_assessment.csv'), index=False)
    
    print("\n" + "="*60)
    print("DATA GENERATION COMPLETE")
    print("="*60)
    print(f"\nGenerated files saved to: {data_dir}/")
    print(f"\n  • employees.csv ({len(employees_df)} records)")
    print(f"  • employee_skills.csv ({len(skills_df)} records)")
    print(f"  • certifications.csv ({len(certs_df)} records)")
    print(f"  • project_history.csv ({len(projects_df)} records)")
    print(f"  • availability.csv ({len(availability_df)} records)")
    print(f"  • opportunities.csv ({len(opportunities_df)} records)")
    print(f"  • self_assessment.csv ({len(assessment_df)} records)")
    print("\nReady to start the Streamlit application!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
