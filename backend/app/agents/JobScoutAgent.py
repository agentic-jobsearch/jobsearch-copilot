import os
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from dotenv import load_dotenv

load_dotenv()

class ExperienceLevel(Enum):
    ENTRY = "entry"
    MID = "mid" 
    SENIOR = "senior"
    LEAD = "lead"
    EXECUTIVE = "executive"

class WorkType(Enum):
    REMOTE = "remote"
    ONSITE = "onsite"
    HYBRID = "hybrid"

class VisaStatus(Enum):
    CITIZEN = "citizen"
    PERMANENT_RESIDENT = "permanent_resident"
    H1B = "h1b"
    F1_OPT = "f1_opt"
    REQUIRES_SPONSORSHIP = "requires_sponsorship"

@dataclass
class SearchConstraints:
    """Define search constraints and filters"""
    # Experience requirements
    min_years_experience: int = 0
    max_years_experience: int = 20
    experience_level: List[ExperienceLevel] = None
    
    # Compensation
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: str = "USD"
    
    # Location preferences
    preferred_locations: List[str] = None
    work_type: List[WorkType] = None
    willing_to_relocate: bool = False
    
    # Visa/Legal requirements
    visa_status: VisaStatus = VisaStatus.CITIZEN
    requires_visa_sponsorship: bool = False
    
    # Company preferences
    company_size_preference: List[str] = None  # startup, small, medium, large, enterprise
    industry_preferences: List[str] = None
    exclude_companies: List[str] = None
    
    # Job characteristics
    job_types: List[str] = None  # full-time, part-time, contract, freelance
    seniority_levels: List[str] = None
    
    def __post_init__(self):
        if self.experience_level is None:
            self.experience_level = [ExperienceLevel.MID]
        if self.preferred_locations is None:
            self.preferred_locations = ["remote"]
        if self.work_type is None:
            self.work_type = [WorkType.REMOTE, WorkType.HYBRID]
        if self.company_size_preference is None:
            self.company_size_preference = ["medium", "large"]
        if self.industry_preferences is None:
            self.industry_preferences = []
        if self.exclude_companies is None:
            self.exclude_companies = []
        if self.job_types is None:
            self.job_types = ["full-time"]
        if self.seniority_levels is None:
            self.seniority_levels = []

@dataclass
class SearchPlan:
    """Complete search plan with keywords, constraints, and strategy"""
    # Search terms
    primary_keywords: List[str]
    secondary_keywords: List[str]
    skill_keywords: List[str]
    
    # Search constraints
    constraints: SearchConstraints
    
    # Search strategy
    search_priority: str  # quality_over_quantity, quantity_over_quality, balanced
    max_results_per_source: int = 50
    search_radius_miles: int = 25
    
    # Ranking criteria weights (0-1, should sum to 1.0)
    ranking_weights: Dict[str, float] = None
    
    # Metadata
    created_at: datetime = None
    valid_until: datetime = None
    
    def __post_init__(self):
        if self.ranking_weights is None:
            self.ranking_weights = {
                "skill_match": 0.3,
                "experience_match": 0.2,
                "salary_match": 0.2,
                "location_preference": 0.15,
                "company_preference": 0.15
            }
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.valid_until is None:
            self.valid_until = datetime.now() + timedelta(days=7)

class PlannerAgent:
    """Creates intelligent search plans based on user profile and preferences"""
    
    def __init__(self):
        self.skill_synonyms = self._load_skill_synonyms()
        self.location_mappings = self._load_location_mappings()
        print("PlannerAgent initialized successfully")
    
    def _load_skill_synonyms(self) -> Dict[str, List[str]]:
        """Load skill synonyms for better search coverage"""
        return {
            "python": ["python", "python3", "django", "flask", "fastapi"],
            "javascript": ["javascript", "js", "node.js", "nodejs", "react", "vue", "angular"],
            "java": ["java", "spring", "spring boot", "hibernate"],
            "sql": ["sql", "mysql", "postgresql", "sqlite", "database"],
            "aws": ["aws", "amazon web services", "ec2", "s3", "lambda"],
            "docker": ["docker", "containerization", "kubernetes", "k8s"],
            "machine learning": ["machine learning", "ml", "ai", "artificial intelligence", "deep learning"],
            "data science": ["data science", "data analysis", "analytics", "pandas", "numpy"],
            "frontend": ["frontend", "front-end", "ui", "user interface", "css", "html"],
            "backend": ["backend", "back-end", "api", "server-side", "microservices"],
            "full stack": ["full stack", "fullstack", "full-stack"],
            "devops": ["devops", "ci/cd", "deployment", "infrastructure"]
        }
    
    def _load_location_mappings(self) -> Dict[str, List[str]]:
        """Load location synonyms and expansions"""
        return {
            "san francisco": ["san francisco", "sf", "bay area", "silicon valley"],
            "new york": ["new york", "nyc", "manhattan", "brooklyn"],
            "seattle": ["seattle", "bellevue", "redmond", "tacoma"],
            "austin": ["austin", "round rock", "cedar park"],
            "boston": ["boston", "cambridge", "somerville"],
            "remote": ["remote", "work from home", "wfh", "distributed", "anywhere"]
        }
    
    def analyze_user_profile(self, user_profile: Dict) -> Dict[str, Any]:
        """Analyze user profile to understand experience level and preferences"""
        analysis = {
            "experience_level": self._determine_experience_level(user_profile),
            "primary_skills": self._extract_primary_skills(user_profile),
            "secondary_skills": self._extract_secondary_skills(user_profile),
            "career_stage": self._determine_career_stage(user_profile),
            "specializations": self._identify_specializations(user_profile)
        }
        
        return analysis
    
    def _determine_experience_level(self, profile: Dict) -> ExperienceLevel:
        """Determine experience level from profile"""
        years_exp = profile.get("years_experience", 0)
        
        if years_exp <= 2:
            return ExperienceLevel.ENTRY
        elif years_exp <= 5:
            return ExperienceLevel.MID
        elif years_exp <= 10:
            return ExperienceLevel.SENIOR
        elif years_exp <= 15:
            return ExperienceLevel.LEAD
        else:
            return ExperienceLevel.EXECUTIVE
    
    def _extract_primary_skills(self, profile: Dict) -> List[str]:
        """Extract primary skills from profile"""
        technical_skills = profile.get("technical_skills", [])
        frameworks = profile.get("frameworks", [])
        
        # Combine and prioritize by frequency/importance
        all_skills = technical_skills + frameworks
        
        # Simple prioritization - take first 5 as primary
        return all_skills[:5] if all_skills else ["software engineer"]
    
    def _extract_secondary_skills(self, profile: Dict) -> List[str]:
        """Extract secondary/supporting skills"""
        technical_skills = profile.get("technical_skills", [])
        frameworks = profile.get("frameworks", [])
        tools = profile.get("tools", [])
        
        all_skills = technical_skills + frameworks + tools
        
        # Return remaining skills after primary
        return all_skills[5:10] if len(all_skills) > 5 else []
    
    def _determine_career_stage(self, profile: Dict) -> str:
        """Determine career stage for targeted search"""
        years_exp = profile.get("years_experience", 0)
        title = profile.get("title", "").lower()
        
        if "senior" in title or "lead" in title or years_exp >= 7:
            return "senior"
        elif "junior" in title or years_exp <= 2:
            return "junior"
        else:
            return "mid_level"
    
    def _identify_specializations(self, profile: Dict) -> List[str]:
        """Identify technical specializations"""
        specializations = []
        
        skills = profile.get("technical_skills", []) + profile.get("frameworks", [])
        skills_lower = [skill.lower() for skill in skills]
        
        # Check for common specializations
        if any(skill in skills_lower for skill in ["react", "vue", "angular", "html", "css"]):
            specializations.append("frontend")
        
        if any(skill in skills_lower for skill in ["python", "java", "node", "api", "database"]):
            specializations.append("backend")
        
        if any(skill in skills_lower for skill in ["aws", "docker", "kubernetes", "devops"]):
            specializations.append("devops")
        
        if any(skill in skills_lower for skill in ["machine learning", "data science", "ai", "tensorflow"]):
            specializations.append("data_science")
        
        return specializations
    
    def generate_keywords(self, user_profile: Dict, preferences: Dict) -> Tuple[List[str], List[str], List[str]]:
        """Generate primary, secondary, and skill-based keywords"""
        
        # Primary keywords from job titles and preferences
        primary_keywords = []
        
        # Add user's current title variations
        user_title = user_profile.get("title", "")
        if user_title:
            primary_keywords.append(user_title.lower())
        
        # Add preference keywords
        pref_keywords = preferences.get("keywords", [])
        primary_keywords.extend([kw.lower() for kw in pref_keywords])
        
        # Add role-based keywords based on experience
        exp_level = self._determine_experience_level(user_profile)
        if exp_level == ExperienceLevel.ENTRY:
            primary_keywords.extend(["junior developer", "entry level", "associate"])
        elif exp_level == ExperienceLevel.SENIOR:
            primary_keywords.extend(["senior developer", "senior engineer", "tech lead"])
        
        # Secondary keywords from specializations
        specializations = self._identify_specializations(user_profile)
        secondary_keywords = []
        
        for spec in specializations:
            if spec == "frontend":
                secondary_keywords.extend(["frontend developer", "ui developer", "react developer"])
            elif spec == "backend":
                secondary_keywords.extend(["backend developer", "api developer", "server engineer"])
            elif spec == "devops":
                secondary_keywords.extend(["devops engineer", "cloud engineer", "infrastructure"])
        
        # Skill keywords with synonyms
        skill_keywords = []
        user_skills = user_profile.get("technical_skills", []) + user_profile.get("frameworks", [])
        
        for skill in user_skills:
            skill_lower = skill.lower()
            skill_keywords.append(skill_lower)
            
            # Add synonyms
            if skill_lower in self.skill_synonyms:
                skill_keywords.extend(self.skill_synonyms[skill_lower])
        
        # Remove duplicates while preserving order
        primary_keywords = list(dict.fromkeys(primary_keywords))
        secondary_keywords = list(dict.fromkeys(secondary_keywords))
        skill_keywords = list(dict.fromkeys(skill_keywords))
        
        return primary_keywords, secondary_keywords, skill_keywords
    
    def create_constraints(self, user_profile: Dict, preferences: Dict) -> SearchConstraints:
        """Create search constraints based on profile and preferences"""
        
        # Experience constraints
        years_exp = user_profile.get("years_experience", 0)
        exp_level = self._determine_experience_level(user_profile)
        
        constraints = SearchConstraints(
            min_years_experience=max(0, years_exp - 2),
            max_years_experience=years_exp + 5,
            experience_level=[exp_level],
            
            # Salary from preferences
            salary_min=preferences.get("salary_min"),
            salary_max=preferences.get("salary_max"),
            
            # Location preferences
            preferred_locations=preferences.get("locations", ["remote"]),
            work_type=[WorkType(wt) for wt in preferences.get("work_types", ["remote", "hybrid"])],
            willing_to_relocate=preferences.get("willing_to_relocate", False),
            
            # Visa status
            visa_status=VisaStatus(preferences.get("visa_status", "citizen")),
            requires_visa_sponsorship=preferences.get("requires_visa_sponsorship", False),
            
            # Company preferences
            company_size_preference=preferences.get("company_sizes", ["medium", "large"]),
            industry_preferences=preferences.get("industries", []),
            exclude_companies=preferences.get("exclude_companies", []),
            
            # Job characteristics
            job_types=preferences.get("job_types", ["full-time"]),
            seniority_levels=preferences.get("seniority_levels", [])
        )
        
        return constraints
    
    def plan(self, user_profile: Dict, preferences: Dict) -> SearchPlan:
        """Create comprehensive search plan"""
        
        print("Creating search plan based on user profile and preferences...")
        
        # Analyze user profile
        profile_analysis = self.analyze_user_profile(user_profile)
        print(f"Detected experience level: {profile_analysis['experience_level'].value}")
        print(f"Primary skills: {', '.join(profile_analysis['primary_skills'][:3])}")
        
        # Generate keywords
        primary_kw, secondary_kw, skill_kw = self.generate_keywords(user_profile, preferences)
        print(f"Generated {len(primary_kw)} primary keywords, {len(skill_kw)} skill keywords")
        
        # Create constraints
        constraints = self.create_constraints(user_profile, preferences)
        
        # Determine search strategy
        search_priority = preferences.get("search_strategy", "balanced")
        max_results = preferences.get("max_results_per_source", 50)
        
        # Create ranking weights based on user priorities
        ranking_weights = self._calculate_ranking_weights(preferences)
        
        search_plan = SearchPlan(
            primary_keywords=primary_kw,
            secondary_keywords=secondary_kw,
            skill_keywords=skill_kw,
            constraints=constraints,
            search_priority=search_priority,
            max_results_per_source=max_results,
            ranking_weights=ranking_weights
        )
        
        print(f"Search plan created successfully")
        print(f"Primary keywords: {', '.join(primary_kw[:3])}")
        print(f"Salary range: ${constraints.salary_min or 'N/A'} - ${constraints.salary_max or 'N/A'}")
        print(f"Preferred locations: {', '.join(constraints.preferred_locations[:3])}")
        
        return search_plan
    
    def _calculate_ranking_weights(self, preferences: Dict) -> Dict[str, float]:
        """Calculate ranking weights based on user priorities"""
        
        # Default weights
        weights = {
            "skill_match": 0.3,
            "experience_match": 0.2,
            "salary_match": 0.2,
            "location_preference": 0.15,
            "company_preference": 0.15
        }
        
        # Adjust based on user preferences
        user_priorities = preferences.get("priorities", {})
        
        if "salary" in user_priorities.get("top_priority", ""):
            weights["salary_match"] = 0.35
            weights["skill_match"] = 0.25
        
        if "remote" in preferences.get("locations", []):
            weights["location_preference"] = 0.1
            weights["skill_match"] = 0.35
        
        if user_priorities.get("company_culture_important", False):
            weights["company_preference"] = 0.25
            weights["salary_match"] = 0.15
        
        # Ensure weights sum to 1.0
        total = sum(weights.values())
        weights = {k: v/total for k, v in weights.items()}
        
        return weights
    
    def validate_plan(self, search_plan: SearchPlan) -> List[str]:
        """Validate search plan and return any issues"""
        issues = []
        
        if not search_plan.primary_keywords:
            issues.append("No primary keywords defined")
        
        if not search_plan.skill_keywords:
            issues.append("No skill keywords defined")
        
        if search_plan.constraints.salary_min and search_plan.constraints.salary_max:
            if search_plan.constraints.salary_min > search_plan.constraints.salary_max:
                issues.append("Minimum salary is higher than maximum salary")
        
        if not search_plan.constraints.preferred_locations:
            issues.append("No preferred locations specified")
        
        # Check if ranking weights sum to approximately 1.0
        weight_sum = sum(search_plan.ranking_weights.values())
        if abs(weight_sum - 1.0) > 0.01:
            issues.append(f"Ranking weights sum to {weight_sum:.2f}, should be 1.0")
        
        return issues
    
    def save_plan(self, search_plan: SearchPlan, filename: str = "search_plan.json"):
        """Save search plan to file"""
        try:
            plan_dict = {
                "primary_keywords": search_plan.primary_keywords,
                "secondary_keywords": search_plan.secondary_keywords,
                "skill_keywords": search_plan.skill_keywords,
                "constraints": {
                    "min_years_experience": search_plan.constraints.min_years_experience,
                    "max_years_experience": search_plan.constraints.max_years_experience,
                    "experience_level": [level.value for level in search_plan.constraints.experience_level],
                    "salary_min": search_plan.constraints.salary_min,
                    "salary_max": search_plan.constraints.salary_max,
                    "preferred_locations": search_plan.constraints.preferred_locations,
                    "work_type": [wt.value for wt in search_plan.constraints.work_type],
                    "visa_status": search_plan.constraints.visa_status.value,
                    "requires_visa_sponsorship": search_plan.constraints.requires_visa_sponsorship,
                    "company_size_preference": search_plan.constraints.company_size_preference,
                    "industry_preferences": search_plan.constraints.industry_preferences,
                    "job_types": search_plan.constraints.job_types
                },
                "search_priority": search_plan.search_priority,
                "max_results_per_source": search_plan.max_results_per_source,
                "ranking_weights": search_plan.ranking_weights,
                "created_at": search_plan.created_at.isoformat(),
                "valid_until": search_plan.valid_until.isoformat()
            }
            
            with open(filename, 'w') as f:
                json.dump(plan_dict, f, indent=2)
            
            print(f"Search plan saved to {filename}")
            return True
            
        except Exception as e:
            print(f"Error saving search plan: {e}")
            return False

# Interactive interface for testing
def interactive_planner():
    """Interactive interface to create and test search plans"""
    
    print("Job Search Planner")
    print("=" * 50)
    
    planner = PlannerAgent()
    
    # Sample user profile for testing
    sample_profile = {
        "name": "John Doe",
        "title": "Software Engineer",
        "years_experience": 5,
        "technical_skills": ["Python", "JavaScript", "SQL"],
        "frameworks": ["React", "Django", "Flask"],
        "tools": ["Git", "Docker", "AWS"]
    }
    
    # Sample preferences
    sample_preferences = {
        "keywords": ["python developer", "full stack engineer"],
        "locations": ["remote", "san francisco", "seattle"],
        "salary_min": 100000,
        "salary_max": 150000,
        "work_types": ["remote", "hybrid"],
        "company_sizes": ["medium", "large"],
        "search_strategy": "balanced"
    }
    
    while True:
        print("\nOptions:")
        print("1. Create search plan with sample data")
        print("2. Create custom search plan")  
        print("3. Validate existing plan")
        print("4. View sample profile and preferences")
        print("5. Exit")
        
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == "1":
            print("\nCreating search plan with sample data...")
            search_plan = planner.plan(sample_profile, sample_preferences)
            
            print(f"\nSearch Plan Summary:")
            print(f"Primary Keywords: {', '.join(search_plan.primary_keywords[:5])}")
            print(f"Skill Keywords: {', '.join(search_plan.skill_keywords[:5])}")
            print(f"Salary Range: ${search_plan.constraints.salary_min} - ${search_plan.constraints.salary_max}")
            print(f"Locations: {', '.join(search_plan.constraints.preferred_locations)}")
            print(f"Experience Level: {search_plan.constraints.experience_level[0].value}")
            
            # Validate plan
            issues = planner.validate_plan(search_plan)
            if issues:
                print(f"\nValidation Issues:")
                for issue in issues:
                    print(f"  - {issue}")
            else:
                print(f"\nSearch plan validation passed!")
            
            # Save option
            save = input(f"\nSave this plan? (y/n): ").strip().lower()
            if save == 'y':
                planner.save_plan(search_plan)
        
        elif choice == "2":
            print("\nCustom search plan creation...")
            print("This would involve collecting user input for profile and preferences")
            print("For now, please modify the sample data in the code")
        
        elif choice == "3":
            filename = input("\nEnter search plan filename (default: search_plan.json): ").strip()
            filename = filename or "search_plan.json"
            
            if os.path.exists(filename):
                print(f"Plan validation would be implemented here")
            else:
                print("File not found")
        
        elif choice == "4":
            print(f"\nSample Profile:")
            print(json.dumps(sample_profile, indent=2))
            print(f"\nSample Preferences:")
            print(json.dumps(sample_preferences, indent=2))
        
        elif choice == "5":
            print("Thank you for using the Job Search Planner!")
            break
        
        else:
            print("Invalid choice. Please select 1-5.")

if __name__ == "__main__":
    interactive_planner()