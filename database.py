"""
Database Layer for Medical Assistant Chatbot
Handles SQLite operations, CSV import, and doctor search functionality
"""

import sqlite3
import pandas as pd
import os
import re
from typing import List, Dict, Optional, Tuple
from config import DATABASE_PATH, CSV_DIRECTORY, SUPPORTED_CITIES


class DoctorDatabase:
    """Manages database operations for doctor recommendations"""
    
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """Establish database connection"""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        return self
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        """Context manager entry"""
        return self.connect()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
    
    def init_database(self):
        """Create database schema if not exists"""
        with self.connect():
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS doctors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    specialty TEXT NOT NULL,
                    city TEXT NOT NULL,
                    specializations TEXT,
                    qualifications TEXT,
                    experience TEXT,
                    reviews INTEGER,
                    fee INTEGER,
                    area TEXT,
                    hospital_clinic TEXT,
                    phone TEXT,
                    timings TEXT,
                    profile_link TEXT
                )
            """)
            
            # Create indexes for faster searches
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_specialty 
                ON doctors(specialty)
            """)
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_city 
                ON doctors(city)
            """)
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_specialty_city 
                ON doctors(specialty, city)
            """)
            
            self.conn.commit()
            print("✓ Database schema initialized successfully")
    
    def extract_specialty_from_filename(self, filename: str) -> str:
        """
        Extract specialty from filename
        Example: 'Psychiatrists_isl.csv' -> 'Psychiatrist'
        """
        base_name = filename.replace('.csv', '')
        specialty_part = base_name.split('_')[0]
        
        # Remove plural 's' if present
        if specialty_part.endswith('s'):
            specialty_part = specialty_part[:-1]
        
        return specialty_part
    
    def extract_city_from_filename(self, filename: str) -> str:
        """
        Extract city from filename
        Example: 'Psychiatrists_isl.csv' -> 'Islamabad'
        Example: 'Dermatologists_lhr.csv' -> 'Lahore'
        """
        if '_isl' in filename.lower():
            return 'Islamabad'
        elif '_lhr' in filename.lower():
            return 'Lahore'
        else:
            return 'Unknown'
    
    def parse_experience_years(self, experience_str: str) -> int:
        """
        Parse experience string to extract years
        Example: 'Year 12' -> 12
        """
        if not experience_str or pd.isna(experience_str):
            return 0
        
        match = re.search(r'(\d+)', str(experience_str))
        if match:
            return int(match.group(1))
        return 0
    
    def import_csv_files(self) -> int:
        """
        Import all CSV files from the directory
        Returns: Number of doctors imported
        """
        with self.connect():
            # Clear existing data
            self.cursor.execute("DELETE FROM doctors")
            
            csv_files = [f for f in os.listdir(CSV_DIRECTORY) 
                        if f.endswith('.csv') and ('_isl' in f or '_lhr' in f)]
            
            total_imported = 0
            
            for csv_file in csv_files:
                specialty = self.extract_specialty_from_filename(csv_file)
                city = self.extract_city_from_filename(csv_file)
                
                file_path = os.path.join(CSV_DIRECTORY, csv_file)
                
                try:
                    df = pd.read_csv(file_path)
                    
                    # Clean data
                    df = df.dropna(subset=['Doc_names'])  # Remove rows without doctor names
                    df = df.fillna('')  # Fill other NaN values with empty string
                    
                    for _, row in df.iterrows():
                        # Parse reviews and fees
                        reviews = 0
                        if row['Reviews'] and str(row['Reviews']).strip():
                            try:
                                reviews = int(row['Reviews'])
                            except (ValueError, TypeError):
                                reviews = 0
                        
                        fee = 0
                        if row['Fees'] and str(row['Fees']).strip():
                            try:
                                fee = int(row['Fees'])
                            except (ValueError, TypeError):
                                fee = 0
                        
                        # Insert into database
                        self.cursor.execute("""
                            INSERT INTO doctors (
                                name, specialty, city, specializations, 
                                qualifications, experience, reviews, fee,
                                area, hospital_clinic, phone, timings, profile_link
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            str(row['Doc_names']).strip(),
                            specialty,
                            city,
                            str(row['Specializations']).strip(),
                            str(row['Qualifications']).strip(),
                            str(row['Experiences']).strip(),
                            reviews,
                            fee,
                            None,  # area - not in CSV
                            None,  # hospital_clinic - not in CSV
                            None,  # phone - not in CSV
                            None,  # timings - not in CSV
                            None   # profile_link - not in CSV
                        ))
                        total_imported += 1
                    
                    print(f"✓ Imported {len(df)} {specialty}s from {city} ({csv_file})")
                
                except Exception as e:
                    print(f"✗ Error importing {csv_file}: {str(e)}")
            
            self.conn.commit()
            print(f"\n✓ Total doctors imported: {total_imported}")
            return total_imported
    
    def search_doctors(
        self, 
        specialty: Optional[str] = None,
        city: Optional[str] = None,
        gender_preference: Optional[str] = None,
        max_fee: Optional[int] = None,
        limit: int = 5
    ) -> List[Dict]:
        """
        Search for doctors with filters and ranking
        
        Args:
            specialty: Medical specialty (e.g., 'Psychiatrist', 'Dermatologist')
            city: City name ('Islamabad' or 'Lahore')
            gender_preference: 'male' or 'female' (checks doctor name)
            max_fee: Maximum consultation fee
            limit: Maximum number of results
        
        Returns:
            List of doctor dictionaries
        """
        with self.connect():
            query = "SELECT * FROM doctors WHERE 1=1"
            params = []
            
            if specialty:
                query += " AND specialty = ?"
                params.append(specialty)
            
            if city:
                query += " AND city = ?"
                params.append(city)
            
            if max_fee:
                query += " AND fee <= ?"
                params.append(max_fee)
            
            self.cursor.execute(query, params)
            rows = self.cursor.fetchall()
            
            # Convert to dictionaries
            columns = [desc[0] for desc in self.cursor.description]
            doctors = [dict(zip(columns, row)) for row in rows]
            
            # Apply gender filter if specified
            if gender_preference:
                doctors = self._filter_by_gender(doctors, gender_preference)
            
            # Rank doctors
            doctors = self._rank_doctors(doctors)
            
            # Return top N results
            return doctors[:limit]
    
    def _filter_by_gender(self, doctors: List[Dict], gender: str) -> List[Dict]:
        """
        Filter doctors by gender based on name patterns
        Note: This is a best-effort approach based on common naming patterns
        """
        if gender.lower() == 'female':
            # Common female name indicators
            female_patterns = ['Dr. ']
            filtered = []
            for doc in doctors:
                name = doc['name']
                # Check for female titles or names
                if any(indicator in name for indicator in ['Dr. ', 'Prof. Dr. ', 'Assist. Prof. Dr.', 'Assoc. Prof. Dr.']):
                    # Simple heuristic: if name doesn't start with common male patterns
                    if not any(male in name for male in ['Dr. Muhammad', 'Dr. M.', 'Dr. Ahmed', 'Dr. Ali', 
                                                          'Dr. Usman', 'Dr. Hassan', 'Dr. Hamza']):
                        filtered.append(doc)
                else:
                    filtered.append(doc)
            return filtered if filtered else doctors
        
        return doctors
    
    def _rank_doctors(self, doctors: List[Dict]) -> List[Dict]:
        """
        Rank doctors by multiple criteria:
        1. Review count (higher is better)
        2. Experience (more years is better)
        3. Fee (lower is better for tie-breaking)
        """
        def ranking_score(doctor):
            reviews = doctor.get('reviews', 0) or 0
            experience_years = self.parse_experience_years(doctor.get('experience', ''))
            fee = doctor.get('fee', 0) or 0
            
            # Scoring algorithm
            # Reviews: weight = 10
            # Experience: weight = 5
            # Fee: weight = -1 (lower fee is better)
            score = (reviews * 10) + (experience_years * 5) - (fee * 0.01)
            return score
        
        return sorted(doctors, key=ranking_score, reverse=True)
    
    def get_all_specialties(self) -> List[str]:
        """Get list of all available specialties"""
        with self.connect():
            self.cursor.execute("SELECT DISTINCT specialty FROM doctors ORDER BY specialty")
            return [row[0] for row in self.cursor.fetchall()]
    
    def get_doctor_count(self, specialty: Optional[str] = None, city: Optional[str] = None) -> int:
        """Get count of doctors matching criteria"""
        with self.connect():
            query = "SELECT COUNT(*) FROM doctors WHERE 1=1"
            params = []
            
            if specialty:
                query += " AND specialty = ?"
                params.append(specialty)
            
            if city:
                query += " AND city = ?"
                params.append(city)
            
            self.cursor.execute(query, params)
            return self.cursor.fetchone()[0]


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def init_database():
    """Initialize database (convenience function)"""
    db = DoctorDatabase()
    db.init_database()


def import_csv_files():
    """Import CSV files (convenience function)"""
    db = DoctorDatabase()
    return db.import_csv_files()


def search_doctors(**kwargs):
    """Search doctors (convenience function)"""
    db = DoctorDatabase()
    return db.search_doctors(**kwargs)


def get_all_specialties():
    """Get all specialties (convenience function)"""
    db = DoctorDatabase()
    return db.get_all_specialties()


# ============================================================================
# MAIN EXECUTION (for testing)
# ============================================================================

if __name__ == "__main__":
    print("Initializing Medical Assistant Database...")
    print("=" * 60)
    
    # Initialize database
    init_database()
    
    # Import CSV files
    total = import_csv_files()
    
    print("\n" + "=" * 60)
    print("Database Statistics:")
    print("=" * 60)
    
    db = DoctorDatabase()
    specialties = db.get_all_specialties()
    
    for specialty in specialties:
        for city in SUPPORTED_CITIES:
            count = db.get_doctor_count(specialty, city)
            print(f"{specialty:20s} in {city:12s}: {count:3d} doctors")
    
    print("\n" + "=" * 60)
    print("Sample Search Test:")
    print("=" * 60)
    
    # Test search
    results = search_doctors(specialty='Psychiatrist', city='Islamabad', limit=3)
    print(f"\nTop 3 Psychiatrists in Islamabad:")
    for i, doc in enumerate(results, 1):
        print(f"{i}. {doc['name']} - Fee: Rs.{doc['fee']} - Reviews: {doc['reviews']}")
