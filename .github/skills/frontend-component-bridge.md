# 🎨 React Component Bridge Skill

Guides the `@frontend-agent` in creating Power Pages compatible components.

## 🎯 Purpose
Ensure React components work within the legacy portal and use React-Bootstrap.

## 🛠️ Actions
1. **Component Scaffold**: Create in `front-fadebooker/src/components/` using TypeScript.
2. **Bootstrap Integration**: Use `react-bootstrap` components only (no Tailwind).
3. **API Hook**: Create/Update TanStack Query hooks in `src/hooks/`.
4. **Shadow DOM Check**: Ensure styles don't conflict with Power Pages global CSS.

## ⚠️ Constraints
- Maximize reuse of `shared/` components.
- Props must be documented with TypeScript interfaces.
- Use `clsx` for conditional class management.
