# Exploratory Data Analysis (EDA) Report: Real-World Resume Dataset
**Course:** AI & Machine Learning | Undergrad Engineering Research  
**Dataset Source:** `sample_data/` Real-World Applicant Dossiers (.docx, .txt)

---

## 1. Overview of the Ingested Dataset

The evaluation dataset consists of 12 candidate resumes spanning three primary industry roles:
1. **Senior Java / J2EE Full-Stack Developers**
2. **IT Business Analysts & Scrum Masters**
3. **Backend Python & Cloud Engineers**

---

## 2. Document Length & Lexical Diversity Statistics

| Candidate File | Format | Character Count | Word Count | Unique Words | Lexical Diversity ($\frac{\text{Unique}}{\text{Total}}$) | Primary Career Domain |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **`employer_mounika details.docx`** | DOCX | 801 | 96 | 78 | 0.8125 | Candidate Metadata / MIS |
| **`Manohar B.docx`** | DOCX | 16,503 | 2,286 | 716 | 0.3132 | Software Engineer / Java Backend |
| **`Priya B.docx`** | DOCX | 45,944 | 6,332 | 840 | 0.1327 | Senior Java Full Stack Dev (9 Pages) |
| **`resume.txt`** | TXT | 834 | 102 | 80 | 0.7843 | Backend Python Developer |
| **`sai k.docx`** | DOCX | 26,809 | 3,804 | 947 | 0.2489 | Sr. Java / J2EE Developer |
| **`Sai Srinivas_Sr_Java_Developer.docx`** | DOCX | 21,671 | 2,974 | 819 | 0.2754 | Sr. Java / J2EE Developer |
| **`TeresaNeetipudi IT BA.DOCX`** | DOCX | 13,230 | 1,716 | 658 | 0.3834 | IT Business Analyst |
| **`Varun.docx`** | DOCX | 23,959 | 3,430 | 989 | 0.2883 | Full Stack / Java Developer |
| **`Vijay Bhargav.docx`** | DOCX | 20,394 | 2,897 | 852 | 0.2941 | Sr. Big Data / Spark / Hadoop Developer |
| **`Vikash_BA_Ab.docx`** | DOCX | 21,024 | 2,800 | 979 | 0.3496 | Sr. Business Analyst / Scrum Master |
| **`Vishnu J.docx`** | DOCX | 17,400 | 2,406 | 712 | 0.2959 | Senior Java Developer |
| **`test_resume.docx`** | DOCX | 99 | 14 | 14 | 1.0000 | Micro-Summary Profile |

---

## 3. Extracted Technical Competencies Matrix

Term frequency distribution for key technical skills across applicants:

| Candidate | Java | Spring | Python | AWS | SQL | Docker | Agile/Scrum | Hadoop/Spark | Jira |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Priya B.** | **77** | **93** | 1 | 20 | 45 | 0 | 19 | 1 | 2 |
| **sai k.** | **45** | **45** | 0 | 0 | 15 | 0 | 11 | 0 | 3 |
| **Sai Srinivas** | **40** | **18** | 7 | 10 | 16 | 1 | 9 | 18 | 2 |
| **Varun** | **31** | **58** | 3 | 11 | 11 | 4 | 6 | 0 | 2 |
| **Manohar B.** | **30** | **23** | 0 | 8 | 16 | 0 | 5 | 0 | 3 |
| **Vijay Bhargav** | **27** | **21** | 16 | 12 | 19 | 2 | 1 | **50** | 2 |
| **Vishnu J.** | **22** | **22** | 0 | 0 | 25 | 0 | 5 | 0 | **10** |
| **Vikash (BA)** | 1 | 0 | 0 | 0 | 15 | 0 | **14** | 0 | 2 |
| **Teresa (BA)** | 1 | 0 | 0 | 0 | 3 | 0 | **7** | 0 | 4 |
| **resume.txt (Py)** | 0 | 0 | **2** | 1 | 1 | 0 | 0 | 0 | 0 |

---

## 4. Key EDA Insights for Presentation & Viva

1. **Extreme Length Disparity:**
   - Real resumes vary by over **60x in length** (from 102 words in concise summaries up to 6,332 words in 9-page enterprise resumes).
   - This proves why traditional search engines like **BM25 fail**: they reward length and keyword accumulation, falsely ranking long Java resumes as top matches for Python roles.

2. **Inverse Lexical Diversity Correlation:**
   - Short resumes exhibit high lexical richness (~80% unique vocabulary), whereas long resumes exhibit low lexical richness (~13% unique vocabulary) due to repeated project descriptions and bullet points.

3. **Natural Talent Clustering:**
   - The dataset clearly segments into 3 distinct talent clusters:
     - **Java/Spring Ecosystem** (Priya, Sai K, Sai Srinivas, Varun, Manohar, Vishnu)
     - **Business Analysis & Agile Governance** (Vikash, Teresa)
     - **Big Data & Analytics** (Vijay Bhargav)

---

## 5. Visual Artifacts
High-resolution plots generated in `eda_plots/`:
- `eda_plots/eda_word_counts.png`: Resume document length horizontal bar chart.
- `eda_plots/eda_skill_heatmap.png`: Technical competency heatmap across applicants.
