from .ml.predict import model_metadata, predict_full, rank_dataset_symptom_matches
from .nlp import extract_symptoms, urgent_flags

# ── Disease-Specific Knowledge Base ──────────────────────────────────────────
# For every disease the ML model can predict, we provide targeted advice.
# Fallback generic advice is used for diseases not in this dict.

DISEASE_KB = {
    "Fungal infection": {
        "advice": [
            "Keep the affected area clean and completely dry",
            "Apply antifungal cream or powder as recommended by a pharmacist",
            "Wear loose, breathable cotton clothing",
            "Avoid sharing towels, socks, or personal items",
            "Change and wash socks and underwear daily",
        ],
        "safety": [
            "Monitor for rash spreading to new areas",
            "Do not scratch — it spreads the infection and risks secondary bacterial infection",
            "If near the scalp, avoid sharing combs or hair accessories",
        ],
        "doctor": "See a doctor if the rash is spreading rapidly, accompanied by fever, or doesn't improve after 2 weeks of over-the-counter treatment.",
    },
    "Allergy": {
        "advice": [
            "Identify and avoid your allergy triggers (pollen, dust, pet dander, certain foods)",
            "Keep windows closed during high-pollen seasons",
            "Use air purifiers with HEPA filters indoors",
            "Take antihistamines as directed by your pharmacist",
            "Stay hydrated and rinse your nose with saline spray",
        ],
        "safety": [
            "Avoid known allergens strictly if you have a history of severe reactions",
            "Always carry an antihistamine tablet if you have known allergies",
            "Know the difference between a mild reaction and anaphylaxis",
        ],
        "doctor": "Seek immediate medical attention if you experience difficulty breathing, swelling of the lips or tongue, or feel faint after allergen exposure — these are signs of anaphylaxis.",
    },
    "GERD": {
        "advice": [
            "Avoid large meals — eat smaller, more frequent portions",
            "Don't lie down for at least 2–3 hours after eating",
            "Elevate the head of your bed by 6–8 inches",
            "Avoid trigger foods: spicy food, citrus, tomatoes, chocolate, coffee, alcohol",
            "Maintain a healthy weight and avoid tight-fitting clothing",
        ],
        "safety": [
            "Do not ignore persistent heartburn lasting more than 2 weeks",
            "Monitor for difficulty swallowing (dysphagia) — seek urgent care",
            "Avoid aspirin and NSAIDs which can worsen acid reflux",
        ],
        "doctor": "Consult a gastroenterologist if symptoms occur more than twice a week, disturb your sleep, or you notice difficulty swallowing or unintended weight loss.",
    },
    "Diabetes": {
        "advice": [
            "Monitor blood glucose levels regularly as advised by your doctor",
            "Follow a low-glycemic, balanced diet — reduce refined sugars and white carbs",
            "Exercise for at least 30 minutes most days of the week",
            "Stay well-hydrated and avoid sugary drinks",
            "Take prescribed medications consistently and don't skip doses",
        ],
        "safety": [
            "Learn to recognise hypoglycemia signs: shakiness, sweating, confusion",
            "Always carry a fast sugar source (glucose tablets, juice) for low blood sugar episodes",
            "Monitor your feet daily for any cuts, sores, or changes in sensation",
        ],
        "doctor": "Regular HbA1c tests every 3 months are important. See your doctor immediately if blood glucose is very high (>300 mg/dL), you feel extremely thirsty and confused, or you notice vision changes.",
    },
    "Hypertension": {
        "advice": [
            "Reduce salt intake to under 2,300 mg per day",
            "Adopt the DASH diet (fruits, vegetables, lean protein, low-fat dairy)",
            "Exercise regularly — aim for 150 minutes of moderate activity per week",
            "Limit alcohol and completely avoid tobacco",
            "Manage stress through meditation, yoga, or breathing techniques",
        ],
        "safety": [
            "Take blood pressure medication exactly as prescribed — don't stop suddenly",
            "Monitor BP regularly at home with a validated device",
            "Headaches with nausea, vision changes, or nose bleeds can indicate a hypertensive crisis",
        ],
        "doctor": "If your BP readings consistently exceed 180/120 mmHg, or you experience severe headache, chest pain, or difficulty breathing, seek emergency care immediately.",
    },
    "Migraine": {
        "advice": [
            "Keep a migraine diary to identify your personal triggers",
            "Common triggers include stress, irregular sleep, dehydration, and certain foods (aged cheese, red wine, MSG)",
            "Rest in a quiet, dark room during an attack",
            "Apply a cold compress to your forehead",
            "Stay well-hydrated and maintain regular sleep patterns",
        ],
        "safety": [
            "Do not overuse pain medications — medication overuse can worsen headaches",
            "Avoid screens and bright lights during an attack",
            "Have a plan with your doctor for severe attacks",
        ],
        "doctor": "Consult a neurologist if migraines occur more than 4 times a month, if pain is unusually severe and sudden ('thunderclap headache'), or if accompanied by fever, stiff neck, or vision changes.",
    },
    "Common Cold": {
        "advice": [
            "Get plenty of rest — sleep is when your immune system fights infection",
            "Stay well-hydrated: water, warm broth, herbal teas",
            "Gargle with warm salt water to soothe a sore throat",
            "Use saline nasal spray or steam inhalation for congestion",
            "Honey and lemon in warm water can soothe symptoms",
        ],
        "safety": [
            "Avoid spreading the virus — wash hands frequently, cover your cough",
            "Monitor for high fever (above 103°F / 39.4°C)",
            "Watch for secondary infections: ear pain, sinus pain, or productive cough with colored phlegm",
        ],
        "doctor": "See a doctor if symptoms worsen after 7–10 days, fever is very high, you have difficulty breathing, or you develop chest pain.",
    },
    "Pneumonia": {
        "advice": [
            "Rest completely — do not push through normal activities",
            "Drink plenty of fluids to help loosen mucus",
            "Complete the full course of any prescribed antibiotics",
            "Use a humidifier to keep air moist and ease breathing",
            "Sleep propped up slightly to ease breathing",
        ],
        "safety": [
            "Pneumonia can be serious — do not delay medical evaluation",
            "Watch for difficulty breathing, lips or fingernails turning blue, confusion, or dropping oxygen levels",
            "Elderly patients and young children are at higher risk of complications",
        ],
        "doctor": "Pneumonia requires medical evaluation. Go to the emergency room immediately if you have severe breathing difficulty, blood in cough, or feel faint or confused.",
    },
    "Bronchial Asthma": {
        "advice": [
            "Use your reliever inhaler (usually blue) exactly as prescribed",
            "Identify and avoid your asthma triggers (dust, pollen, smoke, cold air, exercise)",
            "Always carry your rescue inhaler with you",
            "Follow the asthma action plan given by your doctor",
            "Vacuum and dust regularly; use allergen-proof pillow covers",
        ],
        "safety": [
            "Never ignore worsening symptoms — use your reliever inhaler at the first sign",
            "If your reliever inhaler isn't helping after 5–10 minutes, seek emergency care",
            "Tobacco smoke is a major trigger — avoid it completely",
        ],
        "doctor": "Go to the emergency room immediately if you are severely short of breath, cannot speak in full sentences, have a blue tinge around lips, or your reliever inhaler gives no relief.",
    },
    "Dengue": {
        "advice": [
            "Rest completely and keep yourself comfortable",
            "Drink plenty of fluids: ORS, coconut water, fruit juices, water",
            "Take paracetamol (acetaminophen) for fever and pain — NOT ibuprofen or aspirin",
            "Monitor platelet count as directed by your doctor",
            "Use mosquito nets and repellents to prevent spreading the virus to others via mosquitoes",
        ],
        "safety": [
            "Dengue can cause severe bleeding — monitor for unusual bruising, bleeding gums, or blood in urine/stool",
            "Do NOT take aspirin, ibuprofen, or diclofenac — these increase bleeding risk",
            "Warning signs: severe abdominal pain, persistent vomiting, rapid breathing, fatigue",
        ],
        "doctor": "Dengue is a medical emergency — seek care immediately if you notice bleeding, severe stomach pain, breathing difficulty, extreme fatigue, or restlessness.",
    },
    "Malaria": {
        "advice": [
            "Complete the full course of antimalarial treatment as prescribed",
            "Rest and keep yourself warm during chills",
            "Drink plenty of fluids to prevent dehydration",
            "Use mosquito nets (preferably insecticide-treated) while sleeping",
            "Use mosquito repellent on skin and clothing",
        ],
        "safety": [
            "Malaria can become life-threatening quickly — do not delay medical diagnosis",
            "Monitor for signs of cerebral malaria: confusion, seizures, loss of consciousness",
            "Prevent mosquito bites to avoid spreading to others",
        ],
        "doctor": "Malaria requires prompt medical treatment. Seek immediate care if you have high fever with chills, confusion, or breathing difficulty.",
    },
    "Typhoid": {
        "advice": [
            "Complete the full antibiotic course prescribed by your doctor",
            "Drink only boiled or purified water",
            "Eat soft, easily digestible foods: rice, toast, bananas, boiled vegetables",
            "Maintain strict personal hygiene — wash hands before eating and after using the toilet",
            "Rest adequately and avoid strenuous activity",
        ],
        "safety": [
            "Typhoid is highly contagious through contaminated food and water",
            "Do not handle food for others while infected",
            "Watch for intestinal bleeding or perforation: severe abdominal pain, rigid abdomen",
        ],
        "doctor": "Typhoid requires antibiotic treatment. Seek immediate care for severe abdominal pain, high persistent fever above 103°F, or confusion.",
    },
    "Chicken pox": {
        "advice": [
            "Trim nails short to prevent scratching and secondary skin infections",
            "Apply calamine lotion to soothe itchy blisters",
            "Take lukewarm oatmeal baths to relieve itching",
            "Wear loose, soft cotton clothing",
            "Stay home and isolated until all blisters have crusted over",
        ],
        "safety": [
            "Do NOT give aspirin to children with chickenpox — risk of Reye's syndrome",
            "Chickenpox is highly contagious — avoid contact with pregnant women, newborns, and immunocompromised people",
            "Watch for infected blisters (red, warm, oozing) requiring antibiotics",
        ],
        "doctor": "Consult a doctor if you develop a high fever, the rash becomes infected, you have breathing difficulty, or you have a compromised immune system.",
    },
    "Jaundice": {
        "advice": [
            "Rest completely and avoid strenuous activity",
            "Eat a low-fat diet with plenty of fruits, vegetables, and whole grains",
            "Drink plenty of water and fresh juice (especially sugarcane juice)",
            "Avoid alcohol completely",
            "Avoid fatty, fried, and processed foods",
        ],
        "safety": [
            "Jaundice is usually a sign of an underlying condition — identify and treat the cause",
            "Avoid all alcohol and medications metabolised by the liver without consulting your doctor",
            "Watch for dark urine, pale stools, and intense itching",
        ],
        "doctor": "Consult a doctor promptly if you have jaundice. Seek immediate care if you are confused, have severe abdominal pain, or are vomiting blood.",
    },
    "Tuberculosis": {
        "advice": [
            "Complete the full 6-month antibiotic course — stopping early causes drug-resistant TB",
            "Cover your mouth when coughing or sneezing",
            "Ensure rooms are well-ventilated",
            "Eat a nutritious, protein-rich diet to support recovery",
            "Avoid tobacco and alcohol",
        ],
        "safety": [
            "TB is spread through air — wear a mask in confined spaces during treatment",
            "All close contacts should be screened for TB",
            "Never skip doses — incomplete treatment creates multidrug-resistant TB",
        ],
        "doctor": "TB is treated by infectious disease specialists. Do not self-treat or stop medication early under any circumstances.",
    },
    "Urinary tract infection": {
        "advice": [
            "Drink 8–10 glasses of water daily to flush bacteria",
            "Urinate frequently — don't hold urine for long periods",
            "Wipe from front to back after using the toilet",
            "Avoid irritants: caffeine, alcohol, spicy food during infection",
            "Complete the full course of prescribed antibiotics",
        ],
        "safety": [
            "Do not ignore UTI symptoms — untreated UTIs can spread to the kidneys",
            "Watch for fever with back/flank pain — may indicate kidney involvement",
            "Women who get recurrent UTIs should discuss prevention with their doctor",
        ],
        "doctor": "See a doctor for prescription antibiotics. Go to the emergency room if you have high fever, chills, severe back pain, or vomiting.",
    },
    "Hypoglycemia": {
        "advice": [
            "Follow the 15-15 rule: eat 15g of fast-acting carbs, wait 15 minutes, recheck blood sugar",
            "Keep glucose tablets, juice, or hard candy always accessible",
            "Eat regular meals and never skip them if on diabetes medication",
            "Always carry a medical ID identifying you as diabetic",
            "Inform family and colleagues about hypoglycemia management",
        ],
        "safety": [
            "Do not drive or operate machinery when blood sugar is low",
            "If unconscious, do not try to drink — glucagon injection or emergency services needed",
            "Track triggers: excessive exercise, skipped meals, or medication timing",
        ],
        "doctor": "Seek emergency care immediately for unconsciousness, seizures, or inability to swallow. Discuss frequent hypoglycemic episodes with your endocrinologist.",
    },
    "Heart attack": {
        "advice": [],
        "safety": [
            "🚨 CALL EMERGENCY SERVICES IMMEDIATELY (112 / 911)",
            "Chew an adult aspirin (325mg) if not allergic and if available",
            "Rest completely — do not walk around",
            "Loosen tight clothing around neck and chest",
            "If trained, be ready to perform CPR if the person loses consciousness",
        ],
        "doctor": "This is a LIFE-THREATENING EMERGENCY. Call emergency services immediately. Every minute of delay causes more heart muscle damage.",
        "urgent": True,
    },
    "Hypothyroidism": {
        "advice": [
            "Take thyroid hormone replacement (levothyroxine) at the same time every day on an empty stomach",
            "Wait 30–60 minutes before eating or taking other medications after thyroid medication",
            "Eat a balanced diet — consider selenium-rich foods (Brazil nuts, fish)",
            "Exercise regularly to combat fatigue and weight gain",
            "Monitor for signs of over-medication: anxiety, rapid heartbeat, weight loss",
        ],
        "safety": [
            "Never stop thyroid medication without your doctor's advice",
            "Certain foods (raw cruciferous vegetables, soy) can interfere with thyroid function if eaten in large amounts",
            "Get TSH levels checked every 6–12 months",
        ],
        "doctor": "Hypothyroidism requires lifelong management with regular TSH monitoring. Consult your endocrinologist if symptoms persist despite medication.",
    },
    "Hyperthyroidism": {
        "advice": [
            "Avoid iodine-rich foods (seaweed, iodized salt) unless told otherwise",
            "Rest often — your metabolism is running too fast",
            "Avoid stimulants: caffeine, alcohol, tobacco",
            "Eat high-calorie, nutritious food to compensate for increased metabolism",
            "Wear sunglasses if experiencing eye symptoms",
        ],
        "safety": [
            "Hyperthyroid crisis (thyroid storm) is life-threatening — seek emergency care for extremely rapid heartbeat, high fever, and confusion",
            "Take prescribed antithyroid medications consistently",
            "Avoid sudden iodine loading (contrast dyes, medications with iodine)",
        ],
        "doctor": "Consult an endocrinologist promptly. Seek immediate care for racing heartbeat above 150 bpm, high fever, or confusion.",
    },
    "Acne": {
        "advice": [
            "Wash your face twice daily with a gentle, non-comedogenic cleanser",
            "Use oil-free, non-comedogenic moisturiser and sunscreen",
            "Avoid picking, squeezing, or popping pimples",
            "Use salicylic acid or benzoyl peroxide products as directed",
            "Change pillowcases every 2–3 days",
        ],
        "safety": [
            "Avoid harsh scrubbing which can worsen inflammation",
            "Some medications (certain contraceptives, steroids) can worsen acne — discuss with your doctor",
            "Sun exposure can worsen post-acne dark spots — use SPF 30+",
        ],
        "doctor": "See a dermatologist for moderate-to-severe acne, cystic acne, or if over-the-counter products haven't helped after 3 months.",
    },
    "Psoriasis": {
        "advice": [
            "Moisturise skin daily with thick creams or ointments",
            "Identify and avoid your triggers (stress, infections, certain medications, alcohol)",
            "Take short, lukewarm showers instead of long hot baths",
            "Use mild, fragrance-free soaps and detergents",
            "Get moderate sun exposure but avoid sunburn",
        ],
        "safety": [
            "Do not scratch or pick plaques — infection risk",
            "Monitor for joint pain — psoriatic arthritis affects up to 30% of psoriasis patients",
            "Certain medications (lithium, beta-blockers, antimalarials) can trigger flares",
        ],
        "doctor": "Consult a dermatologist for prescription treatments. See a rheumatologist if you develop joint pain or swelling.",
    },
    "Arthritis": {
        "advice": [
            "Exercise regularly with low-impact activities: swimming, cycling, yoga",
            "Apply ice packs for acute swelling; warm compresses for stiffness",
            "Maintain a healthy weight to reduce load on joints",
            "Use assistive devices (cane, splints) when needed",
            "Take prescribed anti-inflammatory medications with food",
        ],
        "safety": [
            "Do not overexert painful joints — rest when pain is severe",
            "Monitor for joint deformity or reduced range of motion",
            "Long-term NSAID use can cause stomach and kidney problems — take with food",
        ],
        "doctor": "Consult a rheumatologist for proper diagnosis and disease-modifying treatment. Early treatment prevents joint damage.",
    },
    "Osteoarthristis": {
        "advice": [
            "Maintain a healthy weight to reduce joint stress",
            "Exercise regularly: swimming, walking, and strength training support joint health",
            "Use hot and cold therapy alternately for pain and stiffness",
            "Consider physiotherapy for personalised exercise programs",
            "Use supportive footwear with good cushioning",
        ],
        "safety": [
            "Avoid high-impact activities that stress damaged joints",
            "Monitor for sudden increase in pain or swelling — may indicate joint injury",
            "Avoid prolonged kneeling or squatting",
        ],
        "doctor": "See an orthopaedic surgeon if pain is limiting daily function. Joint replacement may be considered in severe cases.",
    },
    "(vertigo) Paroymsal  Positional Vertigo": {
        "advice": [
            "Perform the Epley manoeuvre as instructed by your physiotherapist",
            "Move slowly when getting up from bed — sit on the edge first",
            "Avoid positions that trigger vertigo",
            "Vestibular rehabilitation exercises can significantly reduce symptoms",
            "Stay hydrated and maintain regular sleep",
        ],
        "safety": [
            "Do not drive during active vertigo episodes",
            "Use grab rails in bathrooms and stairways to prevent falls",
            "Rise slowly from seated or lying positions",
        ],
        "doctor": "Consult a neurologist or ENT specialist. If vertigo is accompanied by hearing loss, severe headache, double vision, or difficulty speaking, seek immediate care.",
    },
    "Gastroenteritis": {
        "advice": [
            "Rehydrate with ORS (oral rehydration solution) — small, frequent sips",
            "Eat bland foods: bananas, rice, applesauce, toast (BRAT diet)",
            "Rest as much as possible",
            "Avoid dairy, fatty foods, caffeine, and alcohol until recovered",
            "Wash hands thoroughly — gastroenteritis spreads easily",
        ],
        "safety": [
            "Dehydration is the main danger — monitor for dry mouth, dark urine, dizziness",
            "Young children and elderly patients can dehydrate quickly — seek medical attention earlier",
            "Blood in stool or severe abdominal cramps requires immediate evaluation",
        ],
        "doctor": "See a doctor if symptoms don't improve after 48 hours, if there is blood in stool or vomit, or if you are severely dehydrated.",
    },
    "Peptic ulcer diseae": {
        "advice": [
            "Take prescribed medications (PPIs or H2 blockers) consistently",
            "Eat small, frequent meals instead of large ones",
            "Avoid aspirin, ibuprofen, and other NSAIDs — use paracetamol for pain",
            "Eliminate tobacco and alcohol completely",
            "Avoid spicy and acidic foods that irritate the stomach lining",
        ],
        "safety": [
            "Watch for black or tarry stools — indicates internal bleeding (emergency)",
            "Vomiting blood or coffee-ground material requires immediate emergency care",
            "Complete H. pylori treatment if the bacteria is the cause",
        ],
        "doctor": "Ulcers require medical treatment. Seek emergency care immediately for black or bloody stools, or vomiting blood.",
    },
    "AIDS": {
        "advice": [
            "Adhere to antiretroviral therapy (ART) exactly as prescribed — every dose, every day",
            "Eat a nutritious, well-balanced diet to support immunity",
            "Attend all medical appointments for viral load and CD4 monitoring",
            "Practice safe sex to prevent transmission to others",
            "Avoid raw/undercooked food and close contact with sick individuals",
        ],
        "safety": [
            "Never skip ART medication — resistance can develop quickly",
            "Opportunistic infections are the main danger — report any new symptoms promptly",
            "Avoid live vaccines without consulting your HIV specialist",
        ],
        "doctor": "HIV management requires specialised infectious disease care. Contact your HIV clinic team for any changes in health, new symptoms, or medication concerns.",
    },
    "Drug Reaction": {
        "advice": [
            "Stop the suspected medication and contact your doctor immediately",
            "Keep a record of all medications and supplements you take",
            "Inform all healthcare providers of any previous drug reactions",
            "Carry a medical alert card listing your drug allergies",
        ],
        "safety": [
            "🚨 Severe drug reactions (anaphylaxis, Stevens-Johnson syndrome) are medical emergencies",
            "Difficulty breathing, widespread rash, blistering, or swelling after medication — call emergency services",
            "Do not take the suspected drug again without medical clearance",
        ],
        "doctor": "Contact your doctor immediately if you suspect a drug reaction. Seek emergency care for breathing difficulty, widespread blistering rash, or swelling of face/throat.",
    },
    "Varicose veins": {
        "advice": [
            "Elevate legs above heart level for 15–30 minutes several times daily",
            "Wear compression stockings as recommended by your doctor",
            "Walk regularly — avoid prolonged sitting or standing",
            "Avoid crossing legs when sitting",
            "Maintain a healthy weight",
        ],
        "safety": [
            "Watch for sudden worsening of pain, redness, warmth — may indicate blood clot (DVT)",
            "Do not ignore varicose veins — they can cause ulcers or bleeding",
            "Skin discoloration or ulcers near varicose veins require medical evaluation",
        ],
        "doctor": "Consult a vascular surgeon if veins are causing pain, skin changes, or ulcers. Seek immediate care for sudden severe pain or swelling in one leg.",
    },
}

# Fallback advice for diseases not specifically listed
# Small, source-backed symptom-pattern guide for common presentations. This is
# deliberately separate from the unvalidated ML disease classifier. It suggests
# possibilities to discuss, never diagnoses or gives medication orders.
SYMPTOM_GUIDES = [
    {
        "id": "fever_headache",
        "required": {"fever", "headache"},
        "title": "Fever and headache",
        "possibilities": [
            "A viral respiratory infection, such as influenza or COVID-19",
            "Another common infection; the cause depends on other symptoms and exam findings",
            "Dehydration may contribute to headache, especially with poor fluid intake",
        ],
        "advice": [
            "Rest and drink fluids; if available, use a thermometer and note the temperature and when symptoms began",
            "Consider testing for COVID-19 or influenza when relevant, especially if you are at higher risk or recently exposed",
        ],
        "care": "Contact a healthcare professional if the fever is getting worse, lasts more than 3–4 days, or you are at higher risk because of pregnancy, age, or a chronic condition.",
        "source_urls": [
            "https://www.cdc.gov/flu/signs-symptoms/index.html",
            "https://www.cdc.gov/common-cold/treatment/",
            "https://www.nhs.uk/symptoms/fever-in-adults/",
        ],
    },
    {
        "id": "sneezing_nasal_irritation",
        "required": {"sneezing"},
        "any_of": {"nasal_irritation", "runny_nose"},
        "title": "Sneezing and nasal irritation",
        "possibilities": [
            "Allergic rhinitis (for example, pollen, dust, or animal dander), especially with itchy or watery eyes",
            "A common cold or another mild respiratory virus, especially with sore throat, cough, or feeling unwell",
            "Irritation from smoke, dust, fragrance, or dry air",
        ],
        "advice": [
            "Notice whether symptoms follow a particular exposure and reduce contact with likely irritants",
            "A saline nasal spray or rinse may help; use sterile, distilled, or previously boiled and cooled water for rinses",
        ],
        "care": "Ask a pharmacist or clinician about suitable symptom relief if symptoms are troublesome, persistent, or you have asthma or other long-term conditions.",
        "source_urls": [
            "https://medlineplus.gov/hayfever.html",
            "https://www.nhs.uk/conditions/common-cold/",
            "https://www.cdc.gov/common-cold/treatment/",
        ],
    },
    {
        "id": "cough",
        "required": {"cough"},
        "title": "Cough",
        "possibilities": [
            "A short-lived respiratory virus or throat irritation",
            "Allergies, asthma, reflux, or another cause; duration and associated symptoms matter",
        ],
        "advice": [
            "For a mild cough, rest, drink fluids, and avoid smoke or vaping; honey may soothe a cough for people over 1 year old.",
            "Avoid strenuous exercise if you have fever, chest discomfort, wheezing, or breathlessness.",
        ],
        "care": "Seek medical advice for a cough that is worsening, lasts more than 3 weeks, includes blood, or comes with persistent fever. Get urgent help for severe breathing difficulty or chest pain.",
        "source_urls": ["https://www.nhs.uk/conditions/cough/", "https://www.nhs.uk/symptoms/shortness-of-breath/"],
    },
    {
        "id": "diarrhoea",
        "required": {"diarrhoea"},
        "title": "Diarrhoea",
        "possibilities": [
            "A short-term stomach infection or food-related illness",
            "Medicines, food intolerance, or other causes if symptoms recur or persist",
        ],
        "advice": [
            "Take frequent small sips of fluids; oral rehydration solution can replace water and salts lost through diarrhoea.",
            "Rest and eat as tolerated. Do not take anti-diarrhoea medicine for a child or if there is blood or high fever without clinician advice.",
        ],
        "care": "Get medical advice for blood in stool, signs of dehydration, severe pain, persistent vomiting, or symptoms that do not improve. Seek urgent help if you are very drowsy, confused, or unable to keep fluids down.",
        "source_urls": ["https://www.nhs.uk/conditions/diarrhoea-and-vomiting/"],
    },
    {
        "id": "rash",
        "required": {"skin_rash"},
        "title": "Skin rash",
        "possibilities": [
            "Skin irritation or contact allergy, especially after a new product or exposure",
            "An infection or another skin condition; appearance and accompanying symptoms help distinguish causes",
        ],
        "advice": [
            "Avoid scratching and stop a newly introduced product that may be irritating the skin; use a cool compress for comfort.",
            "Do not apply strong creams or leftover prescription treatment without advice, especially on the face or in children.",
        ],
        "care": "Seek medical advice if the rash spreads, is painful, blisters, affects the eyes or mouth, or comes with fever. Emergency help is needed for sudden swelling of the lips, tongue, or throat or breathing difficulty.",
        "source_urls": ["https://www.nhs.uk/conditions/rashes-babies-and-children/", "https://www.nhs.uk/conditions/anaphylaxis/"],
    },
    {
        "id": "headache",
        "required": {"headache"},
        "title": "Headache",
        "possibilities": [
            "A common primary headache, stress, missed meals, or dehydration",
            "Another cause if the headache is new, persistent, severe, or accompanied by other symptoms",
        ],
        "advice": [
            "For a mild headache, try rest, fluids, regular meals, and a break from screens; avoid activity that makes it worse.",
            "Note the start time, severity, and any triggers or accompanying symptoms.",
        ],
        "care": "Seek urgent care for a sudden extremely severe headache, weakness, confusion, vision or speech changes, or headache with fever and a stiff neck. Arrange a clinician visit for recurring, worsening, or persistent headaches.",
        "source_urls": ["https://www.nhs.uk/conditions/headaches/"],
    },
]

GENERAL_MEDICINE_NOTE = (
    "This checker cannot safely prescribe a medicine, dose, or stop date. No medicine is "
    "side-effect-free for everyone. If you want symptom relief, ask a pharmacist or clinician "
    "what is suitable for your age, pregnancy status, allergies, health conditions, and other "
    "medicines. Follow that product's label and avoid combining products with the same active ingredient."
)


def find_symptom_guide(symptoms: list[str]) -> dict | None:
    present = set(symptoms)
    for guide in SYMPTOM_GUIDES:
        any_of = guide.get("any_of", set())
        if guide["required"].issubset(present) and (not any_of or any_of.intersection(present)):
            return guide
    return None


DEFAULT_ADVICE = {
    "advice": [
        "Rest adequately and avoid strenuous physical activity",
        "Stay well-hydrated — drink 8–10 glasses of water daily",
        "Eat a light, nutritious, balanced diet",
        "Monitor how your symptoms change over time",
        "Keep a symptom diary to share with your healthcare provider",
    ],
    "safety": [
        "Watch for any worsening of symptoms",
        "Note if new symptoms develop and when they started",
        "Avoid self-medicating with prescription drugs",
    ],
    "doctor": "Consider speaking with a qualified healthcare professional if symptoms persist beyond 5 days, worsen, or interfere with normal daily activities.",
}


def normalize(description: str, selected: list[str]) -> list[str]:
    return extract_symptoms(description, selected)


def safety_flags(description: str) -> bool:
    return bool(urgent_flags(description))


def analyze(description: str, normalized: list[str], answers: dict) -> dict:
    """
    Full AI analysis pipeline:
    1. NLP normalises symptoms
    2. Reported symptoms are compared with repeated condition patterns in the source CSV
    3. Feature importance explains the educational classifier output
    4. Care advice follows reported symptoms and warning signs
    5. Urgency flags are checked independently
    """
    result_data = predict_full(normalized, top_k=5)
    dataset_matches = rank_dataset_symptom_matches(normalized, top_k=5)
    predictions  = result_data["predictions"]
    all_preds    = result_data["all_predictions"]
    matched      = result_data["matched_symptoms"]
    triggered    = result_data["triggered_key_features"]
    fi_top       = result_data["feature_importance_top"]

    urgent_reasons = urgent_flags(description)
    guide = find_symptom_guide(normalized)

    # Generic symptom patterns should not inherit an unrelated classifier label
    # (and its disease-specific medicines/advice). Present a source-backed
    # differential guide instead of the raw model's misleading disease ranking.
    if guide:
        predictions = []
        all_preds = []
        primary_label = None
        advice = guide["advice"]
        safety = [
            "These are possibilities, not a diagnosis; symptom overlap is common.",
            "Seek emergency care for trouble breathing, confusion, a seizure, a sudden severe headache, or fever with a stiff neck or a rash that does not fade when pressed.",
        ]
        doctor = guide["care"]
        differential = guide["possibilities"]
        guide_title = guide["title"]
        guide_sources = guide["source_urls"]
    else:
        primary_label = predictions[0]["label"] if predictions else None
        # Advice follows the reported symptoms, never the classifier's disease label.
        advice = ["If symptoms are mild and improving, rest, drink fluids to thirst, and keep a note of when they began and how they change."]
        if "cough" in normalized or "sore_throat" in normalized or "runny_nose" in normalized:
            advice.append("For mild cold-like symptoms, rest, fluids, and avoiding smoke or other irritants are reasonable. Avoid strenuous exercise while feverish or short of breath.")
        if "headache" in normalized:
            advice.append("For a mild headache, try a quiet rest, regular fluids, and a screen break; avoid strenuous activity if it worsens the pain.")
        if "diarrhoea" in normalized or "vomiting" in normalized:
            advice.append("Take frequent small sips of fluid; oral rehydration solution can help replace losses. Seek advice if you cannot keep fluids down.")
        if "skin_rash" in normalized or "itching" in normalized:
            advice.append("Avoid scratching and stop any newly introduced skin product that may be irritating the area; seek care if the rash spreads quickly or becomes painful.")
        if "back_pain" in normalized or "joint_pain" in normalized or "muscle_pain" in normalized:
            advice.append("For mild muscle or joint discomfort without injury, gentle movement within comfort may help; stop if pain increases and avoid strenuous exercise until improving.")
        safety = ["These symptom matches cannot establish a diagnosis. Do not start, stop, or share prescription medicines based on this result."]
        if "chest_pain" in normalized or "breathlessness" in normalized:
            safety.append("New, severe, persistent chest pain or severe breathing difficulty needs emergency assessment now; call your local emergency number (112 in India).")
        if "facial_droop" in normalized or "weakness" in normalized or "difficulty_speaking" in normalized:
            safety.append("Sudden face drooping, one-sided weakness, or trouble speaking is an emergency: call 112 now.")
        if "confusion" in normalized or "fainting" in normalized or "high_fever" in normalized or ("fever" in normalized and "stiff_neck" in normalized):
            safety.append("New confusion, fainting, very high fever, or fever with a stiff neck needs urgent medical assessment.")
        doctor = "Mild symptoms that are steadily improving can often be monitored at home. Arrange medical advice if symptoms worsen, persist, keep returning, interfere with daily activities, or you are worried; seek earlier advice for pregnancy, very young/older age, immune suppression, or significant long-term illness."
        differential = []
        guide_title = None
        guide_sources = []

    prompt_map = [
        (("fever", "headache"), "Do you have a measured temperature, and when did the fever and headache begin? Any stiff neck, rash, or confusion?"),
        (("cough",), "How long have you been coughing? Is there fever, chest pain, wheezing, or any difficulty breathing?"),
        (("abdominal_pain",), "Where is the pain, when did it start, and is it getting worse? Any vomiting, fever, or blood in stool?"),
        (("diarrhoea",), "How long has this been happening? Can you keep fluids down, and are you urinating normally?"),
        (("vomiting",), "How long has this been happening? Can you keep fluids down, and are you urinating normally?"),
        (("skin_rash",), "Where did the rash start, when did it appear, and is it spreading, painful, itchy, or associated with fever?"),
        (("headache",), "When did the headache start, how severe is it, and is it sudden or accompanied by vision changes, weakness, fever, or neck stiffness?"),
    ]
    follow_up_prompt = next((question for keys, question in prompt_map if all(key in normalized for key in keys)), "When did this start, is it improving or worsening, and have you noticed any other symptoms?")

    # Build explanation cards
    explanations = []
    for item in predictions:
        label = item["label"]
        pct   = round(item["confidence"] * 100, 1)
        explanations.append({
            "title": label,
            "confidence": item["confidence"],
            "confidence_pct": pct,
            "description": (
                f"The model identified a {pct}% pattern match for {label}. "
                "This is an educational pattern match, not a clinical diagnosis. "
                "A qualified healthcare professional should evaluate your symptoms in context."
            ),
        })

    return {
        "demo": False,
        "primary_label": primary_label,
        "urgent": bool(urgent_reasons),
        "urgent_reasons": urgent_reasons,
        "nlp_extracted_symptoms": normalized,
        "matched_symptoms": matched,
        "triggered_key_features": triggered,
        "predictions": predictions,
        "all_predictions": all_preds,
        "dataset_matches": dataset_matches,
        "differential": differential,
        "symptom_guide_title": guide_title,
        "symptom_guide_sources": guide_sources,
        "feature_importance_top": fi_top,
        "model": model_metadata(),
        "explanations": explanations,
        "advice": advice,
        "safety": safety,
        "doctor": doctor,
        "medicine_note": GENERAL_MEDICINE_NOTE,
        "follow_up_answers": answers,
        "follow_up_prompt": follow_up_prompt,
        "care_guidance": {
            "emergency": "Get emergency help now for severe breathing difficulty, ongoing severe chest pain, stroke signs, unconsciousness, or a severe allergic reaction.",
            "monitor": "Mild and improving symptoms can be monitored with rest, fluids, and a symptom note.",
            "clinician": doctor,
        },
    }
