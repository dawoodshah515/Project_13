# Medical Assistant Chatbot

Professional AI-powered doctor recommendation system for Islamabad and Lahore, Pakistan.

## 🎯 Features

- **AI-Powered Recommendations**: Uses Google Gemini 2.0 Flash to intelligently match symptoms to specialists
- **Verified Database**: SQLite database with 500+ verified doctors across 5 specialties
- **Two Major Cities**: Comprehensive coverage of Islamabad and Lahore
- **Emergency Detection**: Automatically detects medical emergencies and provides immediate guidance
- **Symptom Mapping**: Converts user symptoms into appropriate medical specialties
- **Dark Theme UI**: Modern, professional interface with bluish highlights

## 🏥 Supported Specialties

- Psychiatrists
- Dermatologists  
- Neurologists
- Gynecologists
- Urologists

## 🚀 Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone or navigate to the project directory**
   ```bash
   cd "f:\A....Internship A to Z\PROJECTS\Project13"
   ```

2. **Install required packages**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the database** (automatic on first run)
   ```bash
   python database.py
   ```

## 🎮 Usage

### Running the Application

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

### Example Queries

**Direct Doctor Search:**
- "Best psychiatrist in Lahore"
- "Female gynecologist in Islamabad"
- "Dermatologist in DHA Lahore"

**Symptom-Based Search:**
- "I have anxiety and panic attacks"
- "Skin rash and itching"
- "Severe headaches and dizziness"

**With Preferences:**
- "Affordable psychiatrist in Islamabad"
- "Female doctor for pregnancy in Lahore"

## 📊 Database Structure

The system imports CSV files with the following naming convention:
- `[Specialty]_isl.csv` → Doctors in Islamabad
- `[Specialty]_lhr.csv` → Doctors in Lahore

CSV columns:
- Doc_names
- Specializations
- Qualifications
- Experiences
- Reviews
- Fees

## 🔒 Important Rules

1. **No Hallucination**: The system ONLY recommends doctors from the verified database
2. **Transparency**: If no matching doctors found, clearly states "System will update in few days"
3. **Emergency Priority**: Medical emergencies are detected and users are directed to immediate help
4. **No Diagnosis**: The system does NOT diagnose conditions or prescribe medication
5. **City Limitation**: Currently only supports Islamabad and Lahore

## 🛠️ Project Structure

```
Project13/
├── app.py                      # Main Streamlit application
├── database.py                 # Database operations and CSV import
├── gemini_agent.py            # Gemini AI integration
├── config.py                  # Configuration and constants
├── requirements.txt           # Python dependencies
├── doctors.db                 # SQLite database (auto-generated)
└── CSV Files/
    ├── Dermatologists_isl.csv
    ├── Dermatologists_lhr.csv
    ├── Gynecologists_isl.csv
    ├── Gynecologists_lhr.csv
    ├── Neurologists_isl.csv
    ├── Neurologists_lhr.csv
    ├── Psychiatrists_isl.csv
    ├── Psychiatrists_lhr.csv
    ├── Urologists_isl.csv
    └── Urologists_lhr.csv
```

## 🧪 Testing

### Test Database Import
```bash
python database.py
```

### Test Gemini Agent
```bash
python gemini_agent.py
```

## 🎨 UI Theme

- **Background**: Black (#0a0a0a)
- **Primary**: Dodger Blue (#1e90ff)
- **Secondary**: Royal Blue (#4169e1)
- **Accent**: Deep Sky Blue (#00bfff)

## ⚠️ Emergency Numbers

**Islamabad:**
- PIMS Hospital Emergency: 051-9261170
- Shifa International Hospital: 051-8463100

**Lahore:**
- Jinnah Hospital Emergency: 042-99231536
- Shaukat Khanum Hospital: 042-35905000

**National:**
- Rescue 1122

## 📝 License

This project is for educational and informational purposes. Always consult with qualified healthcare professionals for medical advice.

## 🤝 Support

For issues or questions, please refer to the system documentation or contact the development team.

---

**Powered by Google Gemini AI | Data from Verified Medical Databases**
