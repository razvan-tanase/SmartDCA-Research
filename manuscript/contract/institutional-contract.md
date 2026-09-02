# Institutional manuscript contract

Contract ID: `smartdca-thesis-institutional-contract-v1`  
Frozen: 2026-09-02
State: approved and frozen with explicit release blockers
Machine requirements digest: `48d20f5cbe08e04a6e8e8f0c72013a454a596cd692e0bdd6b6142b9f43feedc8`

This contract is the authority for institutional manuscript decisions until a
dated replacement is reviewed. It freezes what the available official sources
actually establish and assigns every missing value. A blank cell is never
permission to infer a requirement from another POLITEHNICA faculty, an older
session, or an undocumented conversation.

The machine-readable mirror is
[`requirements.json`](requirements.json). If this narrative and the JSON ever
disagree, the release is blocked until both are reconciled.

## Confirmed identity and scope

| Field | Frozen value | Authority |
|---|---|---|
| Institution | Universitatea Națională de Știință și Tehnologie POLITEHNICA București / National University of Science and Technology POLITEHNICA Bucharest | University finalization regulation and official English Erasmus policy |
| Faculty | Facultatea de Automatică și Calculatoare / Faculty of Automatic Control and Computers | University regulations index and ACS English program page |
| Department shown by the official template | Departamentul de Calculatoare / Computer Science and Engineering Department | Candidate-supplied official faculty template |
| Program | Financial Computing | ACS master studies page |
| Program teaching language | English | ACS master studies page |
| Working title | *Safe Adaptivity in Dollar-Cost Averaging: From an Impossibility Boundary to a Reproducible Empirical Evaluation* | User-approved [effort specification](../../.scratch/smartdca/efforts/thesis-manuscript-assembly/spec.md); still provisional |

The program's teaching language does not by itself prove that the submitted
dissertation must or may be in English. Manuscript-language approval remains a
supervisor/faculty decision.

## Verified university requirements

The Senate-approved 2025-2026 regulation establishes the following bounded
requirements:

- The dissertation is handed in online; registration includes proof of that
  online hand-in (Article 12(1)(b), PDF page index 5).
- Registration includes the originality declaration and similarity report
  (Article 12(1)(d), (i), PDF pages 5-6).
- The dissertation examination is one public presentation and defense
  (Article 17(4), PDF page index 10).
- Evaluation considers the imposed structure, alignment with the signed topic,
  written quality, scientific level, originality, contribution, bibliography,
  reference use, conclusions, engineering correctness, program relevance, and
  presentation (Article 17(7), PDF page index 11).
- A scientific supervisor designated by the program/faculty guides the work.
  The dissertation must answer the topic signed by the department director and
  supervisor, and the supervisor decides whether it is admitted to defense
  (Article 18(1)-(4), PDF pages 11-12).
- The faculty runs an approved similarity check before defense. The faculty
  council sets the program's maximum accepted similarity percentage; the
  supervisor interprets the report, which enters the examination file
  (Article 18(9)-(11), PDF page index 12).
- Annex 2 is an official originality form. It must be completed by hand,
  signed, approved by the scientific supervisor, deposited at registration,
  and included as an integral part of the dissertation (Annex 2, PDF pages
  20-21).
- The registration form records the exact dissertation title in uppercase and
  the scientific supervisor's academic title and name (Annex 1b, PDF page
  index 19).

These requirements come from the retained
[official regulation](../../references/institutional/politehnica-finalization-regulation-2025-2026.pdf).
They do not establish page extent, citation style, typography, or upload
filename.

## Verified faculty template requirements

The candidate supplied the official Faculty of Automatic Control and Computers
thesis template on 2026-09-02. The retained
[2018 template](../../references/institutional/acs-official-thesis-template-2018.pdf)
has SHA-256
`d2d35bc047816a8ad4672f088dac72ed2bcd86837f1c70ce11da143db7e487d5`.
It identifies itself internally as a Romanian/English *Diploma Project*
template and its PDF metadata identifies LaTeX as the creator. The candidate's
explicit identification of this artifact as the official thesis template makes
it the formatting and front-matter authority for this project. Newer official
sources still take precedence for the current university identity and the
master's-dissertation context.

| Area | Frozen template requirement |
|---|---|
| Covers | Romanian cover followed by English cover; each carries institution, faculty, department, two brand marks, document type, title, optional subtitle, candidate, supervisor/advisor with academic title, Bucharest, and year. |
| Front matter | Contents, then a Romanian `SINOPSIS` and English `ABSTRACT` of at most 200 words each sharing one page; acknowledgements are optional. The newer Annex 2 declaration is additionally mandatory, but its exact placement remains unresolved. |
| Page and body | Recommended A4; 2.54 cm on all sides; 12 pt justified body; 1.5 line spacing; 8 pt after paragraphs. |
| Headings | Heading 1 is 14 pt, bold, all caps; Heading 2 is 14 pt bold; Heading 3 is 12 pt. |
| Research route | Introduction (context, problem, objectives, proposed solution, obtained results, route), motivation/requirements, worldwide state of the art with precise positioning, proposed solution, difficult implementation details, quantitative evaluation, conclusions, bibliography, and optional annexes. |
| Figures | Centered, numbered, referred to in prose, and attributed when not candidate-created; move figures larger than half a page to annexes. |
| Formulas | Centered and numbered, with recommended 12 pt formula text. |
| Tables | Numbered, referred to in prose, and set in 9 pt text. |
| Citations | Use one consistent APA, IEEE, Harvard, or numbered style; record web access dates, connect citations directly to supported prose, cite reused figures, support non-obvious claims, cite every bibliography entry, and do not copy or translate source text. LaTeX citation commands and a separate BibTeX file are explicitly supported. |
| Annexes | Optional; suitable for large figures/tables, long code/configuration, screenshots, command output, and material that would interrupt the main route. |

The template gives recommendations rather than a total page/word extent. It
does not settle body language, a single citation style, current logo files,
print/binding rules, a font family, detailed pagination, upload packaging, or
archive rules.

## Unresolved decision register

Every row below blocks a submission candidate. “Evidence needed” is the exact
condition for changing the status; an implementer may not close a row from
memory or convention.

| Decision | Owner | Evidence needed |
|---|---|---|
| Permitted and approved manuscript language | Supervisor, with candidate/secretariat | Written confirmation that the dissertation may be submitted in English |
| Final title and capitalization | Supervisor | Signed topic/title record |
| Target defense/submission session | Candidate | Candidate choice plus the current faculty session announcement |
| Exact upload deadline | Candidate | Current faculty announcement or written secretariat confirmation |
| Expected page/word extent and exclusions | Supervisor | Current ACS/Financial Computing guidance or written decision |
| Named citation/bibliography style | Supervisor | Current faculty/supervisor style decision |
| Duplex rules, binding, and binding offset | Candidate | Written faculty or supervisor guidance |
| Font family, detailed caption style, and pagination | Candidate | Written faculty or supervisor guidance |
| Accepted upload format, size, filename, and packaging | Candidate | Current faculty upload instructions |
| Cover/PDF/repository metadata | Candidate | Current template/upload instructions and official identities |
| Current cover logos and placement | Candidate | Current faculty/university brand assets or confirmation that the 2018 marks remain current |
| Annex 2 placement within the template sequence | Supervisor | Written guidance reconciling the current declaration with the 2018 front matter |
| Financial Computing similarity threshold and exclusions | Candidate | Current faculty-council value |
| Archival deposit, retention, embargo, license, and repository rules | Candidate | Current faculty/library/repository instructions |
| Supervisor-specific structure, review, and delivery rules | Supervisor | Dated written supervisor decision |
| Candidate's exact official name | Candidate | Confirmation of the form required by Annex 1b/official records |
| Supervisor's exact academic title and name | Supervisor | Signed topic record or written confirmation |

The public official pages were inspected on 2026-09-01; the candidate supplied
the missing official manuscript-layout template on 2026-09-02. Annex 2 remains
a separate current declaration form rather than a layout template.

## Authoring and build contract

After full inspection of that template, the repository adopts LaTeX as the single
authoritative manuscript source, BibTeX as the bibliography input, generated
TeX fragments as the asset seam, and PDF as a derived rendered output. The
template itself was generated with LaTeX and explicitly supports LaTeX with a
separate BibTeX file, so this selection preserves its native source/build model.
The reasoning and reversal condition are recorded in
[ADR 0011](../../docs/adr/0011-use-latex-for-the-thesis-source.md).

The shell implements the template's bilingual cover/front-matter route, A4
page size, 25.4 mm margins, body spacing, and heading hierarchy. It is a
template-conformant draft rather than a release candidate because the values in
the unresolved register and visible placeholders are still incomplete. A newer
incompatible official template would require ADR 0011 to be revisited before
continuous drafting.

Run the draft build with:

```bash
python manuscript/build.py
```

Run the clean container build with:

```bash
./manuscript/build-clean.sh
```

Run the submission gate with:

```bash
python manuscript/check_release.py
```

The draft build must succeed while the submission gate must fail until every
blocking row is resolved and every visible placeholder, citation, and required
build input is complete.

## Provenance

| ID | Source | Authority and scope | Accessed |
|---|---|---|---|
| `upb-finalization-regulation-2025-2026` | [Official PDF](https://upb.ro/wp-content/uploads/2026/03/Regulament_finalizare_studii_2025-2026.pdf); retained [local copy](../../references/institutional/politehnica-finalization-regulation-2025-2026.pdf), SHA-256 `dafe9bb886f69b4b83dfad4649747c6d5f93f1376d9aed8d016fd83c15c85261` | Senate-approved university rules for the 2025-2026 finalization sessions; approved 2026-03-26 | 2026-09-01 |
| `upb-regulations-index` | [University regulations index](https://upb.ro/regulamente-si-rapoarte/) | Official index identifying the applicable regulation and faculty | 2026-09-01 |
| `upb-english-identity` | [Erasmus Policy Statement](https://upb.ro/en/erasmus/erasmus-policy-statement/) | Official English rendering of the institution name | 2026-09-01 |
| `acs-master-studies` | [ACS master studies](https://acs.pub.ro/en/admission/master-studies/) | Official faculty listing for program name and teaching language | 2026-09-01 |
| `acs-official-thesis-template-2018` | [Retained official template](../../references/institutional/acs-official-thesis-template-2018.pdf), original filename `Proiect_de_diplomă.pdf`, SHA-256 `d2d35bc047816a8ad4672f088dac72ed2bcd86837f1c70ce11da143db7e487d5` | Supplied directly and identified as official by the candidate; authority for cover structure, front matter, formatting recommendations, research route, figures, formulas, tables, bibliography, and annexes | 2026-09-02 |
| `thesis-effort-spec` | [Approved effort specification](../../.scratch/smartdca/efforts/thesis-manuscript-assembly/spec.md) | Repository authority for the working title and evidence-first manuscript process; not an institutional source | 2026-09-01 |

## Change control

- A new university/faculty rule, official template, or session announcement is
  added with its access date and retained bytes or stable URL before changing a
  verified row.
- Candidate and supervisor decisions need dated evidence and an explicit owner.
- Rendered PDFs never become the editing authority; they are release outputs.
- Continuous chapter drafting remains out of scope for this contract ticket.
