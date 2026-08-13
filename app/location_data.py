"""
AVYRO E-Commerce — Indian Location Data & Pincode Utilities
"""

# Comprehensive list of Indian States & Union Territories
INDIAN_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
    "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
    "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
    "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
    "Andaman and Nicobar Islands", "Chandigarh",
    "Dadra and Nagar Haveli and Daman and Diu", "Delhi", "Jammu and Kashmir",
    "Ladakh", "Lakshadweep", "Puducherry"
]

# Major Indian Cities mapping with State
INDIAN_CITIES = [
    # Gujarat
    {"city": "Ahmedabad", "state": "Gujarat", "pincodes": ["380001", "380002", "380006", "380009", "380015", "380051", "380052", "380054", "380058", "380060"]},
    {"city": "Ahmedabad Cantonment", "state": "Gujarat", "pincodes": ["380004", "380003"]},
    {"city": "Surat", "state": "Gujarat", "pincodes": ["395001", "395002", "395003", "395007", "395009", "395010"]},
    {"city": "Vadodara", "state": "Gujarat", "pincodes": ["390001", "390002", "390007", "390011", "390020"]},
    {"city": "Rajkot", "state": "Gujarat", "pincodes": ["360001", "360002", "360003", "360004", "360005"]},
    {"city": "Bhavnagar", "state": "Gujarat", "pincodes": ["364001", "364002", "364003"]},
    {"city": "Jamnagar", "state": "Gujarat", "pincodes": ["361001", "361002", "361005", "361008"]},
    {"city": "Junagadh", "state": "Gujarat", "pincodes": ["362001", "362002"]},
    {"city": "Gandhinagar", "state": "Gujarat", "pincodes": ["382007", "382010", "382016", "382021", "382024"]},
    {"city": "Anand", "state": "Gujarat", "pincodes": ["388001", "388120"]},
    {"city": "Navsari", "state": "Gujarat", "pincodes": ["396445"]},
    {"city": "Bharuch", "state": "Gujarat", "pincodes": ["392001"]},
    {"city": "Vapi", "state": "Gujarat", "pincodes": ["396191", "396195"]},
    {"city": "Morbi", "state": "Gujarat", "pincodes": ["363641", "363642"]},

    # Maharashtra
    {"city": "Mumbai", "state": "Maharashtra", "pincodes": ["400001", "400002", "400004", "400050", "400051", "400053", "400069", "400070", "400099"]},
    {"city": "Thane", "state": "Maharashtra", "pincodes": ["400601", "400602", "400604", "400607"]},
    {"city": "Navi Mumbai", "state": "Maharashtra", "pincodes": ["400703", "400705", "400706"]},
    {"city": "Pune", "state": "Maharashtra", "pincodes": ["411001", "411002", "411004", "411014", "411038", "411057"]},
    {"city": "Nagpur", "state": "Maharashtra", "pincodes": ["440001", "440010", "440012"]},
    {"city": "Nashik", "state": "Maharashtra", "pincodes": ["422001", "422002", "422003", "422005"]},
    {"city": "Aurangabad", "state": "Maharashtra", "pincodes": ["431001", "431005"]},
    {"city": "Solapur", "state": "Maharashtra", "pincodes": ["413001", "413002"]},
    {"city": "Kolhapur", "state": "Maharashtra", "pincodes": ["416001", "416003"]},

    # Delhi
    {"city": "Delhi", "state": "Delhi", "pincodes": ["110001", "110002", "110003", "110005", "110006", "110015", "110020", "110092"]},
    {"city": "New Delhi", "state": "Delhi", "pincodes": ["110001", "110011", "110021"]},

    # Karnataka
    {"city": "Bengaluru", "state": "Karnataka", "pincodes": ["560001", "560002", "560004", "560025", "560034", "560037", "560066", "560100"]},
    {"city": "Mysuru", "state": "Karnataka", "pincodes": ["570001", "570002", "570004"]},
    {"city": "Mangaluru", "state": "Karnataka", "pincodes": ["575001", "575002", "575003"]},

    # Telangana
    {"city": "Hyderabad", "state": "Telangana", "pincodes": ["500001", "500002", "500003", "500016", "500032", "500081"]},
    {"city": "Secunderabad", "state": "Telangana", "pincodes": ["500003", "500009", "500015"]},

    # Tamil Nadu
    {"city": "Chennai", "state": "Tamil Nadu", "pincodes": ["600001", "600002", "600004", "600017", "600028", "600096"]},
    {"city": "Coimbatore", "state": "Tamil Nadu", "pincodes": ["641001", "641002", "641012"]},
    {"city": "Madurai", "state": "Tamil Nadu", "pincodes": ["625001", "625002"]},

    # West Bengal
    {"city": "Kolkata", "state": "West Bengal", "pincodes": ["700001", "700002", "700009", "700016", "700091"]},
    {"city": "Howrah", "state": "West Bengal", "pincodes": ["711101", "711102"]},

    # Rajasthan
    {"city": "Jaipur", "state": "Rajasthan", "pincodes": ["302001", "302002", "302004", "302015", "302020"]},
    {"city": "Jodhpur", "state": "Rajasthan", "pincodes": ["342001", "342003"]},
    {"city": "Udaipur", "state": "Rajasthan", "pincodes": ["313001", "313002"]},

    # Uttar Pradesh
    {"city": "Lucknow", "state": "Uttar Pradesh", "pincodes": ["226001", "226002", "226010"]},
    {"city": "Kanpur", "state": "Uttar Pradesh", "pincodes": ["208001", "208002"]},
    {"city": "Agra", "state": "Uttar Pradesh", "pincodes": ["282001", "282002"]},
    {"city": "Varanasi", "state": "Uttar Pradesh", "pincodes": ["221001", "221002"]},
    {"city": "Noida", "state": "Uttar Pradesh", "pincodes": ["201301", "201303", "201307"]},
    {"city": "Ghaziabad", "state": "Uttar Pradesh", "pincodes": ["201001", "201002", "201009"]},

    # Haryana & Punjab
    {"city": "Gurugram", "state": "Haryana", "pincodes": ["122001", "122002", "122018"]},
    {"city": "Chandigarh", "state": "Chandigarh", "pincodes": ["160001", "160002", "160017"]},
    {"city": "Amritsar", "state": "Punjab", "pincodes": ["143001", "143002"]},
    {"city": "Ludhiana", "state": "Punjab", "pincodes": ["141001", "141002"]},

    # Kerala
    {"city": "Kochi", "state": "Kerala", "pincodes": ["682001", "682011", "682035"]},
    {"city": "Thiruvananthapuram", "state": "Kerala", "pincodes": ["695001", "695002"]},

    # Madhya Pradesh & Bihar
    {"city": "Indore", "state": "Madhya Pradesh", "pincodes": ["452001", "452002", "452010"]},
    {"city": "Bhopal", "state": "Madhya Pradesh", "pincodes": ["462001", "462003", "462016"]},
    {"city": "Patna", "state": "Bihar", "pincodes": ["800001", "800002", "800013"]}
]

def search_cities(query):
    query = (query or '').strip().lower()
    if not query:
        return INDIAN_CITIES[:10]
    
    matches = []
    for c in INDIAN_CITIES:
        if query in c['city'].lower():
            matches.append(c)
    return matches[:15]

def search_states(query):
    query = (query or '').strip().lower()
    if not query:
        return INDIAN_STATES[:10]
    
    return [s for s in INDIAN_STATES if query in s.lower()][:10]

def lookup_local_pincode(pincode):
    pincode = str(pincode).strip()
    for c in INDIAN_CITIES:
        if pincode in c.get('pincodes', []):
            return {
                'valid': True,
                'city': c['city'],
                'state': c['state'],
                'districts': [c['city']],
                'states': [c['state']],
                'pincode': pincode
            }
    
    # Generic format validation for Indian 6-digit PIN codes (1-9 starting digit, non-repetitive junk like 000000 or 123456)
    invalid_patterns = {'000000', '123456', '111111', '222222', '333333', '444444', '555555', '666666', '777777', '888888', '999999'}
    if len(pincode) == 6 and pincode.isdigit() and pincode[0] != '0' and pincode not in invalid_patterns:
        return {
            'valid': True,
            'city': '',
            'state': '',
            'districts': [],
            'states': [],
            'pincode': pincode
        }
    
    return None
