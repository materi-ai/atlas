# Materi Atlas Docs

This repository contains the Materi documentation site (Mintlify).

## Documentation contract

Before adding or editing content, read the contract:

-   [documentation-contract.mdx](documentation-contract.mdx)

It defines the stub rubric, required sections per doc type, and source-of-truth rules that keep docs accurate across many services.

## Local development

Install the Mintlify CLI:

```bash
npm i -g mint
```

Run the local preview from this folder (where `docs.json` lives):

```bash
mint dev
```

Preview at `http://localhost:3000`.

## Link validation

```bash
mint broken-links
```
