"""
Geographic Analysis Module for NYC Public Schools Substitute Renewal Analytics
Handles ZIP code mapping, borough analysis, and geographic data processing
"""

import pandas as pd

def get_nyc_zip_borough_mapping():
    """
    Returns a dictionary mapping NYC ZIP codes and neighboring counties to boroughs/areas
    Based on official NYC ZIP code boundaries and surrounding counties
    """
    zip_to_borough = {}
    
    # Manhattan: 10001-10282
    for zip_code in range(10001, 10283):
        zip_to_borough[str(zip_code)] = 'Manhattan'
    
    # Brooklyn: 11201-11256
    for zip_code in range(11201, 11257):
        zip_to_borough[str(zip_code)] = 'Brooklyn'
    
    # Queens: 11004-11005, 11101-11109, 11351-11697
    for zip_code in range(11004, 11006):
        zip_to_borough[str(zip_code)] = 'Queens'
    for zip_code in range(11101, 11110):
        zip_to_borough[str(zip_code)] = 'Queens'
    for zip_code in range(11351, 11698):
        zip_to_borough[str(zip_code)] = 'Queens'
    
    # Bronx: 10451-10475
    for zip_code in range(10451, 10476):
        zip_to_borough[str(zip_code)] = 'Bronx'
    
    # Staten Island: 10301-10314
    for zip_code in range(10301, 10315):
        zip_to_borough[str(zip_code)] = 'Staten Island'
    
    # === NEIGHBORING COUNTIES ===
    
    # Westchester County (North of NYC)
    westchester_zips = [
        "10501", "10502", "10503", "10504", "10505", "10506", "10507", "10509", 
        "10510", "10511", "10514", "10517", "10518", "10520", "10521", "10522", 
        "10523", "10526", "10527", "10528", "10530", "10532", "10533", "10535", 
        "10536", "10537", "10538", "10540", "10541", "10543", "10545", "10546", 
        "10547", "10548", "10549", "10550", "10551", "10552", "10553", "10560", 
        "10562", "10566", "10567", "10570", "10571", "10572", "10573", "10576", 
        "10577", "10578", "10579", "10580", "10583", "10587", "10588", "10589", 
        "10590", "10591", "10594", "10595", "10596", "10597", "10598", "10601", 
        "10602", "10603", "10604", "10605", "10606", "10607", "10610", "10701", 
        "10702", "10703", "10704", "10705", "10706", "10707", "10708", "10709", 
        "10710", "10801", "10802", "10803", "10804", "10805"
    ]
    for zip_code in westchester_zips:
        zip_to_borough[zip_code] = 'Westchester County'
    
    # Nassau County (Long Island West)
    nassau_zips = [
        "11001", "11002", "11003", "11010", "11020", "11021", "11022", "11023", 
        "11024", "11025", "11026", "11027", "11030", "11040", "11042", "11050", 
        "11051", "11052", "11053", "11054", "11055", "11096", "11501", "11507", 
        "11509", "11510", "11514", "11516", "11518", "11520", "11530", "11531", 
        "11532", "11533", "11534", "11535", "11536", "11545", "11547", "11548", 
        "11549", "11550", "11551", "11552", "11553", "11554", "11555", "11556", 
        "11557", "11558", "11559", "11560", "11561", "11563", "11565", "11566", 
        "11568", "11569", "11570", "11571", "11572", "11575", "11576", "11577", 
        "11579", "11580", "11581", "11582", "11590", "11592", "11593", "11594", 
        "11595", "11596", "11597", "11598", "11599"
    ]
    for zip_code in nassau_zips:
        zip_to_borough[zip_code] = 'Nassau County'
    
    # Suffolk County (Long Island East)
    suffolk_zips = [
        "11701", "11702", "11703", "11704", "11705", "11706", "11707", "11708", 
        "11709", "11710", "11713", "11714", "11715", "11716", "11717", "11718", 
        "11719", "11720", "11721", "11722", "11724", "11725", "11726", "11727", 
        "11729", "11730", "11731", "11732", "11733", "11734", "11735", "11736", 
        "11737", "11738", "11739", "11740", "11741", "11742", "11743", "11746", 
        "11747", "11749", "11751", "11752", "11753", "11754", "11755", "11756", 
        "11757", "11758", "11760", "11763", "11764", "11766", "11767", "11768", 
        "11769", "11770", "11771", "11772", "11773", "11775", "11776", "11777", 
        "11778", "11779", "11780", "11782", "11783", "11784", "11786", "11787", 
        "11788", "11789", "11790", "11792", "11794", "11795", "11796", "11798", 
        "11901", "11930", "11931", "11932", "11933", "11934", "11935", "11937", 
        "11939", "11940", "11941", "11942", "11944", "11946", "11947", "11948", 
        "11949", "11950", "11951", "11952", "11953", "11954", "11955", "11956", 
        "11957", "11958", "11959", "11960", "11961", "11962", "11963", "11964", 
        "11965", "11967", "11968", "11969", "11970", "11971", "11972", "11973", 
        "11975", "11976", "11977", "11978", "11980"
    ]
    for zip_code in suffolk_zips:
        zip_to_borough[zip_code] = 'Suffolk County'
    
    # Bergen County, NJ
    bergen_zips = [
        "07010", "07020", "07024", "07026", "07027", "07028", "07030", "07031", 
        "07032", "07047", "07410", "07401", "07407", "07430", "07450", "07452", 
        "07458", "07463", "07465", "07481", "07603", "07604", "07605", "07606", 
        "07607", "07608", "07620", "07621", "07624", "07626", "07627", "07628", 
        "07630", "07631", "07632", "07640", "07641", "07642", "07643", "07644", 
        "07645", "07646", "07647", "07648", "07649", "07650", "07652", "07653", 
        "07656", "07657", "07660", "07661", "07662", "07663", "07666", "07670", 
        "07675", "07676", "07677", "07699"
    ]
    for zip_code in bergen_zips:
        zip_to_borough[zip_code] = 'Bergen County, NJ'
    
    # Hudson County, NJ
    hudson_zips = [
        "07030", "07087", "07093", "07094", "07097", "07302", "07304", "07305", 
        "07306", "07307", "07308", "07310", "07311", "07395", "07399", "07030", 
        "07047", "07086", "07087", "07093", "07094", "07097"
    ]
    for zip_code in hudson_zips:
        zip_to_borough[zip_code] = 'Hudson County, NJ'
    
    # Union County, NJ
    union_zips = [
        "07016", "07023", "07027", "07033", "07036", "07060", "07062", "07063", 
        "07064", "07065", "07066", "07067", "07076", "07080", "07083", "07090", 
        "07201", "07202", "07203", "07204", "07208", "07922", "07924"
    ]
    for zip_code in union_zips:
        zip_to_borough[zip_code] = 'Union County, NJ'
    
    # Essex County, NJ
    essex_zips = [
        "07003", "07017", "07028", "07042", "07043", "07044", "07050", "07052", 
        "07102", "07103", "07104", "07105", "07106", "07107", "07108", "07112", 
        "07114", "07175", "07184", "07188", "07189", "07191", "07192", "07193", 
        "07195", "07198", "07199"
    ]
    for zip_code in essex_zips:
        zip_to_borough[zip_code] = 'Essex County, NJ'
    
    # Rockland County, NY
    rockland_zips = [
        "10901", "10913", "10920", "10923", "10926", "10927", "10928", "10930", 
        "10931", "10932", "10952", "10954", "10956", "10960", "10962", "10965", 
        "10968", "10970", "10974", "10975", "10976", "10977", "10980", "10982", 
        "10983", "10984", "10986", "10987", "10989", "10994", "10996", "10997", 
        "10998"
    ]
    for zip_code in rockland_zips:
        zip_to_borough[zip_code] = 'Rockland County, NY'
    
    # Fairfield County, CT
    fairfield_zips = [
        "06801", "06802", "06803", "06804", "06807", "06810", "06811", "06820", 
        "06824", "06825", "06830", "06831", "06840", "06850", "06851", "06853", 
        "06854", "06855", "06856", "06880", "06881", "06883", "06888", "06890", 
        "06896", "06897", "06901", "06902", "06903", "06904", "06905", "06906", 
        "06907", "06910", "06911", "06912", "06913", "06914", "06926", "06927", 
        "06928"
    ]
    for zip_code in fairfield_zips:
        zip_to_borough[zip_code] = 'Fairfield County, CT'
    
    return zip_to_borough

def map_zip_to_borough(postal_code):
    """
    Map a ZIP code to its corresponding NYC borough or neighboring county
    
    Args:
        postal_code (str): ZIP code
        
    Returns:
        str: Borough/county name or 'Unknown' if not found
    """
    if pd.isna(postal_code) or postal_code in ['nan', 'None', '']:
        return 'Unknown'
    
    # Clean the postal code - convert to string and strip whitespace
    postal_str = str(postal_code).strip().upper()
    
    # Handle common variations
    if postal_str in ['NAN', 'NONE', '', '0', '0.0']:
        return 'Unknown'
    
    # Handle ZIP+4 format (e.g., "10001-1234")
    if '-' in postal_str:
        postal_str = postal_str.split('-')[0]
    
    # Handle decimal format (e.g., "10001.0")
    if '.' in postal_str:
        postal_str = postal_str.split('.')[0]
    
    # Pad with zeros if needed (e.g., "1001" -> "01001")
    if len(postal_str) == 4 and postal_str.isdigit():
        postal_str = '0' + postal_str
    
    # Only process if it's a valid 5-digit number
    if not (postal_str.isdigit() and len(postal_str) == 5):
        return 'Unknown'
    
    zip_to_borough = get_nyc_zip_borough_mapping()
    return zip_to_borough.get(postal_str, 'Unknown')

def analyze_substitute_data_by_borough(df_para, df_teacher):
    """
    Analyze substitute data by NYC borough and neighboring counties
    
    Args:
        df_para (pd.DataFrame): Paraprofessional data with Borough column
        df_teacher (pd.DataFrame): Teacher data with Borough column
        
    Returns:
        dict: Borough analysis results
    """
    borough_data = {}
    
    # Initialize borough data structure
    boroughs = ['Manhattan', 'Brooklyn', 'Queens', 'Bronx', 'Staten Island', 
                'Westchester County', 'Nassau County', 'Suffolk County', 
                'Bergen County, NJ', 'Hudson County, NJ', 'Union County, NJ', 
                'Essex County, NJ', 'Rockland County, NY', 'Fairfield County, CT', 
                'Unknown']
    
    for borough in boroughs:
        borough_data[borough] = {
            'para_total': 0,
            'para_eligible': 0,
            'para_complete': 0,
            'para_outstanding': 0,
            'teacher_total': 0,
            'teacher_eligible': 0,
            'teacher_complete': 0,
            'teacher_outstanding': 0,
            'para_completion_rate': 0,
            'teacher_completion_rate': 0
        }
    
    # Process paraprofessional data
    if df_para is not None and not df_para.empty:
        print(f"Processing {len(df_para)} paraprofessional records for geographic analysis...")
        
        # Get total counts by borough from ALL data
        para_total_by_borough = df_para.groupby('Borough').size().to_dict()
        print(f"Para totals by area: {para_total_by_borough}")
        
        # Only filter by Status for borough analysis - much simpler
        df_para_eligible = df_para[df_para['Status'].notna()].copy()
        
        print(f"Para records with status: {len(df_para_eligible)}")
        
        # Calculate completion status - just check if Status is 'COMP' vs 'OUT'
        df_para_eligible['Complete'] = (df_para_eligible['Status'] == 'COMP')
        
        # Group by borough
        para_borough_stats = df_para_eligible.groupby('Borough').agg({
            'Empl ID': 'count',
            'Complete': 'sum'
        }).reset_index()
        
        para_borough_stats.columns = ['Borough', 'Total_Eligible', 'Total_Complete']
        para_borough_stats['Total_Outstanding'] = para_borough_stats['Total_Eligible'] - para_borough_stats['Total_Complete']
        
        print(f"Para area stats:\n{para_borough_stats}")
        
        # Update borough data
        for _, row in para_borough_stats.iterrows():
            borough = row['Borough']
            if borough in borough_data:
                borough_data[borough]['para_total'] = para_total_by_borough.get(borough, 0)
                borough_data[borough]['para_eligible'] = row['Total_Eligible']
                borough_data[borough]['para_complete'] = row['Total_Complete']
                borough_data[borough]['para_outstanding'] = row['Total_Outstanding']
                borough_data[borough]['para_completion_rate'] = (
                    row['Total_Complete'] / row['Total_Eligible'] * 100
                    if row['Total_Eligible'] > 0 else 0
                )
    
    # Process teacher data
    if df_teacher is not None and not df_teacher.empty:
        print(f"Processing {len(df_teacher)} teacher records for geographic analysis...")
        
        # Get total counts by borough from ALL data
        teacher_total_by_borough = df_teacher.groupby('Borough').size().to_dict()
        print(f"Teacher totals by area: {teacher_total_by_borough}")
        
        # Only filter by Status for borough analysis - much simpler
        df_teacher_eligible = df_teacher[df_teacher['Status'].notna()].copy()
        
        print(f"Teacher records with status: {len(df_teacher_eligible)}")
        
        # Calculate completion status - just check if Status is 'COMP' vs 'OUT'
        df_teacher_eligible['Complete'] = (df_teacher_eligible['Status'] == 'COMP')
        
        # Group by borough
        teacher_borough_stats = df_teacher_eligible.groupby('Borough').agg({
            'Empl ID': 'count',
            'Complete': 'sum'
        }).reset_index()
        
        teacher_borough_stats.columns = ['Borough', 'Total_Eligible', 'Total_Complete']
        teacher_borough_stats['Total_Outstanding'] = teacher_borough_stats['Total_Eligible'] - teacher_borough_stats['Total_Complete']
        
        print(f"Teacher area stats:\n{teacher_borough_stats}")
        
        # Update borough data
        for _, row in teacher_borough_stats.iterrows():
            borough = row['Borough']
            if borough in borough_data:
                borough_data[borough]['teacher_total'] = teacher_total_by_borough.get(borough, 0)
                borough_data[borough]['teacher_eligible'] = row['Total_Eligible']
                borough_data[borough]['teacher_complete'] = row['Total_Complete']
                borough_data[borough]['teacher_outstanding'] = row['Total_Outstanding']
                borough_data[borough]['teacher_completion_rate'] = (
                    row['Total_Complete'] / row['Total_Eligible'] * 100
                    if row['Total_Eligible'] > 0 else 0
                )
    
    return borough_data

def get_zip_coordinates(zip_code):
    """
    Get latitude and longitude coordinates for a given ZIP code
    
    Args:
        zip_code (str): ZIP code to get coordinates for
        
    Returns:
        dict: Dictionary with 'lat' and 'lon' keys, or None if not found
    """
    # Comprehensive NYC area ZIP code coordinates
    zip_coords = {
        # Manhattan ZIP codes
        '10001': {'lat': 40.7505, 'lon': -73.9934}, '10002': {'lat': 40.7157, 'lon': -73.9860},
        '10003': {'lat': 40.7322, 'lon': -73.9867}, '10004': {'lat': 40.7047, 'lon': -74.0142},
        '10005': {'lat': 40.7069, 'lon': -74.0113}, '10006': {'lat': 40.7096, 'lon': -74.0130},
        '10007': {'lat': 40.7133, 'lon': -74.0070}, '10009': {'lat': 40.7268, 'lon': -73.9779},
        '10010': {'lat': 40.7397, 'lon': -73.9773}, '10011': {'lat': 40.7405, 'lon': -74.0014},
        '10012': {'lat': 40.7253, 'lon': -74.0034}, '10013': {'lat': 40.7200, 'lon': -74.0026},
        '10014': {'lat': 40.7342, 'lon': -74.0064}, '10016': {'lat': 40.7464, 'lon': -73.9756},
        '10017': {'lat': 40.7520, 'lon': -73.9717}, '10018': {'lat': 40.7549, 'lon': -73.9930},
        '10019': {'lat': 40.7658, 'lon': -73.9873}, '10020': {'lat': 40.7584, 'lon': -73.9738},
        '10021': {'lat': 40.7697, 'lon': -73.9598}, '10022': {'lat': 40.7575, 'lon': -73.9709},
        '10023': {'lat': 40.7765, 'lon': -73.9814}, '10024': {'lat': 40.7875, 'lon': -73.9745},
        '10025': {'lat': 40.7982, 'lon': -73.9671}, '10026': {'lat': 40.8017, 'lon': -73.9527},
        '10027': {'lat': 40.8115, 'lon': -73.9530}, '10028': {'lat': 40.7763, 'lon': -73.9532},
        '10029': {'lat': 40.7919, 'lon': -73.9441}, '10030': {'lat': 40.8182, 'lon': -73.9444},
        '10031': {'lat': 40.8251, 'lon': -73.9495}, '10032': {'lat': 40.8387, 'lon': -73.9417},
        '10033': {'lat': 40.8502, 'lon': -73.9342}, '10034': {'lat': 40.8677, 'lon': -73.9212},
        '10035': {'lat': 40.7957, 'lon': -73.9389}, '10036': {'lat': 40.7590, 'lon': -73.9845},
        '10037': {'lat': 40.8142, 'lon': -73.9370}, '10038': {'lat': 40.7086, 'lon': -74.0020},
        '10039': {'lat': 40.8267, 'lon': -73.9363}, '10040': {'lat': 40.8588, 'lon': -73.9302},
        
        # Brooklyn ZIP codes (sample - major ones)
        '11201': {'lat': 40.6945, 'lon': -73.9901}, '11203': {'lat': 40.6514, 'lon': -73.9342},
        '11204': {'lat': 40.6189, 'lon': -73.9842}, '11205': {'lat': 40.6945, 'lon': -73.9665},
        '11206': {'lat': 40.7022, 'lon': -73.9421}, '11207': {'lat': 40.6720, 'lon': -73.8946},
        '11208': {'lat': 40.6591, 'lon': -73.8736}, '11209': {'lat': 40.6226, 'lon': -74.0305},
        '11210': {'lat': 40.6282, 'lon': -73.9473}, '11211': {'lat': 40.7115, 'lon': -73.9535},
        '11212': {'lat': 40.6627, 'lon': -73.9063}, '11213': {'lat': 40.6711, 'lon': -73.9363},
        '11214': {'lat': 40.5993, 'lon': -73.9942}, '11215': {'lat': 40.6628, 'lon': -73.9865},
        '11216': {'lat': 40.6808, 'lon': -73.9419}, '11217': {'lat': 40.6806, 'lon': -73.9779},
        '11218': {'lat': 40.6434, 'lon': -73.9773}, '11219': {'lat': 40.6323, 'lon': -73.9963},
        '11220': {'lat': 40.6412, 'lon': -74.0170}, '11221': {'lat': 40.6911, 'lon': -73.9275},
        '11222': {'lat': 40.7284, 'lon': -73.9474}, '11223': {'lat': 40.5969, 'lon': -73.9732},
        '11224': {'lat': 40.5775, 'lon': -73.9874}, '11225': {'lat': 40.6622, 'lon': -73.9541},
        '11226': {'lat': 40.6465, 'lon': -73.9563}, '11228': {'lat': 40.6166, 'lon': -74.0120},
        '11229': {'lat': 40.6008, 'lon': -73.9442}, '11230': {'lat': 40.6226, 'lon': -73.9652},
        '11231': {'lat': 40.6782, 'lon': -74.0067}, '11232': {'lat': 40.6569, 'lon': -74.0090},
        '11233': {'lat': 40.6783, 'lon': -73.9196}, '11234': {'lat': 40.5992, 'lon': -73.9192},
        '11235': {'lat': 40.5847, 'lon': -73.9484}, '11236': {'lat': 40.6396, 'lon': -73.9014},
        '11237': {'lat': 40.7040, 'lon': -73.8811}, '11238': {'lat': 40.6795, 'lon': -73.9646},
        '11239': {'lat': 40.6471, 'lon': -73.8705}, '11249': {'lat': 40.7208, 'lon': -73.9425},
        '11251': {'lat': 40.6901, 'lon': -73.9901}, '11252': {'lat': 40.6901, 'lon': -73.9901},
        
        # Queens ZIP codes (sample - major ones)
        '11004': {'lat': 40.7450, 'lon': -73.7713}, '11005': {'lat': 40.7480, 'lon': -73.7713},
        '11101': {'lat': 40.7359, 'lon': -73.9392}, '11102': {'lat': 40.7734, 'lon': -73.9196},
        '11103': {'lat': 40.7634, 'lon': -73.9118}, '11104': {'lat': 40.7443, 'lon': -73.9196},
        '11105': {'lat': 40.7789, 'lon': -73.9067}, '11106': {'lat': 40.7628, 'lon': -73.9302},
        '11354': {'lat': 40.7687, 'lon': -73.8370}, '11355': {'lat': 40.7498, 'lon': -73.8201},
        '11356': {'lat': 40.7848, 'lon': -73.8468}, '11357': {'lat': 40.7858, 'lon': -73.8269},
        '11358': {'lat': 40.7608, 'lon': -73.7958}, '11360': {'lat': 40.7828, 'lon': -73.7784},
        '11361': {'lat': 40.7638, 'lon': -73.7738}, '11362': {'lat': 40.7578, 'lon': -73.7678},
        '11363': {'lat': 40.7718, 'lon': -73.7535}, '11364': {'lat': 40.7448, 'lon': -73.7735},
        '11365': {'lat': 40.7407, 'lon': -73.7949}, '11366': {'lat': 40.7288, 'lon': -73.7949},
        '11367': {'lat': 40.7318, 'lon': -73.8249}, '11368': {'lat': 40.7508, 'lon': -73.8549},
        '11369': {'lat': 40.7628, 'lon': -73.8649}, '11370': {'lat': 40.7648, 'lon': -73.8949},
        '11372': {'lat': 40.7548, 'lon': -73.8749}, '11373': {'lat': 40.7408, 'lon': -73.8749},
        '11374': {'lat': 40.7288, 'lon': -73.8549}, '11375': {'lat': 40.7198, 'lon': -73.8349},
        '11377': {'lat': 40.7437, 'lon': -73.9049}, '11378': {'lat': 40.7167, 'lon': -73.8949},
        '11379': {'lat': 40.7217, 'lon': -73.8749}, '11385': {'lat': 40.7017, 'lon': -73.8749},
        '11411': {'lat': 40.6917, 'lon': -73.7449}, '11412': {'lat': 40.6997, 'lon': -73.7649},
        '11413': {'lat': 40.6717, 'lon': -73.7649}, '11414': {'lat': 40.6577, 'lon': -73.8449},
        '11415': {'lat': 40.7067, 'lon': -73.8249}, '11416': {'lat': 40.6837, 'lon': -73.8449},
        '11417': {'lat': 40.6777, 'lon': -73.8349}, '11418': {'lat': 40.6977, 'lon': -73.8349},
        '11419': {'lat': 40.6917, 'lon': -73.8149}, '11420': {'lat': 40.6677, 'lon': -73.7649},
        '11421': {'lat': 40.6937, 'lon': -73.8649}, '11422': {'lat': 40.6597, 'lon': -73.7349},
        '11423': {'lat': 40.7097, 'lon': -73.7649}, '11426': {'lat': 40.7377, 'lon': -73.7049},
        '11427': {'lat': 40.7297, 'lon': -73.7249}, '11428': {'lat': 40.7177, 'lon': -73.7449},
        '11429': {'lat': 40.7087, 'lon': -73.7349}, '11432': {'lat': 40.7147, 'lon': -73.7949},
        '11433': {'lat': 40.6987, 'lon': -73.7949}, '11434': {'lat': 40.6747, 'lon': -73.7749},
        '11435': {'lat': 40.7007, 'lon': -73.8049}, '11436': {'lat': 40.6857, 'lon': -73.7749},
        
        # Bronx ZIP codes (sample - major ones)
        '10451': {'lat': 40.8204, 'lon': -73.9252}, '10452': {'lat': 40.8407, 'lon': -73.9240},
        '10453': {'lat': 40.8518, 'lon': -73.9123}, '10454': {'lat': 40.8088, 'lon': -73.9187},
        '10455': {'lat': 40.8142, 'lon': -73.9089}, '10456': {'lat': 40.8278, 'lon': -73.9098},
        '10457': {'lat': 40.8476, 'lon': -73.9009}, '10458': {'lat': 40.8618, 'lon': -73.8883},
        '10459': {'lat': 40.8238, 'lon': -73.8942}, '10460': {'lat': 40.8418, 'lon': -73.8783},
        '10461': {'lat': 40.8478, 'lon': -73.8353}, '10462': {'lat': 40.8418, 'lon': -73.8604},
        '10463': {'lat': 40.8795, 'lon': -73.9073}, '10464': {'lat': 40.8445, 'lon': -73.7854},
        '10465': {'lat': 40.8265, 'lon': -73.8254}, '10466': {'lat': 40.8895, 'lon': -73.8504},
        '10467': {'lat': 40.8735, 'lon': -73.8783}, '10468': {'lat': 40.8678, 'lon': -73.9004},
        '10469': {'lat': 40.8678, 'lon': -73.8504}, '10470': {'lat': 40.8895, 'lon': -73.8354},
        '10471': {'lat': 40.9045, 'lon': -73.8984}, '10472': {'lat': 40.8298, 'lon': -73.8704},
        '10473': {'lat': 40.8198, 'lon': -73.8504}, '10474': {'lat': 40.8098, 'lon': -73.8904},
        '10475': {'lat': 40.8795, 'lon': -73.8254},
        
        # Staten Island ZIP codes
        '10301': {'lat': 40.6348, 'lon': -74.0776}, '10302': {'lat': 40.6278, 'lon': -74.0987},
        '10303': {'lat': 40.6348, 'lon': -74.0987}, '10304': {'lat': 40.6098, 'lon': -74.0865},
        '10305': {'lat': 40.5898, 'lon': -74.0754}, '10306': {'lat': 40.5698, 'lon': -74.1243},
        '10307': {'lat': 40.5098, 'lon': -74.2443}, '10308': {'lat': 40.5548, 'lon': -74.1654},
        '10309': {'lat': 40.5298, 'lon': -74.2054}, '10310': {'lat': 40.6298, 'lon': -74.1154},
        '10311': {'lat': 40.6098, 'lon': -74.1654}, '10312': {'lat': 40.5548, 'lon': -74.1954},
        '10313': {'lat': 40.5798, 'lon': -74.2054}, '10314': {'lat': 40.5998, 'lon': -74.1654}
    }
    
    # Clean the ZIP code input
    clean_zip = str(zip_code).split('.')[0].split('-')[0].strip()
    
    # Return coordinates if found
    return zip_coords.get(clean_zip)
