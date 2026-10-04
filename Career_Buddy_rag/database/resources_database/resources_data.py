"""Curated learning resources and platforms."""

LEARNING_PLATFORMS = {
    "free": [
        {
            "name": "freeCodeCamp",
            "url": "https://www.freecodecamp.org",
            "type": "Interactive Coding",
            "best_for": ["Web Development", "JavaScript", "Python", "Data Science"],
            "description": "Free coding bootcamp with certifications. 3000+ hours of curriculum.",
        },
        {
            "name": "The Odin Project",
            "url": "https://www.theodinproject.com",
            "type": "Full Curriculum",
            "best_for": ["Full Stack Development", "Ruby on Rails", "JavaScript"],
            "description": "Complete full-stack curriculum with real projects.",
        },
        {
            "name": "CS50 (Harvard)",
            "url": "https://cs50.harvard.edu",
            "type": "University Course",
            "best_for": ["Computer Science Fundamentals", "Programming Basics"],
            "description": "Harvard's famous intro to CS course. Covers C, Python, SQL, HTML/CSS, JS.",
        },
        {
            "name": "Khan Academy",
            "url": "https://www.khanacademy.org/computing",
            "type": "Interactive",
            "best_for": ["Programming Basics", "Algorithms", "SQL"],
            "description": "Free courses with interactive exercises and videos.",
        },
        {
            "name": "MIT OpenCourseWare",
            "url": "https://ocw.mit.edu",
            "type": "University Course",
            "best_for": ["Computer Science", "Mathematics", "AI/ML"],
            "description": "Free MIT course materials including lectures and assignments.",
        },
        {
            "name": "Full Stack Open",
            "url": "https://fullstackopen.com",
            "type": "University Course",
            "best_for": ["React", "Node.js", "Full Stack JavaScript"],
            "description": "University of Helsinki's full stack web development course.",
        },
        {
            "name": "Kaggle Learn",
            "url": "https://www.kaggle.com/learn",
            "type": "Micro-courses",
            "best_for": ["Data Science", "Machine Learning", "Python", "SQL"],
            "description": "Free micro-courses with hands-on notebooks and competitions.",
        },
        {
            "name": "Google Digital Garage",
            "url": "https://learndigital.withgoogle.com/digitalgarage",
            "type": "Courses",
            "best_for": ["Digital Marketing", "Career Development", "Data"],
            "description": "Free Google courses with certifications.",
        },
    ],
    "paid": [
        {
            "name": "Udemy",
            "url": "https://www.udemy.com",
            "type": "Course Platform",
            "price_range": "₹399-₹3,999 (sale prices)",
            "best_for": ["Any tech skill", "Practical projects"],
            "description": "Huge course library. Wait for sales - courses go to ₹399.",
        },
        {
            "name": "Coursera",
            "url": "https://www.coursera.org",
            "type": "University Courses",
            "price_range": "$39-$79/month or free audit",
            "best_for": ["Data Science", "AI/ML", "Cloud", "University certificates"],
            "description": "University-level courses from Google, IBM, Stanford etc. Financial aid available.",
        },
        {
            "name": "Pluralsight",
            "url": "https://www.pluralsight.com",
            "type": "Tech Skills",
            "price_range": "$29/month",
            "best_for": ["Cloud", "DevOps", "Software Development"],
            "description": "In-depth tech courses with skill assessments.",
        },
        {
            "name": "Educative.io",
            "url": "https://www.educative.io",
            "type": "Interactive",
            "price_range": "$18/month",
            "best_for": ["System Design", "Coding Interviews", "Programming"],
            "description": "Text-based interactive courses. Great for interview prep.",
        },
    ],
    "practice": [
        {
            "name": "LeetCode",
            "url": "https://leetcode.com",
            "type": "Coding Problems",
            "best_for": ["DSA", "Coding Interviews", "Problem Solving"],
            "description": "2000+ coding problems. Essential for tech interviews.",
        },
        {
            "name": "HackerRank",
            "url": "https://www.hackerrank.com",
            "type": "Coding & Certifications",
            "best_for": ["Coding Practice", "Skill Certifications", "Company Tests"],
            "description": "Practice coding with skill-based certifications.",
        },
        {
            "name": "Frontend Mentor",
            "url": "https://www.frontendmentor.io",
            "type": "Project Challenges",
            "best_for": ["Frontend Development", "CSS", "JavaScript"],
            "description": "Real-world frontend challenges with design files.",
        },
        {
            "name": "Exercism",
            "url": "https://exercism.org",
            "type": "Mentored Practice",
            "best_for": ["Learning New Languages", "Code Review"],
            "description": "Free code practice in 65+ languages with mentorship.",
        },
        {
            "name": "Project Euler",
            "url": "https://projecteuler.net",
            "type": "Math + Programming",
            "best_for": ["Mathematics", "Algorithms", "Problem Solving"],
            "description": "Mathematical/computational problems for coders.",
        },
    ],
}

YOUTUBE_CHANNELS = {
    "programming_general": [
        {"name": "freeCodeCamp", "url": "https://www.youtube.com/@freecodecamp", "subscribers": "9M+", "language": "English", "best_for": "Full courses on any topic"},
        {"name": "Fireship", "url": "https://www.youtube.com/@Fireship", "subscribers": "3M+", "language": "English", "best_for": "Quick tech explanations, 100 seconds series"},
        {"name": "Traversy Media", "url": "https://www.youtube.com/@TraversyMedia", "subscribers": "2M+", "language": "English", "best_for": "Web development crash courses"},
        {"name": "The Net Ninja", "url": "https://www.youtube.com/@NetNinja", "subscribers": "1.3M+", "language": "English", "best_for": "Step-by-step web dev tutorials"},
        {"name": "Programming with Mosh", "url": "https://www.youtube.com/@programmingwithmosh", "subscribers": "4M+", "language": "English", "best_for": "Beginner-friendly programming"},
    ],
    "hindi": [
        {"name": "CodeWithHarry", "url": "https://www.youtube.com/@CodeWithHarry", "subscribers": "18M+", "language": "Hindi", "best_for": "Programming in Hindi, DSA, Web Dev"},
        {"name": "Apna College", "url": "https://www.youtube.com/@ApnaCollegeOfficial", "subscribers": "7M+", "language": "Hindi", "best_for": "DSA, Java, Web Development"},
        {"name": "Chai aur Code", "url": "https://www.youtube.com/@chaborcode", "subscribers": "700K+", "language": "Hindi", "best_for": "JavaScript, React, Backend"},
        {"name": "Love Babbar", "url": "https://www.youtube.com/@LoveBabbar", "subscribers": "1.5M+", "language": "Hindi", "best_for": "DSA, CP, Placement prep"},
        {"name": "Telusko", "url": "https://www.youtube.com/@Telusko", "subscribers": "2M+", "language": "English/Hindi", "best_for": "Java, Spring Boot, Python"},
        {"name": "Kunal Kushwaha", "url": "https://www.youtube.com/@KunalKushwaha", "subscribers": "900K+", "language": "English/Hindi", "best_for": "DevOps, DSA, Open Source"},
    ],
    "data_science_ml": [
        {"name": "3Blue1Brown", "url": "https://www.youtube.com/@3blue1brown", "subscribers": "6M+", "language": "English", "best_for": "Math visualization, Linear Algebra, Neural Networks"},
        {"name": "Sentdex", "url": "https://www.youtube.com/@sentdex", "subscribers": "1.3M+", "language": "English", "best_for": "Python, ML, Deep Learning"},
        {"name": "StatQuest", "url": "https://www.youtube.com/@statquest", "subscribers": "1.2M+", "language": "English", "best_for": "Statistics, ML concepts explained simply"},
        {"name": "Krish Naik", "url": "https://www.youtube.com/@krishnaik06", "subscribers": "1M+", "language": "English/Hindi", "best_for": "Data Science, ML, End-to-end projects"},
        {"name": "CampusX", "url": "https://www.youtube.com/@campusx-official", "subscribers": "600K+", "language": "Hindi", "best_for": "Data Science, ML complete courses"},
    ],
    "devops_cloud": [
        {"name": "TechWorld with Nana", "url": "https://www.youtube.com/@TechWorldwithNana", "subscribers": "1.2M+", "language": "English", "best_for": "DevOps, Docker, Kubernetes, AWS"},
        {"name": "NetworkChuck", "url": "https://www.youtube.com/@NetworkChuck", "subscribers": "3.8M+", "language": "English", "best_for": "Networking, Cloud, Cybersecurity"},
        {"name": "KodeKloud", "url": "https://www.youtube.com/@KodeKloud", "subscribers": "400K+", "language": "English", "best_for": "DevOps, Kubernetes, Terraform"},
        {"name": "Abhishek Veeramalla", "url": "https://www.youtube.com/@AbhishekVeeramalla", "subscribers": "500K+", "language": "English/Hindi", "best_for": "DevOps, AWS, Kubernetes"},
    ],
    "career_guidance": [
        {"name": "Coder's Gyan", "url": "https://www.youtube.com/@CodersGyan", "subscribers": "200K+", "language": "Hindi", "best_for": "Career advice, Web Dev"},
        {"name": "Anuj Bhaiya", "url": "https://www.youtube.com/@AnujBhaiya", "subscribers": "800K+", "language": "Hindi", "best_for": "DSA, Career roadmaps"},
        {"name": "Harkirat Singh", "url": "https://www.youtube.com/@haraborat", "subscribers": "1M+", "language": "English/Hindi", "best_for": "Full stack, Freelancing, Career"},
    ],
}

INTERVIEW_RESOURCES = {
    "dsa": [
        {"title": "NeetCode Roadmap", "url": "https://neetcode.io/roadmap", "description": "Curated 150 LeetCode problems with video solutions"},
        {"title": "Striver's SDE Sheet", "url": "https://takeuforward.org/interviews/strivers-sde-sheet-top-coding-interview-problems/", "description": "180 must-do DSA problems for interviews"},
        {"title": "Blind 75", "url": "https://leetcode.com/discuss/general-discussion/460599/blind-75-leetcode-questions", "description": "75 essential LeetCode problems"},
    ],
    "system_design": [
        {"title": "System Design Primer (GitHub)", "url": "https://github.com/donnemartin/system-design-primer", "description": "Comprehensive system design guide"},
        {"title": "Gaurav Sen YouTube", "url": "https://www.youtube.com/@gaborsen", "description": "System design concepts explained well"},
        {"title": "Alex Xu - System Design Interview", "url": "https://www.amazon.com/System-Design-Interview-insiders-Second/dp/B08CMF2CQF", "description": "Popular system design book"},
    ],
    "behavioral": [
        {"title": "STAR Method Guide", "url": "https://www.themuse.com/advice/star-interview-method", "description": "Framework for behavioral interview answers"},
        {"title": "Top 50 Behavioral Questions", "url": "https://www.glassdoor.com/blog/common-interview-questions/", "description": "Most common behavioral questions"},
    ],
}

COMMUNITIES = [
    {"name": "r/cscareerquestions", "url": "https://reddit.com/r/cscareerquestions", "platform": "Reddit", "description": "Career advice for CS professionals"},
    {"name": "r/learnprogramming", "url": "https://reddit.com/r/learnprogramming", "platform": "Reddit", "description": "Help for beginners learning to code"},
    {"name": "Dev.to", "url": "https://dev.to", "platform": "Website", "description": "Developer community for sharing knowledge"},
    {"name": "Hashnode", "url": "https://hashnode.com", "platform": "Website", "description": "Blogging platform for developers"},
    {"name": "Discord - Reactiflux", "url": "https://discord.gg/reactiflux", "platform": "Discord", "description": "Largest React community"},
    {"name": "Discord - Python", "url": "https://discord.gg/python", "platform": "Discord", "description": "Python community"},
    {"name": "Stack Overflow", "url": "https://stackoverflow.com", "platform": "Website", "description": "Q&A for programmers"},
]


def get_all_platforms():
    return LEARNING_PLATFORMS


def get_youtube_channels(category=None):
    if category:
        return YOUTUBE_CHANNELS.get(category, [])
    return YOUTUBE_CHANNELS


def get_interview_resources():
    return INTERVIEW_RESOURCES


def get_communities():
    return COMMUNITIES


def search_resources(query):
    """Search across all resources."""
    query_lower = query.lower()
    results = []

    # Search platforms
    for category, platforms in LEARNING_PLATFORMS.items():
        for platform in platforms:
            searchable = f"{platform['name']} {' '.join(platform['best_for'])} {platform['description']}".lower()
            if query_lower in searchable:
                results.append({**platform, "source": f"Platform ({category})"})

    # Search YouTube channels
    for category, channels in YOUTUBE_CHANNELS.items():
        for channel in channels:
            searchable = f"{channel['name']} {channel['best_for']}".lower()
            if query_lower in searchable:
                results.append({**channel, "source": f"YouTube ({category})"})

    return results