# 🚀 Talent Gap Analyzer - API Integration Guide

> **UAB The Hack 2025** - Complete integration guide for frontend/backend teams

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Main API Functions](#-main-api-functions)
- [Data Formats](#-data-formats)
- [Usage Examples](#-usage-examples)
- [Frontend Integration](#-frontend-integration)
- [API Endpoints (REST)](#-api-endpoints-rest)
- [Performance & Validation](#-performance--validation)

---

## 🔥 Quick Start

### Installation & Setup
```bash
# Clone repository
git clone https://github.com/OriolRoura/TalentGapAnalyzer-UABTheHack.git
cd TalentGapAnalyzer-UABTheHack

# Install dependencies
pip install -r requirements.txt

# Quick demo
python main_challenge.py
```

### One-Line Analysis
```python
from main_challenge import TalentGapAnalyzer

# Complete analysis pipeline
analyzer = TalentGapAnalyzer()
results = analyzer.run_complete_analysis()
```

---

## 🔌 Main API Functions

### 🎯 **PRIMARY FUNCTION: Complete Analysis**

#### `TalentGapAlgorithm.run_full_analysis()`

**Location**: `algorithm/talent_gap_algorithm.py`

```python
from algorithm.talent_gap_algorithm import TalentGapAlgorithm

# Initialize
algorithm = TalentGapAlgorithm(
    org_config=org_config_dict,        # Organization configuration
    vision_futura=vision_futura_dict,  # Future vision with roles
    algorithm_weights={                # Algorithm weights (optional)
        'skills': 0.50,               # 50% - Skills compatibility
        'responsibilities': 0.25,     # 25% - Responsibilities match
        'ambitions': 0.15,           # 15% - Career ambitions
        'dedication': 0.10           # 10% - Time dedication
    }
)

# Load employees
algorithm.load_employees_data(employees_list)

# Execute complete analysis
results = algorithm.run_full_analysis()
```

**Returns**: Complete analysis dictionary with all results

---

### 👤 **Employee-Specific Analysis**

#### `get_employee_analysis(employee_id)`

```python
employee_analysis = algorithm.get_employee_analysis("1001")

# Parameters:
# - employee_id: str (e.g., "1001")

# Returns:
{
    'employee_info': {
        'id': '1001',
        'name': 'Jordi Casals',
        'current_role': 'Head of Strategy',
        'chapter': 'Strategy'
    },
    'career_options': [              # Top compatible roles
        {
            'role_id': 'R-STR-LEAD',
            'role_title': 'Head of Strategy',
            'compatibility_score': 0.88,
            'readiness_band': 'READY'
        }
    ],
    'skill_profile': {
        'S-OKR': 'EXPERTO',
        'S-ANALISIS': 'AVANZADO'
    },
    'recommendations': [             # Personalized recommendations
        "Ready for Head of Strategy role",
        "Consider leadership training"
    ]
}
```

---

### 🎯 **Role-Specific Analysis**

#### `get_role_analysis(role_id)`

```python
role_analysis = algorithm.get_role_analysis("R-STR-LEAD")

# Parameters:
# - role_id: str (e.g., "R-STR-LEAD")

# Returns:
{
    'role_info': {
        'id': 'R-STR-LEAD',
        'title': 'Head of Strategy',
        'level': 'Lead',
        'required_skills': ['S-OKR', 'S-ANALISIS', 'S-STAKE']
    },
    'candidate_ranking': [           # Candidates ordered by score
        {
            'employee_id': '1001',
            'employee_name': 'Jordi Casals',
            'compatibility_score': 0.88,
            'readiness_band': 'READY'
        }
    ],
    'readiness_stats': {
        'ready_count': 1,
        'ready_with_support_count': 0,
        'average_score': 0.43
    },
    'hiring_recommendation': {
        'internal_candidate': True,
        'recommended_employee': 'Jordi Casals',
        'confidence': 0.88
    }
}
```

---

### 📊 **Export Functions**

#### `export_results(format)`

```python
# Export as JSON
json_results = algorithm.export_results(format='json')

# Export as CSV
csv_results = algorithm.export_results(format='csv')

# Parameters:
# - format: str ('json' | 'csv' | 'excel')

# Returns: Formatted data dictionary
```

---

## 📋 Data Formats

### **Input: Employee Data**
```python
employees_data = [
    {
        'id': '1001',
        'nombre': 'Jordi Casals',
        'email': 'jordi.casals@quether.com',
        'chapter': 'Strategy',
        'rol_actual': 'Head of Strategy',
        'antigüedad': '24m',
        'habilidades': {
            'S-OKR': 9,           # Scale 1-10
            'S-ANALISIS': 9,
            'S-STAKE': 8
        },
        'responsabilidades_actuales': [
            'OKRs y gobierno',
            'Workshops C-level'
        ],
        'ambiciones': {
            'especialidades_preferidas': ['Estrategia', 'Pricing'],
            'nivel_aspiración': 'lead'
        },
        'dedicacion_actual': {
            'Royal': 40,          # Hours per project
            'Arquimbau': 25
        }
    }
]
```

### **Input: Organization Config**
```python
org_config = {
    'organization': {
        'nombre': 'Quether Consulting'
    },
    'roles': [
        {
            'id': 'R-STR-LEAD',
            'título': 'Head of Strategy',
            'nivel': 'Lead',
            'responsabilidades': [
                'Definir visión estratégica',
                'Alinear roadmap'
            ],
            'habilidades_requeridas': ['S-OKR', 'S-ANALISIS']
        }
    ],
    'skills': [
        {
            'id': 'S-OKR',
            'nombre': 'OKRs y Roadmapping',
            'categoría': 'Estrategia',
            'peso': 5
        }
    ]
}
```

### **Input: Future Vision**
```python
vision_futura = {
    'roles_necesarios': [           # Or 'roles_futuros'
        {
            'id': 'R-STR-LEAD',
            'título': 'Head of Strategy',
            'nivel': 'Lead',
            'capítulo': 'Strategy',
            'modalidad': 'FT',
            'cantidad': 1,
            'objetivos_asociados': [
                'OKRs y gobierno',
                'Propuesta de valor'
            ]
        }
    ]
}
```

---

### **Output: Main Results Structure**
```python
results = {
    'metadata': {
        'analysis_timestamp': '2025-11-08T16:21:32',
        'total_employees': 10,
        'total_roles': 12,
        'algorithm_version': '1.0.0',
        'overall_readiness': 0.8,     # Percentage
        'ready_transitions': 1
    },
    'compatibility_matrix': {
        'summary': {...},
        'detailed_results': [         # Main data for frontend
            {
                'employee_id': '1001',
                'employee_name': 'Jordi Casals',
                'role_id': 'R-STR-LEAD',
                'role_title': 'Head of Strategy',
                'overall_score': 0.88,   # 0-1 scale
                'band': 'READY',         # READY | READY_WITH_SUPPORT | NEAR | FAR | NOT_VIABLE
                'skills_score': 0.90,
                'responsibilities_score': 0.85,
                'ambitions_score': 0.95,
                'dedication_score': 1.0
            }
        ]
    },
    'rankings': {
        'role_rankings': {            # Candidates per role
            'R-STR-LEAD': [
                {
                    'employee_name': 'Jordi Casals',
                    'gap_result': {...}
                }
            ]
        }
    },
    'gap_analysis': {
        'skill_gaps': [...],
        'bottlenecks': [
            {
                'skill_name': 'OKRs y Roadmapping',
                'gap_percentage': 45.2,
                'blocked_transitions': 8
            }
        ]
    },
    'recommendations': {
        'strategic': [...],
        'organizational': [...],
        'individual': [...]
    }
}
```

---

## 💻 Usage Examples

### **Example 1: Dashboard KPIs**
```python
# Get main dashboard metrics
overall_readiness = results['metadata']['overall_readiness']
ready_transitions = results['metadata']['ready_transitions']
total_employees = results['metadata']['total_employees']
total_roles = results['metadata']['total_roles']

print(f"Readiness: {overall_readiness:.1f}%")
print(f"Ready employees: {ready_transitions}")
```

### **Example 2: Employee List with Best Match**
```python
# Get best match for each employee
employee_best_matches = {}
for result in results['compatibility_matrix']['detailed_results']:
    emp_id = result['employee_id']
    emp_name = result['employee_name']
    
    if emp_id not in employee_best_matches or result['overall_score'] > employee_best_matches[emp_id]['score']:
        employee_best_matches[emp_id] = {
            'name': emp_name,
            'best_role': result['role_title'],
            'score': result['overall_score'],
            'band': result['band']
        }
```

### **Example 3: Role Candidates Ranking**
```python
# Get candidates for specific role
def get_role_candidates(results, role_id):
    candidates = [
        item for item in results['compatibility_matrix']['detailed_results']
        if item['role_id'] == role_id
    ]
    # Sort by score (highest first)
    candidates.sort(key=lambda x: x['overall_score'], reverse=True)
    return candidates

# Usage
strategy_candidates = get_role_candidates(results, 'R-STR-LEAD')
print(f"Top candidate: {strategy_candidates[0]['employee_name']} - {strategy_candidates[0]['overall_score']:.2f}")
```

### **Example 4: Skills Gap Analysis**
```python
# Analyze critical bottlenecks
bottlenecks = results['gap_analysis']['bottlenecks']
for bottleneck in bottlenecks:
    skill_name = bottleneck['skill_name']
    gap_percentage = bottleneck['gap_percentage']
    blocked_transitions = bottleneck['blocked_transitions']
    
    print(f"Bottleneck: {skill_name}")
    print(f"  Gap: {gap_percentage:.1f}%")
    print(f"  Blocks: {blocked_transitions} transitions")
```

---

## 🎨 Frontend Integration

### **React/Vue Component Example**
```javascript
// API call example
const analyzeEmployees = async () => {
    const response = await fetch('/api/analyze/full', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            employees: employeeData,
            org_config: orgConfig,
            vision_futura: visionData
        })
    });
    
    const results = await response.json();
    
    // Dashboard metrics
    setOverallReadiness(results.metadata.overall_readiness);
    setReadyTransitions(results.metadata.ready_transitions);
    
    // Employee-role matrix
    setCompatibilityMatrix(results.compatibility_matrix.detailed_results);
    
    // Bottlenecks
    setBottlenecks(results.gap_analysis.bottlenecks);
};
```

### **Dashboard Widgets**
```javascript
// Readiness gauge
const ReadinessGauge = ({ readiness }) => (
    <div className="gauge">
        <span>{readiness.toFixed(1)}%</span>
        <span>Overall Readiness</span>
    </div>
);

// Top matches table
const TopMatches = ({ matrix }) => {
    const topMatches = matrix
        .sort((a, b) => b.overall_score - a.overall_score)
        .slice(0, 10);
        
    return (
        <table>
            <thead>
                <tr>
                    <th>Employee</th>
                    <th>Role</th>
                    <th>Score</th>
                    <th>Band</th>
                </tr>
            </thead>
            <tbody>
                {topMatches.map(match => (
                    <tr key={`${match.employee_id}-${match.role_id}`}>
                        <td>{match.employee_name}</td>
                        <td>{match.role_title}</td>
                        <td>{(match.overall_score * 100).toFixed(1)}%</td>
                        <td className={`band-${match.band.toLowerCase()}`}>
                            {match.band}
                        </td>
                    </tr>
                ))}
            </tbody>
        </table>
    );
};
```

---

## 🔗 API Endpoints (REST)

### **Suggested REST API Implementation**

```python
from flask import Flask, request, jsonify
from algorithm.talent_gap_algorithm import TalentGapAlgorithm

app = Flask(__name__)

@app.route('/api/analyze/full', methods=['POST'])
def analyze_full():
    data = request.json
    
    algorithm = TalentGapAlgorithm(
        org_config=data['org_config'],
        vision_futura=data['vision_futura']
    )
    
    algorithm.load_employees_data(data['employees'])
    results = algorithm.run_full_analysis()
    
    return jsonify(results)

@app.route('/api/employees/<employee_id>', methods=['GET'])
def get_employee_analysis(employee_id):
    # Implementation using get_employee_analysis()
    pass

@app.route('/api/roles/<role_id>/candidates', methods=['GET'])
def get_role_candidates(role_id):
    # Implementation using get_role_analysis()
    pass

@app.route('/api/export/<format>', methods=['GET'])
def export_results(format):
    # Implementation using export_results()
    pass
```

### **Endpoint Documentation**

| Endpoint | Method | Description | Parameters |
|----------|--------|-------------|------------|
| `/api/analyze/full` | POST | Complete analysis | `{employees, org_config, vision_futura}` |
| `/api/employees/{id}` | GET | Employee analysis | `employee_id` |
| `/api/roles/{id}/candidates` | GET | Role candidates | `role_id` |
| `/api/export/{format}` | GET | Export results | `format: json|csv|excel` |

---

## ⚡ Performance & Validation

### **Challenge Requirements**
- ✅ **Processing Time**: < 30 minutes for 300 employees
- ✅ **Current Performance**: 0.002s per employee (10 employees in 0.02s)
- ✅ **Projected Performance**: 300 employees in ~0.6 seconds
- ✅ **Reproducibility**: Deterministic calculations
- ✅ **Data Validation**: Automatic integrity checks

### **Validation Checklist**
```python
# Performance validation
assert results['metadata']['total_processing_time'] < 1800  # 30 min
assert len(results['compatibility_matrix']['detailed_results']) > 0
assert all(0 <= item['overall_score'] <= 1 for item in results['compatibility_matrix']['detailed_results'])

# Data integrity
assert results['metadata']['total_employees'] > 0
assert results['metadata']['total_roles'] > 0
assert sum(algorithm.weights.values()) == 1.0  # Weights sum to 100%
```

---

## 🚀 Quick Demo Commands

### **Challenge Demo**
```bash
# Complete challenge pipeline
python main_challenge.py

# Output files generated:
# - challenge_outputs/gap_matrix_TIMESTAMP.csv
# - challenge_outputs/full_results_TIMESTAMP.json
# - challenge_outputs/performance_metrics_TIMESTAMP.json
# - challenge_outputs/banda_distribution_TIMESTAMP.csv
```

### **Interactive Demo**
```bash
# Interactive analysis with multiple scenarios
python algorithm/main.py
```

### **Custom Analysis**
```python
# Custom weights example
from main_challenge import TalentGapAnalyzer

analyzer = TalentGapAnalyzer()
org_config, vision_futura, employees_data = analyzer.load_and_validate_data()

# Custom algorithm weights
custom_weights = {
    'skills': 0.60,        # Prioritize skills more
    'responsibilities': 0.20,
    'ambitions': 0.10,
    'dedication': 0.10
}

results = analyzer.run_gap_analysis(
    org_config, 
    vision_futura, 
    employees_data,
    custom_weights=custom_weights
)
```

---

## 📞 Support & Contact

**For Integration Support:**
- **Algorithm Questions**: Check `algorithm/README.md`
- **Data Format Issues**: See examples in `/dataSet/`
- **Performance Issues**: Review challenge validation logs

**Team Contact**: UAB The Hack 2025 - Quether Consulting Challenge

---

## 📄 License

MIT License - UAB The Hack 2025

---

**🎯 Ready to integrate? Start with the [Quick Start](#-quick-start) section!**