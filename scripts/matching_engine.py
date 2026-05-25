"""
Matching Engine for FDE Staffing Intelligence Platform

This module contains the core algorithmic logic for matching employees to
staffing opportunities. The engine uses a multi-dimensional scoring approach
that combines skill match, seniority alignment, sector fit, availability,
certifications, career alignment, and location fit.

All recommendations are fully explainable and transparent - no black boxes.
Every score can be traced back to specific data and calculation logic.

DESIGN PHILOSOPHY:
- Multi-dimensional scoring: 7 independent factors combined
- Transparency first: Every score has a detailed explanation
- Explainability over complexity: Clear logic that humans can understand
- Audit trail: Full traceability of all scoring decisions
- Human oversight: System recommends, humans decide
"""

import pandas as pd
from typing import List, Dict, Tuple
from datetime import datetime, timedelta


class MatchingEngine:
    """
    Core recommendation engine for staffing opportunity matching.
    
    Scores employees against opportunities using seven dimensions:
    1. Skill Match (30%) - Technical capability alignment
    2. Seniority (20%) - Career stage fit
    3. Sector Experience (15%) - Industry knowledge
    4. Availability (20%) - Timeline and capacity fit
    5. Certifications (10%) - Compliance and credentials
    6. Career Alignment (5%) - Personal development fit
    7. Location Fit (5%) - Geographic and mobility alignment
    
    All scores normalized to 0-100 scale for comparability.
    """
    
    def __init__(self, employees_df: pd.DataFrame, skills_df: pd.DataFrame,
                 certifications_df: pd.DataFrame, project_history_df: pd.DataFrame,
                 availability_df: pd.DataFrame, opportunities_df: pd.DataFrame,
                 self_assessment_df: pd.DataFrame):
        """
        Initialize the matching engine with all required datasets.
        
        Args:
            employees_df: Employee master records
            skills_df: Skills inventory with proficiency levels
            certifications_df: Certifications and training records
            project_history_df: Historical project assignments
            availability_df: Current availability and allocation status
            opportunities_df: Staffing opportunities/demand
            self_assessment_df: Employee career development data
        """
        self.employees = employees_df
        self.skills = skills_df
        self.certifications = certifications_df
        self.projects = project_history_df
        self.availability = availability_df
        self.opportunities = opportunities_df
        self.assessments = self_assessment_df
        
        # Scoring weights (must sum to 1.0)
        self.weights = {
            'skill': 0.30,        # Skill match - most important
            'seniority': 0.20,    # Career stage alignment
            'sector': 0.15,       # Industry experience
            'availability': 0.20, # Can they start when needed?
            'certification': 0.10, # Compliance and credentials
            'career': 0.05,       # Personal development fit
            'location': 0.05      # Geographic constraints
        }
        
        # Proficiency level scoring map
        self.proficiency_scores = {
            'Beginner': 25,
            'Intermediate': 50,
            'Advanced': 75,
            'Expert': 100
        }
        
        # Seniority level hierarchy
        self.seniority_hierarchy = {
            'Junior': 1,
            'Mid-Level': 2,
            'Senior': 3,
            'Lead': 4,
            'Principal': 5
        }
    
    def rank_candidates(self, opportunity_id: int, 
                       top_n: int = 10) -> List[Dict]:
        """
        Generate ranked list of candidates for staffing opportunity.
        
        Args:
            opportunity_id: ID of opportunity to match against
            top_n: Number of top candidates to return detailed scores for
        
        Returns:
            List of candidate recommendations sorted by overall_score descending
            Each record includes: employee info, scores, explanation, risks
        """
        # Get opportunity details
        opp = self.opportunities[
            self.opportunities['opportunity_id'] == opportunity_id
        ]
        
        if opp.empty:
            return []
        
        opp = opp.iloc[0]
        
        # Score all employees
        all_scores = []
        for _, emp in self.employees.iterrows():
            score_data = self.score_employee_for_opportunity(emp, opp)
            all_scores.append(score_data)
        
        # Sort by overall score descending
        ranked = sorted(all_scores, 
                       key=lambda x: x['overall_score'], 
                       reverse=True)
        
        # Generate detailed explanations for top N
        for rec in ranked[:top_n]:
            rec['explanation'] = self.generate_explanation(
                rec, opp
            )
            rec['risks'] = self.flag_risks(rec, opp)
        
        return ranked
    
    def score_employee_for_opportunity(
        self, employee: pd.Series, 
        opportunity: pd.Series
    ) -> Dict:
        """
        Calculate composite score for employee-opportunity pairing.
        
        Returns dict with:
        - overall_score: Weighted combination of all dimensions (0-100)
        - Breakdown of each scoring dimension
        - Employee and opportunity metadata
        """
        emp_id = employee['employee_id']
        
        # Calculate each dimension
        skill_score = self._score_skill_match(emp_id, opportunity)
        seniority_score = self._score_seniority_alignment(
            employee, opportunity
        )
        sector_score = self._score_sector_fit(employee, opportunity)
        availability_score = self._score_availability(emp_id, opportunity)
        cert_score = self._score_certifications(emp_id, opportunity)
        career_score = self._score_career_alignment(emp_id, opportunity)
        location_score = self._score_location_fit(emp_id, opportunity)
        
        # Calculate weighted overall score
        overall_score = (
            self.weights['skill'] * skill_score +
            self.weights['seniority'] * seniority_score +
            self.weights['sector'] * sector_score +
            self.weights['availability'] * availability_score +
            self.weights['certification'] * cert_score +
            self.weights['career'] * career_score +
            self.weights['location'] * location_score
        )
        
        return {
            'employee_id': emp_id,
            'name': f"{employee['first_name']} {employee['last_name']}",
            'email': employee['email'],
            'seniority': employee['seniority_level'],
            'sector': employee['primary_sector'],
            'location': employee['location'],
            'overall_score': round(overall_score, 0),
            'scoring_breakdown': {
                'skill_match': round(skill_score, 0),
                'seniority_alignment': round(seniority_score, 0),
                'sector_experience': round(sector_score, 0),
                'availability': round(availability_score, 0),
                'certifications': round(cert_score, 0),
                'career_alignment': round(career_score, 0),
                'location_fit': round(location_score, 0)
            }
        }
    
    def _score_skill_match(self, emp_id: int, opportunity: pd.Series) -> int:
        """
        Score employee skill match against opportunity requirements (0-100).
        
        Logic:
        - Identify required skills from opportunity
        - Find matching skills in employee inventory
        - Adjust for proficiency level
        - Calculate: (matched_count / total_required) * avg_proficiency
        
        Example:
            Required: Python, SQL, Azure, Power BI
            Employee: Python (Expert), SQL (Advanced), Azure (Intermediate)
            Score: (3/4 matched) * ((100+75+50)/3 average proficiency)
                 = 75% * 75% = 56
        """
        # Parse required skills from opportunity
        required_skills = [
            s.strip() for s in opportunity['required_skills'].split(',')
        ]
        
        # Get employee's skills
        emp_skills = self.skills[self.skills['employee_id'] == emp_id]
        
        if emp_skills.empty and required_skills:
            return 0  # No skills, can't match
        
        # Calculate matches
        matched_count = 0
        proficiency_scores = []
        
        for req_skill in required_skills:
            skill_match = emp_skills[
                emp_skills['skill_name'].str.lower() == req_skill.lower()
            ]
            
            if not skill_match.empty:
                matched_count += 1
                proficiency = skill_match.iloc[0]['proficiency_level']
                proficiency_scores.append(
                    self.proficiency_scores.get(proficiency, 50)
                )
        
        if not proficiency_scores:
            return 0
        
        # Score = (matched_ratio) * (avg_proficiency)
        matched_ratio = matched_count / len(required_skills)
        avg_proficiency = sum(proficiency_scores) / len(proficiency_scores) / 100
        
        skill_score = matched_ratio * avg_proficiency * 100
        return min(100, int(skill_score))
    
    def _score_seniority_alignment(
        self, employee: pd.Series, 
        opportunity: pd.Series
    ) -> int:
        """
        Score alignment between employee seniority and opportunity level (0-100).
        
        Logic:
        - Match employee level to required level
        - Exact match = 100
        - One level below = 60 (stretch opportunity)
        - Two+ levels below = 40 (risky)
        - Above = 80-100 depending on gap (overqualified ok, but not ideal)
        """
        emp_level = self.seniority_hierarchy.get(
            employee['seniority_level'], 3
        )
        req_level = self.seniority_hierarchy.get(
            opportunity['required_seniority'], 3
        )
        
        diff = emp_level - req_level
        
        if diff == 0:
            return 100  # Exact match
        elif diff == 1:
            return 80   # One level above (fine)
        elif diff > 1:
            return 70   # Overqualified (could bore them)
        elif diff == -1:
            return 60   # One level below (stretch)
        else:
            return 40   # Multiple levels below (risky)
    
    def _score_sector_fit(self, employee: pd.Series, 
                         opportunity: pd.Series) -> int:
        """
        Score employee sector experience vs. opportunity sector (0-100).
        
        Logic:
        - Primary sector match = 100
        - Secondary sector match = 70
        - No sector match = check project history for similar
        - Bonus for diverse experience = up to 80
        """
        opp_sector = opportunity['client_sector']
        
        if employee['primary_sector'] == opp_sector:
            return 100
        
        if employee['secondary_sector'] == opp_sector:
            return 70
        
        # Check project history for sector experience
        emp_projects = self.projects[
            self.projects['employee_id'] == employee['employee_id']
        ]
        
        if not emp_projects.empty:
            matching_projects = emp_projects[
                emp_projects['sector'] == opp_sector
            ]
            if not matching_projects.empty:
                return 60  # Some experience
        
        return 40  # No direct experience, but willing to learn
    
    def _score_availability(self, emp_id: int, 
                           opportunity: pd.Series) -> int:
        """
        Score availability for upcoming opportunity (0-100).
        
        Logic:
        - Check available % capacity
        - Check when employee will be available
        - Compare to opportunity start date
        - Score based on: capacity * timeline_fit
        
        Example:
            Available: 40%, Ready: 2 weeks, Opp start: 2 weeks
            Score: 40% available * 100% timing = 40
        """
        avail = self.availability[
            self.availability['employee_id'] == emp_id
        ]
        
        if avail.empty:
            return 50  # Unknown availability
        
        avail = avail.iloc[0]
        
        # Current availability percentage
        available_pct = avail['available_percentage']
        
        # When can they start?
        next_available = pd.to_datetime(avail['next_available_date'])
        opp_start = pd.to_datetime(opportunity['start_date'])
        days_until_needed = (opp_start - datetime.now()).days
        days_until_available = (next_available - datetime.now()).days
        
        # Timeline fit: are they free when needed?
        if days_until_available <= days_until_needed:
            timeline_fit = 100
        else:
            # Penalize if not available when needed
            timeline_fit = max(0, 100 - ((days_until_available - 
                                         days_until_needed) * 5))
        
        # Availability score = capacity * timeline
        availability_score = (available_pct * timeline_fit) / 100
        
        return min(100, int(availability_score))
    
    def _score_certifications(self, emp_id: int, 
                             opportunity: pd.Series) -> int:
        """
        Score certification status and compliance (0-100).
        
        Logic:
        - Check for active certifications (vs. expired)
        - Flag if certifications expiring soon
        - Assume all certs contribute to score
        - More active certs = higher score
        """
        emp_certs = self.certifications[
            self.certifications['employee_id'] == emp_id
        ]
        
        if emp_certs.empty:
            return 60  # No certs, but maybe not required
        
        # Count active vs. expired
        emp_certs['expiry_date'] = pd.to_datetime(emp_certs['expiry_date'])
        today = pd.to_datetime(datetime.now().date())
        
        active_certs = emp_certs[emp_certs['expiry_date'] > today]
        expired_certs = emp_certs[emp_certs['expiry_date'] <= today]
        
        active_count = len(active_certs)
        expired_count = len(expired_certs)
        
        # Score: based on active:expired ratio
        if expired_count == 0:
            return 100  # All active
        
        total = active_count + expired_count
        cert_score = (active_count / total) * 100
        
        return min(100, int(cert_score))
    
    def _score_career_alignment(self, emp_id: int, 
                               opportunity: pd.Series) -> int:
        """
        Score alignment between employee career goals and opportunity (0-100).
        
        Logic:
        - Does opportunity match stated career goal?
        - Does opportunity align with sector preference?
        - Does it support learning preference?
        - Higher score if aligned, moderate score if neutral
        """
        assessment = self.assessments[
            self.assessments['employee_id'] == emp_id
        ]
        
        if assessment.empty:
            return 70  # Neutral assessment
        
        assessment = assessment.iloc[0]
        
        score = 70  # Base score for opportunity
        
        # Bonus if sector preference matches
        if assessment['sector_preference'] == opportunity['client_sector']:
            score += 15
        
        # Bonus if opportunity supports career goal
        career_goal = assessment['career_goal']
        if 'Promotion' in career_goal or 'Senior' in opportunity['required_seniority']:
            score += 10
        
        return min(100, score)
    
    def _score_location_fit(self, emp_id: int, 
                           opportunity: pd.Series) -> int:
        """
        Score geographic and mobility fit (0-100).
        
        Logic:
        - Check if employee is mobile/willing to relocate
        - Check if remote work is supported
        - Match location preferences
        """
        emp = self.employees[self.employees['employee_id'] == emp_id]
        avail = self.availability[self.availability['employee_id'] == emp_id]
        
        if emp.empty or avail.empty:
            return 70
        
        emp = emp.iloc[0]
        avail = avail.iloc[0]
        
        opp_location = opportunity['location'].lower()
        emp_location = emp['location'].lower()
        
        # Location match
        if emp_location == opp_location or 'remote' in opp_location:
            return 100  # No relocation needed
        
        # Check willingness
        if avail['mobility_willing']:
            return 80  # Willing to relocate
        
        if avail['remote_willing'] and 'remote' in opp_location:
            return 100  # Can work remotely
        
        return 50  # Location mismatch and not mobile
    
    def generate_explanation(self, candidate: Dict, 
                            opportunity: pd.Series) -> Dict:
        """
        Generate human-readable explanation for scoring decision.
        
        Returns dict with:
        - strengths: Why this is a good fit
        - considerations: Concerns or risks
        - recommendation: Summary statement
        """
        breakdown = candidate['scoring_breakdown']
        
        strengths = []
        considerations = []
        
        # Skill match analysis
        if breakdown['skill_match'] >= 85:
            strengths.append(
                f"Excellent skill match - {breakdown['skill_match']}% of "
                "required skills at strong proficiency levels"
            )
        elif breakdown['skill_match'] >= 70:
            strengths.append(
                f"Good skill match - {breakdown['skill_match']}% of "
                "required skills available"
            )
        elif breakdown['skill_match'] >= 50:
            considerations.append(
                f"Moderate skill match ({breakdown['skill_match']}%) - "
                "some skills need development"
            )
        else:
            considerations.append(
                f"Limited skill match ({breakdown['skill_match']}%) - "
                "significant skill development needed"
            )
        
        # Seniority analysis
        if breakdown['seniority_alignment'] == 100:
            strengths.append("Seniority level is exact match for role")
        elif breakdown['seniority_alignment'] >= 80:
            strengths.append("Well-aligned seniority level")
        elif breakdown['seniority_alignment'] < 60:
            considerations.append(
                f"Seniority may be below requirement "
                f"({breakdown['seniority_alignment']}%) - "
                "stretch assignment"
            )
        
        # Sector analysis
        if breakdown['sector_experience'] == 100:
            strengths.append("Direct primary sector expertise")
        elif breakdown['sector_experience'] >= 70:
            strengths.append("Strong sector background")
        elif breakdown['sector_experience'] < 50:
            considerations.append(
                "Limited sector experience - will need to ramp up "
                "on industry context"
            )
        
        # Availability analysis
        if breakdown['availability'] >= 80:
            strengths.append("High availability and can start on timeline")
        elif breakdown['availability'] < 50:
            considerations.append(
                "Limited availability - may have scheduling challenges"
            )
        
        # Certification analysis
        if breakdown['certifications'] < 70:
            considerations.append(
                "Some certifications missing or expiring - "
                "verify compliance"
            )
        
        # Generate recommendation text
        overall = candidate['overall_score']
        if overall >= 85:
            recommendation = "Highly recommended. Strong fit across all dimensions."
        elif overall >= 75:
            recommendation = "Recommended. Good fit with minor considerations."
        elif overall >= 65:
            recommendation = "Consider with caution. Some concerns about fit."
        else:
            recommendation = "Not recommended. Significant concerns about fit."
        
        return {
            'strengths': strengths,
            'considerations': considerations,
            'recommendation': recommendation
        }
    
    def flag_risks(self, candidate: Dict, 
                  opportunity: pd.Series) -> List[str]:
        """
        Identify and flag risks for human decision-maker review.
        
        Returns list of risk flags that should receive attention.
        """
        risks = []
        breakdown = candidate['scoring_breakdown']
        emp_id = candidate['employee_id']
        
        # Red flag: Critical skill gap
        if breakdown['skill_match'] < 50:
            risks.append("RED: Critical skill gaps - high training risk")
        
        # Red flag: Significant seniority mismatch
        if breakdown['seniority_alignment'] < 50:
            risks.append("RED: Significant seniority gap - may struggle")
        
        # Yellow flag: Certification concerns
        emp_certs = self.certifications[
            self.certifications['employee_id'] == emp_id
        ]
        if not emp_certs.empty:
            emp_certs['expiry_date'] = pd.to_datetime(
                emp_certs['expiry_date']
            )
            today = pd.to_datetime(datetime.now().date())
            expiring_soon = emp_certs[
                (emp_certs['expiry_date'] > today) &
                (emp_certs['expiry_date'] < today + timedelta(days=180))
            ]
            if not expiring_soon.empty:
                risks.append(
                    "YELLOW: Certifications expiring in next 6 months - "
                    "plan renewals"
                )
        
        # Yellow flag: Limited availability
        if breakdown['availability'] < 60:
            risks.append(
                "YELLOW: Limited availability - coordination needed"
            )
        
        # Yellow flag: Sector mismatch
        if breakdown['sector_experience'] < 50:
            risks.append(
                "YELLOW: Outside primary sectors - industry learning curve"
            )
        
        return risks
