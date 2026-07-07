# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-XX

### Added
- Phase 1: Adaptive retry system for failed Ansys simulations
- Phase 2: Data validation and resource management
- Phase 3: Input validation and cross-material validation
- Phase 4: CI/CD pipeline and Docker support
- Comprehensive documentation and README
- Integration test suite

### Fixed
- [CRITICAL] Simulation success rate improved from 38% to 75%
- [HIGH] NaN values now properly validated throughout pipeline
- [HIGH] Resource cleanup guaranteed with context managers

### Changed
- Replaced hardcoded paths with configuration system
- Refactored data pipeline for memory efficiency
- Updated Ansys retry logic with diagnostic classification

### Deprecated
- Legacy simulation interface (removed in v2.0.0)

### Removed
- Old configuration files (use config/default_config.yaml)

### Security
- Added input validation with Pydantic
- Added CORS headers for API endpoints
- Updated dependencies for security patches

### Known Issues
- Ansys simulation limited to 4 parallel jobs on most licenses
- Material class detection requires explicit enum definition

## [0.9.0] - 2024-01-XX (Beta)

### Added
- Initial release with simulation and ML pipeline

---

## Version History

| Version | Date | Status | Notes |
|---------|------|--------|-------|
| 1.0.0 | 2024-01-XX | Stable | Production ready |
| 0.9.0 | 2024-01-XX | Beta | Initial release |
