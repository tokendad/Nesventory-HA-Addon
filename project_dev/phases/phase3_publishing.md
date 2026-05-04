# Phase 3: Publishing & Distribution

**Goal:** Publish the integration to HACS and ensure discoverability.

## Status: Not Started — depends on Phase 1 + Phase 2
## Last Updated: 2026-05-04

## Dependencies
- Phase 1 implementation must be complete, including the remaining API verification follow-up items
- Phase 2 features should be stable
- Automated tests and manual validation must pass before release

## Objectives
- [ ] Finalize repository structure
- [ ] Complete documentation
- [ ] Add validation and CI workflows
- [ ] Submit to HACS default repository
- [ ] Create release process

## Tasks

### 1. Repository Decision
**Decision Point:** Separate repo vs. monorepo

**Current Status:** Using separate repository (`Nesventory-HA-Addon`)

**Advantages:**
- Clean separation of concerns
- Independent versioning
- HACS releases don't trigger on main NesVentory changes
- Easier maintenance

**Requirements:**
- [x] Repository is public
- [x] Separate from main NesVentory repo
- [ ] Add proper GitHub releases

### 2. Documentation
Create comprehensive user documentation.

**README.md Requirements:**
- [x] Clear project description
- [ ] Screenshots of integration in HA
- [x] Installation instructions (HACS + Manual)
- [x] Configuration guide with examples
- [ ] Troubleshooting section
- [x] Feature list
- [x] Requirements (HA version, NesVentory version)
- [x] Badge for HACS

**Additional Docs:**
- [ ] `CONTRIBUTING.md` - Does not exist yet; create contribution guidelines
- [x] `CHANGELOG.md` - Version history exists
- [ ] `LICENSE` - Does not exist yet; add before HACS release

### 3. HACS Requirements Validation

**Repository Structure Check:**
```
✓ Root: hacs.json
✓ Root: custom_components/
✓ Root: README.md
- Root: info.md (optional, prettier display in HACS)
- Root: CONTRIBUTING.md (recommended, currently missing)
- Root: LICENSE (needed before release, currently missing)
```

**Current `hacs.json`:**
```json
{
  "name": "NesVentory",
  "render_readme": true,
  "homeassistant": "2024.1.0"
}
```

**Notes:**
- The current file does **not** include a `filename` key
- For this integration repository, `filename` may not be needed unless release packaging is changed to require a zip asset
- The `homeassistant` key already documents the minimum supported Home Assistant version

**manifest.json Validation:**
- [x] Valid domain name
- [ ] Update version from `0.0.1` to `0.1.0` for the first release
- [x] Working documentation URL
- [x] Working issue tracker URL
- [x] Correct `iot_class`
- [x] Requirements listed
- [x] Code owners specified

### 4. Quality Assurance

**Code Quality:**
- [ ] All Python files follow HA coding standards
- [ ] Type hints where appropriate
- [ ] Docstrings for all classes/functions
- [ ] No security issues (secrets, hardcoded values)
- [ ] Proper logging (info, warning, error levels)

**Testing:**
- [ ] Manual testing on latest HA version
- [ ] Manual testing on HA minimum version
- [ ] Test with unavailable NesVentory backend
- [ ] Test configuration flow edge cases
- [ ] Test service calls
- [ ] Test sensor updates

**Validation Tools:**
- [ ] Run `python3 -m script.hassfest` (or equivalent hassfest workflow) to validate `manifest.json`
- [ ] Add HACS validation using `hacs/action` in GitHub Actions

### 5. GitHub Actions CI
Create `.github/workflows/` for repeatable validation on pull requests.

**Minimum Workflows:**
- [ ] Hassfest validation workflow
- [ ] HACS validation workflow
- [ ] PR lint workflow running at minimum `pylint` and `black --check`

**Notes:**
- No project CI workflow is in place yet
- CI should block obvious metadata and style regressions before release

### 6. Versioning & Releases

**Semantic Versioning:**
- Use format: `MAJOR.MINOR.PATCH`
- Start with `0.1.0` for the initial release
- Document breaking changes clearly

**GitHub Releases:**
- [ ] Create release workflow/process
- [ ] Tag releases properly (`v0.1.0`)
- [ ] Include changelog in release notes
- [ ] Attach any necessary assets

**First Release Checklist:**
- [ ] Version `0.1.0` in `custom_components/nesventory/manifest.json` (currently `0.0.1`)
- [ ] Complete CHANGELOG.md entry
- [ ] All Phase 1 features working
- [ ] Phase 2 scope complete enough for intended first release
- [ ] Documentation complete
- [ ] Create Git tag `v0.1.0`
- [ ] Create GitHub release

### 7. HACS Submission

**Pre-submission:**
- [x] Repository is public
- [ ] All requirements met
- [ ] At least one release published
- [x] README has installation instructions

**Submission Process:**
1. Fork `hacs/default` repository
2. Add integration to `custom_components.json`
3. Create pull request
4. Wait for review
5. Address any feedback
6. Merge approved

**Post-submission:**
- [x] README already includes a HACS badge
- [x] README already includes a HACS/custom repository install method
- [ ] Announce in community forums (optional)

### 8. Maintenance Plan

**Ongoing Tasks:**
- Monitor GitHub issues
- Update for HA breaking changes
- Regular dependency updates
- Community support

**Update Process:**
1. Make changes
2. Update version in manifest.json
3. Update CHANGELOG.md
4. Create Git tag
5. Create GitHub release
6. HACS auto-updates users

## Testing Checklist
- [ ] Fresh install via HACS in test HA instance
- [ ] Verify all features work
- [ ] Check documentation accuracy
- [ ] Validate links in README
- [ ] Test upgrade path (if updating)

## Success Metrics
- Successful HACS listing
- Clean installation process
- Positive user feedback
- No critical bugs in first week

## Notes
- HACS validation can take a few days
- Be responsive to reviewer feedback
- Consider beta testers before public release
- Join HA Discord for integration support
