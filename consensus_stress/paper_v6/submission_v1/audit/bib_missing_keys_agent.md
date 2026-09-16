# Bibliography missing-key audit

**Scope.** This independent audit addresses only the four citation keys used by
`consensus_stress/paper_v6/submission_v1/latex/main.tex` but absent from
`submission_v1/references.bib` at the start of this task:

- `angelopoulos-bates-2021-conformal`
- `glockner-etal-2018-breaking`
- `irving-etal-2018-ai-safety-debate`
- `kaushik-etal-2019-counterfactually-augmented`

**Audit date.** 2026-09-16 (Asia/Shanghai).

**Files written.**

1. `consensus_stress/paper_v6/submission_v1/references.bib` — appended exactly
   the four verified entries below.
2. `consensus_stress/paper_v6/submission_v1/audit/bib_missing_keys_agent.md` —
   this audit report.

No `manuscript.md`, `latex/main.tex`, section file, experiment file, frozen
artifact, or relay output was modified.

## Verification method

Relay candidates were not treated as evidence. Metadata was checked against
first-party records:

- arXiv abstract pages and the official arXiv API at
  `https://export.arxiv.org/api/query?id_list=<id>` for the three arXiv records;
- the official ACL Anthology landing page and machine-readable BibTeX export for
  the Glockner et al. paper.

All checked endpoints returned HTTP 200 on 2026-09-16. For the three arXiv
records, the `year` in the BibTeX entry is the first public arXiv submission
year reported by the API, which matches the requested citation-key year. This
keeps the requested 2021/2018/2019 identity rather than silently substituting a
later revision year. The Kaushik arXiv record additionally reports
“Published at ICLR 2020”; the entry below intentionally retains the 2019 arXiv
preprint identity because the requested key is explicitly the 2019 key.

## Source-by-source reconciliation

| Key | Official source | Verified authors | Verified title | Year and venue used in BibTeX | URL field |
|---|---|---|---|---|---|
| `angelopoulos-bates-2021-conformal` | arXiv:2107.07511 abstract/API | Anastasios N. Angelopoulos; Stephen Bates | *A Gentle Introduction to Conformal Prediction and Distribution-Free Uncertainty Quantification* | 2021; arXiv preprint `arXiv:2107.07511` | `https://arxiv.org/abs/2107.07511` |
| `glockner-etal-2018-breaking` | ACL Anthology P18-2103 page and `.bib` export | Max Glockner; Vered Shwartz; Yoav Goldberg | *Breaking NLI Systems with Sentences that Require Simple Lexical Inferences* | 2018; *Proceedings of the 56th Annual Meeting of the Association for Computational Linguistics (Volume 2: Short Papers)* | `https://aclanthology.org/P18-2103/` |
| `irving-etal-2018-ai-safety-debate` | arXiv:1805.00899 abstract/API | Geoffrey Irving; Paul Christiano; Dario Amodei | *AI safety via debate* | 2018; arXiv preprint `arXiv:1805.00899` | `https://arxiv.org/abs/1805.00899` |
| `kaushik-etal-2019-counterfactually-augmented` | arXiv:1909.12434 abstract/API | Divyansh Kaushik; Eduard Hovy; Zachary C. Lipton | *Learning the Difference that Makes a Difference with Counterfactually-Augmented Data* | 2019; arXiv preprint `arXiv:1909.12434` (the record notes later publication at ICLR 2020) | `https://arxiv.org/abs/1909.12434` |

### Exact ACL record used for Glockner et al.

The ACL Anthology BibTeX export supplied the author list, title, venue,
year, address, publisher, pages, URL, and DOI for `P18-2103`; these fields were
copied into the new entry rather than reconstructed from the relay output.

### Version-year note for arXiv records

The official arXiv API exposes both the first publication date and later record
updates. The requested keys encode the initial arXiv years. Therefore:

- Angelopoulos--Bates uses 2021, the API's first publication year for
  arXiv:2107.07511, even though the record has later revisions.
- Irving--Christiano--Amodei uses 2018, the API's publication year for
  arXiv:1805.00899.
- Kaushik--Hovy--Lipton uses 2019, the API's first publication year for
  arXiv:1909.12434; its API comment records the later ICLR 2020 publication.

## Post-write checks

The four requested keys now occur exactly once each in `references.bib`. A
static comparison of citation commands in `latex/main.tex` against BibTeX keys
should therefore no longer report these four keys as missing. This audit does
not claim that a TeX compiler or PDF build was run.
