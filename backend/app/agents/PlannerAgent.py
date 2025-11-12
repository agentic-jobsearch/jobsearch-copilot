import os
import json
import asyncio
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from dotenv import load_dotenv
import threading
import time

load_dotenv()

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskType(Enum):
    PROFILE_SETUP = "profile_setup"
    JOB_SEARCH = "job_search"
    RESUME_CREATION = "resume_creation"
    COVER_LETTER = "cover_letter"
    APPLICATION_PREP = "application_prep"
    INTERVIEW_PREP = "interview_prep"
    FOLLOW_UP = "follow_up"

class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class Task:
    """Represents a task in the job search workflow"""
    task_id: str
    task_type: TaskType
    description: str
    agent_assigned: str
    status: TaskStatus = TaskStatus.PENDING
    priority: Priority = Priority.MEDIUM
    
    # Dependencies
    depends_on: List[str] = None
    blocks: List[str] = None
    
    # Execution details
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_duration: timedelta = None
    
    # Data
    input_data: Dict[str, Any] = None
    output_data: Dict[str, Any] = None
    error_message: str = ""
    
    # Progress tracking
    progress_percentage: int = 0
    
    def __post_init__(self):
        if self.depends_on is None:
            self.depends_on = []
        if self.blocks is None:
            self.blocks = []
        if self.input_data is None:
            self.input_data = {}
        if self.output_data is None:
            self.output_data = {}
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class WorkflowPlan:
    """Complete workflow plan for job search process"""
    plan_id: str
    user_goal: str
    tasks: List[Task]
    dependencies_graph: Dict[str, List[str]]
    estimated_completion: datetime
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

class AgentInterface:
    """Base interface for all agents"""
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.status = "ready"
        self.current_task = None
    
    def execute_task(self, task: Task) -> Dict[str, Any]:
        """Execute a task and return results"""
        raise NotImplementedError("Subclasses must implement execute_task")
    
    def get_capabilities(self) -> List[str]:
        """Return list of capabilities this agent supports"""
        raise NotImplementedError("Subclasses must implement get_capabilities")

class PlannerAgent:
    """Central orchestrator for the job search system"""
    
    def __init__(self):
        self.agents = {}
        self.active_workflows = {}
        self.completed_workflows = {}
        self.task_queue = []
        self.running = False
        
        # Initialize agent registry
        self._register_agents()
        
        # Workflow templates
        self.workflow_templates = self._load_workflow_templates()
        
        print("PlannerAgent initialized successfully")
        print(f"Registered agents: {list(self.agents.keys())}")
    
    def _register_agents(self):
        """Register available agents in the system"""
        # Mock agent registrations - in real implementation, these would be actual agent instances
        self.agents = {
            "resume_parser": {
                "class": "ResumeParser",
                "capabilities": ["parse_pdf", "parse_docx", "extract_profile"],
                "status": "ready"
            },
            "job_scout": {
                "class": "JobScoutAgent", 
                "capabilities": ["search_jobs", "filter_jobs", "rank_jobs"],
                "status": "ready"
            },
            "writer": {
                "class": "WriterAgent",
                "capabilities": ["create_resume", "create_cover_letter", "tailor_content"],
                "status": "ready"
            },
            "qa_agent": {
                "class": "QAAgent",
                "capabilities": ["answer_questions", "job_analysis", "interview_prep"],
                "status": "ready"
            },
            "application_tracker": {
                "class": "ApplicationTracker",
                "capabilities": ["track_applications", "follow_up_reminders", "status_updates"],
                "status": "ready"
            }
        }
    
    def _load_workflow_templates(self) -> Dict[str, List[Dict]]:
        """Load predefined workflow templates"""
        return {
            "first_time_job_search": [
                {"type": "profile_setup", "agent": "resume_parser", "description": "Set up user profile"},
                {"type": "job_search", "agent": "job_scout", "description": "Find matching jobs", "depends_on": ["profile_setup"]},
                {"type": "resume_creation", "agent": "writer", "description": "Create tailored resumes", "depends_on": ["job_search"]},
                {"type": "application_prep", "agent": "writer", "description": "Prepare application materials", "depends_on": ["resume_creation"]}
            ],
            
            "experienced_job_search": [
                {"type": "job_search", "agent": "job_scout", "description": "Advanced job search"},
                {"type": "resume_creation", "agent": "writer", "description": "Update existing resume"},
                {"type": "application_prep", "agent": "writer", "description": "Prepare targeted applications"}
            ],
            
            "single_application": [
                {"type": "resume_creation", "agent": "writer", "description": "Create resume for specific job"},
                {"type": "cover_letter", "agent": "writer", "description": "Create cover letter"}
            ],
            
            "interview_preparation": [
                {"type": "interview_prep", "agent": "qa_agent", "description": "Prepare for interviews"},
                {"type": "follow_up", "agent": "application_tracker", "description": "Schedule follow-ups"}
            ]
        }
    
    def understand_user_goal(self, user_input: str, context: Dict = None) -> Dict[str, Any]:
        """Parse and understand user's goal using AI"""
        
        understanding_prompt = f"""
        Analyze this user request and determine their job search goal:
        
        User Input: "{user_input}"
        Context: {json.dumps(context or {}, indent=2)}
        
        Return JSON with:
        {{
            "primary_goal": "main objective",
            "goal_type": "first_time_search|experienced_search|single_application|interview_prep|profile_update",
            "urgency": "low|medium|high|critical",
            "specific_requirements": ["requirement1", "requirement2"],
            "missing_information": ["what info is needed"],
            "recommended_workflow": "workflow_template_name",
            "estimated_time": "time estimate",
            "success_criteria": ["how to measure success"]
        }}
        """
        
        try:
            from openai import OpenAI
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": understanding_prompt}],
                temperature=0.1
            )
            
            understanding = json.loads(response.choices[0].message.content)
            print(f"Understood goal: {understanding['primary_goal']}")
            print(f"Recommended workflow: {understanding['recommended_workflow']}")
            
            return understanding
            
        except Exception as e:
            print(f"Error understanding user goal: {e}")
            return {
                "primary_goal": user_input,
                "goal_type": "experienced_search",
                "urgency": "medium",
                "recommended_workflow": "experienced_job_search"
            }
    
    def decompose_goal_into_tasks(self, goal_understanding: Dict, user_data: Dict = None) -> List[Task]:
        """Break down the goal into specific tasks"""
        
        workflow_name = goal_understanding.get("recommended_workflow", "experienced_job_search")
        template = self.workflow_templates.get(workflow_name, self.workflow_templates["experienced_job_search"])
        
        tasks = []
        
        for i, task_template in enumerate(template):
            task_id = f"{workflow_name}_{i+1}"
            
            task = Task(
                task_id=task_id,
                task_type=TaskType(task_template["type"]),
                description=task_template["description"],
                agent_assigned=task_template["agent"],
                depends_on=task_template.get("depends_on", []),
                priority=Priority.HIGH if goal_understanding.get("urgency") == "high" else Priority.MEDIUM,
                input_data=user_data or {}
            )
            
            # Set estimated duration based on task type
            duration_map = {
                TaskType.PROFILE_SETUP: timedelta(minutes=10),
                TaskType.JOB_SEARCH: timedelta(minutes=15),
                TaskType.RESUME_CREATION: timedelta(minutes=5),
                TaskType.COVER_LETTER: timedelta(minutes=3),
                TaskType.APPLICATION_PREP: timedelta(minutes=8),
                TaskType.INTERVIEW_PREP: timedelta(minutes=20),
                TaskType.FOLLOW_UP: timedelta(minutes=2)
            }
            
            task.estimated_duration = duration_map.get(task.task_type, timedelta(minutes=10))
            
            tasks.append(task)
        
        print(f"Created {len(tasks)} tasks for workflow: {workflow_name}")
        return tasks
    
    def create_workflow_plan(self, user_input: str, user_data: Dict = None) -> WorkflowPlan:
        """Create a complete workflow plan"""
        
        print(f"Creating workflow plan for: {user_input}")
        
        # Understand the goal
        goal_understanding = self.understand_user_goal(user_input, user_data)
        
        # Decompose into tasks
        tasks = self.decompose_goal_into_tasks(goal_understanding, user_data)
        
        # Build dependency graph
        dependencies = {}
        for task in tasks:
            dependencies[task.task_id] = task.depends_on
        
        # Calculate estimated completion time
        total_duration = sum([task.estimated_duration for task in tasks], timedelta())
        estimated_completion = datetime.now() + total_duration
        
        plan = WorkflowPlan(
            plan_id=f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            user_goal=goal_understanding["primary_goal"],
            tasks=tasks,
            dependencies_graph=dependencies,
            estimated_completion=estimated_completion
        )
        
        print(f"Workflow plan created with {len(tasks)} tasks")
        print(f"Estimated completion: {estimated_completion.strftime('%H:%M:%S')}")
        
        return plan
    
    def execute_workflow(self, workflow_plan: WorkflowPlan) -> Dict[str, Any]:
        """Execute the workflow plan"""
        
        print(f"Starting workflow execution: {workflow_plan.plan_id}")
        
        self.active_workflows[workflow_plan.plan_id] = workflow_plan
        execution_results = {
            "workflow_id": workflow_plan.plan_id,
            "status": "running",
            "completed_tasks": [],
            "failed_tasks": [],
            "current_task": None,
            "progress_percentage": 0,
            "started_at": datetime.now()
        }
        
        try:
            # Execute tasks in dependency order
            completed_task_ids = set()
            
            while len(completed_task_ids) < len(workflow_plan.tasks):
                # Find next executable task
                next_task = self._find_next_executable_task(workflow_plan.tasks, completed_task_ids)
                
                if not next_task:
                    print("No more executable tasks found. Checking for circular dependencies...")
                    break
                
                # Execute the task
                print(f"Executing task: {next_task.description}")
                execution_results["current_task"] = next_task.task_id
                
                task_result = self._execute_single_task(next_task)
                
                if task_result["status"] == "success":
                    next_task.status = TaskStatus.COMPLETED
                    next_task.completed_at = datetime.now()
                    next_task.output_data = task_result["data"]
                    completed_task_ids.add(next_task.task_id)
                    execution_results["completed_tasks"].append(next_task.task_id)
                    
                    print(f"Task completed successfully: {next_task.description}")
                else:
                    next_task.status = TaskStatus.FAILED
                    next_task.error_message = task_result.get("error", "Unknown error")
                    execution_results["failed_tasks"].append(next_task.task_id)
                    
                    print(f"Task failed: {next_task.description} - {next_task.error_message}")
                
                # Update progress
                progress = (len(completed_task_ids) / len(workflow_plan.tasks)) * 100
                execution_results["progress_percentage"] = int(progress)
            
            # Final status
            if len(execution_results["failed_tasks"]) == 0:
                execution_results["status"] = "completed"
                execution_results["message"] = "All tasks completed successfully"
            else:
                execution_results["status"] = "partially_completed"
                execution_results["message"] = f"{len(execution_results['failed_tasks'])} tasks failed"
            
            execution_results["completed_at"] = datetime.now()
            
            # Move to completed workflows
            self.completed_workflows[workflow_plan.plan_id] = workflow_plan
            if workflow_plan.plan_id in self.active_workflows:
                del self.active_workflows[workflow_plan.plan_id]
            
            print(f"Workflow execution completed: {execution_results['status']}")
            
        except Exception as e:
            execution_results["status"] = "failed"
            execution_results["error"] = str(e)
            print(f"Workflow execution failed: {e}")
        
        return execution_results
    
    def _find_next_executable_task(self, tasks: List[Task], completed_task_ids: set) -> Optional[Task]:
        """Find the next task that can be executed"""
        
        for task in tasks:
            # Skip if already completed or failed
            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                continue
            
            # Check if all dependencies are completed
            dependencies_met = all(dep_id in completed_task_ids for dep_id in task.depends_on)
            
            if dependencies_met:
                return task
        
        return None
    
    def _execute_single_task(self, task: Task) -> Dict[str, Any]:
        """Execute a single task using the appropriate agent"""
        
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.now()
        
        try:
            agent_name = task.agent_assigned
            
            if agent_name not in self.agents:
                return {"status": "error", "error": f"Agent {agent_name} not found"}
            
            # Simulate task execution (in real implementation, call actual agent)
            print(f"Executing {task.task_type.value} with {agent_name}")
            
            # Mock execution based on task type
            if task.task_type == TaskType.PROFILE_SETUP:
                result = self._mock_profile_setup(task)
            elif task.task_type == TaskType.JOB_SEARCH:
                result = self._mock_job_search(task)
            elif task.task_type == TaskType.RESUME_CREATION:
                result = self._mock_resume_creation(task)
            elif task.task_type == TaskType.COVER_LETTER:
                result = self._mock_cover_letter(task)
            else:
                result = {"status": "success", "data": {"message": f"Task {task.task_type.value} completed"}}
            
            # Simulate processing time
            time.sleep(0.5)
            
            return result
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _mock_profile_setup(self, task: Task) -> Dict[str, Any]:
        """Mock profile setup execution"""
        return {
            "status": "success",
            "data": {
                "profile_created": True,
                "profile_id": "user_123",
                "skills_extracted": ["Python", "JavaScript", "React"],
                "experience_level": "mid"
            }
        }
    
    def _mock_job_search(self, task: Task) -> Dict[str, Any]:
        """Mock job search execution"""
        return {
            "status": "success",
            "data": {
                "jobs_found": 25,
                "top_matches": ["job_1", "job_2", "job_3"],
                "search_completed": True
            }
        }
    
    def _mock_resume_creation(self, task: Task) -> Dict[str, Any]:
        """Mock resume creation execution"""
        return {
            "status": "success",
            "data": {
                "resume_created": True,
                "resume_path": "resume_company_20231201.md",
                "tailored_for": "Software Engineer role"
            }
        }
    
    def _mock_cover_letter(self, task: Task) -> Dict[str, Any]:
        """Mock cover letter creation"""
        return {
            "status": "success", 
            "data": {
                "cover_letter_created": True,
                "cover_letter_path": "cover_letter_company_20231201.md"
            }
        }
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get current status of a workflow"""
        
        if workflow_id in self.active_workflows:
            workflow = self.active_workflows[workflow_id]
            status = "active"
        elif workflow_id in self.completed_workflows:
            workflow = self.completed_workflows[workflow_id]
            status = "completed"
        else:
            return {"error": "Workflow not found"}
        
        # Calculate progress
        total_tasks = len(workflow.tasks)
        completed_tasks = len([t for t in workflow.tasks if t.status == TaskStatus.COMPLETED])
        failed_tasks = len([t for t in workflow.tasks if t.status == TaskStatus.FAILED])
        
        return {
            "workflow_id": workflow_id,
            "status": status,
            "progress": {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "failed_tasks": failed_tasks,
                "percentage": int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0
            },
            "estimated_completion": workflow.estimated_completion.isoformat(),
            "tasks": [
                {
                    "id": task.task_id,
                    "description": task.description,
                    "status": task.status.value,
                    "agent": task.agent_assigned,
                    "progress": task.progress_percentage
                }
                for task in workflow.tasks
            ]
        }
    
    def combine_results(self, workflow_id: str) -> Dict[str, Any]:
        """Combine results from all tasks into final coherent output"""
        
        if workflow_id not in self.completed_workflows:
            return {"error": "Workflow not completed yet"}
        
        workflow = self.completed_workflows[workflow_id]
        
        # Collect all successful task outputs
        successful_outputs = []
        for task in workflow.tasks:
            if task.status == TaskStatus.COMPLETED and task.output_data:
                successful_outputs.append({
                    "task_type": task.task_type.value,
                    "description": task.description,
                    "output": task.output_data
                })
        
        # Create comprehensive summary
        final_result = {
            "workflow_id": workflow_id,
            "user_goal": workflow.user_goal,
            "status": "completed",
            "summary": f"Successfully completed {len(successful_outputs)} out of {len(workflow.tasks)} tasks",
            "deliverables": self._extract_deliverables(successful_outputs),
            "next_steps": self._generate_next_steps(successful_outputs),
            "task_results": successful_outputs,
            "completion_time": datetime.now().isoformat()
        }
        
        return final_result
    
    def _extract_deliverables(self, outputs: List[Dict]) -> List[str]:
        """Extract deliverable files and results"""
        deliverables = []
        
        for output in outputs:
            if output["task_type"] == "resume_creation":
                if "resume_path" in output["output"]:
                    deliverables.append(f"Resume: {output['output']['resume_path']}")
            
            elif output["task_type"] == "cover_letter":
                if "cover_letter_path" in output["output"]:
                    deliverables.append(f"Cover Letter: {output['output']['cover_letter_path']}")
            
            elif output["task_type"] == "job_search":
                if "jobs_found" in output["output"]:
                    deliverables.append(f"Job Search Results: {output['output']['jobs_found']} opportunities found")
        
        return deliverables
    
    def _generate_next_steps(self, outputs: List[Dict]) -> List[str]:
        """Generate recommended next steps based on completed tasks"""
        next_steps = []
        
        # Check what was accomplished
        has_job_search = any(o["task_type"] == "job_search" for o in outputs)
        has_resume = any(o["task_type"] == "resume_creation" for o in outputs)
        has_cover_letter = any(o["task_type"] == "cover_letter" for o in outputs)
        
        if has_job_search and has_resume:
            next_steps.append("Review and customize resumes for top job matches")
            next_steps.append("Begin submitting applications to priority companies")
        
        if has_resume or has_cover_letter:
            next_steps.append("Proofread all application materials")
            next_steps.append("Set up application tracking system")
        
        next_steps.append("Schedule follow-up reminders for submitted applications")
        next_steps.append("Prepare for potential interview opportunities")
        
        return next_steps

# Interactive interface for testing
def interactive_planner():
    """Interactive interface to test the PlannerAgent"""
    
    print("Job Search Orchestrator - PlannerAgent")
    print("=" * 60)
    
    planner = PlannerAgent()
    
    while True:
        print("\nWhat would you like to do?")
        print("1. Plan a complete job search workflow")
        print("2. Execute a workflow")
        print("3. Check workflow status")
        print("4. View completed workflows")
        print("5. Test goal understanding")
        print("6. Exit")
        
        choice = input("\nEnter choice (1-6): ").strip()
        
        if choice == "1":
            user_goal = input("\nDescribe what you want to accomplish: ").strip()
            
            if user_goal:
                # Create workflow plan
                workflow_plan = planner.create_workflow_plan(user_goal)
                
                print(f"\nWorkflow Plan Created:")
                print(f"Plan ID: {workflow_plan.plan_id}")
                print(f"Goal: {workflow_plan.user_goal}")
                print(f"Total Tasks: {len(workflow_plan.tasks)}")
                print(f"Estimated Completion: {workflow_plan.estimated_completion.strftime('%H:%M:%S')}")
                
                print(f"\nTask Breakdown:")
                for task in workflow_plan.tasks:
                    deps = f" (depends on: {', '.join(task.depends_on)})" if task.depends_on else ""
                    print(f"  - {task.description} [{task.agent_assigned}]{deps}")
                
                # Ask if user wants to execute
                execute = input(f"\nExecute this workflow now? (y/n): ").strip().lower()
                if execute == 'y':
                    print(f"\nExecuting workflow...")
                    result = planner.execute_workflow(workflow_plan)
                    
                    print(f"\nExecution Results:")
                    print(f"Status: {result['status']}")
                    print(f"Progress: {result['progress_percentage']}%")
                    print(f"Completed Tasks: {len(result['completed_tasks'])}")
                    print(f"Failed Tasks: {len(result['failed_tasks'])}")
                    
                    if result['status'] in ['completed', 'partially_completed']:
                        # Show final results
                        final_results = planner.combine_results(workflow_plan.plan_id)
                        print(f"\nFinal Results:")
                        print(f"Summary: {final_results['summary']}")
                        print(f"Deliverables: {', '.join(final_results['deliverables'])}")
                        print(f"Next Steps: {final_results['next_steps'][0] if final_results['next_steps'] else 'None'}")
        
        elif choice == "2":
            workflow_id = input("\nEnter workflow ID to execute: ").strip()
            if workflow_id in planner.active_workflows:
                result = planner.execute_workflow(planner.active_workflows[workflow_id])
                print(f"Execution completed: {result['status']}")
            else:
                print("Workflow not found or already completed")
        
        elif choice == "3":
            workflow_id = input("\nEnter workflow ID to check: ").strip()
            status = planner.get_workflow_status(workflow_id)
            
            if "error" not in status:
                print(f"\nWorkflow Status:")
                print(f"Status: {status['status']}")
                print(f"Progress: {status['progress']['percentage']}%")
                print(f"Tasks: {status['progress']['completed_tasks']}/{status['progress']['total_tasks']} completed")
                
                print(f"\nTask Details:")
                for task in status['tasks']:
                    print(f"  - {task['description']}: {task['status']}")
            else:
                print(f"Error: {status['error']}")
        
        elif choice == "4":
            if planner.completed_workflows:
                print(f"\nCompleted Workflows:")
                for wf_id, workflow in planner.completed_workflows.items():
                    print(f"  - {wf_id}: {workflow.user_goal}")
            else:
                print("No completed workflows found")
        
        elif choice == "5":
            test_input = input("\nEnter a goal to test understanding: ").strip()
            understanding = planner.understand_user_goal(test_input)
            print(f"\nGoal Understanding:")
            print(json.dumps(understanding, indent=2))
        
        elif choice == "6":
            print("Thank you for using the Job Search Orchestrator!")
            break
        
        else:
            print("Invalid choice. Please select 1-6.")

if __name__ == "__main__":
    interactive_planner()