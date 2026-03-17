# Project Rules

## UI/UX Rules

### RTL (Right-to-Left) Alignment
**Rule**: All user interface elements must be aligned to the right (RTL - Right-to-Left).

**Rationale**:
- Supports right-to-left languages like Hebrew and Arabic
- Ensures proper text flow and readability
- Consistent with RTL language conventions
- Improves user experience for RTL users

**Implementation**:
- Use CSS `direction: rtl` on main containers
- Ensure proper mirroring of UI elements
- Test with RTL languages during development
- Use RTL-aware CSS frameworks or libraries

**Exceptions**:
- Code editors and technical content may remain LTR
- External libraries that don't support RTL

**Enforcement**:
- Code reviews must check RTL compliance
- Automated tests for RTL layout
- Design reviews include RTL considerations