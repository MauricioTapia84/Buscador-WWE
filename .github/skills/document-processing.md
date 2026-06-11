# 📄 Document Conversion & Office Processing Skill

Empowers the `@documentation-agent` and `@backend-agent` to handle Word, Excel, PDF, and Markdown conversions.

## 🎯 Purpose
Enable automated report generation (Word/Excel) and documentation synchronization between technical (Markdown) and administrative (PDF/Word) formats.

## 🛠️ Actions
1. **Markdown to Word/PDF**: 
   - Parse Markdown syntax to generate `.docx` using `docx` and `mammoth`.
   - Convert Markdown documentation to `.pdf` for client reporting or legal contracts.
2. **Excel Report Engineering**:
   - Aggregate database data (e.g., appointments, revenue) and export to `.xlsx` using `exceljs`.
   - Ensure cell formatting and styling for professional reports.
3. **Information Extraction**:
   - Read legacy `.pdf` or `.docx` files from the `Documentación/` folder to extract requirements or specifications.
   - Convert extracted text into formatted `.md` files for the codebase.
4. **Data Sync**:
   - Ensure `API_DOCUMENTATION.md` can be exported as a professional PDF for stakeholders.

## ⚠️ Constraints
- Large files should be processed using Node.js streams to avoid memory overflow.
- All generated documents must follow the naming convention: `[ID]_[Type]_[Date].extension`.
- Ensure no sensitive PII (Personally Identifiable Information) is included in exported files unless encrypted.
