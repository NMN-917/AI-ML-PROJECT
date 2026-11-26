import os
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

def build_official_presentation(template_path, output_path, plots_dir):
    prs = pptx.Presentation(template_path)
    
    # Slide 1: Title
    s1 = prs.slides[0]
    if s1.shapes.title:
        s1.shapes.title.text = "RESUMATCH"
        s1.shapes.title.text_frame.paragraphs[0].font.name = "Arial"
        s1.shapes.title.text_frame.paragraphs[0].font.size = Pt(36)
        s1.shapes.title.text_frame.paragraphs[0].font.bold = True
    
    # Subtitle placeholder
    for shp in s1.shapes:
        if shp != s1.shapes.title and shp.has_text_frame and "Couse Name" in shp.text_frame.text:
            tf = shp.text_frame
            tf.clear()
            lines = [
                ("AI-Driven Semantic Resume–Job Matching System", True, 18, RGBColor(0, 51, 102)),
                ("", False, 8, RGBColor(0, 0, 0)),
                ("Course Name: Statistical Machine Learning", True, 13, RGBColor(50, 50, 50)),
                ("Course Code: CSET211", True, 13, RGBColor(50, 50, 50)),
                ("", False, 6, RGBColor(0, 0, 0)),
                ("Submitted by:", True, 13, RGBColor(0, 51, 102)),
                ("• Harshita Rajput (S25CSEU1658)", False, 12, RGBColor(20, 20, 20)),
                ("• Naman Jain (S25CSEU1684)", False, 12, RGBColor(20, 20, 20)),
                ("• Vedansh Aggarwal (S25CSEU1562)", False, 12, RGBColor(20, 20, 20)),
                ("", False, 6, RGBColor(0, 0, 0)),
                ("Supervised by: Mr. Biswajit Jana", True, 13, RGBColor(0, 51, 102)),
                ("School of Computer Science Engineering & Technology", False, 11, RGBColor(80, 80, 80)),
                ("Bennett University (Times of India Group)", True, 12, RGBColor(0, 51, 102))
            ]
            for text, bold, size, color in lines:
                p = tf.add_paragraph()
                p.text = text
                p.font.name = "Arial"
                p.font.size = Pt(size)
                p.font.bold = bold
                p.font.color.rgb = color

    def populate_slide(slide, title_text, bullets):
        if slide.shapes.title:
            slide.shapes.title.text = title_text
            slide.shapes.title.text_frame.paragraphs[0].font.name = "Arial"
            slide.shapes.title.text_frame.paragraphs[0].font.size = Pt(28)
            slide.shapes.title.text_frame.paragraphs[0].font.bold = True
            slide.shapes.title.text_frame.paragraphs[0].font.color.rgb = RGBColor(0, 51, 102)
        
        for shp in slide.shapes:
            if shp != slide.shapes.title and shp.has_text_frame and shp.name.startswith("Content"):
                tf = shp.text_frame
                tf.clear()
                tf.word_wrap = True
                for idx, (b_text, level, bold, size) in enumerate(bullets):
                    p = tf.add_paragraph() if idx > 0 else tf.paragraphs[0]
                    p.text = b_text
                    p.level = level
                    p.font.name = "Calibri"
                    p.font.size = Pt(size)
                    p.font.bold = bold
                    p.font.color.rgb = RGBColor(30, 30, 30) if not bold else RGBColor(0, 51, 102)

    # Slide 2: Abstract
    populate_slide(prs.slides[1], "Abstract", [
        ("Problem Definition:", 0, True, 15),
        ("Traditional Applicant Tracking Systems (ATS) rely on literal keyword matching. Candidates describing identical skills using synonyms (e.g., 'managed 5 interns' vs 'leadership experience') are unjustly filtered out.", 1, False, 13),
        ("Objectives & Methodology:", 0, True, 15),
        ("Develop an AI-driven resume screener using Sentence-BERT (all-MiniLM-L6-v2) to map resumes and job postings into 384D dense semantic embeddings, comparing contextual similarity against TF-IDF and Okapi BM25 baselines.", 1, False, 13),
        ("Key Findings & Results:", 0, True, 15),
        ("In controlled synonym tests, TF-IDF keyword scores collapsed by 22.4% to 48.5%, falsely rejecting qualified engineers. In contrast, dense sentence embeddings preserved stable recognition (variance < 4%), validating true contextual understanding.", 1, False, 13)
    ])

    # Slide 3: Introduction (1)
    populate_slide(prs.slides[2], "Introduction (1)", [
        ("Background:", 0, True, 16),
        ("Recruitment pipelines in tech receive hundreds of applicant resumes per job opening.", 1, False, 14),
        ("Automated screening software is universally employed for first-round candidate shortlisting.", 1, False, 14),
        ("Most commercial systems rely entirely on keyword frequencies and boolean search filters.", 1, False, 14),
        ("Problem Statement:", 0, True, 16),
        ("Literal word matching cannot comprehend semantic equivalence between technical terms.", 1, False, 14),
        ("Qualified candidates who phrase experience naturally are unfairly penalized and eliminated.", 1, False, 14),
        ("Keyword stuffing enables unqualified candidates to bypass filters without actual competency.", 1, False, 14)
    ])

    # Slide 4: Introduction (2)
    populate_slide(prs.slides[3], "Introduction (2)", [
        ("Project Objectives:", 0, True, 16),
        ("Design a dual-engine screening pipeline comparing Statistical ML (TF-IDF) vs Deep Learning.", 1, False, 14),
        ("Build a robust parser supporting real multi-page candidate dossiers (.docx tables, .pdf, .txt).", 1, False, 14),
        ("Implement automated qualification classification thresholds (Selected, Borderline, Rejected).", 1, False, 14),
        ("Provide interactive visualization and REST API endpoints for recruiter decision transparency.", 1, False, 14),
        ("Methodology Overview:", 0, True, 16),
        ("Preprocess and normalize heterogeneous resume dossiers into structured text blocks.", 1, False, 14),
        ("Generate dense semantic embeddings using all-MiniLM-L6-v2 and evaluate cosine similarity.", 1, False, 14),
        ("Benchmark against TF-IDF keyword overlap to diagnose vocabulary distortion.", 1, False, 14)
    ])

    # Slide 5: Literature Review (1)
    populate_slide(prs.slides[4], "Literature Review (1)", [
        ("Existing Solution Analysis & Theoretical Foundations:", 0, True, 15),
        ("Commercial ATS (Taleo, Workday, iCIMS):", 1, True, 13),
        ("Scan resumes for verbatim terms; lack latent semantic reasoning; vulnerable to keyword gaming.", 2, False, 12),
        ("TF-IDF (Term Frequency – Inverse Document Frequency):", 1, True, 13),
        ("Weighs word rarity across the corpus, but operates as an uncontextualized Bag-of-Words (BoW). Treats 'management' and 'leadership' as orthogonal, unrelated dimensions.", 2, False, 12),
        ("Okapi BM25 Ranking Algorithm:", 1, True, 13),
        ("Industrial standard in Elasticsearch; introduces non-linear term saturation and document length normalization, yet remains bounded by exact lexical tokens.", 2, False, 12),
        ("Identified Research Gap:", 1, True, 13),
        ("None of these baseline methods possess contextual sentence-level understanding. Dense embedding representations are required to bridge the vocabulary mismatch.", 2, False, 12)
    ])

    # Slide 6: Methodology (1)
    populate_slide(prs.slides[5], "Methodology (1)", [
        ("Data Collection & Description:", 0, True, 15),
        ("Authentic Applicant Dossiers:", 1, True, 14),
        ("Collected 12 authentic real-world candidate resumes in .docx and .txt formats across enterprise career tracks, ensuring realistic document complexity rather than synthetic test stubs.", 2, False, 13),
        ("Target Career Domains Represented:", 1, True, 14),
        ("• Senior Java / J2EE & Spring Full-Stack Developers (Priya, Sai K, Sai Srinivas, Varun, Manohar)", 2, False, 12),
        ("• IT Business Analysts & Agile Scrum Masters (Vikash, Teresa)", 2, False, 12),
        ("• Backend Python & Cloud Engineers (resume.txt, Technova SDE)", 2, False, 12),
        ("Controlled Evaluation Test Pairs:", 1, True, 14),
        ("Engineered controlled candidate pairs (Aditya Simple vs. Synonyms; Rohit Keywords vs. Synonyms) where technical competencies remain identical and only vocabulary phrasing is varied.", 2, False, 13)
    ])

    # Slide 7: Methodology (2)
    populate_slide(prs.slides[6], "Methodology (2)", [
        ("Data Preprocessing Pipeline:", 0, True, 16),
        ("Multi-Format Document Parsing (data_loader.py):", 1, True, 14),
        ("• Word Documents (.docx): Extracted paragraph XML nodes and traversed nested table structures, joining cells with pipe delimiters (|) to prevent skill grid omission.", 2, False, 13),
        ("• PDF Documents (.pdf): Streamed binary page trees using pypdf, aggregating text sequentially.", 2, False, 13),
        ("• Text Files (.txt): Ingested UTF-8 byte streams with graceful decoding fallbacks.", 2, False, 13),
        ("Text Cleaning & Normalization:", 1, True, 14),
        ("• Stripped trailing whitespaces and collapsed multi-newline blocks into clean spacing.", 2, False, 13),
        ("• Strictly preserved sentence punctuation and casing structure to maintain semantic syntax required by transformer attention heads.", 2, False, 13)
    ])

    # Slide 8: Methodology (3) - EDA & Tools (with chart!)
    s8 = prs.slides[7]
    populate_slide(s8, "Methodology (3)", [
        ("Exploratory Data Analysis (EDA):", 0, True, 14),
        ("• Length Disparity: Resumes range from 14 words up to 6,332 words (>60x variance), proving keyword counts are biased toward verbose profiles.", 1, False, 11),
        ("• Lexical Diversity: Short dossiers have high richness (~81%), while extensive profiles drop to ~13% due to repetitive bullet points.", 1, False, 11),
        ("• Domain Clustering: Skill term matrix confirms distinct clusters in Java/Spring, Big Data (Hadoop/Spark), and Agile governance.", 1, False, 11),
        ("Tools & Technologies:", 0, True, 14),
        ("• Python 3.13, PyTorch, Hugging Face sentence-transformers (all-MiniLM-L6-v2).", 1, False, 11),
        ("• scikit-learn (TfidfVectorizer, cosine_similarity), python-docx, pypdf.", 1, False, 11),
        ("• FastAPI & Uvicorn (REST API), Matplotlib & Seaborn (EDA Visualizations).", 1, False, 11)
    ])
    # Resize content placeholder to left half, and add chart on right half
    for shp in s8.shapes:
        if shp != s8.shapes.title and shp.has_text_frame and shp.name.startswith("Content"):
            shp.left = Inches(0.5)
            shp.top = Inches(1.6)
            shp.width = Inches(4.8)
            shp.height = Inches(4.7)
            break
    
    chart_path = os.path.join(plots_dir, "eda_word_counts.png")
    if os.path.exists(chart_path):
        s8.shapes.add_picture(chart_path, Inches(5.4), Inches(1.8), width=Inches(4.2))

    # Slide 9: Methodology (4) - Workflow Diagram
    s9 = prs.slides[8]
    if s9.shapes.title:
        s9.shapes.title.text = "Methodology (4)"
        s9.shapes.title.text_frame.paragraphs[0].font.name = "Arial"
        s9.shapes.title.text_frame.paragraphs[0].font.size = Pt(28)
        s9.shapes.title.text_frame.paragraphs[0].font.bold = True
        s9.shapes.title.text_frame.paragraphs[0].font.color.rgb = RGBColor(0, 51, 102)
    
    # Repurpose content placeholder to subtitle/caption
    for shp in s9.shapes:
        if shp != s9.shapes.title and shp.has_text_frame and shp.name.startswith("Content"):
            shp.text_frame.clear()
            p = shp.text_frame.paragraphs[0]
            p.text = "End-to-End RESUMATCH Architectural Pipeline & Workflow"
            p.font.name = "Arial"
            p.font.size = Pt(13)
            p.font.bold = True
            p.font.color.rgb = RGBColor(0, 51, 102)
            shp.left = Inches(0.5)
            shp.top = Inches(1.3)
            shp.width = Inches(9.0)
            shp.height = Inches(0.4)
            break
            
    wf_path = os.path.join(plots_dir, "system_workflow_diagram.png")
    if os.path.exists(wf_path):
        s9.shapes.add_picture(wf_path, Inches(0.6), Inches(1.8), width=Inches(8.8))

    # Slide 10: Implementation and technical progress
    populate_slide(prs.slides[9], "Implementation and technical progress", [
        ("AIML Model Selection & Justification:", 0, True, 15),
        ("Chosen Deep Learning Model: all-MiniLM-L6-v2 (Sentence-BERT)", 1, True, 13),
        ("• Architecture: 6 Transformer encoder layers, 12 attention heads, 22.7M parameters.", 2, False, 12),
        ("• Dense Latent Space: Generates 384-dimensional dense semantic vector representations.", 2, False, 12),
        ("Why all-MiniLM-L6-v2 was Selected:", 1, True, 13),
        ("• High Inference Speed: ~20ms CPU latency per dossier (5x faster than BERT-base / RoBERTa).", 2, False, 12),
        ("• High Accuracy Retention: Preserves >99% semantic accuracy of BERT-base on benchmark NLI/STS.", 2, False, 12),
        ("• Lightweight Deployment: Operates on edge CPU hardware without requiring dedicated GPU.", 2, False, 12),
        ("• Chunk Pooling Architecture: Handles multi-page resumes exceeding 256 tokens via mean-pooling.", 2, False, 12),
        ("Empirical Validation & Benchmark Findings:", 1, True, 13),
        ("• On synonym test pairs, TF-IDF drops by 22.4% to 48.5%, penalizing qualified candidates.", 2, False, 12),
        ("• Sentence Transformers showed consistent recognition (+3.8% delta), proving semantic invariance.", 2, False, 12)
    ])

    # Slide 11: Conclusion & Future Work
    populate_slide(prs.slides[10], "Conclusion & Future Work", [
        ("Summary of Milestone 2 Achievements:", 0, True, 15),
        ("• Implemented end-to-end dual-model evaluation system (TF-IDF vs. all-MiniLM-L6-v2).", 1, False, 13),
        ("• Ingested and conducted thorough EDA on 12 real-world candidate dossiers across 3 domains.", 1, False, 13),
        ("• Quantitatively proved keyword-matching vulnerability to the 'synonym penalty'.", 1, False, 13),
        ("• Deployed automated hiring decision classification (Selected >= 60%, Borderline, Rejected).", 1, False, 13),
        ("• Created working FastAPI server and responsive dashboard for real-time inference.", 1, False, 13),
        ("Future Work Plan (Milestone 3 & Final Delivery):", 0, True, 15),
        ("• Recruiter Feedback Loop: Fine-tune transformer layers via Triplet Loss from recruiter decisions.", 1, False, 13),
        ("• Section-Level Explainability: Implement cross-attention clause mapping to highlight specific matching skills.", 1, False, 13),
        ("• Optical Character Recognition (OCR): Integrate Tesseract OCR pipeline for scanned image PDFs.", 1, False, 13),
        ("• Docker Containerization: Package FastAPI backend and web UI for cloud deployment.", 1, False, 13)
    ])

    prs.save(output_path)
    print(f"Successfully generated official template presentation at: {output_path}")

build_official_presentation('PPT_Template_SML.pptx', 'RESUMATCH_Milestone_2_Official_Template.pptx', 'eda_plots')
