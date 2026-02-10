"""
Company name extraction utility
Extracts company names from news articles and tender documents
"""

import re


class CompanyExtractor:
    """Extract company names from text using pattern matching"""
    
    # Common company suffixes
    COMPANY_SUFFIXES = [
        'Ltd', 'Limited', 'Corporation', 'Corp', 'Inc', 'Incorporated',
        'LLC', 'Pvt', 'Private', 'Public', 'Co', 'Company',
        'Industries', 'Enterprises', 'Group', 'Holdings', 'Partners'
    ]
    
    # Indian PSU/Government organizations
    PSU_KEYWORDS = [
        'ONGC', 'IOCL', 'BPCL', 'HPCL', 'GAIL', 'Oil India',
        'Indian Oil', 'Bharat Petroleum', 'Hindustan Petroleum',
        'NNPC', 'Petronet', 'MRPL', 'CPCL', 'NRL'
    ]
    
    # Major Indian companies
    MAJOR_COMPANIES = [
        'Reliance', 'Tata', 'Adani', 'Birla', 'Mahindra',
        'Vedanta', 'Essar', 'Jindal', 'Larsen & Toubro', 'L&T',
        'Wipro', 'Infosys', 'TCS', 'HCL', 'Tech Mahindra',
        'ITC', 'HUL', 'Nestle', 'Britannia', 'Dabur',
        'Gillette', 'Quant', 'ICRA'
    ]
    
    @classmethod
    def extract_companies(cls, text):
        """Extract company names from text"""
        companies = []
        
        # Check for PSUs first
        for psu in cls.PSU_KEYWORDS:
            if psu.lower() in text.lower():
                companies.append(psu)
        
        # Check for major companies
        for company in cls.MAJOR_COMPANIES:
            if company.lower() in text.lower():
                # Try to get full name with suffix
                pattern = rf'\b({re.escape(company)})\s+({"|".join(cls.COMPANY_SUFFIXES)})\b'
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    companies.append(match.group(0))
                else:
                    companies.append(company)
        
        # Pattern for "Company Name Ltd/Limited/etc"
        suffix_pattern = r'\b([A-Z][A-Za-z&\s]+(?:' + '|'.join(cls.COMPANY_SUFFIXES) + r'))\b'
        matches = re.findall(suffix_pattern, text)
        for match in matches:
            # Filter out very short or very long names
            if 3 < len(match.split()) < 6 and len(match) < 50:
                companies.append(match.strip())
        
        # Remove duplicates while preserving order
        seen = set()
        unique_companies = []
        for company in companies:
            company_lower = company.lower().strip()
            if company_lower not in seen and len(company) > 2:
                seen.add(company_lower)
                unique_companies.append(company.strip())
        
        # Return first company or empty list
        return unique_companies[:3]  # Top 3 companies max
    
    @classmethod
    def extract_primary_company(cls, text):
        """Extract the primary/most relevant company from text"""
        companies = cls.extract_companies(text)
        
        if not companies:
            # Try to extract from common patterns
            # "Company announces", "Company reported", etc.
            patterns = [
                r'([A-Z][A-Za-z\s&]+?)\s+(?:announces|reported|launched|signed|awarded)',
                r'(?:by|from)\s+([A-Z][A-Za-z\s&]+?)\s+(?:Ltd|Limited|Corporation)',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text)
                if match:
                    return match.group(1).strip()
            
            return None
        
        return companies[0]
    
    @classmethod
    def get_industry_from_text(cls, text):
        """Determine industry from text content"""
        text_lower = text.lower()
        
        # Industry keywords
        industries = {
            'Oil & Gas': ['oil', 'gas', 'petroleum', 'refinery', 'fuel', 'diesel', 'petrol', 'lng', 'lpg'],
            'Chemicals': ['chemical', 'pharma', 'pharmaceutical', 'drug'],
            'Manufacturing': ['manufacturing', 'factory', 'plant', 'production'],
            'Technology': ['software', 'tech', 'IT', 'digital', 'ai', 'automation'],
            'FMCG': ['fmcg', 'consumer goods', 'packaged'],
            'Finance': ['bank', 'finance', 'investment', 'fund', 'mutual fund'],
            'Infrastructure': ['infrastructure', 'construction', 'highway', 'road'],
            'Textiles': ['textile', 'fabric', 'garment', 'apparel'],
            'Agriculture': ['agriculture', 'agri', 'farming', 'crop']
        }
        
        for industry, keywords in industries.items():
            if any(keyword in text_lower for keyword in keywords):
                return industry
        
        return 'General Business'
