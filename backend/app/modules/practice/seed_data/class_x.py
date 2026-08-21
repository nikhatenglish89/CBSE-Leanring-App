"""CBSE Class X practice-set question bank (NCERT-aligned, original content)."""

QUESTIONS: dict[str, list[dict]] = {
    "Mathematics": [
        {
            "question_text": "Using prime factorisation, what is the HCF of 6 and 20?",
            "options": ["2", "4", "6", "10"],
            "correct_index": 0,
            "explanation": "6 = 2 x 3 and 20 = 2^2 x 5, so the only common prime factor is 2.",
        },
        {
            "question_text": "Which of the following is an irrational number?",
            "options": ["√4", "√9", "√2", "1/2"],
            "correct_index": 2,
            "explanation": "√2 cannot be written as p/q with integers p, q (q ≠ 0), unlike the other options.",
        },
        {
            "question_text": "What is the degree of the polynomial p(x) = 3x^2 + 5x - 7?",
            "options": ["1", "2", "3", "0"],
            "correct_index": 1,
            "explanation": "The degree is the highest power of x in the polynomial, which is 2.",
        },
        {
            "question_text": "One zero of the polynomial x^2 - 4 is 2. What is the other zero?",
            "options": ["-2", "2", "4", "-4"],
            "correct_index": 0,
            "explanation": "x^2 - 4 = (x - 2)(x + 2), so the zeroes are 2 and -2.",
        },
        {
            "question_text": "For a quadratic polynomial ax^2 + bx + c, the sum of its zeroes equals:",
            "options": ["c/a", "-b/a", "b/a", "-c/a"],
            "correct_index": 1,
            "explanation": "By the relation between zeroes and coefficients, sum of zeroes = -b/a.",
        },
        {
            "question_text": (
                "For the pair of linear equations a1x + b1y = c1 and a2x + b2y = c2, "
                "if a1/a2 = b1/b2 ≠ c1/c2, the lines are:"
            ),
            "options": ["Intersecting", "Coincident", "Parallel (no solution)", "Perpendicular"],
            "correct_index": 2,
            "explanation": "Equal slopes with different intercepts means the lines never meet, so there is no solution.",
        },
        {
            "question_text": (
                "For a pair of linear equations, if a1/a2 = b1/b2 = c1/c2, the pair has:"
            ),
            "options": ["No solution", "A unique solution", "Infinitely many solutions", "Exactly two solutions"],
            "correct_index": 2,
            "explanation": "When all three ratios are equal, both equations represent the same line.",
        },
        {
            "question_text": (
                "For the quadratic equation ax^2 + bx + c = 0, if the discriminant b^2 - 4ac > 0, "
                "the equation has:"
            ),
            "options": ["No real roots", "Two equal real roots", "Two distinct real roots", "Only one root"],
            "correct_index": 2,
            "explanation": "A positive discriminant means the square root term is a real, non-zero value, giving two distinct roots.",
        },
        {
            "question_text": "What are the roots of the equation x^2 - 5x + 6 = 0?",
            "options": ["2 and 3", "1 and 6", "-2 and -3", "2 and -3"],
            "correct_index": 0,
            "explanation": "Factorising gives (x - 2)(x - 3) = 0, so x = 2 or x = 3.",
        },
        {
            "question_text": "What is the common difference of the AP 3, 7, 11, 15, ...?",
            "options": ["3", "4", "5", "7"],
            "correct_index": 1,
            "explanation": "Each term is obtained by adding 4 to the previous term.",
        },
        {
            "question_text": "What is the 10th term of the AP 2, 5, 8, 11, ...?",
            "options": ["29", "26", "32", "27"],
            "correct_index": 0,
            "explanation": "Using an = a + (n-1)d with a=2, d=3, n=10: a10 = 2 + 9(3) = 29.",
        },
        {
            "question_text": (
                "The sum of the first n terms of an AP with first term a and common difference d is given by:"
            ),
            "options": [
                "Sn = n/2 [2a + (n-1)d]",
                "Sn = n [2a + (n-1)d]",
                "Sn = n/2 [a + (n-1)d]",
                "Sn = n/2 [2a + nd]",
            ],
            "correct_index": 0,
            "explanation": "This is the standard sum formula for an arithmetic progression.",
        },
        {
            "question_text": (
                "The theorem stating that a line drawn parallel to one side of a triangle divides "
                "the other two sides proportionally is known as:"
            ),
            "options": ["Pythagoras Theorem", "Basic Proportionality Theorem", "Mid-point Theorem", "Angle Sum Theorem"],
            "correct_index": 1,
            "explanation": "This is the Basic Proportionality Theorem, also called Thales' Theorem.",
        },
        {
            "question_text": "Two triangles are similar by the AA criterion if:",
            "options": [
                "All three sides are proportional",
                "Two angles of one triangle equal two angles of the other",
                "One angle and two sides are equal",
                "Their areas are equal",
            ],
            "correct_index": 1,
            "explanation": "If two angles match, the third must also match (angle sum = 180 degrees), making the triangles similar.",
        },
        {
            "question_text": "What is the distance between the points (0, 0) and (3, 4)?",
            "options": ["5", "6", "7", "4"],
            "correct_index": 0,
            "explanation": "Distance = √((3-0)^2 + (4-0)^2) = √(9+16) = √25 = 5.",
        },
        {
            "question_text": "What are the coordinates of the midpoint of the segment joining (2, 4) and (6, 8)?",
            "options": ["(4, 6)", "(3, 5)", "(8, 12)", "(2, 4)"],
            "correct_index": 0,
            "explanation": "Midpoint = ((2+6)/2, (4+8)/2) = (4, 6).",
        },
        {
            "question_text": "What is the value of sin 30°?",
            "options": ["1/2", "√3/2", "1", "0"],
            "correct_index": 0,
            "explanation": "sin 30° is a standard trigonometric value equal to 1/2.",
        },
        {
            "question_text": "Which of the following is a correct trigonometric identity?",
            "options": [
                "sin²θ + cos²θ = 1",
                "sin²θ - cos²θ = 1",
                "sinθ + cosθ = 1",
                "sin²θ x cos²θ = 1",
            ],
            "correct_index": 0,
            "explanation": "This is the fundamental Pythagorean trigonometric identity, true for all θ.",
        },
        {
            "question_text": (
                "The angle formed between the horizontal line and the line of sight when an observer "
                "looks upward at an object is called the:"
            ),
            "options": ["Angle of depression", "Angle of elevation", "Angle of incidence", "Angle of refraction"],
            "correct_index": 1,
            "explanation": "Looking upward from the horizontal gives the angle of elevation.",
        },
        {
            "question_text": "How many tangents can be drawn to a circle from a point outside it?",
            "options": ["1", "2", "3", "Infinite"],
            "correct_index": 1,
            "explanation": "Exactly two tangents can be drawn to a circle from any external point.",
        },
    ],
    "Science": [
        {
            "question_text": "What type of reaction is 2Mg + O2 → 2MgO?",
            "options": ["Combination reaction", "Decomposition reaction", "Displacement reaction", "Double displacement reaction"],
            "correct_index": 0,
            "explanation": "Two reactants combine to form a single product, which defines a combination reaction.",
        },
        {
            "question_text": "Which gas is evolved when a metal reacts with a dilute acid?",
            "options": ["Oxygen", "Hydrogen", "Carbon dioxide", "Nitrogen"],
            "correct_index": 1,
            "explanation": "Metals reacting with dilute acids displace hydrogen gas, e.g. Zn + H2SO4 → ZnSO4 + H2.",
        },
        {
            "question_text": "What is the pH of a neutral solution at room temperature?",
            "options": ["0", "7", "14", "1"],
            "correct_index": 1,
            "explanation": "A pH of 7 indicates a neutral solution, neither acidic nor basic.",
        },
        {
            "question_text": "Which of these compounds is commonly used as an antacid to treat acidity?",
            "options": ["Sodium chloride", "Magnesium hydroxide", "Sulphuric acid", "Copper sulphate"],
            "correct_index": 1,
            "explanation": "Magnesium hydroxide is a mild base that neutralises excess stomach acid.",
        },
        {
            "question_text": "Which metal is so reactive that it is stored under kerosene?",
            "options": ["Iron", "Sodium", "Copper", "Gold"],
            "correct_index": 1,
            "explanation": "Sodium reacts vigorously with air and water, so it is stored under kerosene oil.",
        },
        {
            "question_text": "What is the chemical formula of baking soda?",
            "options": ["NaHCO3", "Na2CO3", "NaOH", "CaCO3"],
            "correct_index": 0,
            "explanation": "Baking soda is sodium hydrogen carbonate, NaHCO3.",
        },
        {
            "question_text": "Elements in the same group of the periodic table have the same number of:",
            "options": ["Protons", "Neutrons", "Valence electrons", "Isotopes"],
            "correct_index": 2,
            "explanation": "Elements are grouped by matching valence electron count, which drives similar chemical behaviour.",
        },
        {
            "question_text": "The functional group -OH is characteristic of which class of compounds?",
            "options": ["Aldehydes", "Alcohols", "Carboxylic acids", "Ketones"],
            "correct_index": 1,
            "explanation": "The hydroxyl group -OH defines the alcohol family of organic compounds.",
        },
        {
            "question_text": "Which of the following is the basic structural and functional unit of the kidney?",
            "options": ["Neuron", "Nephron", "Alveolus", "Nephridium"],
            "correct_index": 1,
            "explanation": "The nephron filters blood and forms urine, making it the kidney's functional unit.",
        },
        {
            "question_text": "Which hormone regulates blood sugar level in humans?",
            "options": ["Adrenaline", "Thyroxine", "Insulin", "Testosterone"],
            "correct_index": 2,
            "explanation": "Insulin, secreted by the pancreas, lowers blood glucose levels.",
        },
        {
            "question_text": "Which part of the human eye controls the amount of light entering it?",
            "options": ["Retina", "Cornea", "Iris", "Pupil"],
            "correct_index": 2,
            "explanation": "The iris is the muscular structure that adjusts the size of the pupil to regulate light entry.",
        },
        {
            "question_text": "In human females, which organ produces the egg cell?",
            "options": ["Uterus", "Ovary", "Fallopian tube", "Cervix"],
            "correct_index": 1,
            "explanation": "The ovaries produce and release egg cells (ova) during the menstrual cycle.",
        },
        {
            "question_text": "The process by which offspring resemble their parents is called:",
            "options": ["Evolution", "Heredity", "Variation", "Speciation"],
            "correct_index": 1,
            "explanation": "Heredity is the passing of traits from parents to offspring through genes.",
        },
        {
            "question_text": "A concave mirror always forms a virtual image when the object is placed:",
            "options": ["Beyond the centre of curvature", "At the focus", "Between the pole and the focus", "At the centre of curvature"],
            "correct_index": 2,
            "explanation": "When the object is between the pole and focus, the reflected rays diverge, forming a virtual, magnified image.",
        },
        {
            "question_text": "The bending of light as it passes from one medium to another is called:",
            "options": ["Reflection", "Refraction", "Dispersion", "Diffraction"],
            "correct_index": 1,
            "explanation": "Refraction is the change in direction of light when it crosses a boundary between media of different densities.",
        },
        {
            "question_text": "The SI unit of electrical resistance is:",
            "options": ["Ampere", "Volt", "Ohm", "Watt"],
            "correct_index": 2,
            "explanation": "Resistance is measured in ohms, symbol Ω.",
        },
        {
            "question_text": "According to Ohm's law, the relationship between voltage (V), current (I), and resistance (R) is:",
            "options": ["V = I/R", "V = IR", "V = R/I", "V = I + R"],
            "correct_index": 1,
            "explanation": "Ohm's law states V = IR at constant temperature.",
        },
        {
            "question_text": "The device that produces electric current by rotating a coil in a magnetic field is called a/an:",
            "options": ["Electric motor", "Generator", "Transformer", "Galvanometer"],
            "correct_index": 1,
            "explanation": "A generator converts mechanical energy into electrical energy using electromagnetic induction.",
        },
        {
            "question_text": "Which of these is a renewable source of energy?",
            "options": ["Coal", "Petroleum", "Solar energy", "Natural gas"],
            "correct_index": 2,
            "explanation": "Solar energy is continuously replenished by the sun, unlike fossil fuels.",
        },
        {
            "question_text": "The green pigment in plants that captures sunlight for photosynthesis is called:",
            "options": ["Xylem", "Chlorophyll", "Stomata", "Cellulose"],
            "correct_index": 1,
            "explanation": "Chlorophyll absorbs light energy, which drives the process of photosynthesis.",
        },
    ],
    "English": [
        {
            "question_text": "Choose the correct form of the verb: 'She ___ to school every day.'",
            "options": ["go", "goes", "going", "gone"],
            "correct_index": 1,
            "explanation": "Third-person singular subjects ('she') take the -s form of the verb in simple present tense.",
        },
        {
            "question_text": "Which of the following is a correctly punctuated question?",
            "options": ["Where are you going.", "Where are you going?", "where are you going?", "Where are you going"],
            "correct_index": 1,
            "explanation": "A question must start with a capital letter and end with a question mark.",
        },
        {
            "question_text": "Choose the correct passive voice of: 'The teacher is teaching the lesson.'",
            "options": [
                "The lesson is taught by the teacher.",
                "The lesson was being taught by the teacher.",
                "The lesson is being taught by the teacher.",
                "The lesson has been taught by the teacher.",
            ],
            "correct_index": 2,
            "explanation": "Present continuous active ('is teaching') becomes present continuous passive ('is being taught').",
        },
        {
            "question_text": "Fill in the blank with the correct modal: 'You ___ finish your homework before dinner.'",
            "options": ["can", "must", "may", "would"],
            "correct_index": 1,
            "explanation": "'Must' expresses obligation, which fits the context of a required task.",
        },
        {
            "question_text": "Choose the correct reported speech for: He said, 'I am tired.'",
            "options": [
                "He said that he is tired.",
                "He said that he was tired.",
                "He says that he was tired.",
                "He said that I was tired.",
            ],
            "correct_index": 1,
            "explanation": "In reported speech, present tense shifts to past tense and the pronoun changes to match the subject.",
        },
        {
            "question_text": "Identify the synonym of 'benevolent'.",
            "options": ["Cruel", "Kind", "Angry", "Selfish"],
            "correct_index": 1,
            "explanation": "'Benevolent' means kind and generous.",
        },
        {
            "question_text": "Identify the antonym of 'abundant'.",
            "options": ["Plentiful", "Scarce", "Huge", "Rich"],
            "correct_index": 1,
            "explanation": "'Abundant' means plentiful, so its opposite is 'scarce'.",
        },
        {
            "question_text": "Choose the correctly spelled word.",
            "options": ["Recieve", "Receive", "Receeve", "Receve"],
            "correct_index": 1,
            "explanation": "The correct spelling follows 'i before e except after c' is an exception here: it is 'receive'.",
        },
        {
            "question_text": "Select the sentence with the correct article usage.",
            "options": [
                "I saw a elephant at the zoo.",
                "I saw an elephant at the zoo.",
                "I saw the a elephant at the zoo.",
                "I saw elephant at the zoo.",
            ],
            "correct_index": 1,
            "explanation": "'Elephant' begins with a vowel sound, so it takes the article 'an'.",
        },
        {
            "question_text": "Choose the correctly structured conditional sentence.",
            "options": [
                "If it will rain, I will stay home.",
                "If it rains, I will stay home.",
                "If it rain, I will stay home.",
                "If it rained, I will stay home.",
            ],
            "correct_index": 1,
            "explanation": "First conditional sentences use simple present in the 'if' clause and 'will' in the main clause.",
        },
        {
            "question_text": "Identify the part of speech of the underlined word: 'She sings BEAUTIFULLY.'",
            "options": ["Adjective", "Adverb", "Noun", "Verb"],
            "correct_index": 1,
            "explanation": "'Beautifully' describes how she sings, which makes it an adverb.",
        },
        {
            "question_text": "Choose the correct preposition: 'The book is ___ the table.'",
            "options": ["in", "on", "at", "by"],
            "correct_index": 1,
            "explanation": "'On' correctly describes an object resting on a surface.",
        },
        {
            "question_text": "Choose the sentence that correctly uses the present perfect tense.",
            "options": [
                "I have finished my homework.",
                "I finished my homework yesterday.",
                "I am finishing my homework.",
                "I will finish my homework.",
            ],
            "correct_index": 0,
            "explanation": "The present perfect tense is formed with 'have/has' plus a past participle.",
        },
        {
            "question_text": "Identify the correctly formed question tag: 'She is coming, ___?'",
            "options": ["isn't it", "isn't she", "doesn't she", "wasn't she"],
            "correct_index": 1,
            "explanation": "The tag must match the subject 'she' and the auxiliary verb 'is', negated.",
        },
        {
            "question_text": "Choose the correct plural form of 'child'.",
            "options": ["childs", "children", "childes", "childern"],
            "correct_index": 1,
            "explanation": "'Child' has the irregular plural form 'children'.",
        },
        {
            "question_text": "Select the correct comparative form of 'good'.",
            "options": ["gooder", "best", "better", "more good"],
            "correct_index": 2,
            "explanation": "'Good' has the irregular comparative form 'better'.",
        },
        {
            "question_text": "Choose the sentence that is free from grammatical error.",
            "options": [
                "Neither of the boys were present.",
                "Neither of the boys was present.",
                "Neither of the boys is being present.",
                "Neither of the boys has being present.",
            ],
            "correct_index": 1,
            "explanation": "'Neither' takes a singular verb, so 'was' is correct.",
        },
        {
            "question_text": "Identify the correct indirect form: She said, 'I will call you tomorrow.'",
            "options": [
                "She said that she will call me tomorrow.",
                "She said that she would call me the next day.",
                "She says that she would call me tomorrow.",
                "She said she calls me tomorrow.",
            ],
            "correct_index": 1,
            "explanation": "'Will' shifts to 'would' and 'tomorrow' shifts to 'the next day' in reported speech.",
        },
        {
            "question_text": "Choose the correctly punctuated sentence using a semicolon.",
            "options": [
                "I like tea, however I dislike coffee.",
                "I like tea; however, I dislike coffee.",
                "I like tea however; I dislike coffee.",
                "I like tea, however; I dislike coffee.",
            ],
            "correct_index": 1,
            "explanation": "A semicolon joins two related independent clauses, followed by a comma after the connecting adverb 'however'.",
        },
        {
            "question_text": "Choose the correct word: '___ going to the market.'",
            "options": ["Their", "There", "They're", "Thier"],
            "correct_index": 2,
            "explanation": "'They're' is the contraction of 'they are', which fits the sentence.",
        },
    ],
    "Hindi": [
        {
            "question_text": "'राम एक अच्छा लड़का है।' इस वाक्य में 'अच्छा' शब्द कौन सा है?",
            "options": ["संज्ञा", "सर्वनाम", "विशेषण", "क्रिया"],
            "correct_index": 2,
            "explanation": "'अच्छा' संज्ञा (लड़का) की विशेषता बता रहा है, इसलिए यह विशेषण है।",
        },
        {
            "question_text": "'हवा' शब्द का पर्यायवाची शब्द चुनिए।",
            "options": ["पवन", "जल", "अग्नि", "पृथ्वी"],
            "correct_index": 0,
            "explanation": "'पवन' और 'हवा' दोनों का अर्थ वायु है, अतः ये पर्यायवाची हैं।",
        },
        {
            "question_text": "'रात' शब्द का विलोम शब्द क्या है?",
            "options": ["दिन", "सुबह", "शाम", "संध्या"],
            "correct_index": 0,
            "explanation": "'रात' का सीधा विपरीत अर्थ 'दिन' है।",
        },
        {
            "question_text": "'हाथ पर हाथ धरे बैठना' मुहावरे का सही अर्थ क्या है?",
            "options": ["बहुत परिश्रम करना", "निष्क्रिय रहना", "बहुत खुश होना", "झगड़ा करना"],
            "correct_index": 1,
            "explanation": "यह मुहावरा किसी काम को न करते हुए निष्क्रिय बैठे रहने की स्थिति के लिए प्रयोग होता है।",
        },
        {
            "question_text": "'राजा + इन्द्र' के मेल से कौन-सा शब्द बनेगा?",
            "options": ["राजेन्द्र", "राजइन्द्र", "राजिन्द्र", "राजान्द्र"],
            "correct_index": 0,
            "explanation": "आ + इ = ए (गुण संधि) के नियम से 'राजा + इन्द्र' मिलकर 'राजेन्द्र' बनता है।",
        },
        {
            "question_text": "'विद्यालय' शब्द किन दो शब्दों के मेल से बना है?",
            "options": ["विद्या + आलय", "विद्या + लय", "विद्य + आलय", "विद्या + अलय"],
            "correct_index": 0,
            "explanation": "'विद्या' और 'आलय' के मेल (आ+आ=आ, दीर्घ संधि) से 'विद्यालय' शब्द बनता है।",
        },
        {
            "question_text": "'पुस्तकालय' शब्द में कौन-सा समास है?",
            "options": ["तत्पुरुष समास", "द्वंद्व समास", "बहुव्रीहि समास", "अव्ययीभाव समास"],
            "correct_index": 0,
            "explanation": "'पुस्तकों का आलय' अर्थ में परसर्ग का लोप होने से यह तत्पुरुष समास है।",
        },
        {
            "question_text": "'नीलकंठ' (जिसका कंठ नीला है, अर्थात् शिव) शब्द में कौन-सा समास है?",
            "options": ["तत्पुरुष समास", "द्वंद्व समास", "बहुव्रीहि समास", "कर्मधारय समास"],
            "correct_index": 2,
            "explanation": "जहाँ समस्त पद किसी अन्य अर्थ (शिव) की ओर संकेत करता है, वहाँ बहुव्रीहि समास होता है।",
        },
        {
            "question_text": "'लड़का' शब्द का बहुवचन रूप क्या होगा?",
            "options": ["लड़के", "लड़का", "लड़कों", "लड़कियाँ"],
            "correct_index": 0,
            "explanation": "पुल्लिंग शब्द 'लड़का' का सामान्य बहुवचन रूप 'लड़के' होता है।",
        },
        {
            "question_text": "'गाय' शब्द का लिंग क्या है?",
            "options": ["पुल्लिंग", "स्त्रीलिंग", "नपुंसक लिंग", "उभयलिंगी"],
            "correct_index": 1,
            "explanation": "'गाय' स्त्रीलिंग संज्ञा है।",
        },
        {
            "question_text": "'वह पत्र लिखता है।' वाच्य की दृष्टि से यह वाक्य कौन-सा है?",
            "options": ["कर्तृवाच्य", "कर्मवाच्य", "भाववाच्य", "निषेधवाच्य"],
            "correct_index": 0,
            "explanation": "इस वाक्य में क्रिया का रूप कर्ता (वह) के अनुसार है, इसलिए यह कर्तृवाच्य है।",
        },
        {
            "question_text": "'सुनना' क्रिया का कर्मवाच्य रूप क्या होगा?",
            "options": ["सुना जाता है", "सुनता है", "सुनाया", "सुनकर"],
            "correct_index": 0,
            "explanation": "कर्मवाच्य में क्रिया 'जाना' सहायक क्रिया के साथ बनती है, जैसे 'सुना जाता है'।",
        },
        {
            "question_text": "'जो कठिनाई से प्राप्त हो' के लिए उपयुक्त एक शब्द क्या होगा?",
            "options": ["सुलभ", "दुर्लभ", "सुगम", "अलभ्य"],
            "correct_index": 1,
            "explanation": "'दुर्लभ' का अर्थ ही है जो कठिनाई से प्राप्त हो।",
        },
        {
            "question_text": "पत्र लेखन में 'प्रिय मित्र' जैसा संबोधन किस प्रकार के पत्र में प्रयुक्त होता है?",
            "options": ["औपचारिक पत्र", "अनौपचारिक पत्र", "कार्यालयी पत्र", "आवेदन पत्र"],
            "correct_index": 1,
            "explanation": "मित्रों-परिवार को लिखे जाने वाले अनौपचारिक पत्रों में ऐसा आत्मीय संबोधन प्रयुक्त होता है।",
        },
        {
            "question_text": "'श्याम काला है, किन्तु सुंदर है।' यह किस प्रकार का वाक्य है?",
            "options": ["सरल वाक्य", "संयुक्त वाक्य", "मिश्र वाक्य", "विस्मयादिबोधक वाक्य"],
            "correct_index": 1,
            "explanation": "दो स्वतंत्र उपवाक्य समुच्चयबोधक 'किन्तु' से जुड़े हैं, इसलिए यह संयुक्त वाक्य है।",
        },
        {
            "question_text": "'चरण-कमल बंदौं हरि राई।' पंक्ति में कौन-सा अलंकार है?",
            "options": ["उपमा अलंकार", "रूपक अलंकार", "अनुप्रास अलंकार", "यमक अलंकार"],
            "correct_index": 1,
            "explanation": "यहाँ चरण को सीधे कमल कहा गया है (बिना 'जैसा/सा' शब्द के), इसलिए यह रूपक अलंकार है।",
        },
        {
            "question_text": "जहाँ किसी वर्ण की आवृत्ति बार-बार हो, वहाँ कौन-सा अलंकार होता है?",
            "options": ["उपमा अलंकार", "रूपक अलंकार", "अनुप्रास अलंकार", "उत्प्रेक्षा अलंकार"],
            "correct_index": 2,
            "explanation": "वर्णों की आवृत्ति पर आधारित अलंकार को अनुप्रास अलंकार कहते हैं।",
        },
        {
            "question_text": "'राम रावण को मारता है।' का कर्मवाच्य रूप चुनिए।",
            "options": [
                "राम के द्वारा रावण को मारा जाता है।",
                "रावण राम को मारता है।",
                "राम रावण से मारा गया।",
                "रावण राम के द्वारा मारा जाएगा।",
            ],
            "correct_index": 0,
            "explanation": "कर्मवाच्य में कर्म (रावण) मुख्य होता है और कर्ता के साथ 'के द्वारा' लगता है।",
        },
        {
            "question_text": "'हिमालय' शब्द किन दो शब्दों से मिलकर बना है?",
            "options": ["हिम + आलय", "हिम + लय", "हि + मालय", "हिमा + लय"],
            "correct_index": 0,
            "explanation": "'हिम' (बर्फ) और 'आलय' (घर) के मेल से 'हिमालय' शब्द बनता है, अर्थात् बर्फ का घर।",
        },
        {
            "question_text": "'हरि' शब्द किस प्रकार का शब्द है, जिसके एक से अधिक अर्थ (जैसे विष्णु, सिंह, बंदर) होते हैं?",
            "options": ["एकार्थी शब्द", "अनेकार्थी शब्द", "पर्यायवाची शब्द", "विलोम शब्द"],
            "correct_index": 1,
            "explanation": "एक ही शब्द के कई भिन्न अर्थ होने पर उसे अनेकार्थी शब्द कहा जाता है।",
        },
    ],
    "Social Science": [
        {
            "question_text": "The idea of modern nationalism in Europe is most closely linked to which event?",
            "options": ["The Industrial Revolution", "The French Revolution", "World War I", "The Renaissance"],
            "correct_index": 1,
            "explanation": "The French Revolution of 1789 introduced ideas of the nation as a political community, spreading nationalist ideals across Europe.",
        },
        {
            "question_text": "Who led the Salt March (Dandi March) in 1930?",
            "options": ["Jawaharlal Nehru", "Mahatma Gandhi", "Subhas Chandra Bose", "Bhagat Singh"],
            "correct_index": 1,
            "explanation": "Mahatma Gandhi led the Dandi March to protest the British salt tax as part of the Civil Disobedience Movement.",
        },
        {
            "question_text": "The Non-Cooperation Movement in India was launched in which year?",
            "options": ["1920", "1930", "1942", "1919"],
            "correct_index": 0,
            "explanation": "Gandhi launched the Non-Cooperation Movement in 1920 following the Khilafat and Jallianwala Bagh events.",
        },
        {
            "question_text": "Nazism, as a political ideology, is most closely associated with which country?",
            "options": ["Italy", "Germany", "Spain", "France"],
            "correct_index": 1,
            "explanation": "Nazism emerged in Germany under Adolf Hitler's leadership in the 1920s-30s.",
        },
        {
            "question_text": "The spread of print culture played a major role in shaping public opinion during which period in India?",
            "options": ["Ancient India", "Medieval India", "Colonial India", "Post-independence India"],
            "correct_index": 2,
            "explanation": "The introduction of the printing press by Europeans transformed communication and nationalist ideas during colonial rule.",
        },
        {
            "question_text": "Which of these is classified as a renewable resource?",
            "options": ["Coal", "Natural gas", "Forest", "Petroleum"],
            "correct_index": 2,
            "explanation": "Forests can regenerate over time with proper management, unlike fossil fuels which are finite.",
        },
        {
            "question_text": "The Tropic of Cancer passes through approximately how many Indian states?",
            "options": ["4", "8", "10", "2"],
            "correct_index": 1,
            "explanation": "The Tropic of Cancer crosses through 8 Indian states, including Gujarat, Rajasthan, and West Bengal.",
        },
        {
            "question_text": "Which river is often called the 'Sorrow of Bihar' due to its frequent devastating floods?",
            "options": ["Ganga", "Kosi", "Yamuna", "Brahmaputra"],
            "correct_index": 1,
            "explanation": "The Kosi river frequently changes course and causes severe flooding in Bihar.",
        },
        {
            "question_text": "Which crop requires high temperature, high humidity, and annual rainfall above 200 cm?",
            "options": ["Wheat", "Rice", "Millets", "Barley"],
            "correct_index": 1,
            "explanation": "Rice is a kharif crop that thrives in hot, humid conditions with heavy rainfall.",
        },
        {
            "question_text": "The main reason for locating steel plants like Bhilai and Bokaro in those regions was the nearby availability of:",
            "options": ["Iron ore and coal", "Cheap labour only", "Coastal access only", "Foreign investment only"],
            "correct_index": 0,
            "explanation": "Steel plants are located near raw material sources like iron ore and coal to reduce transport costs.",
        },
        {
            "question_text": "Which mode of transport is often described as the 'lifeline' of the Indian economy?",
            "options": ["Roadways", "Railways", "Airways", "Waterways"],
            "correct_index": 1,
            "explanation": "Railways carry the bulk of India's freight and passenger traffic across long distances, earning this description.",
        },
        {
            "question_text": "Power sharing among different social/community groups, as seen in Belgium's community government, is an example of:",
            "options": ["Vertical power sharing", "Horizontal power sharing", "Community government power sharing", "No power sharing"],
            "correct_index": 2,
            "explanation": "This form, distinct from sharing between levels of government, distributes power among social/cultural communities.",
        },
        {
            "question_text": "India is a federal country, meaning political power is divided between the:",
            "options": ["President and Prime Minister", "Union government and state governments", "Supreme Court and Parliament", "Army and Police"],
            "correct_index": 1,
            "explanation": "Federalism in India divides power between the central (Union) government and the state governments.",
        },
        {
            "question_text": "The political party that wins a majority of seats in the Lok Sabha forms the:",
            "options": ["Opposition", "Judiciary", "Ruling (central) government", "Election Commission"],
            "correct_index": 2,
            "explanation": "The party or coalition with a majority in the Lok Sabha forms the government at the centre.",
        },
        {
            "question_text": "Which of these is NOT considered a guaranteed outcome of democracy?",
            "options": ["Accountable government", "Guaranteed economic growth every year", "Dignity of citizens", "Legitimate government"],
            "correct_index": 1,
            "explanation": "Democracy does not guarantee year-on-year economic growth, though it promotes accountable and legitimate governance.",
        },
        {
            "question_text": (
                "Development that meets present needs without compromising the ability of future "
                "generations to meet their own needs is called:"
            ),
            "options": ["Economic growth", "Sustainable development", "Human development", "Green revolution"],
            "correct_index": 1,
            "explanation": "This is the standard definition of sustainable development.",
        },
        {
            "question_text": "Which sector of the Indian economy includes activities like agriculture, forestry, and fishing?",
            "options": ["Primary sector", "Secondary sector", "Tertiary sector", "Quaternary sector"],
            "correct_index": 0,
            "explanation": "The primary sector covers activities that directly use natural resources, such as farming and fishing.",
        },
        {
            "question_text": "Formal sources of credit in India include banks and:",
            "options": ["Moneylenders", "Cooperative societies", "Traders", "Relatives"],
            "correct_index": 1,
            "explanation": "Cooperative societies, along with banks, are regulated formal sources of credit, unlike moneylenders or relatives.",
        },
        {
            "question_text": "The process of rapid integration of countries through foreign trade and investment is known as:",
            "options": ["Liberalisation", "Privatisation", "Globalisation", "Nationalisation"],
            "correct_index": 2,
            "explanation": "Globalisation refers to the increasing interconnection of economies through trade and investment.",
        },
        {
            "question_text": "Which act empowers Indian consumers to file complaints against defective goods or deficient services?",
            "options": ["Right to Information Act", "Consumer Protection Act", "Right to Education Act", "Companies Act"],
            "correct_index": 1,
            "explanation": "The Consumer Protection Act provides the legal framework for consumers to seek redressal.",
        },
    ],
}
