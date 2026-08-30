from pydantic import BaseModel

class Personal(BaseModel):
    name: str
    role: str
    location: str
    email: str
    linkedin: str
    github: str
    portfolio: str


class Education(BaseModel):
    institution: str
    degree: str
    location: str
    period: str
    highlights: list[str]

class Skills(BaseModel):
    frontend: list[str]
    backend: list[str]
    database: list[str]
    caching: list[str]
    ai: list[str]
    devops: list[str]
    security: list[str]
    languages: list[str]




class Experience(BaseModel):
    company: str
    role: str
    type: str
    period: str
    responsibilities: list[str]


class Project(BaseModel):
    name: str
    type: str
    description: str
    technologies: list[str]
    highlights: list[str]
    github: str
    live: str



class GithubProfile(BaseModel):
    username: str
    profile_url: str
    public_repositories: int
    followers: int
    following: int

    current_focus: list[str]
    professional_focus: list[str]
    open_to: list[str]

    engineering_depth: dict[str, str]
    impact_metrics: dict[str, str | int]

    goals_2026: list[str]


class AdditionalInformation(BaseModel):
    working_habits: list[str]
    learning_and_problem_solving: list[str]


class Candidate(BaseModel):
    personal: Personal
    summary: str
    education: list[Education]
    skills: Skills
    experience: list[Experience]
    projects: list[Project]
    achievements: list[str]
    additional_information: AdditionalInformation
    certifications: list[str]
    github_profile: GithubProfile