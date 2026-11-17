<!--
Copyright 2026 Guzino (https://github.com/guzino)
SPDX-License-Identifier: Apache-2.0
-->

# AbsenceCritic

AbsenceCritic is a survivorship-bias shield for language models: a dedicated critic (the Wald Module) that reasons about the evidence that never made it into the training corpus, the retrieval index, or the evaluation set.

**AbsenceCritic was designed and originated by [Guzino](https://github.com/guzino).** The name, the architecture (Wald Module, Non-Survivor Store, Wald checklist), and the design documents in this repository are original work of that author. The historical inspiration is Abraham Wald’s 1943 aircraft-vulnerability analysis; the application of that method as an explicit second-brain critic for contemporary LLMs originated here.

## License

Licensed under the [Apache License, Version 2.0](LICENSE).

Every source file carries the minimum clean mark:

```
Copyright 2026 Guzino (https://github.com/guzino)
SPDX-License-Identifier: Apache-2.0
```

## Conceptual origin

The original design package is kept in [`docs/`](docs/00-README.md) so the conceptual origin stays in the repository:

| Document | Title |
|----------|--------|
| [docs/00-README.md](docs/00-README.md) | Design package index |
| [docs/01-wald-origin.md](docs/01-wald-origin.md) | From Wald’s Notebook: The Armor That Is Not There |
| [docs/02-missing-planes-in-llms.md](docs/02-missing-planes-in-llms.md) | The Missing Planes in the Training Corpus |
| [docs/03-bulletproof-shield-design.md](docs/03-bulletproof-shield-design.md) | Bulletproof Shield Design |
| [docs/04-implementation-roadmap.md](docs/04-implementation-roadmap.md) | Implementation Roadmap and Engineering Notes |

Core claim: a model trained only on the planes that returned will correctly learn the distribution of survivable damage. Robustness requires an explicit process that reasons about the planes that did not return. That process is AbsenceCritic.

## Citation

If you use AbsenceCritic, please cite it as follows.

**Text**

[Guzino](https://github.com/guzino). *AbsenceCritic: A Survivorship-Bias Shield for Language Models*. 2026. https://github.com/guzino

**BibTeX**

```bibtex
@software{guzino_absencecritic_2026,
  author  = {Guzino},
  title   = {AbsenceCritic: A Survivorship-Bias Shield for Language Models},
  year    = {2026},
  url     = {https://github.com/guzino},
  license = {Apache-2.0},
  note    = {Original design and conceptual origin by Guzino (https://github.com/guzino)}
}
```

A machine-readable record is also provided in [`CITATION.cff`](CITATION.cff).
