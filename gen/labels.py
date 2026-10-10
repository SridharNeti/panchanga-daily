"""Names used on the site, in English and Telugu. Index 0 = first item.

Telugu spellings are our own (PyJHora's Telugu lists have several errors);
please have a Telugu reader proofread before publishing.
"""

SAMVATSARA = {
    "en": ["Prabhava", "Vibhava", "Shukla", "Pramoduta", "Prajotpatti", "Angirasa", "Shrimukha", "Bhava",
           "Yuva", "Dhata", "Ishvara", "Bahudhanya", "Pramathi", "Vikrama", "Vrisha", "Chitrabhanu",
           "Svabhanu", "Tarana", "Parthiva", "Vyaya", "Sarvajit", "Sarvadhari", "Virodhi", "Vikriti",
           "Khara", "Nandana", "Vijaya", "Jaya", "Manmatha", "Durmukhi", "Hevilambi", "Vilambi",
           "Vikari", "Sharvari", "Plava", "Shubhakrit", "Shobhakrit", "Krodhi", "Vishvavasu", "Parabhava",
           "Plavanga", "Kilaka", "Saumya", "Sadharana", "Virodhikrit", "Paridhavi", "Pramadicha", "Ananda",
           "Rakshasa", "Nala", "Pingala", "Kalayukti", "Siddharthi", "Raudri", "Durmati", "Dundubhi",
           "Rudhirodgari", "Raktakshi", "Krodhana", "Akshaya"],
    "te": ["ప్రభవ", "విభవ", "శుక్ల", "ప్రమోదూత", "ప్రజోత్పత్తి", "ఆంగీరస", "శ్రీముఖ", "భావ",
           "యువ", "ధాత", "ఈశ్వర", "బహుధాన్య", "ప్రమాది", "విక్రమ", "వృష", "చిత్రభాను",
           "స్వభాను", "తారణ", "పార్థివ", "వ్యయ", "సర్వజిత్", "సర్వధారి", "విరోధి", "వికృతి",
           "ఖర", "నందన", "విజయ", "జయ", "మన్మథ", "దుర్ముఖి", "హేవిళంబి", "విళంబి",
           "వికారి", "శార్వరి", "ప్లవ", "శుభకృత్", "శోభకృత్", "క్రోధి", "విశ్వావసు", "పరాభవ",
           "ప్లవంగ", "కీలక", "సౌమ్య", "సాధారణ", "విరోధికృత్", "పరీధావి", "ప్రమాదీచ", "ఆనంద",
           "రాక్షస", "నల", "పింగళ", "కాళయుక్తి", "సిద్ధార్థి", "రౌద్రి", "దుర్మతి", "దుందుభి",
           "రుధిరోద్గారి", "రక్తాక్షి", "క్రోధన", "అక్షయ"],
}

AYANA = {"en": ["Uttarayana", "Dakshinayana"], "te": ["ఉత్తరాయణం", "దక్షిణాయనం"]}

RITU = {
    "en": ["Vasanta", "Grishma", "Varsha", "Sharad", "Hemanta", "Shishira"],
    "te": ["వసంత", "గ్రీష్మ", "వర్ష", "శరద్", "హేమంత", "శిశిర"],
}

MASA = {
    "en": ["Chaitra", "Vaishakha", "Jyeshtha", "Ashadha", "Shravana", "Bhadrapada", "Ashvayuja",
           "Kartika", "Margashira", "Pushya", "Magha", "Phalguna"],
    "te": ["చైత్రం", "వైశాఖం", "జ్యేష్ఠం", "ఆషాఢం", "శ్రావణం", "భాద్రపదం", "ఆశ్వయుజం",
           "కార్తికం", "మార్గశిరం", "పుష్యం", "మాఘం", "ఫాల్గుణం"],
}
ADHIKA = {"en": "Adhika", "te": "అధిక"}

PAKSHA = {"en": ["Shukla", "Krishna"], "te": ["శుక్ల", "కృష్ణ"]}

# 15 names; Purnima at index 14, Amavasya handled separately (tithi 30).
TITHI = {
    "en": ["Pratipada", "Dvitiya", "Tritiya", "Chaturthi", "Panchami", "Shashthi", "Saptami", "Ashtami",
           "Navami", "Dashami", "Ekadashi", "Dvadashi", "Trayodashi", "Chaturdashi", "Purnima"],
    "te": ["పాడ్యమి", "విదియ", "తదియ", "చవితి", "పంచమి", "షష్ఠి", "సప్తమి", "అష్టమి",
           "నవమి", "దశమి", "ఏకాదశి", "ద్వాదశి", "త్రయోదశి", "చతుర్దశి", "పౌర్ణమి"],
}
AMAVASYA = {"en": "Amavasya", "te": "అమావాస్య"}

VARA = {  # Monday = 0, matching datetime.weekday()
    "en": ["Monday (Somavara)", "Tuesday (Mangalavara)", "Wednesday (Budhavara)", "Thursday (Guruvara)",
           "Friday (Shukravara)", "Saturday (Shanivara)", "Sunday (Bhanuvara)"],
    "te": ["సోమవారం", "మంగళవారం", "బుధవారం", "గురువారం", "శుక్రవారం", "శనివారం", "ఆదివారం"],
}

NAKSHATRA = {
    "en": ["Ashvini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya",
           "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati",
           "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana",
           "Dhanishtha", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"],
    "te": ["అశ్విని", "భరణి", "కృత్తిక", "రోహిణి", "మృగశిర", "ఆర్ద్ర", "పునర్వసు", "పుష్యమి",
           "ఆశ్లేష", "మఘ", "పూర్వ ఫల్గుణి", "ఉత్తర ఫల్గుణి", "హస్త", "చిత్త", "స్వాతి",
           "విశాఖ", "అనూరాధ", "జ్యేష్ఠ", "మూల", "పూర్వాషాఢ", "ఉత్తరాషాఢ", "శ్రవణం",
           "ధనిష్ఠ", "శతభిషం", "పూర్వాభాద్ర", "ఉత్తరాభాద్ర", "రేవతి"],
}

YOGA = {
    "en": ["Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda", "Sukarma", "Dhriti",
           "Shula", "Ganda", "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra", "Siddhi", "Vyatipata",
           "Variyan", "Parigha", "Shiva", "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma", "Aindra",
           "Vaidhriti"],
    "te": ["విష్కంభ", "ప్రీతి", "ఆయుష్మాన్", "సౌభాగ్య", "శోభన", "అతిగండ", "సుకర్మ", "ధృతి",
           "శూల", "గండ", "వృద్ధి", "ధ్రువ", "వ్యాఘాత", "హర్షణ", "వజ్ర", "సిద్ధి", "వ్యతీపాత",
           "వరీయాన్", "పరిఘ", "శివ", "సిద్ధ", "సాధ్య", "శుభ", "శుక్ల", "బ్రహ్మ", "ఐంద్ర",
           "వైధృతి"],
}

# Karana: 7 movable repeat; 4 fixed at the ends of the month.
KARANA_MOVABLE = {
    "en": ["Bava", "Balava", "Kaulava", "Taitila", "Garaja", "Vanija", "Vishti (Bhadra)"],
    "te": ["బవ", "బాలవ", "కౌలవ", "తైతిల", "గరజ", "వణిజ", "విష్టి (భద్ర)"],
}
KARANA_FIXED = {
    "en": ["Kimstughna", "Shakuni", "Chatushpada", "Naga"],
    "te": ["కింస్తుఘ్న", "శకుని", "చతుష్పాద", "నాగ"],
}

RASI = {
    "en": ["Mesha", "Vrishabha", "Mithuna", "Karkataka", "Simha", "Kanya", "Tula", "Vrischika",
           "Dhanus", "Makara", "Kumbha", "Mina"],
    "te": ["మేషం", "వృషభం", "మిథునం", "కర్కాటకం", "సింహం", "కన్య", "తుల", "వృశ్చికం",
           "ధనుస్సు", "మకరం", "కుంభం", "మీనం"],
}

CITY_TE = {"lombard": "లోంబార్డ్", "naperville": "నేపర్‌విల్", "normal": "నార్మల్", "dallas": "డాలస్", "raleigh": "రాలీ",
           "hyderabad": "హైదరాబాద్", "mumbai": "ముంబై", "kolkata": "కోల్‌కతా", "bengaluru": "బెంగళూరు",
           "chennai": "చెన్నై"}
