# TalentGapAnalyzer - UAB The Hack 2025

## 🎯 Overview

TalentGapAnalyzer is an innovative HR analytics tool developed for UAB The Hack 2025 that helps organizations identify and bridge talent gaps within their workforce. The platform analyzes employee skills, ambitions, and role requirements to provide actionable insights for career development and organizational planning.

## ✨ Features

- **Employee Skills Analysis**: Comprehensive evaluation of employee competencies and potential
- **Role Compatibility Matrix**: Visual representation of employee-role fit across the organization
- **Gap Identification**: Automated detection of skill gaps and development opportunities
- **Career Path Recommendations**: AI-driven suggestions for employee career progression
- **Future Vision Planning**: Strategic workforce planning and development insights

## 🏗️ Project Structure

```
TalentGapAnalyzer/
├── frontend/               # React frontend application
│   ├── components/        # React components
│   ├── services/         # API services
│   └── utils/           # Utility functions
├── algorithm/            # Core analysis algorithms
│   ├── gap_analyzer.py   # Gap analysis logic
│   └── models.py        # Data models
└── api/                 # Backend API
    ├── routes/         # API endpoints
    └── services/      # Business logic
```

## 🚀 Getting Started

### Prerequisites

- Node.js (v18 or higher)
- Python 3.9+
- npm or yarn

### Frontend Setup

```bash
cd frontend/frontend-talent-gap
npm install
npm run dev
```

### Backend Setup

```bash
cd api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## 🛠️ Technologies Used

### Frontend
- React 19
- TailwindCSS
- Vite
- Recharts for data visualization
- React Router for navigation

### Backend
- Python
- FastAPI
- Pandas for data analysis
- Scikit-learn for ML algorithms

## 📊 Core Features

1. **Gap Matrix Visualization**
   - Interactive compatibility matrix
   - Color-coded scoring system
   - Role-based filtering

2. **Employee Analysis**
   - Skill assessment
   - Career path tracking
   - Development recommendations

3. **Future Vision**
   - Workforce planning tools
   - Skill trend analysis
   - Development forecasting

## 🔄 API Integration

The application uses a RESTful API for data communication. Key endpoints include:

- `/api/employee-matrix`: Employee compatibility data
- `/api/gap-analysis`: Detailed gap analysis
- `/api/recommendations`: Career recommendations