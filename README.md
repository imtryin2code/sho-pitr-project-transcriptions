# Joe Peter Project: 1941 Chinook Jargon Transcriptions

> ### 🌐 [Explore the Interactive Archive & Dictionary](https://imtryin2code.github.io/sho-pitr-project-transcriptions/)
> **The Project Web Page** provides a searchable dictionary, live frequency counts of Joe Peter's vocabulary, and formatted reading guides. It is the primary interface for this archive.

- **Current Progress:** 9/30 recordings transcribed.
- **Project History:** 3 years of active transcription completed.
- **Estimated Completion:** 2032 (Approx. 6 years remaining).

---

## 📜 Project Overview
This repository preserves and digitizes a unique linguistic encounter from **1941**. The recordings feature **Jack Marr** reciting English sentences from Franz Boas’s [*Chinookan Texts*](https://archive.org/details/chinooktexts00boas) (1894), followed by **Joe Peter**, an Indigenous elder, providing the equivalent in **Chinook Jargon**.

Our goal is to transform these historical metal disc recordings into accessible, searchable, and educational formats for language revitalization.

---

## 📂 Repository Structure
The project is organized to provide both raw technical data and user-friendly exports:

* **`[Disc-ID]/`**: (e.g., `682-S1`) Contains the original ELAN (`.eaf`) linguistic transcription files.
* **`exports/`**: The central hub for accessing the transcriptions in various formats:
    * **[Markdown](./exports/markdown)**: Best for quick reading directly on GitHub.
    * **[PDFs](./exports/pdfs)**: Print-ready versions for offline study.
    * **[Word Docs](./exports/word-docs)**: Editable versions for educators and lesson planning.
* **`audio-previews/`**: Low-bitrate MP3s for reference (Full WAVs stored externally).
* **`metadata/`**: Contains the [Master Transcription List](./metadata/master_transcription_list.csv)—a searchable index of every line spoken.
* **`scripts/`**: Python tools used to automate the data pipeline.

---

## 🛠 How to Use This Archive

### For Language Learners & Educators
If you want to read or print the stories, navigate to the **[`exports/`](./exports)** folder. 
* Use the **PDFs** for high-quality printing.
* Use the **Word Docs** if you want to create your own learning materials or vocabulary lists.

### For Linguists
The raw transcription data is available in the **`.eaf`** format within the disc-specific folders. These can be opened using [ELAN](https://archive.mpi.nl/tla/elan) for deep phonetic or structural analysis.

---

## ⌨️ Transcription Notation Legend
To maintain consistency across the archive, the following notations are used to indicate audio quality, speaker behavior, and transcription confidence within the **primary transcription lines**:

| Notation | Description |
| :--- | :--- |
| `<text>` | Low confidence due to poor audio quality or group disagreement |
| `<<text>>` | Very low confidence due to extremely poor audio quality |
| `tex(t)` | Part of the word was not heard or dropped from speech |
| `{text}` | English word used within Chinuk-Wawa speech |
| `{{text}}` | English word(s) spoken by Joe Peter in conversation with Jack Marr |
| `<...>` | Unknown word(s) or voiced sound(s) |
| `text/` | Pause in speech following the word |
| `<text A/text B>` | Ambiguous; group members hear either A or B in even numbers |
| `..` | Hesitation or stutter |

### 🔍 Research Notes Categories & Bracket Structural Rules
The parsing engine reads the `Notes_Text` fields directly, sorting entries dynamically into specialized tracking files using these exact bracketed identifiers and syntax wrappers:

| Tag Indicator | Associated Category / Structural Rule | Core Purpose |
| :--- | :--- | :--- |
| `[LING]` | 🗣️ Linguistic & Phonetic Observations | Tracks shifts in pronunciation, phonetic deviations, and grammar logs. |
| `[HIST]` | 📜 Cultural & Historical Context Logs | Captures background context, historical references, and community anecdotes. |
| `[INFO]` | 💡 General Informational Notes | General observations, track metadata markers, or structural explanations. |
| `[TEX]` | 🎓 Exemplary Teaching Examples | Highlights excellent data segments optimized for language learning materials. |
| `[VEX]` | 🎵 High-Quality Vocalization Examples | Isolates distinct vocal inflections, expressions, or exceptional audio clarity. |
| `[OTL]` | 🌐 Other Languages Utilized | Notes where English, Marr, or outside linguistic fragments overlap text segments. |
| `[NOTE]` | 📝 Workspace Footnotes & Comments | General internal commentary, alignment flags, or raw project reminders. |
| `[?]` / `[UNCERTAIN]` | ❓ Uncertain Segments Requiring Review | Flags questionable translations or unclear phonetics requiring peer review. |
| `\|text\|` | Phonetic Deviation Indicator | Applied inside notes to isolate specific speech variants from standard dictionary records. |
| `[[text]]` | Standard GR Spelling Variant | Applied inside notes to link non-standard pronunciations back to standard Grand Ronde spellings. |

---

## 🔬 Research & Observations
- **Active Insights:** 424 specific linguistic observations.
- **Dialect Variations:** 137 identified pronunciation patterns.
- **Logs:** [Research Log](./exports/markdown/Research_Observations_Log.md) | [Variation Report](./exports/markdown/Dialect_Variation_Report.md)

---

## 🛠 Tools & Citation
All transcriptions in this archive are created and managed using [ELAN](https://archive.mpi.nl/tla/elan), developed by the Max Planck Institute for Psycholinguistics.

**To cite the software used in this project:**
> ELAN (Version 7.1) [Computer software]. (2026). Nijmegen: Max Planck Institute for Psycholinguistics. Retrieved from https://archive.mpi.nl/tla/elan

---

## 📈 Project Progress

**Current Completion:** 9/30 recordings processed.

 | Recording ID | Description | Status | Formats Available | 
 | :--- | :--- | :--- | :--- | 
 | [682-S1](https://github.com/imtryin2code/sho-pitr-project-transcriptions/blob/main/audio-previews/682-S1.mp3) | Boas Text Recitation | ✅ Completed | PDF, MD, DOCX | 
 | [682-S2](https://github.com/imtryin2code/sho-pitr-project-transcriptions/blob/main/audio-previews/682-S2.mp3) | Boas Text Recitation | ✅ Completed | PDF, MD, DOCX | 
 | [683-S1](https://github.com/imtryin2code/sho-pitr-project-transcriptions/blob/main/audio-previews/683-S1.mp3) | Boas Text Recitation | ✅ Completed | PDF, MD, DOCX | 
 | [683-S2](https://github.com/imtryin2code/sho-pitr-project-transcriptions/blob/main/audio-previews/683-S2.mp3) | Boas Text Recitation | ✅ Completed | PDF, MD, DOCX | 
 | [684-S1](https://github.com/imtryin2code/sho-pitr-project-transcriptions/blob/main/audio-previews/684-S1.mp3) | Boas Text Recitation | ✅ Completed | PDF, MD, DOCX | 
 | **684-S2** | Boas Text Recitation | 🟡 In Progress |  | 
 | [685-S1](https://github.com/imtryin2code/sho-pitr-project-transcriptions/blob/main/audio-previews/685-S1.mp3) | Boas Text Recitation | ✅ Completed | PDF, MD, DOCX | 
 | **685-S2** | Boas Text Recitation | 🟡 In Progress |  | 
 | **686-S1** | Boas Text Recitation | 🟡 In Progress |  | 
 | **686-S2** | Boas Text Recitation | 🟡 In Progress |  | 
 | **687-S1** | Boas Text Recitation | 🟡 In Progress |  | 
 | **687-S2** | Boas Text Recitation | 🟡 In Progress |  | 
 | **688-S1** | Boas Text Recitation | 🟡 In Progress |  | 
 | **688-S2** | Boas Text Recitation | 🟡 In Progress |  | 
 | **689-S1** | Boas Text Recitation | 🟡 In Progress |  | 
 | **689-S2** | Boas Text Recitation | 🟡 In Progress |  | 
 | **690-S1** | Boas Text Recitation | 🟡 In Progress |  | 
 | **690-S2** | Boas Text Recitation | 🟡 In Progress |  | 
 | **691-S1** | Boas Text Recitation | 🟡 In Progress |  | 
 | **691-S2** | Boas Text Recitation | 🟡 In Progress |  | 
 | **692-S1** | Boas Text Recitation | 🟡 In Progress |  | 
 | **692-S2** | Boas Text Recitation | 🟡 In Progress |  | 
 | **693-S1** | Boas Text Recitation | 🟡 In Progress |  | 
 | [693-S2](https://github.com/imtryin2code/sho-pitr-project-transcriptions/blob/main/audio-previews/693-S2.mp3) | Boas Text Recitation | ✅ Completed | PDF, MD, DOCX | 
 | [694-S1](https://github.com/imtryin2code/sho-pitr-project-transcriptions/blob/main/audio-previews/694-S1.mp3) | Boas Text Recitation | ✅ Completed | PDF, MD, DOCX | 
 | [694-S2](https://github.com/imtryin2code/sho-pitr-project-transcriptions/blob/main/audio-previews/694-S2.mp3) | Boas Text Recitation | ✅ Completed | PDF, MD, DOCX | 
 | **695-S1** | Boas Text Recitation | 🟡 In Progress |  | 
 | **695-S2** | Boas Text Recitation | 🟡 In Progress |  | 
 | **696-S1** | Boas Text Recitation | 🟡 In Progress |  | 
 | **696-S2** | Boas Text Recitation | 🟡 In Progress |  |

---

## 🤝 Contributing
This is a public archive. If you find a transcription error or have historical context to add:
1. **Fork** the repository.
2. Create a new **Branch**.
3. Submit a **Pull Request** for review.

*Special thanks to the community members and linguists dedicated to the preservation of Chinook Jargon.*
