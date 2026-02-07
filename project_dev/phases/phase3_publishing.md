# Phase 3: Publishing & Distribution

**Goal:** Publish integration to HACS and ensure discoverability.

## Status: Not Started

## Dependencies
- Phase 1 must be completed
- Phase 2 features should be stable
- All testing must pass

## Objectives
- [ ] Finalize repository structure
- [ ] Complete documentation
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
✓ Repository is public
✓ Separate from main NesVentory repo
- Needs proper GitHub releases

### 2. Documentation
Create comprehensive user documentation.

**README.md Requirements:**
- [ ] Clear project description
- [ ] Screenshots of integration in HA
- [ ] Installation instructions (HACS + Manual)
- [ ] Configuration guide with examples
- [ ] Troubleshooting section
- [ ] Feature list
- [ ] Requirements (HA version, NesVentory version)
- [ ] Badge for HACS

**Additional Docs:**
- [ ] `CONTRIBUTING.md` - Contribution guidelines
- [ ] `CHANGELOG.md` - Version history
- [ ] `LICENSE` - License file (if not present)

### 3. HACS Requirements Validation

**Repository Structure Check:**
```
✓ Root: hacs.json
✓ Root: custom_components/
✓ Root: README.md
- Root: info.md (optional, prettier display in HACS)
```

**hacs.json Validation:**
```json
{
  "name": "NesVentory",
  "render_readme": true,
  "filename": "nesventory.zip"
}
```

**manifest.json Validation:**
- [ ] Valid domain name
- [ ] Correct version format (semver)
- [ ] Working documentation URL
- [ ] Working issue tracker URL
- [ ] Correct iot_class
- [ ] All requirements listed
- [ ] Code owners specified

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
- [ ] Run `hassfest` validation
- [ ] Check with HACS action (GitHub workflow)

### 5. Versioning & Releases

**Semantic Versioning:**
- Use format: `MAJOR.MINOR.PATCH`
- Start with `0.1.0` for initial release
- Document breaking changes clearly

**GitHub Releases:**
- [ ] Create release workflow/process
- [ ] Tag releases properly (`v0.1.0`)
- [ ] Include changelog in release notes
- [ ] Attach any necessary assets

**First Release Checklist:**
- [ ] Version `0.1.0` in manifest.json
- [ ] Complete CHANGELOG.md entry
- [ ] All Phase 1 features working
- [ ] Documentation complete
- [ ] Create Git tag `v0.1.0`
- [ ] Create GitHub release

### 6. HACS Submission

**Pre-submission:**
- [ ] Repository is public
- [ ] All requirements met
- [ ] At least one release published
- [ ] README has clear installation instructions

**Submission Process:**
1. Fork `hacs/default` repository
2. Add integration to `custom_components.json`
3. Create pull request
4. Wait for review
5. Address any feedback
6. Merge approved

**Post-submission:**
- [ ] Update README with HACS badge
- [ ] Update documentation with HACS install method
- [ ] Announce in community forums (optional)

### 7. Maintenance Plan

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
