# <type>(<scope>): <short summary>
#
# Types:
#   feat      – new feature
#   fix       – bug fix
#   docs      – documentation only
#   style     – formatting, no logic change
#   refactor  – code restructure, no feature/fix
#   test      – add or update tests
#   chore     – build, config, dependencies
#   ci        – GitHub Actions / workflow changes
#   pipeline  – vault-library-pipeline logic (rename, metadata, export)
#
# Scopes (optional):
#   cli, config, metadata, rename, export, zotero, obsidian, templates, workflow
#
# Examples:
#   feat(cli): add --watch mode for continuous PDF ingestion
#   fix(metadata): handle missing PDF creation date gracefully
#   docs(templates): update Obsidian YAML frontmatter fields
#   chore(deps): bump PyPDF2 to 3.1.0
#
# Summary rules:
#   - imperative mood  ("add", not "added" or "adds")
#   - no capital first letter
#   - no period at end
#   - 72 characters max
#
# Body (optional, leave blank line after summary):
#   Explain WHY, not WHAT. Reference issues with: closes #N, fixes #N
