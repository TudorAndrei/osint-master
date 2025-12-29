# Project Context

## Purpose
OSINT (Open Source Intelligence) master project for collecting, analyzing, and managing intelligence from publicly available sources.

## Tech Stack
- Python 3.11 (with uv for package management)
- Bun (JavaScript runtime for tooling and scripts)
- OpenSpec (spec-driven development framework)

## Project Conventions

### Code Style
- Python: Follow PEP 8 conventions
- Use type hints where appropriate
- Prefer descriptive variable and function names
- Keep functions focused and single-purpose

### Architecture Patterns
- Spec-driven development using OpenSpec
- Capability-based organization (one capability per directory)
- Keep implementations simple until complexity is proven necessary

### Testing Strategy
- Write tests for all new capabilities
- Test requirements and scenarios as defined in specs
- Prefer integration tests that verify spec scenarios

### Git Workflow
- Create change proposals before implementing features
- Use descriptive commit messages
- Archive completed changes after deployment

## Domain Context
OSINT involves collecting information from publicly available sources such as:
- Social media platforms
- Public databases and registries
- News articles and publications
- Public APIs and web services
- Domain and IP information

Key considerations:
- Respect rate limits and terms of service
- Handle data privacy and ethical concerns
- Ensure data accuracy and source verification
- Manage large volumes of collected data efficiently

## Important Constraints
- Must comply with terms of service of all data sources
- Respect rate limits and implement appropriate throttling
- Handle data privacy regulations (GDPR, etc.) where applicable
- Ensure ethical use of collected intelligence

## External Dependencies
- OpenSpec CLI tool (`@fission-ai/openspec`) for spec management
- Python packages managed via uv (to be defined as project evolves)
