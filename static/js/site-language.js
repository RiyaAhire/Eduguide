(() => {
  const phrases = {
    "Home": "होम",
    "Colleges": "कॉलेज",
    "Explore Colleges": "कॉलेज देखें",
    "Explore Courses": "कोर्सेज देखें",
    "Cutoff": "कटऑफ",
    "Prediction": "पूर्वानुमान",
    "Admission Process": "प्रवेश प्रक्रिया",
    "About": "परिचय",
    "My profile": "मेरी प्रोफ़ाइल",
    "Logout": "लॉग आउट",
    "Login": "लॉग इन",
    "Register": "रजिस्टर करें",
    "Toggle dark/light mode": "डार्क/लाइट मोड बदलें",
    "Admission data, made clear": "प्रवेश की जानकारी, अब आसान",
    "ADMISSION DATA, MADE CLEAR": "प्रवेश की जानकारी, अब आसान",
    "A clearer path to your": "आपके अगले कॉलेज तक",
    "next college.": "का आसान रास्ता।",
    "Explore real college, course and cutoff records, then use your saved profile to make a better informed admission decision.": "कॉलेज, पाठ्यक्रम और पिछले वर्षों के कटऑफ देखें। अपनी प्रोफ़ाइल के आधार पर प्रवेश का बेहतर निर्णय लें।",
    "Find my colleges": "मेरे कॉलेज खोजें",
    "Explore cutoffs": "कटऑफ देखें",
    "Profile-based predictions": "प्रोफ़ाइल आधारित अनुमान",
    "Historical cutoff records": "पिछले वर्षों के कटऑफ रिकॉर्ड",
    "Colleges": "कॉलेज",
    "Guidance": "मार्गदर्शन",
    "Plan with clarity": "सही जानकारी के साथ योजना बनाएँ",
    "Profile": "प्रोफ़ाइल",
    "Ready to match": "मिलान के लिए तैयार",
    "START EXPLORING": "खोज शुरू करें",
    "College guidance, without the clutter.": "कॉलेज की जानकारी, आसान तरीके से।",
    "Discover colleges and courses, then use your profile when you are ready to predict.": "कॉलेज और पाठ्यक्रम देखें। अनुमान पाने के लिए अपनी प्रोफ़ाइल का उपयोग करें।",
    "Explore colleges": "कॉलेज देखें",
    "Colleges to explore": "देखने के लिए कॉलेज",
    "Unique courses": "अलग-अलग पाठ्यक्रम",
    "Prediction accuracy": "अनुमान की सटीकता",
    "HOW EDUGUIDE HELPS": "EDUGUIDE कैसे मदद करता है",
    "From profile to possibilities": "प्रोफ़ाइल से नए अवसरों तक",
    "One focused flow, using data that is already in the platform.": "प्लेटफ़ॉर्म पर उपलब्ध डेटा से आसान और स्पष्ट प्रक्रिया।",
    "Save your profile": "अपनी प्रोफ़ाइल सेव करें",
    "Register once with your marks, category and preferences.": "अपने अंक, श्रेणी और पसंद के साथ एक बार रजिस्टर करें।",
    "Compare cutoffs": "कटऑफ की तुलना करें",
    "Browse past cutoff data by college, course, category and CAP round.": "पिछले कटऑफ डेटा को कॉलेज, पाठ्यक्रम, श्रेणी और CAP राउंड के अनुसार देखें।",
    "Use prediction": "अनुमान देखें",
    "Your saved profile is ready whenever you return to prediction.": "अनुमान देखने के लिए आपकी सेव की गई प्रोफ़ाइल हमेशा तैयार है।",
    "EXPLORE WITH CONFIDENCE": "आत्मविश्वास के साथ खोजें",
    "Everything in one admission workspace": "प्रवेश से जुड़ी हर जानकारी एक जगह",
    "College directory": "कॉलेज सूची",
    "Search the colleges currently listed in EduGuide and explore their course options.": "EduGuide में सूचीबद्ध कॉलेज खोजें और उनके पाठ्यक्रम देखें।",
    "Cutoff explorer": "कटऑफ खोजें",
    "Filter actual stored cutoff records by year, college, course, category and round.": "कटऑफ रिकॉर्ड को वर्ष, कॉलेज, पाठ्यक्रम, श्रेणी और राउंड से फ़िल्टर करें।",
    "Profile prediction": "प्रोफ़ाइल आधारित अनुमान",
    "Use a saved admission profile without entering the same details every visit.": "हर बार जानकारी भरे बिना अपनी सेव की गई प्रवेश प्रोफ़ाइल का उपयोग करें।",
    "READY WHEN YOU ARE": "जब आप तैयार हों",
    "Start your admission journey with better context.": "बेहतर जानकारी के साथ प्रवेश की तैयारी शुरू करें।",
    "Create your profile once and use it whenever you want to explore college predictions.": "एक बार अपनी प्रोफ़ाइल बनाएँ और कॉलेज अनुमान देखने के लिए उसका उपयोग करें।",
    "Open my prediction": "मेरा अनुमान खोलें",
    "Create my profile": "मेरी प्रोफ़ाइल बनाएँ",
    "Explore Colleges": "कॉलेज देखें",
    "Find the right college for your career and future.": "अपने करियर और भविष्य के लिए सही कॉलेज चुनें।",
    "Search college by name or location...": "कॉलेज का नाम या स्थान खोजें...",
    "College Code:": "कॉलेज कोड:",
    "View Details": "विवरण देखें",
    "No Colleges Found": "कोई कॉलेज नहीं मिला",
    "Discover diploma courses and find the path that matches your interests and career goals.": "डिप्लोमा पाठ्यक्रम देखें और अपनी रुचि व करियर लक्ष्य के अनुसार विकल्प चुनें।",
    "Search for a course...": "पाठ्यक्रम खोजें...",
    "All Categories": "सभी श्रेणियाँ",
    "Check College Cutoffs": "कॉलेज कटऑफ देखें",
    "Admission Year": "प्रवेश वर्ष",
    "College": "कॉलेज",
    "Select a college": "कॉलेज चुनें",
    "Course": "पाठ्यक्रम",
    "Select a course": "पाठ्यक्रम चुनें",
    "Category Code": "श्रेणी कोड",
    "All category codes": "सभी श्रेणी कोड",
    "CAP Round": "CAP राउंड",
    "All CAP rounds": "सभी CAP राउंड",
    "CUTOFF RESULTS": "कटऑफ परिणाम",
    "Your saved admission profile": "आपकी सेव की गई प्रवेश प्रोफ़ाइल",
    "These values are used for every prediction. They are loaded directly from your account.": "हर अनुमान के लिए इन विवरणों का उपयोग किया जाता है। ये आपके खाते से लिए गए हैं।",
    "Percentage": "प्रतिशत",
    "Category": "श्रेणी",
    "Preferred branch": "पसंदीदा शाखा",
    "Preferred location": "पसंदीदा स्थान",
    "College type": "कॉलेज का प्रकार",
    "Calculate my college matches": "मेरे कॉलेज विकल्प खोजें",
    "We compare your percentage with historical cutoffs for your category and preferred branch. Results are guidance, not an admission guarantee.": "हम आपके प्रतिशत की तुलना आपकी श्रेणी और पसंदीदा शाखा के पिछले कटऑफ से करते हैं। यह मार्गदर्शन है, प्रवेश की गारंटी नहीं।",
    "YOUR DATA-BASED RESULTS": "डेटा पर आधारित आपके परिणाम",
    "Predicted colleges for your profile": "आपकी प्रोफ़ाइल के लिए सुझाए गए कॉलेज",
    "YOUR PERSONALIZED ADMISSION REPORT": "आपकी व्यक्तिगत प्रवेश रिपोर्ट",
    "A clearer path to your next college.": "आपके अगले कॉलेज तक पहुँचने का आसान रास्ता।",
    "Your matches are based on your saved profile and historical cutoff records.": "आपके विकल्प आपकी सेव की गई प्रोफ़ाइल और पिछले कटऑफ रिकॉर्ड पर आधारित हैं।",
    "Profile score": "प्रोफ़ाइल स्कोर",
    "College matches": "मिले हुए कॉलेज",
    "Strongest match": "सबसे बेहतर विकल्प",
    "Applicant profile": "आवेदक की प्रोफ़ाइल",
    "Applicant": "आवेदक",
    "Report date": "रिपोर्ट की तारीख",
    "CHANCE DISTRIBUTION": "संभावना का विवरण",
    "Your match outlook": "आपके विकल्पों की स्थिति",
    "High chance": "अच्छी संभावना",
    "Good chance": "संभावना है",
    "Moderate chance": "मध्यम संभावना",
    "Stretch option": "कठिन विकल्प",
    "matches": "विकल्प",
    "Chance bands compare your percentage with eligible historical cutoffs. They are guidance, not guarantees.": "संभावना श्रेणियाँ आपके प्रतिशत की तुलना पिछले कटऑफ से करती हैं। ये मार्गदर्शन हैं, गारंटी नहीं।",
    "Download prediction report": "अनुमान रिपोर्ट डाउनलोड करें",
    "How this works:": "यह कैसे काम करता है:",
    "PROFILE REQUIRED": "प्रोफ़ाइल आवश्यक है",
    "Register before using predictions": "अनुमान देखने से पहले रजिस्टर करें",
    "Prediction uses your percentage, category, branch, location and college preference. Create an account once and EduGuide will save these details for future visits.": "अनुमान के लिए आपके प्रतिशत, श्रेणी, शाखा, स्थान और कॉलेज की पसंद का उपयोग होता है। एक बार खाता बनाएँ; EduGuide ये विवरण सेव रखेगा।",
    "Create my profile →": "मेरी प्रोफ़ाइल बनाएँ →",
    "How the prediction is calculated": "अनुमान कैसे तैयार होता है",
    "A transparent comparison of your saved details and the admission data in the database.": "आपके सेव किए गए विवरण और डेटाबेस के प्रवेश डेटा की स्पष्ट तुलना।",
    "Match your profile": "प्रोफ़ाइल का मिलान",
    "We filter records using your preferred branch, category, location and college type.": "हम आपकी पसंदीदा शाखा, श्रेणी, स्थान और कॉलेज के प्रकार के अनुसार रिकॉर्ड फ़िल्टर करते हैं।",
    "Your percentage is compared against the historical category cutoff for every matching course.": "हर मेल खाते पाठ्यक्रम के लिए आपके प्रतिशत की तुलना पिछली श्रेणी के कटऑफ से की जाती है।",
    "Rank the choices": "विकल्पों की क्रमबद्ध सूची",
    "Results are ordered by the score gap and shown as high, good, moderate or stretch chances.": "परिणाम स्कोर के अंतर के अनुसार क्रमबद्ध हैं और संभावना की श्रेणियों में दिखाए जाते हैं।",
    "About the College": "कॉलेज के बारे में",
    "About the Course": "पाठ्यक्रम के बारे में",
    "College Information": "कॉलेज की जानकारी",
    "Course Information": "पाठ्यक्रम की जानकारी",
    "Duration": "अवधि",
    "Level": "स्तर",
    "Field": "क्षेत्र",
    "Mode": "प्रकार",
    "Major Subjects": "मुख्य विषय",
    "Career Opportunities": "करियर के अवसर",
    "Skills You'll Develop": "आप जो कौशल सीखेंगे",
    "Higher Studies": "आगे की पढ़ाई",
    "Interested in this course?": "इस पाठ्यक्रम में रुचि है?",
    "Explore colleges offering this course.": "यह पाठ्यक्रम देने वाले कॉलेज देखें।",
    "Back to Explore Colleges": "कॉलेज सूची पर वापस जाएँ",
    "About the College": "कॉलेज के बारे में",
    "About this course": "इस पाठ्यक्रम के बारे में",
    "Save personal details": "व्यक्तिगत विवरण सेव करें",
    "Edit personal details": "व्यक्तिगत विवरण संपादित करें",
    "Full name": "पूरा नाम",
    "Username": "यूज़रनेम",
    "Email address": "ईमेल पता",
    "Prediction details": "अनुमान के विवरण",
    "SSC percentage": "SSC प्रतिशत",
    "SSC passing year": "SSC उत्तीर्ण वर्ष",
    "Preferred branch": "पसंदीदा शाखा",
    "Preferred location": "पसंदीदा स्थान",
    "College type": "कॉलेज का प्रकार",
    "Admission year": "प्रवेश वर्ष",
    "Save changes": "बदलाव सेव करें",
    "Password": "पासवर्ड",
    "Forgot password?": "पासवर्ड भूल गए?",
    "Don't have an account?": "खाता नहीं है?",
    "Already have an account?": "पहले से खाता है?",
    "Continue": "जारी रखें",
    "Next": "आगे",
    "Previous": "पीछे",
    "Search": "खोजें",
    "Filter": "फ़िल्टर करें",
    "Clear filters": "फ़िल्टर हटाएँ",
    "No results found": "कोई परिणाम नहीं मिला",
    "Loading...": "लोड हो रहा है...",
    "Home": "होम"
  };

  const translations = new Map(
    Object.entries(phrases).map(([english, hindi]) => [english.trim().replace(/\s+/g, " ").toLocaleLowerCase("en-US"), hindi]),
  );
  const textOriginals = new WeakMap();
  const attributeOriginals = new WeakMap();
  const fields = ["placeholder", "aria-label", "title", "alt"];
  const toggle = document.getElementById("languageToggle");
  const toggleText = document.getElementById("languageToggleText");
  if (!toggle || !toggleText) return;

  function normalized(text) {
    return text.trim().replace(/\s+/g, " ").toLocaleLowerCase("en-US");
  }

  function translateText(node, hindi) {
    if (!textOriginals.has(node)) textOriginals.set(node, node.nodeValue);
    const original = textOriginals.get(node);
    const translated = hindi ? translations.get(normalized(original)) : null;
    const leading = original.match(/^\s*/)?.[0] || "";
    const trailing = original.match(/\s*$/)?.[0] || "";
    const nextValue = translated ? `${leading}${translated}${trailing}` : original;
    if (node.nodeValue !== nextValue) node.nodeValue = nextValue;
  }

  function translateAttributes(element, hindi) {
    if (!attributeOriginals.has(element)) attributeOriginals.set(element, {});
    const originals = attributeOriginals.get(element);
    fields.forEach((field) => {
      if (!element.hasAttribute(field)) return;
      if (!(field in originals)) originals[field] = element.getAttribute(field);
      const original = originals[field];
      const translated = hindi ? translations.get(normalized(original)) : null;
      if (translated && element.getAttribute(field) !== translated) element.setAttribute(field, translated);
      else if (!hindi && element.getAttribute(field) !== original) element.setAttribute(field, original);
    });
    if (["button", "submit", "reset"].includes(element.type) && element.hasAttribute("value")) {
      if (!("value" in originals)) originals.value = element.value;
      const original = originals.value;
      const translated = hindi ? translations.get(normalized(original)) : null;
      if (translated) element.value = translated;
      else if (!hindi) element.value = original;
    }
  }

  function translateTree(root, hindi) {
    if (root.nodeType === Node.TEXT_NODE) {
      translateText(root, hindi);
      return;
    }
    if (root.nodeType !== Node.ELEMENT_NODE && root !== document) return;
    const start = root === document ? document.body : root;
    if (!start) return;
    if (start.nodeType === Node.ELEMENT_NODE) translateAttributes(start, hindi);
    const walker = document.createTreeWalker(start, NodeFilter.SHOW_TEXT, {
      acceptNode(node) {
        const parent = node.parentElement;
        return parent && !parent.closest("script, style, noscript") ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT;
      },
    });
    let node;
    while ((node = walker.nextNode())) translateText(node, hindi);
    start.querySelectorAll("*").forEach((element) => translateAttributes(element, hindi));
  }

  function setLanguage(hindi) {
    document.documentElement.lang = hindi ? "hi" : "en";
    translateTree(document, hindi);
    toggleText.textContent = hindi ? "English" : "हिन्दी";
    toggle.setAttribute("aria-label", hindi ? "Switch website language to English" : "Switch website language to Hindi");
    toggle.setAttribute("aria-pressed", String(hindi));
    try {
      localStorage.setItem("eduguide-language", hindi ? "hi" : "en");
    } catch (_) {
      // Language switching still works when browser storage is unavailable.
    }
  }

  let isHindi = false;
  try {
    isHindi = localStorage.getItem("eduguide-language") === "hi";
  } catch (_) {
    // Default to English when browser storage is unavailable.
  }
  setLanguage(isHindi);
  toggle.addEventListener("click", () => {
    isHindi = !isHindi;
    setLanguage(isHindi);
  });

  new MutationObserver((records) => {
    records.forEach((record) => {
      record.addedNodes.forEach((node) => translateTree(node, isHindi));
    });
  }).observe(document.body, { childList: true, subtree: true });
})();
