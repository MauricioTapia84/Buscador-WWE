# ☁️ Cloudinary & Image Processing Skill

Automation for image handling and AI photo simulation.

## 🎯 Purpose
Standardize image uploads, transformations, and digital photography simulation.

## 🛠️ Actions
1. **Service Implementation**: Complete `CloudinaryService.js` in `src/infraestructure/storage/`.
2. **Signature Generation**: Implement server-side signatures for secure uploads.
3. **Simulated Filters**: Apply Cloudinary transformations (e.g., `e_sepia`, `c_fill,h_500,w_500`) to simulate different photographic styles.
4. **Relational Photography**: Handle association between `Cita` and multiple photo assets.

## ⚠️ Constraints
- Never expose API Secrets in code (use `process.env.CLOUDINARY_SECRET`).
- All images must be resized on the server (or via transformation URL) to save bandwidth.
