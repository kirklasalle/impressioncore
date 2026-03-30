# Templates Listing

**Created:** March 29, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #ids #standardized_header #docs\reference\templates_listing.md #deployment #documentation #inference #testing #tokenization #training #web_interface  
**Category:** Reference Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

# ImpressionCore Web Templates

This document provides a listing of the template files in the `src/web/templates` directory of the ImpressionCore project.

## Current Templates

Based on the codebase, the following templates have been identified:

- `base.html`: The base template that other templates extend
- `define_model.html`: Template for defining and configuring model architecture

## Template Structure

The templates follow a hierarchical structure where most pages extend the `base.html` template, which provides common elements like:

- Navigation bar
- Footer
- Common CSS/JS includes
- Page structure

## Template Relationships

``` text
base.html
└── define_model.html
```

## Potential Missing Templates

Based on the documentation in `user_guide.md`, these templates might be needed:

1. `index.html` or `intro.html`: Main landing page
2. `setup.html`: Environment setup page
3. `unified_builder.html`: Central hub for building models
4. `tokenizer.html`, `tokenizer_text.html`, `tokenizer_image.html`, `tokenizer_info.html`: Tokenizer-related pages
5. `data_prep.html`: Data preparation page
6. `pretrain.html`: Pretraining configuration
7. `train.html`: Training configuration
8. `evaluate.html`: Model evaluation page
9. `inference.html`: Testing inference
10. `deploy.html`: Model deployment options

## Next Steps

- Implement the missing templates
- Ensure consistent styling across all templates
- Add proper navigation between related templates
- Include proper error handling and feedback mechanisms
