SCRIPT_BODY_PROMPTS = {
    "en": """
Write a SPOKEN YouTube Shorts script BODY (NO CTA).

CRITICAL GOAL:
Maximize viewer retention. The first 1–2 lines must immediately stop scrolling.

STRICT RULES:
- Strictly between 110–120 words
- Natural spoken English (like explaining to a friend)
- No meta language (no “this video”, “you will learn”, etc.)
- No CTA
- No emojis, lists, headings, or formatting
- Short, punchy sentences
- Easy to understand when heard once

STRUCTURE (MANDATORY):
1) Start with a strong curiosity hook or shocking thought
   - A counterintuitive fact
   - A direct second-person statement
   - A surprising question
2) Quickly explain WHY this matters to the viewer personally
3) Reveal the insight step-by-step, not all at once
4) End with a satisfying realization or thought-provoking line (NO CTA)

HOOK EXAMPLES (DO NOT COPY, JUST FOLLOW STYLE):
- “Your brain is lying to you more often than you think.”
- “This feeling isn’t tiredness. It’s something else.”
- “Most people misunderstand what their brain is actually doing here.”

TOPIC:
{idea}

Return ONLY the spoken script body.
""",

    "hi": """
YouTube Shorts के लिए बोला जाने वाला स्क्रिप्ट लिखिए (CTA नहीं).

मुख्य उद्देश्य:
दर्शक को पहले 2 सेकंड में रोकना और अंत तक वीडियो देखने के लिए मजबूर करना।

सख़्त नियम:
- 90–110 शब्द
- सरल, बोलचाल की हिंदी (जैसे किसी दोस्त को समझा रहे हों)
- कोई अंग्रेज़ी शब्द नहीं
- कोई मेटा भाषा नहीं (जैसे “इस वीडियो में”)
- कोई CTA नहीं
- छोटे और साफ़ वाक्य
- पहली बार सुनने में ही समझ आ जाना चाहिए

संरचना (अनिवार्य):
1) शुरुआत एक चौंकाने वाली या जिज्ञासा पैदा करने वाली पंक्ति से करें
   - कोई उलटी लगने वाली बात
   - सीधे दर्शक से बात
   - ऐसा सवाल जो सोचने पर मजबूर करे
2) तुरंत बताएँ कि यह बात दर्शक के लिए क्यों ज़रूरी है
3) जानकारी धीरे-धीरे खोलें, एक साथ सब कुछ न बताएं
4) अंत में एक गहरी या सोचने वाली बात पर खत्म करें (CTA नहीं)

उदाहरण (कॉपी न करें, केवल शैली समझें):
- “आपका दिमाग आपको जितना लगता है, उससे ज़्यादा बार धोखा देता है।”
- “यह थकान नहीं है, कुछ और हो रहा है।”
- “ज़्यादातर लोग यहाँ अपने दिमाग को गलत समझते हैं।”

विषय:
{idea}

केवल बोला जाने वाला स्क्रिप्ट लौटाएँ।
""",

    "hi-en": """
YouTube Shorts के लिए बोला जाने वाला Hinglish script लिखिए (CTA नहीं).

CRITICAL GOAL:
पहले 2 सेकंड में viewer का ध्यान खींचना और video को end तक देखने के लिए मजबूर करना।

STRICT RULES:
- Strictly between 90–110 शब्द
- Natural Hinglish (Hindi + common English words)
- ज़्यादा heavy English या बहुत शुद्ध हिंदी नहीं
- कोई meta language नहीं (जैसे “इस वीडियो में”)
- कोई CTA नहीं
- Short, punchy sentences
- बोलते समय natural और smooth लगना चाहिए

STRUCTURE (MANDATORY):
1) शुरुआत strong hook से करें
   - कोई shocking thought
   - सीधे viewer से बात
   - ऐसा सवाल जो curiosity पैदा करे
2) तुरंत बताएँ कि यह बात viewer की life से कैसे जुड़ी है
3) Information धीरे-धीरे reveal करें, एक साथ नहीं
4) End एक satisfying या सोचने वाली line पर करें (CTA नहीं)

HOOK STYLE EXAMPLES (कॉपी न करें, केवल style समझें):
- “Your brain is playing a game with you, and you don’t even realize it.”
- “यह थकान नहीं है, your brain कुछ और signal भेज रहा है.”
- “Most people think they understand this, but they don’t.”

TOPIC:
{idea}

केवल बोला जाने वाला script लौटाएँ।
"""
}
