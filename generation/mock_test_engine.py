import json
import random
import re
from typing import Any, Optional


# ==============================================================================
# COMPREHENSIVE CURATED QUESTION BANK ACROSS ALL UPSC GS SUBJECTS & CSAT
# ==============================================================================
MOCK_QUESTION_BANK = [
    # --------------------------------------------------------------------------
    # 1. INDIAN POLITY & CONSTITUTION
    # --------------------------------------------------------------------------
    {
        "id": 101,
        "subject": "Indian Polity & Constitution",
        "topic": "Preamble & Constitutional Philosophy",
        "question": "With reference to the Preamble of the Constitution of India, consider the following statements:\n1. The Preamble is an integral part of the Constitution.\n2. It can be amended under Article 368 without destroying the basic structure.\n3. The Preamble is directly enforceable in a court of law.\n\nWhich of the statements given above is/are correct?",
        "options": [
            "A) 1 and 2 only",
            "B) 2 and 3 only",
            "C) 1 and 3 only",
            "D) 1, 2 and 3"
        ],
        "correct_opt": "A",
        "explanation": "Statement 1 is correct: In the Kesavananda Bharati case (1973), the Supreme Court explicitly held that the Preamble is an integral part of the Constitution.\nStatement 2 is correct: The Preamble can be amended under Article 368, provided that the Basic Structure of the Constitution is not damaged or altered (as done by the 42nd Amendment Act, 1976).\nStatement 3 is INCORRECT: The Preamble is non-justiciable and non-enforceable in courts of law; its provisions cannot be enforced as standalone legal rights."
    },
    {
        "id": 102,
        "subject": "Indian Polity & Constitution",
        "topic": "Fundamental Rights & Judicial Review",
        "question": "Which of the following Fundamental Rights under the Indian Constitution is/are available to BOTH Indian citizens and foreigners (except enemy aliens)?\n1. Right to equality before law and equal protection of laws (Article 14)\n2. Protection of language, script, and culture of minorities (Article 29)\n3. Protection of life and personal liberty (Article 21)\n4. Equality of opportunity in matters of public employment (Article 16)\n\nSelect the correct answer using the code given below:",
        "options": [
            "A) 1 and 3 only",
            "B) 1, 2 and 3 only",
            "C) 2 and 4 only",
            "D) 1, 3 and 4 only"
        ],
        "correct_opt": "A",
        "explanation": "Articles 15, 16, 19, 29, and 30 are available ONLY to Indian citizens.\nArticles 14, 20, 21, 21A, 22, 23, 24, 25, 26, 27, and 28 are available to ALL persons (both citizens and foreigners, except enemy aliens).\nTherefore, Articles 14 (Statement 1) and 21 (Statement 3) are available to foreigners, while Articles 29 and 16 are exclusive to citizens."
    },
    {
        "id": 103,
        "subject": "Indian Polity & Constitution",
        "topic": "Parliament & Parliamentary Committees",
        "question": "Consider the following statements regarding the Public Accounts Committee (PAC):\n1. It consists of not more than 22 members (15 from Lok Sabha and 7 from Rajya Sabha).\n2. A Minister is not eligible to be elected as a member of the Committee.\n3. The Chairman of the Committee is appointed by the President of India from amongst its members.\n\nWhich of the statements given above are correct?",
        "options": [
            "A) 1 and 2 only",
            "B) 2 and 3 only",
            "C) 1 and 3 only",
            "D) 1, 2 and 3"
        ],
        "correct_opt": "A",
        "explanation": "Statement 1 is correct: PAC comprises 22 members (15 Lok Sabha, 7 Rajya Sabha) elected by proportional representation.\nStatement 2 is correct: A Minister cannot be elected as a member of PAC; if a member becomes a minister, they cease to be a member.\nStatement 3 is INCORRECT: The Chairman of the Committee is appointed by the Speaker of the Lok Sabha (not the President), and by convention since 1967, the Chairman is selected from the Opposition."
    },
    {
        "id": 104,
        "subject": "Indian Polity & Constitution",
        "topic": "Constitutional & Statutory Bodies",
        "question": "Which of the following authorities are CONSTITUTIONAL BODIES established directly by the Constitution of India?\n1. Election Commission of India (Article 324)\n2. National Human Rights Commission (NHRC)\n3. Finance Commission (Article 280)\n4. Central Vigilance Commission (CVC)\n\nSelect the correct answer using the code given below:",
        "options": [
            "A) 1 and 3 only",
            "B) 1, 2 and 3 only",
            "C) 2 and 4 only",
            "D) 1, 3 and 4 only"
        ],
        "correct_opt": "A",
        "explanation": "Election Commission (Article 324) and Finance Commission (Article 280) derive their establishment directly from the Constitution and are Constitutional Bodies.\nNHRC is a statutory body established under the Protection of Human Rights Act, 1993.\nCVC was created by an executive resolution in 1964 and granted statutory status by the CVC Act, 2003."
    },
    {
        "id": 105,
        "subject": "Indian Polity & Constitution",
        "topic": "Anti-Defection Law (Tenth Schedule)",
        "question": "With reference to the Anti-Defection Law contained in the Tenth Schedule of the Constitution, consider the following statements:\n1. A nominated member of a House becomes disqualified if they join any political party within six months of taking their seat.\n2. The presiding officer's decision on disqualification is subject to judicial review by the Supreme Court and High Courts.\n\nWhich of the statements given above is/are correct?",
        "options": [
            "A) 1 only",
            "B) 2 only",
            "C) Both 1 and 2",
            "D) Neither 1 nor 2"
        ],
        "correct_opt": "B",
        "explanation": "Statement 1 is INCORRECT: A nominated member is allowed to join a political party within the first 6 months of taking their seat without incurring disqualification. They become disqualified ONLY if they join a political party AFTER the expiry of 6 months.\nStatement 2 is correct: In Kihoto Hollohan v. Zachillhu (1992), the Supreme Court declared that the Speaker/Chairman acts as a tribunal while deciding defection petitions, and their decision is subject to judicial review on grounds of mala fides or perversity."
    },

    # --------------------------------------------------------------------------
    # 2. MODERN INDIAN HISTORY & ART & CULTURE
    # --------------------------------------------------------------------------
    {
        "id": 201,
        "subject": "Modern Indian History",
        "topic": "Colonial Administrative Acts & Reforms",
        "question": "With reference to the Government of India Act, 1919 (Montagu-Chelmsford Reforms), consider the following statements:\n1. It introduced dyarchy in the executive government of the provinces.\n2. It separated provincial budgets from the Central budget for the first time.\n3. It established bicameralism at the provincial level across all British provinces.\n\nWhich of the statements given above are correct?",
        "options": [
            "A) 1 and 2 only",
            "B) 2 and 3 only",
            "C) 1 and 3 only",
            "D) 1, 2 and 3"
        ],
        "correct_opt": "A",
        "explanation": "Statement 1 is correct: The Act of 1919 divided provincial subjects into 'Transferred' (administered by Governor with ministers) and 'Reserved' (administered by Governor with executive council), known as Dyarchy.\nStatement 2 is correct: It demarcated and separated provincial budgets from the Central budget, allowing provincial legislatures to enact their own budgets.\nStatement 3 is INCORRECT: Bicameralism was introduced at the CENTRAL legislature by the 1919 Act (Council of State and Legislative Assembly). Bicameralism in provinces was introduced later by the Government of India Act, 1935 in six out of eleven provinces."
    },
    {
        "id": 202,
        "subject": "Modern Indian History",
        "topic": "Socio-Religious Reform Movements",
        "question": "Consider the following statements regarding the Brahmo Samaj and Arya Samaj:\n1. Raja Ram Mohan Roy established the Brahmo Samaj and opposed polytheism and idol worship based on Upanishadic monotheism.\n2. Swami Dayananda Saraswati gave the call 'Back to the Vedas' and accepted the authority of the Puranas as divine revelation.\n\nWhich of the statements given above is/are correct?",
        "options": [
            "A) 1 only",
            "B) 2 only",
            "C) Both 1 and 2",
            "D) Neither 1 nor 2"
        ],
        "correct_opt": "A",
        "explanation": "Statement 1 is correct: Raja Ram Mohan Roy founded Brahmo Sabha (1828), which advocated monotheism based on Upanishads and vehemently condemned idolatry and caste prejudices.\nStatement 2 is INCORRECT: Swami Dayananda Saraswati established Arya Samaj (1875) and proclaimed 'Back to the Vedas'. However, he REJECTED the authority of later religious scriptures like the Puranas, which he regarded as full of superstitions and idol worship."
    },
    {
        "id": 203,
        "subject": "Modern Indian History",
        "topic": "National Freedom Movement (1920-1942)",
        "question": "Which of the following events took place during the Civil Disobedience Movement (1930-1934)?\n1. Dharasana Salt Raid led by Sarojini Naidu, Imam Saheb, and Manilal\n2. Formation of the parallel government ('Prati Sarkar') in Satara by Nana Patil\n3. Rani Gaidinliu leading the Heraka religious movement against British rule in Nagaland/Manipur\n\nSelect the correct answer using the code given below:",
        "options": [
            "A) 1 and 3 only",
            "B) 1 and 2 only",
            "C) 2 and 3 only",
            "D) 1, 2 and 3"
        ],
        "correct_opt": "A",
        "explanation": "Statement 1 is correct: Dharasana salt works in Gujarat were raided in May 1930 during the Civil Disobedience Movement.\nStatement 2 is INCORRECT: The parallel government ('Prati Sarkar') in Satara was set up during the QUIT INDIA MOVEMENT (1942-43), not the Civil Disobedience Movement.\nStatement 3 is correct: Rani Gaidinliu led the rebellion in the northeast during the Civil Disobedience Movement at age 13, for which Jawaharlal Nehru conferred on her the title 'Rani'."
    },
    {
        "id": 204,
        "subject": "Modern Indian History",
        "topic": "Indian Art & Architecture",
        "question": "In the context of ancient and medieval Indian temple architecture, consider the following statements:\n1. The Nagara style of architecture is characterized by a high curvilinear tower known as a Shikhara, without elaborate boundary walls or Gopurams.\n2. The Dravida style temples feature pyramidal stepped towers called Vimana, enclosed by high compound walls with entrance gateways called Gopurams.\n3. The Vesara style represents an indigenous hybrid style that developed under the Chalukyas and Hoysalas in Karnataka.\n\nWhich of the statements given above are correct?",
        "options": [
            "A) 1 and 2 only",
            "B) 2 and 3 only",
            "C) 1, 2 and 3",
            "D) 1 and 3 only"
        ],
        "correct_opt": "C",
        "explanation": "All three statements are correct. Nagara style (North India) temples typically lack boundary walls and gopurams and feature shikhara towers on raised platforms (Jagati). Dravida style (South India) features enclosed boundary walls, imposing gopurams, and stepped pyramidal vimana. Vesara style developed in the Deccan under the Later Chalukyas and Hoysalas, synthesizing elements of both traditions."
    },
    {
        "id": 205,
        "subject": "Modern Indian History",
        "topic": "Tribal & Peasant Revolts",
        "question": "Consider the following pairs of historical uprisings and their primary leaders:\n1. Santhal Hool (1855-56) : Sidhu and Kanhu Murmu\n2. Munda Ulgulan (1899-1900) : Birsa Munda\n3. Rampa Rebellion (1922-24) : Alluri Sitarama Raju\n\nHow many of the pairs given above are correctly matched?",
        "options": [
            "A) Only one pair",
            "B) Only two pairs",
            "C) All three pairs",
            "D) None of the pairs"
        ],
        "correct_opt": "C",
        "explanation": "All three pairs are correctly matched:\n1. Santhal Hool (1855-56) in Rajmahal hills was led by brothers Sidhu and Kanhu Murmu against zamindars and moneylenders (Dikus).\n2. Munda Ulgulan (1899-1900) in Chotanagpur was led by Birsa Munda against feudal erosion of Khuntkatti land tenure.\n3. Rampa Rebellion (1922-24) in the Godavari agency tract was led by Alluri Sitarama Raju against the Madras Forest Act."
    },

    # --------------------------------------------------------------------------
    # 3. INDIAN ECONOMY & BUDGET
    # --------------------------------------------------------------------------
    {
        "id": 301,
        "subject": "Indian Economy & Budget",
        "topic": "Monetary Policy & Banking",
        "question": "With reference to the Monetary Policy Committee (MPC) in India, consider the following statements:\n1. It determines the benchmark policy repo rate to achieve the consumer price inflation target.\n2. It is a 6-member committee consisting of three members from the RBI and three external members appointed by the Central Government.\n3. The Governor of the RBI acts as the ex-officio Chairman and possesses a casting vote in case of a tie.\n\nWhich of the statements given above are correct?",
        "options": [
            "A) 1 and 2 only",
            "B) 2 and 3 only",
            "C) 1 and 3 only",
            "D) 1, 2 and 3"
        ],
        "correct_opt": "D",
        "explanation": "All three statements are correct under Section 45ZB of the amended RBI Act, 1934:\n1. MPC fixes the benchmark repo rate to achieve the statutory inflation target (4% +/- 2% CPI).\n2. It has 6 members: RBI Governor, Deputy Governor in charge of monetary policy, one RBI officer, and 3 external government-appointed experts.\n3. The Governor presides as ex-officio Chair and has a casting vote if votes are evenly divided."
    },
    {
        "id": 302,
        "subject": "Indian Economy & Budget",
        "topic": "Fiscal Deficit & Public Finance",
        "question": "Which of the following correctly defines 'Primary Deficit' in the Union Budget of India?",
        "options": [
            "A) Fiscal Deficit minus Interest Payments",
            "B) Revenue Deficit minus Capital Expenditure",
            "C) Fiscal Deficit minus Net Borrowings from Abroad",
            "D) Total Budget Deficit minus Disinvestment Proceeds"
        ],
        "correct_opt": "A",
        "explanation": "Primary Deficit = Fiscal Deficit - Interest Payments.\nIt reflects the government's borrowing requirements to finance current fiscal operations excluding the interest burden of historical debt accumulated in previous years. A zero primary deficit indicates that borrowings are strictly utilized only to service past debt."
    },
    {
        "id": 303,
        "subject": "Indian Economy & Budget",
        "topic": "Inflation Indices (CPI vs WPI)",
        "question": "In the context of macroeconomic indicators in India, consider the following statements regarding CPI and WPI:\n1. The Wholesale Price Index (WPI) does not capture the price movement of services, whereas the Consumer Price Index (CPI) includes services.\n2. Headline inflation targeted by the Reserve Bank of India for monetary policy is based on WPI.\n3. The weightage of food articles is higher in CPI than in WPI.\n\nWhich of the statements given above are correct?",
        "options": [
            "A) 1 and 2 only",
            "B) 1 and 3 only",
            "C) 2 and 3 only",
            "D) 1, 2 and 3"
        ],
        "correct_opt": "B",
        "explanation": "Statement 1 is correct: WPI measures prices of goods only at the wholesale stage and completely excludes services. CPI includes both goods and services (education, medical, transport).\nStatement 2 is INCORRECT: Since 2014, based on the Urjit Patel Committee recommendations, the RBI uses CPI (Combined) as its sole anchor for headline inflation targeting, not WPI.\nStatement 3 is correct: Food and beverages comprise ~45.86% of the CPI (Combined) basket, whereas in WPI, primary food articles and manufactured food account for ~24.4%."
    },
    {
        "id": 304,
        "subject": "Indian Economy & Budget",
        "topic": "External Sector & Balance of Payments",
        "question": "Which of the following items are included in the 'Capital Account' of the Balance of Payments (BoP) of India?\n1. Foreign Direct Investment (FDI)\n2. Remittances sent home by Indian workers abroad\n3. External Commercial Borrowings (ECBs)\n4. NRI Bank Deposits\n\nSelect the correct answer using the code given below:",
        "options": [
            "A) 1, 3 and 4 only",
            "B) 1 and 2 only",
            "C) 2, 3 and 4 only",
            "D) 1, 2, 3 and 4"
        ],
        "correct_opt": "A",
        "explanation": "Items 1 (FDI), 3 (ECBs), and 4 (NRI Deposits) involve changes in international financial assets/liabilities of India and are recorded in the CAPITAL ACCOUNT.\nItem 2 (Remittances) represents unilateral secondary income transfers and is recorded in the CURRENT ACCOUNT (under invisibles), not the capital account."
    },
    {
        "id": 305,
        "subject": "Indian Economy & Budget",
        "topic": "Agriculture Pricing & MSP",
        "question": "With reference to the Minimum Support Price (MSP) regime in India, consider the following statements:\n1. The Commission for Agricultural Costs and Prices (CACP) is a statutory body that announces the MSP.\n2. The final decision on the fixation of MSP is taken by the Cabinet Committee on Economic Affairs (CCEA).\n3. MSP is currently announced for 22 mandated agricultural crops and Fair and Remunerative Price (FRP) for sugarcane.\n\nWhich of the statements given above are correct?",
        "options": [
            "A) 1 and 2 only",
            "B) 2 and 3 only",
            "C) 1 and 3 only",
            "D) 1, 2 and 3"
        ],
        "correct_opt": "B",
        "explanation": "Statement 1 is INCORRECT: CACP is an attached office of the Ministry of Agriculture and Farmers Welfare; it is an advisory body, NOT a statutory body. CACP recommends prices, but does NOT announce them.\nStatement 2 is correct: The final approval and announcement of MSP is made by the Cabinet Committee on Economic Affairs (CCEA) chaired by the Prime Minister.\nStatement 3 is correct: MSP covers 22 mandated crops (14 Kharif, 6 Rabi, 2 commercial) plus FRP for Sugarcane under the Sugarcane (Control) Order."
    },

    # --------------------------------------------------------------------------
    # 4. ENVIRONMENT & ECOLOGY
    # --------------------------------------------------------------------------
    {
        "id": 401,
        "subject": "Environment & Ecology",
        "topic": "Protected Area Network & Wildlife Protection",
        "question": "Under the Wildlife (Protection) Act, 1972, which of the following categories of protected areas allows the continuation of community rights and private ownership of land within its boundaries without extinction?",
        "options": [
            "A) National Parks",
            "B) Wildlife Sanctuaries",
            "C) Community Reserves",
            "D) Conservation Reserves only on Government land"
        ],
        "correct_opt": "B",
        "explanation": "In a Wildlife Sanctuary, certain human activities and pre-existing traditional rights (such as grazing of livestock, limited private land holding) may be permitted by the Chief Wildlife Warden.\nIn contrast, in a National Park, no human habitation or private rights are allowed whatsoever; all private rights must be acquired and extinguished before final notification."
    },
    {
        "id": 402,
        "subject": "Environment & Ecology",
        "topic": "Wetlands & Ramsar Convention",
        "question": "With reference to the 'Montreux Record' under the Ramsar Convention, which of the following statements is correct?",
        "options": [
            "A) It is a register of wetland sites of international importance where changes in ecological character have occurred, are occurring, or are likely to occur.",
            "B) It is a list of endangered aquatic species threatened with imminent extinction globally.",
            "C) It is a database of artificial wetlands constructed exclusively for wastewater treatment.",
            "D) It includes all Ramsar sites located within UNESCO Biosphere Reserves."
        ],
        "correct_opt": "A",
        "explanation": "The Montreux Record is a register of wetland sites on the Ramsar List of Wetlands of International Importance where changes in ecological character have occurred, are occurring, or are likely to occur as a result of technological developments, pollution, or other human interference.\nIn India, Keoladeo National Park (Rajasthan) and Loktak Lake (Manipur) are currently maintained on the Montreux Record (Chilika Lake was successfully removed in 2002 after restoration)."
    },
    {
        "id": 403,
        "subject": "Environment & Ecology",
        "topic": "Climate Change & UNFCCC Agreements",
        "question": "Consider the following statements regarding the Paris Agreement (COP21):\n1. It aims to hold the increase in the global average temperature to well below 2°C above pre-industrial levels and pursue efforts to limit it to 1.5°C.\n2. Nationally Determined Contributions (NDCs) submitted by parties are legally binding greenhouse gas reduction targets.\n3. Article 6 of the Paris Agreement provides a framework for international carbon market mechanisms.\n\nWhich of the statements given above are correct?",
        "options": [
            "A) 1 and 2 only",
            "B) 1 and 3 only",
            "C) 2 and 3 only",
            "D) 1, 2 and 3"
        ],
        "correct_opt": "B",
        "explanation": "Statement 1 is correct: Article 2 of the Paris Agreement explicitly outlines the long-term temperature goal of well below 2°C, striving for 1.5°C.\nStatement 2 is INCORRECT: The procedural requirement to submit NDCs regularly is binding, but the specific numerical mitigation targets contained inside NDCs are voluntary and NOT legally enforceable under international law.\nStatement 3 is correct: Article 6 establishes rules for voluntary international carbon trading and cooperative approaches (Articles 6.2 and 6.4)."
    },
    {
        "id": 404,
        "subject": "Environment & Ecology",
        "topic": "Biodiversity Conservation & Hotspots",
        "question": "To qualify as a 'Biodiversity Hotspot' as defined by Conservation International, a region must satisfy which of the following criteria?\n1. It must contain at least 1,500 species of vascular plants (> 0.5% of world’s total) as endemics.\n2. It has to have lost at least 70% of its original primary native vegetation.\n\nSelect the correct answer using the code given below:",
        "options": [
            "A) 1 only",
            "B) 2 only",
            "C) Both 1 and 2",
            "D) Neither 1 nor 2"
        ],
        "correct_opt": "C",
        "explanation": "Both criteria are strictly required under Norman Myers' definition adopted by Conservation International:\n1. Endemism threshold: It must hold at least 1,500 endemic vascular plant species.\n2. Threat threshold: It must have lost at least 70% of its original primary habitat (i.e. <= 30% original habitat remaining).\nIndia has four hotspots: Western Ghats, Eastern Himalayas, Indo-Burma, and Sundaland (Nicobar Islands)."
    },
    {
        "id": 405,
        "subject": "Environment & Ecology",
        "topic": "Environmental Pollution & Air Quality",
        "question": "Which of the following air pollutants are monitored for the calculation of the National Air Quality Index (AQI) in India?\n1. Particulate Matter (PM10 and PM2.5)\n2. Nitrogen Dioxide (NO2) and Sulphur Dioxide (SO2)\n3. Carbon Dioxide (CO2)\n4. Ozone (O3) and Lead (Pb)\n\nSelect the correct answer using the code given below:",
        "options": [
            "A) 1, 2 and 4 only",
            "B) 1, 2 and 3 only",
            "C) 2, 3 and 4 only",
            "D) 1, 2, 3 and 4"
        ],
        "correct_opt": "A",
        "explanation": "India's National AQI considers 8 pollutants: PM10, PM2.5, NO2, SO2, CO, O3, NH3 (Ammonia), and Pb (Lead).\nCarbon Dioxide (CO2) is a major greenhouse gas causing global warming, but it is NOT one of the 8 criteria pollutants monitored for India's Air Quality Index."
    },

    # --------------------------------------------------------------------------
    # 5. GEOGRAPHY & MAPPING
    # --------------------------------------------------------------------------
    {
        "id": 501,
        "subject": "Geography & Mapping",
        "topic": "Climatology & Indian Monsoon",
        "question": "With reference to the Indian Monsoon, consider the following statements regarding the Indian Ocean Dipole (IOD):\n1. A positive IOD is characterized by warmer than normal sea surface temperatures in the western Indian Ocean and cooler waters in the eastern Indian Ocean.\n2. A positive IOD usually brings above-average monsoon rainfall to the Indian subcontinent.\n\nWhich of the statements given above is/are correct?",
        "options": [
            "A) 1 only",
            "B) 2 only",
            "C) Both 1 and 2",
            "D) Neither 1 nor 2"
        ],
        "correct_opt": "C",
        "explanation": "Both statements are correct:\n1. A positive Indian Ocean Dipole (IOD) entails warmer SSTs in the western equatorial Indian Ocean (near African coast) and cooler SSTs near Indonesia/eastern Indian Ocean.\n2. The increased convective precipitation over the western Indian Ocean reinforces the southwest monsoon flow, helping compensate for negative El Niño impacts and delivering above-normal or healthy rainfall to India."
    },
    {
        "id": 502,
        "subject": "Geography & Mapping",
        "topic": "Indian Drainage Systems",
        "question": "Consider the following rivers of India:\n1. Narmada\n2. Tapi\n3. Mahanadi\n4. Godavari\n\nWhich of the above are WEST-FLOWING rivers that drain into the Arabian Sea through rift valleys?",
        "options": [
            "A) 1 and 2 only",
            "B) 2 and 3 only",
            "C) 1, 2 and 4 only",
            "D) 3 and 4 only"
        ],
        "correct_opt": "A",
        "explanation": "Narmada and Tapi are major peninsular rivers that flow westwards through rift valleys created by faulting (between Vindhyas and Satpuras for Narmada; south of Satpuras for Tapi) and drain into the Gulf of Khambhat (Arabian Sea), forming estuaries.\nMahanadi and Godavari are east-flowing rivers that drain into the Bay of Bengal and form large deltas."
    },
    {
        "id": 503,
        "subject": "Geography & Mapping",
        "topic": "International Choke Points & Straits",
        "question": "Consider the following pairs of international straits and the water bodies they connect:\n1. Strait of Malacca : Andaman Sea and South China Sea\n2. Bab-el-Mandeb : Red Sea and Gulf of Aden\n3. Strait of Hormuz : Persian Gulf and Gulf of Oman\n\nHow many of the pairs given above are correctly matched?",
        "options": [
            "A) Only one pair",
            "B) Only two pairs",
            "C) All three pairs",
            "D) None of the pairs"
        ],
        "correct_opt": "C",
        "explanation": "All three strategic maritime choke points are correctly matched:\n1. Strait of Malacca connects the Andaman Sea (Indian Ocean) with the South China Sea (Pacific Ocean).\n2. Bab-el-Mandeb connects the Red Sea to the Gulf of Aden (leading into the Arabian Sea).\n3. Strait of Hormuz connects the Persian Gulf to the Gulf of Oman."
    },
    {
        "id": 504,
        "subject": "Geography & Mapping",
        "topic": "Soils of India & Agriculture",
        "question": "Which of the following characteristics are typically associated with 'Black Soils' (Regur) of India?\n1. Formed primarily by the weathering of basaltic Deccan trap lava.\n2. High clay content with high moisture-retention capacity.\n3. Rich in nitrogen, phosphorus, and organic matter.\n4. Exhibits self-ploughing characteristics due to swelling when wet and developing deep cracks when dry.\n\nSelect the correct answer using the code given below:",
        "options": [
            "A) 1, 2 and 4 only",
            "B) 1 and 3 only",
            "C) 2, 3 and 4 only",
            "D) 1, 2, 3 and 4"
        ],
        "correct_opt": "A",
        "explanation": "Statements 1, 2, and 4 are correct: Black soil is derived from Deccan lava, is fine-textured clayey, retains moisture exceptionally well, and develops wide cracks during dry periods causing self-aeration ('self-ploughing').\nStatement 3 is INCORRECT: Black soil is generally DEFICIENT in nitrogen, phosphorus, and humus/organic matter, though it is rich in lime, iron, magnesia, and potash."
    },

    # --------------------------------------------------------------------------
    # 6. SCIENCE & TECHNOLOGY
    # --------------------------------------------------------------------------
    {
        "id": 601,
        "subject": "Science & Technology",
        "topic": "Biotechnology & Gene Editing",
        "question": "In the context of modern genetics and biotechnology, what is 'CRISPR-Cas9' frequently mentioned in the news?",
        "options": [
            "A) A molecular targeted gene-editing technology that allows researchers to alter DNA sequences.",
            "B) A high-orbit surveillance satellite system developed by ISRO.",
            "C) A deep-learning algorithm used in quantum cryptography.",
            "D) A newly discovered antibiotic targeting multidrug-resistant tuberculosis bacteria."
        ],
        "correct_opt": "A",
        "explanation": "CRISPR-Cas9 (Clustered Regularly Interspaced Short Palindromic Repeats - Cas9 enzyme) is a breakthrough molecular tool for precise genome editing. It uses a guide RNA to direct the Cas9 endonuclease enzyme to cut double-stranded DNA at specific sequences, enabling gene insertion, deletion, or modification."
    },
    {
        "id": 602,
        "subject": "Science & Technology",
        "topic": "Space Technology & ISRO Missions",
        "question": "With reference to the launch vehicles developed by ISRO, consider the following statements:\n1. Polar Satellite Launch Vehicle (PSLV) is a four-stage launch vehicle with alternating solid and liquid propulsion stages.\n2. Launch Vehicle Mark 3 (LVM3 / GSLV Mk III) uses an indigenous Cryogenic Upper Stage (C25).\n3. PSLV is incapable of launching payloads into Geosynchronous Transfer Orbit (GTO).\n\nWhich of the statements given above is/are correct?",
        "options": [
            "A) 1 and 2 only",
            "B) 2 only",
            "C) 1 and 3 only",
            "D) 1, 2 and 3"
        ],
        "correct_opt": "A",
        "explanation": "Statement 1 is correct: PSLV is a 4-stage vehicle: 1st solid, 2nd liquid (Vikas engine), 3rd solid, 4th liquid.\nStatement 2 is correct: LVM3 is a 3-stage vehicle using two solid strap-on boosters (S200), a liquid core (L110), and a high-thrust cryogenic upper stage (C25).\nStatement 3 is INCORRECT: PSLV has launched numerous satellites into GTO (such as Chandrayaan-1, Mars Orbiter Mission, and private communication satellites), though its maximum GTO payload capacity (~1400 kg) is lower than LVM3 (~4000 kg)."
    },
    {
        "id": 603,
        "subject": "Science & Technology",
        "topic": "Emerging Tech & Quantum Computing",
        "question": "Consider the following statements regarding 'Quantum Key Distribution' (QKD):\n1. It uses principles of quantum mechanics to establish a secure communication channel between two parties.\n2. Any eavesdropping attempt changes the quantum state of the photons, instantly alerting the communicating parties.\n\nWhich of the statements given above is/are correct?",
        "options": [
            "A) 1 only",
            "B) 2 only",
            "C) Both 1 and 2",
            "D) Neither 1 nor 2"
        ],
        "correct_opt": "C",
        "explanation": "Both statements are correct: QKD exploits quantum phenomena like superposition and the Heisenberg Uncertainty Principle (measurement collapse). If an unauthorized third party intercepts quantum cryptographic keys transmitted via polarized photons, the quantum state is irrevocably disturbed, immediately exposing the interception."
    },
    {
        "id": 604,
        "subject": "Science & Technology",
        "topic": "Clean Energy & Green Hydrogen",
        "question": "Under India's National Green Hydrogen Mission, what distinguishes 'Green Hydrogen' from Grey and Blue Hydrogen?",
        "options": [
            "A) Green Hydrogen is produced by water electrolysis utilizing renewable electricity, generating zero carbon emissions.",
            "B) Green Hydrogen is derived from natural gas combined with carbon capture and storage.",
            "C) Green Hydrogen is extracted directly from deep geothermal volcanic vents.",
            "D) Green Hydrogen is produced using enriched uranium inside breeder reactors."
        ],
        "correct_opt": "A",
        "explanation": "Green hydrogen is generated through electrolysis of water using renewable energy sources (solar, wind), producing only oxygen as a byproduct with zero carbon emissions.\nGrey hydrogen is produced from natural gas (methane steam reforming) without capturing emissions. Blue hydrogen uses fossil fuels but captures and stores the emitted CO2 (CCUS)."
    },

    # --------------------------------------------------------------------------
    # 7. CSAT (QUANTITATIVE & LOGICAL REASONING)
    # --------------------------------------------------------------------------
    {
        "id": 701,
        "subject": "CSAT (Aptitude & Reasoning)",
        "topic": "Number Systems & Percentages",
        "question": "In an examination, 70% of candidates passed in English, 80% passed in Mathematics, and 10% failed in both subjects. If 144 candidates passed in both subjects, what was the total number of candidates who appeared for the exam?",
        "options": [
            "A) 240",
            "B) 200",
            "C) 250",
            "D) 300"
        ],
        "correct_opt": "A",
        "explanation": "Let total candidates be 100%.\nCandidates failing in both = 10%. Hence, candidates passing in at least one subject = 100% - 10% = 90%.\nUsing Union formula: P(English U Maths) = P(English) + P(Maths) - P(English and Maths)\n90% = 70% + 80% - P(Both)\n90% = 150% - P(Both) => P(Both) = 60%.\nGiven that 60% of total candidates = 144.\nTotal candidates = (144 / 60) * 100 = 240."
    },
    {
        "id": 702,
        "subject": "CSAT (Aptitude & Reasoning)",
        "topic": "Logical Deductions & Syllogisms",
        "question": "Read the following statements and conclusions:\nStatements:\n1. All IAS officers are civil servants.\n2. Some civil servants are researchers.\n\nConclusions:\nI. Some researchers are civil servants.\nII. All IAS officers are researchers.\n\nWhich of the conclusion(s) logically follow(s)?",
        "options": [
            "A) Only conclusion I follows",
            "B) Only conclusion II follows",
            "C) Both conclusion I and II follow",
            "D) Neither conclusion I nor II follows"
        ],
        "correct_opt": "A",
        "explanation": "From Statement 2: 'Some civil servants are researchers' directly converts to 'Some researchers are civil servants' (Simple conversion of I-type proposition). Therefore, Conclusion I strictly follows.\nConclusion II does not follow because there is no universal relationship connecting IAS officers with researchers."
    }
]


# ==============================================================================
# SUBJECT MAPPINGS & CANONICAL GROUPS
# ==============================================================================
CORE_SUBJECTS = [
    "Indian Polity & Constitution",
    "Modern Indian History",
    "Indian Economy & Budget",
    "Environment & Ecology",
    "Geography & Mapping",
    "Science & Technology",
    "CSAT (Aptitude & Reasoning)"
]

SUBJECT_SYLLABUS_MAP = {
    "Indian Polity & Constitution": {"paper": "GS Paper 2", "topics": ["Preamble", "Fundamental Rights", "Parliament", "Constitutional Bodies"]},
    "Modern Indian History": {"paper": "GS Paper 1", "topics": ["Freedom Struggle", "Colonial Acts", "Art & Architecture", "Tribal Uprisings"]},
    "Indian Economy & Budget": {"paper": "GS Paper 3", "topics": ["Monetary Policy", "Fiscal Deficit", "Inflation", "Banking", "Agriculture"]},
    "Environment & Ecology": {"paper": "GS Paper 3", "topics": ["Wetlands", "Wildlife Protection", "Biodiversity", "Climate Change"]},
    "Geography & Mapping": {"paper": "GS Paper 1", "topics": ["Indian Monsoon", "Drainage Systems", "Soils of India", "Maritime Choke Points"]},
    "Science & Technology": {"paper": "GS Paper 3", "topics": ["Biotechnology", "Space & ISRO", "Quantum Computing", "Clean Energy"]},
    "CSAT (Aptitude & Reasoning)": {"paper": "CSAT Paper 2", "topics": ["Number Systems", "Percentages", "Logical Deductions", "Reading Comprehension"]}
}


# ==============================================================================
# AI MOCK GENERATOR ENGINE
# ==============================================================================
def _parse_llm_json(raw_text: str) -> list[dict]:
    """Safely extracts JSON array from LLM response text."""
    if not raw_text:
        return []
    # Strip markdown fences
    cleaned = re.sub(r"^```(?:json)?\s*", "", raw_text.strip(), flags=re.MULTILINE)
    cleaned = re.sub(r"\s*```$", "", cleaned.strip(), flags=re.MULTILINE)

    # Find [ ... ]
    match = re.search(r"\[.*\]", cleaned, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            pass

    try:
        data = json.loads(cleaned)
        if isinstance(data, list):
            return data
    except Exception:
        pass
    return []


def generate_mock_test(
    subject: str = "Full-Length Simulation (Multi-Subject Diagnostic)",
    num_questions: int = 10,
    difficulty: str = "UPSC Prelims Standard",
    custom_topic: str = "",
    use_ai: bool = True
) -> dict[str, Any]:
    """
    Generates an authentic UPSC Prelims Mock Test.
    Uses Groq LLM if available and requested; seamlessly falls back to the
    curated high-yield question bank to guarantee immediate availability.
    """
    questions: list[dict] = []
    is_multi_subject = (
        "Full-Length" in subject
        or "Multi-Subject" in subject
        or "All Subjects" in subject
    )

    # 1. Attempt dynamic AI generation via Groq if enabled
    if use_ai:
        try:
            import config
            client = config.get_groq_client()

            subj_prompt = (
                "a balanced mix of UPSC core subjects (Indian Polity, Modern History, Indian Economy, Environment & Ecology, Geography, and Science & Technology)"
                if is_multi_subject
                else f"the subject '{subject}'" + (f" with specific focus on '{custom_topic}'" if custom_topic else "")
            )

            prompt = f"""You are the Chief Examination Controller and UPSC CSE Faculty at PW OnlyIAS.
Generate an authentic {num_questions}-question UPSC Civil Services Prelims Multiple Choice Test on {subj_prompt}.
The difficulty level must be strictly calibrated to: '{difficulty}'.

Requirements:
1. UPSC Format: High-quality statement-based questions ('1 and 2 only', '1, 2 and 3', 'None', etc.) or factual elimination style.
2. Provide exactly 4 options for each question labeled 'A) ...', 'B) ...', 'C) ...', 'D) ...'.
3. Detail the exact correct option letter ('A', 'B', 'C', or 'D').
4. Write a comprehensive, high-yield faculty explanation for each statement.

Respond ONLY with a valid JSON array of objects. Do NOT include markdown introduction or text outside the JSON.
Schema for each question object:
{{
  "id": integer (1 to {num_questions}),
  "subject": string (One of: "Indian Polity & Constitution", "Modern Indian History", "Indian Economy & Budget", "Environment & Ecology", "Geography & Mapping", "Science & Technology", "CSAT (Aptitude & Reasoning)"),
  "topic": string (specific microtopic name),
  "question": string (the full question text with statements 1, 2, 3 and the question query),
  "options": [string, string, string, string],
  "correct_opt": string ("A", "B", "C", or "D"),
  "explanation": string (detailed faculty rationale)
}}"""

            response = client.chat.completions.create(
                model=config.LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.25,
                max_tokens=3000
            )
            raw_content = response.choices[0].message.content or ""
            parsed = _parse_llm_json(raw_content)

            # Validate generated questions
            valid_qs = []
            for item in parsed:
                if (
                    isinstance(item, dict)
                    and item.get("question")
                    and isinstance(item.get("options"), list)
                    and len(item["options"]) == 4
                    and item.get("correct_opt") in ["A", "B", "C", "D"]
                ):
                    valid_qs.append(item)

            if len(valid_qs) >= min(3, num_questions):
                questions = valid_qs[:num_questions]
        except Exception as e:
            print(f"[MockEngine] AI generation note: {e}. Falling back to curated question bank.")

    # 2. Fallback to Curated Question Bank
    if not questions:
        if is_multi_subject:
            # Select balanced questions across all subjects
            by_subj: dict[str, list[dict]] = {}
            for q in MOCK_QUESTION_BANK:
                s = q["subject"]
                by_subj.setdefault(s, []).append(q)

            selected = []
            # Round-robin pick from each subject
            shuffled_subjects = list(by_subj.keys())
            random.shuffle(shuffled_subjects)

            idx = 0
            while len(selected) < num_questions:
                subj = shuffled_subjects[idx % len(shuffled_subjects)]
                available = [q for q in by_subj[subj] if q not in selected]
                if available:
                    selected.append(random.choice(available))
                idx += 1
                if all(len([q for q in by_subj[s] if q not in selected]) == 0 for s in shuffled_subjects):
                    break
            questions = selected
        else:
            # Filter for specific subject
            matched = [
                q for q in MOCK_QUESTION_BANK
                if subject.lower() in q["subject"].lower()
                or (custom_topic and custom_topic.lower() in q.get("topic", "").lower())
            ]
            if not matched:
                matched = MOCK_QUESTION_BANK
            random.shuffle(matched)
            questions = matched[:num_questions]

    # Re-index questions cleanly 1..N
    formatted_questions = []
    for idx, q in enumerate(questions, start=1):
        q_copy = dict(q)
        q_copy["id"] = idx
        formatted_questions.append(q_copy)

    title = (
        f"Full-Length Multi-Subject Prelims Diagnostic Mock ({len(formatted_questions)} Qs)"
        if is_multi_subject
        else f"Sectional Prelims Mock: {subject} ({len(formatted_questions)} Qs)"
    )

    return {
        "title": title,
        "subject": subject,
        "difficulty": difficulty,
        "num_questions": len(formatted_questions),
        "questions": formatted_questions,
        "is_multi_subject": is_multi_subject
    }


# ==============================================================================
# COMPREHENSIVE PERFORMANCE EVALUATION & WEAK / STRONG SUBJECTS REPORT
# ==============================================================================
def evaluate_mock_test(
    test_obj: dict[str, Any],
    user_answers: dict[int, Optional[str]]
) -> dict[str, Any]:
    """
    Evaluates student test answers with standard UPSC marking (+2.0 correct, -0.66 incorrect).
    Computes diagnostic analytics:
    - Overall Scorecard & Cutoff estimate
    - Subject-wise breakdown (Strong, Moderate, Weak subjects)
    - Specific microtopics missed
    - Actionable AI recommendations linking to Syllabus Navigator
    """
    questions = test_obj.get("questions", [])
    total_q = len(questions)

    correct_count = 0
    incorrect_count = 0
    skipped_count = 0

    evaluated_questions = []
    subject_stats: dict[str, dict[str, Any]] = {}

    for q in questions:
        qid = q["id"]
        subj = q.get("subject", "General Studies")
        topic = q.get("topic", "Core Microtopic")
        correct_letter = str(q.get("correct_opt", "A")).strip().upper()[0]

        if subj not in subject_stats:
            subject_stats[subj] = {
                "subject": subj,
                "total": 0,
                "attempted": 0,
                "correct": 0,
                "incorrect": 0,
                "skipped": 0,
                "marks": 0.0,
                "topics_missed": []
            }

        subject_stats[subj]["total"] += 1
        user_choice = user_answers.get(qid)

        is_attempted = user_choice is not None and str(user_choice).strip() != ""
        is_correct = False

        if not is_attempted:
            skipped_count += 1
            subject_stats[subj]["skipped"] += 1
            status = "skipped"
            earned = 0.0
        else:
            subject_stats[subj]["attempted"] += 1
            # Extract choice letter (e.g. from "A) 1 and 2 only" -> "A")
            user_letter = str(user_choice).strip().upper()[0]

            if user_letter == correct_letter:
                is_correct = True
                correct_count += 1
                subject_stats[subj]["correct"] += 1
                subject_stats[subj]["marks"] += 2.0
                status = "correct"
                earned = 2.0
            else:
                incorrect_count += 1
                subject_stats[subj]["incorrect"] += 1
                subject_stats[subj]["marks"] -= 0.66
                subject_stats[subj]["topics_missed"].append(topic)
                status = "incorrect"
                earned = -0.66

        evaluated_questions.append({
            "id": qid,
            "subject": subj,
            "topic": topic,
            "question": q["question"],
            "options": q["options"],
            "correct_opt": correct_letter,
            "user_choice": user_choice,
            "status": status,
            "earned": earned,
            "explanation": q.get("explanation", "")
        })

    # Marks calculations
    gross_marks = correct_count * 2.0
    negative_marks = incorrect_count * 0.66
    net_marks = max(0.0, gross_marks - negative_marks)
    max_marks = total_q * 2.0

    attempted_total = correct_count + incorrect_count
    accuracy_pct = (correct_count / attempted_total * 100.0) if attempted_total > 0 else 0.0
    score_pct = (net_marks / max_marks * 100.0) if max_marks > 0 else 0.0

    # Categorize Strong, Moderate, and Weak Subjects
    strong_subjects = []
    moderate_subjects = []
    weak_subjects = []

    for subj, data in subject_stats.items():
        att = data["attempted"]
        corr = data["correct"]
        subj_acc = (corr / att * 100.0) if att > 0 else 0.0
        data["accuracy"] = round(subj_acc, 1)
        data["marks"] = round(data["marks"], 2)

        if att > 0 and subj_acc >= 70.0:
            data["category"] = "strong"
            data["badge"] = "🟢 Strong Subject"
            data["assessment"] = f"Outstanding conceptual clarity ({subj_acc:.0f}% accuracy). Solid grasp of foundational principles."
            strong_subjects.append(data)
        elif att > 0 and subj_acc >= 50.0:
            data["category"] = "moderate"
            data["badge"] = "🟡 Moderate / Needs Polish"
            data["assessment"] = f"Good baseline ({subj_acc:.0f}% accuracy), but susceptible to negative marking on statement elimination."
            moderate_subjects.append(data)
        else:
            data["category"] = "weak"
            data["badge"] = "🔴 Weak Subject (Priority)"
            data["assessment"] = f"Critical study gap ({subj_acc:.0f}% accuracy). Low accuracy and multiple negative penalties incurred."
            weak_subjects.append(data)

    # Sort each list by accuracy descending
    strong_subjects.sort(key=lambda x: x["accuracy"], reverse=True)
    moderate_subjects.sort(key=lambda x: x["accuracy"], reverse=True)
    weak_subjects.sort(key=lambda x: x["accuracy"])

    # Performance tier indicator
    if score_pct >= 65.0:
        tier_title = "🔥 High Prelims Qualification Tier"
        tier_desc = "Your score comfortably surpasses the typical UPSC GS-1 Prelims cutoff range (~86-94 / 200). Maintain momentum with periodic full simulations."
        tier_color = "#059669"
    elif score_pct >= 45.0:
        tier_title = "⚖️ Borderline Competitive Tier"
        tier_desc = "Within striking range of the Prelims cutoff. Reducing negative marking and converting moderate subjects to strong will secure qualification."
        tier_color = "#D97706"
    else:
        tier_title = "🚨 Foundation Consolidation Needed"
        tier_desc = "Score is currently below competitive threshold. Intensive revision of weak subject microtopics in Syllabus Navigator is strongly advised."
        tier_color = "#DC2626"

    # Actionable AI study recommendations
    study_recommendations = []
    for w in weak_subjects:
        s_name = w["subject"]
        paper_info = SUBJECT_SYLLABUS_MAP.get(s_name, {"paper": "Syllabus Navigator", "topics": []})
        paper_name = paper_info.get("paper", "Syllabus Navigator")
        missed_topics_str = ", ".join(w["topics_missed"][:2]) if w["topics_missed"] else "Core fundamentals"

        study_recommendations.append({
            "subject": s_name,
            "paper": paper_name,
            "priority": "HIGH",
            "action": f"Revisit {paper_name} in the Syllabus Navigator to complete foundational microtopics in {s_name} (especially {missed_topics_str}). Solve 10 PYQs on this topic before retaking.",
            "prompt_for_copilot": f"Explain the core UPSC Prelims concepts and common elimination traps for '{s_name}' (focus: {missed_topics_str})."
        })

    for m in moderate_subjects:
        s_name = m["subject"]
        study_recommendations.append({
            "subject": s_name,
            "paper": "PYQ Drills",
            "priority": "MEDIUM",
            "action": f"Practice statement-elimination drills for {s_name}. Your conceptual base is sound; focus on avoiding traps with extreme words ('all', 'never', 'only').",
            "prompt_for_copilot": f"Give me 5 high-yield statement elimination questions on '{s_name}' with detailed trick breakdowns."
        })

    return {
        "title": test_obj.get("title", "UPSC Prelims Mock Test"),
        "total_questions": total_q,
        "attempted": attempted_total,
        "correct": correct_count,
        "incorrect": incorrect_count,
        "skipped": skipped_count,
        "gross_marks": round(gross_marks, 2),
        "negative_marks": round(negative_marks, 2),
        "net_marks": round(net_marks, 2),
        "max_marks": round(max_marks, 2),
        "accuracy_pct": round(accuracy_pct, 1),
        "score_pct": round(score_pct, 1),
        "tier_title": tier_title,
        "tier_desc": tier_desc,
        "tier_color": tier_color,
        "subject_stats": subject_stats,
        "strong_subjects": strong_subjects,
        "moderate_subjects": moderate_subjects,
        "weak_subjects": weak_subjects,
        "study_recommendations": study_recommendations,
        "evaluated_questions": evaluated_questions
    }
