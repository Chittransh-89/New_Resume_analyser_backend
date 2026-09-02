SKILLS_MAP = {
    # ==============================
    # PROGRAMMING LANGUAGES
    # ==============================
    "python": ["python", "py", "python3", "python 3"],
    "javascript": ["javascript", "js", "es6", "ecmascript", "node", "nodejs", "node.js", "node js"],
    "typescript": ["typescript", "ts"],
    "java": ["java", "core java", "java 8", "java 11"],
    "c++": ["c++", "cpp", "c plus plus"],
    "c": ["c programming", "c language"],
    "c#": ["c#", "csharp", "c sharp"],
    "go": ["golang", "go lang"],
    "rust": ["rust", "rustlang"],
    "ruby": ["ruby", "rails"],
    "php": ["php", "php7", "php8"],
    "swift": ["swift", "swiftui"],
    "kotlin": ["kotlin"],
    "scala": ["scala"],
    "r": ["r language", "r programming"],


    # ==============================
    # WEB FRONTEND
    # ==============================
    "react": ["react", "reactjs", "react.js", "react native"],
    "angular": ["angular", "angularjs", "angular 2"],
    "vue": ["vue", "vuejs", "vue.js"],
    "next.js": ["next", "nextjs", "next.js", "next js"],
    "nuxt": ["nuxt", "nuxtjs"],
    "svelte": ["svelte", "sveltekit"],
    "html": ["html", "html5"],
    "css": ["css", "css3", "scss", "sass", "less"],
    "tailwind": ["tailwind", "tailwindcss", "tailwind css"],
    "bootstrap": ["bootstrap"],
    "redux": ["redux", "react-redux"],


    # ==============================
    # WEB BACKEND
    # ==============================
    "nodejs": [
        "node", "nodejs", "node.js",
        "express", "expressjs", "express.js"
    ],
    "django": ["django"],
    "flask": ["flask"],
    "fastapi": ["fastapi", "fast api"],
    "spring": ["spring", "spring boot", "springboot"],
    "nestjs": ["nestjs", "nest.js"],
    "laravel": ["laravel"],
    "asp.net": ["asp.net", "aspnet", ".net", "dotnet"],


    # ==============================
    # DATABASES
    # ==============================
    "sql": [
        "sql", "mysql", "postgresql", "postgres",
        "sqlite", "plsql", "t-sql", "tsql"
    ],
    "mongodb": ["mongodb", "mongo", "nosql"],
    "redis": ["redis", "redis cache"],
    "elasticsearch": ["elasticsearch", "elastic search", "elastcisearch"],
    "cassandra": ["cassandra"],
    "dynamodb": ["dynamodb", "dynamo db"],
    "firebase": ["firebase", "firestore"],


    # ==============================
    # MACHINE LEARNING / AI
    # ==============================
    "machine learning": [
        "ml", "machine learning", "machinelearning",
        "ml algorithms", "ml models"
    ],
    "deep learning": [
        "deep learning", "dl", "deeplearning",
        "neural network", "neural networks",
        "cnn", "rnn", "lstm", "gan"
    ],
    "neural networks": [
        "neural network", "neural networks",
        "ann", "cnn", "rnn", "lstm"
    ],
    "computer vision": [
        "computer vision", "cv", "opencv", "image processing"
    ],
    "nlp": [
        "nlp", "natural language processing",
        "text processing", "text mining"
    ],
    "transformers": [
        "transformer", "transformers",
        "transformer models", "bert", "gpt",
        "llm", "large language model"
    ],
    "pytorch": ["pytorch", "torch"],
    "tensorflow": ["tensorflow", "tf", "tensor flow", "keras"],
    "scikit-learn": ["scikit-learn", "sklearn", "scikit learn"],
    "pandas": ["pandas"],
    "numpy": ["numpy"],
    "matplotlib": ["matplotlib", "plt"],
    "seaborn": ["seaborn"],
    "xgboost": ["xgboost", "xgb"],
    "lightgbm": ["lightgbm", "lgbm"],
    "huggingface": [
        "huggingface", "hugging face",
        "transformers library"
    ],
    "langchain": ["langchain", "lang chain"],
    "llama": [
        "llama", "llama2", "llama 2", "llama-2", "llama3"
    ],
    "rag": ["rag", "retrieval augmented generation"],
    "vector database": [
        "vector database", "vector db",
        "faiss", "pinecone", "weaviate",
        "chromadb", "qdrant"
    ],
    "prompt engineering": [
        "prompt engineering", "prompt design"
    ],
    "agents": [
        "ai agents", "autogen", "langgraph", "agentic"
    ],
    "mlflow": ["mlflow", "ml flow"],
    "kubeflow": ["kubeflow", "kube flow"],
    "onnx": ["onnx"],
    "tensorrt": ["tensorrt", "tensor rt"],


    # ==============================
    # DATA ENGINEERING
    # ==============================
    "spark": ["spark", "pyspark", "apache spark"],
    "hadoop": ["hadoop", "hdfs", "mapreduce"],
    "kafka": ["kafka", "apache kafka"],
    "airflow": ["airflow", "apache airflow"],
    "databricks": ["databricks"],
    "snowflake": ["snowflake"],
    "bigquery": ["bigquery", "big query"],


    # ==============================
    # DEVOPS / CI-CD
    # ==============================
    "docker": [
        "docker", "dockerfile",
        "docker-compose", "docker compose",
        "compose", "compose file"
    ],
    "kubernetes": [
        "kubernetes", "k8s", "k8",
        "kube", "kubectl", "helm", "minikube"
    ],
    "containerd": ["containerd", "container d"],

    "ci/cd": [
        "ci/cd", "ci cd", "ci-cd", "cicd",
        "continuous integration",
        "continuous deployment",
        "continuous delivery"
    ],
    "github actions": [
        "github actions", "gh actions",
        "github action", "gha",
        "github workflow", "github ci"
    ],
    "gitlab ci": [
        "gitlab ci", "gitlab-ci",
        "gitlabci", "gitlab pipeline"
    ],
    "jenkins": [
        "jenkins", "jenkinsfile", "jenkins pipeline"
    ],
    "circleci": ["circleci", "circle ci"],
    "travis": ["travis ci", "travisci"],
    "argo": ["argo cd", "argocd", "argo workflow"],


    # ==============================
    # CLOUD
    # ==============================
    "aws": [
        "aws", "amazon web services",
        "aws ec2", "aws s3", "aws lambda",
        "aws sagemaker", "amazon s3",
        "ec2", "s3", "lambda", "sagemaker",
        "rds", "cloudwatch"
    ],
    "azure": [
        "azure", "microsoft azure",
        "azure devops", "azure ml",
        "azure functions"
    ],
    "azure ml": [
        "azure ml", "azureml",
        "azure machine learning"
    ],
    "gcp": [
        "gcp", "google cloud",
        "google cloud platform",
        "bigquery", "firebase", "cloud run"
    ],
    "terraform": ["terraform", "tf"],
    "ansible": ["ansible"],
    "prometheus": ["prometheus"],


    # ==============================
    # VERSION CONTROL / TOOLS
    # ==============================
    "git": [
        "git", "github", "gitlab",
        "bitbucket", "version control",
        "git workflow"
    ],
    "linux": [
        "linux", "ubuntu", "unix",
        "debian", "bash", "shell",
        "shell scripting"
    ],
    "windows": ["windows server", "powershell"],


    # ==============================
    # APIs / TOOLS
    # ==============================
    "rest api": [
        "rest api", "rest", "restful",
        "restful api", "api development",
        "api design"
    ],
    "graphql": ["graphql", "graph ql"],
    "postman": ["postman"],
    "swagger": ["swagger", "openapi"],


    # ==============================
    # TESTING
    # ==============================
    "pytest": [
        "pytest", "py test",
        "unit test", "unit testing",
        "test automation"
    ],
    "jest": ["jest", "react testing"],
    "selenium": ["selenium"],
    "cypress": ["cypress"],


    # ==============================
    # METHODOLOGIES / SOFTWARE DESIGN
    # ==============================
    "agile": ["agile", "scrum", "kanban", "jira"],
    "microservices": [
        "microservices", "microservice",
        "service mesh", "istio", "grpc"
    ],
    "system design": [
        "system design",
        "high level design",
        "hld", "lld"
    ],
    "data structures": [
        "data structures", "dsa", "algorithms"
    ],
    "oop": [
        "oop", "object oriented",
        "object-oriented"
    ],


    # ==============================
    # DATA / ML VERSION CONTROL
    # ==============================
    "dvc": ["dvc", "data version control"],
}

JOB_ROLE_ALIASES = {
    # ========================
    # Machine Learning & AI
    # ========================
    "machine learning engineer": [
        "ml engineer", "machine learning developer", "ml developer",
        "ai/ml engineer", "ml ops engineer", "machine learning specialist",
        "applied ml engineer", "ml research engineer", "machine learning architect"
    ],
    "data scientist": [
        "data science engineer", "senior data scientist", "junior data scientist",
        "data science specialist", "applied data scientist", "research data scientist",
        "data science analyst", "statistical data scientist"
    ],
    "ai engineer": [
        "artificial intelligence engineer", "ai developer", "ai specialist",
        "ai researcher", "ai solutions engineer", "ai software engineer",
        "ai architect", "cognitive engineer", "intelligent systems engineer"
    ],
    "deep learning engineer": [
        "deep learning developer", "neural network engineer", "dl engineer",
        "deep learning researcher", "deep learning specialist",
        "computer vision engineer", "nlp engineer"
    ],
    "nlp engineer": [
        "natural language processing engineer", "nlp developer",
        "nlp specialist", "computational linguist", "text mining engineer",
        "language model engineer", "conversational ai engineer",
        "speech recognition engineer"
    ],
    "computer vision engineer": [
        "cv engineer", "image processing engineer", "vision ai engineer",
        "visual ai engineer", "computer vision developer",
        "image recognition engineer", "object detection engineer"
    ],
    "mlops engineer": [
        "ml operations engineer", "machine learning operations engineer",
        "ml platform engineer", "ml infrastructure engineer",
        "ai operations engineer", "model deployment engineer",
        "ml reliability engineer"
    ],

    # ========================
    # Data Engineering
    # ========================
    "data engineer": [
        "big data engineer", "data pipeline engineer", "etl developer",
        "data infrastructure engineer", "data platform engineer",
        "data integration engineer", "data warehouse engineer",
        "data architect", "analytics engineer"
    ],
    "data analyst": [
        "business data analyst", "junior data analyst", "senior data analyst",
        "data analytics specialist", "reporting analyst", "insights analyst",
        "data visualization analyst", "marketing data analyst",
        "financial data analyst", "operations analyst"
    ],
    "business intelligence engineer": [
        "bi engineer", "bi developer", "bi analyst",
        "business intelligence developer", "bi architect",
        "reporting engineer", "dashboard developer",
        "analytics engineer", "bi specialist"
    ],

    # ========================
    # Software Development
    # ========================
    "software engineer": [
        "software developer", "software programmer", "application developer",
        "software development engineer", "sde", "software architect",
        "full stack developer", "full stack engineer", "programmer",
        "senior software engineer", "junior software engineer"
    ],
    "frontend developer": [
        "front end developer", "frontend engineer", "front end engineer",
        "ui developer", "ui engineer", "web developer",
        "react developer", "angular developer", "vue developer",
        "javascript developer", "frontend specialist"
    ],
    "backend developer": [
        "back end developer", "backend engineer", "back end engineer",
        "server side developer", "api developer", "api engineer",
        "node developer", "django developer", "spring developer",
        "backend specialist", "server side engineer"
    ],
    "full stack developer": [
        "full stack engineer", "fullstack developer", "fullstack engineer",
        "full-stack developer", "full-stack engineer",
        "mean stack developer", "mern stack developer",
        "web application developer", "full stack programmer"
    ],
    "mobile developer": [
        "mobile app developer", "mobile application developer",
        "android developer", "ios developer", "react native developer",
        "flutter developer", "swift developer", "kotlin developer",
        "cross platform developer", "mobile engineer"
    ],
    "android developer": [
        "android engineer", "android app developer",
        "android application developer", "kotlin developer",
        "java android developer", "android specialist",
        "android software engineer"
    ],
    "ios developer": [
        "ios engineer", "ios app developer", "ios application developer",
        "swift developer", "objective c developer", "apple developer",
        "iphone developer", "ios specialist", "ios software engineer"
    ],

    # ========================
    # DevOps & Cloud
    # ========================
    "devops engineer": [
        "dev ops engineer", "devops specialist", "devops architect",
        "site reliability engineer", "sre", "platform engineer",
        "infrastructure engineer", "release engineer",
        "build and release engineer", "devops developer"
    ],
    "cloud engineer": [
        "cloud architect", "cloud developer", "cloud specialist",
        "cloud infrastructure engineer", "cloud solutions engineer",
        "aws engineer", "azure engineer", "gcp engineer",
        "cloud operations engineer", "cloud systems engineer"
    ],
    "site reliability engineer": [
        "sre", "site reliability specialist", "reliability engineer",
        "production engineer", "platform reliability engineer",
        "systems reliability engineer", "devops sre"
    ],
    "kubernetes engineer": [
        "k8s engineer", "kubernetes specialist", "container orchestration engineer",
        "kubernetes developer", "kubernetes administrator",
        "kubernetes architect", "k8s developer"
    ],
    "aws engineer": [
        "aws developer", "aws architect", "aws solutions architect",
        "amazon web services engineer", "aws cloud engineer",
        "aws specialist", "aws devops engineer"
    ],
    "azure engineer": [
        "azure developer", "azure architect", "azure solutions architect",
        "microsoft azure engineer", "azure cloud engineer",
        "azure specialist", "azure devops engineer"
    ],

    # ========================
    # Cybersecurity
    # ========================
    "cybersecurity engineer": [
        "cyber security engineer", "information security engineer",
        "security engineer", "network security engineer",
        "application security engineer", "cybersecurity specialist",
        "security software engineer", "cyber engineer"
    ],
    "penetration tester": [
        "pen tester", "ethical hacker", "security tester",
        "offensive security engineer", "red team engineer",
        "vulnerability analyst", "security researcher",
        "bug bounty hunter", "pentester"
    ],
    "security analyst": [
        "cybersecurity analyst", "information security analyst",
        "soc analyst", "security operations analyst",
        "threat analyst", "cyber threat analyst",
        "incident response analyst", "network security analyst"
    ],

    # ========================
    # Database
    # ========================
    "database administrator": [
        "dba", "database admin", "sql dba", "database manager",
        "database engineer", "oracle dba", "mysql dba",
        "postgresql dba", "database specialist", "database developer"
    ],
    "database developer": [
        "sql developer", "database programmer", "pl/sql developer",
        "t-sql developer", "database engineer", "database architect",
        "data modeler", "database designer"
    ],

    # ========================
    # QA & Testing
    # ========================
    "qa engineer": [
        "quality assurance engineer", "software tester", "test engineer",
        "qa analyst", "quality engineer", "qa developer",
        "automation tester", "manual tester", "test analyst",
        "quality control engineer"
    ],
    "automation test engineer": [
        "test automation engineer", "automation qa engineer",
        "selenium tester", "automation tester",
        "automated testing engineer", "sdet",
        "software development engineer in test"
    ],

    # ========================
    # Product & Project Management
    # ========================
    "product manager": [
        "pm", "product owner", "senior product manager",
        "junior product manager", "associate product manager",
        "technical product manager", "digital product manager",
        "product lead", "product specialist"
    ],
    "project manager": [
        "it project manager", "technical project manager",
        "senior project manager", "junior project manager",
        "program manager", "delivery manager", "scrum master",
        "agile project manager", "pmp certified project manager"
    ],
    "scrum master": [
        "agile coach", "agile scrum master", "certified scrum master",
        "csm", "agile project manager", "scrum coach",
        "agile delivery lead", "sprint master"
    ],

    # ========================
    # UI/UX Design
    # ========================
    "ui/ux designer": [
        "ui designer", "ux designer", "user interface designer",
        "user experience designer", "product designer",
        "interaction designer", "visual designer",
        "ui/ux developer", "experience designer"
    ],
    "graphic designer": [
        "visual designer", "creative designer", "brand designer",
        "digital designer", "multimedia designer",
        "motion graphics designer", "illustration designer",
        "graphic artist"
    ],

    # ========================
    # Networking
    # ========================
    "network engineer": [
        "network administrator", "network specialist", "network architect",
        "network analyst", "network technician", "cisco engineer",
        "network infrastructure engineer", "wan engineer", "lan engineer",
        "network support engineer"
    ],
    "systems administrator": [
        "sysadmin", "system administrator", "it administrator",
        "linux administrator", "windows administrator",
        "systems engineer", "it systems administrator",
        "infrastructure administrator", "server administrator"
    ],

    # ========================
    # Embedded & Hardware
    # ========================
    "embedded systems engineer": [
        "embedded engineer", "firmware engineer", "embedded developer",
        "embedded software engineer", "embedded systems developer",
        "rtos engineer", "embedded c developer", "microcontroller engineer",
        "iot engineer", "hardware software engineer"
    ],
    "hardware engineer": [
        "hardware developer", "electronics engineer", "circuit design engineer",
        "pcb designer", "hardware design engineer", "vlsi engineer",
        "fpga engineer", "chip design engineer", "hardware architect"
    ],

    # ========================
    # Blockchain
    # ========================
    "blockchain developer": [
        "blockchain engineer", "smart contract developer",
        "web3 developer", "solidity developer", "ethereum developer",
        "defi developer", "nft developer", "crypto developer",
        "distributed ledger developer", "blockchain specialist"
    ],

    # ========================
    # Game Development
    # ========================
    "game developer": [
        "game engineer", "game programmer", "unity developer",
        "unreal engine developer", "game designer", "game developer",
        "3d game developer", "indie game developer",
        "game software engineer", "gameplay engineer"
    ],

    # ========================
    # Business & Finance
    # ========================
    "business analyst": [
        "ba", "business systems analyst", "it business analyst",
        "functional analyst", "requirements analyst",
        "process analyst", "strategy analyst",
        "business process analyst", "enterprise analyst"
    ],
    "financial analyst": [
        "finance analyst", "investment analyst", "equity analyst",
        "risk analyst", "quantitative analyst", "quant analyst",
        "credit analyst", "portfolio analyst", "fp&a analyst"
    ],

    # ========================
    # Marketing & Sales
    # ========================
    "digital marketing specialist": [
        "digital marketer", "online marketing specialist",
        "seo specialist", "sem specialist", "social media specialist",
        "content marketer", "growth hacker", "performance marketer",
        "digital marketing analyst", "e-commerce marketer"
    ],
    "data driven marketer": [
        "marketing data analyst", "marketing analyst",
        "marketing science analyst", "crm analyst",
        "customer insights analyst", "marketing intelligence analyst"
    ],

    # ========================
    # Research
    # ========================
    "research scientist": [
        "ai researcher", "ml researcher", "research engineer",
        "applied scientist", "applied researcher",
        "senior research scientist", "principal research scientist",
        "research specialist", "r&d engineer"
    ],

    # ========================
    # IT Support
    # ========================
    "it support engineer": [
        "technical support engineer", "it helpdesk engineer",
        "helpdesk technician", "desktop support engineer",
        "it support specialist", "it technician",
        "service desk engineer", "level 1 support", "level 2 support"
    ],
    
}
