# 🌥️ IMAGINTIX — Cloud Removal from Satellite Images

IMAGINTIX is a final-year AI project that removes cloud cover from satellite images using a GAN-based model.  
Users upload an image via a web interface and receive a processed, cloud-free result from the backend.

---

## ⚙️ Tech Stack
- Frontend: React + TypeScript
- Backend: FastAPI (Python)
- AI Model: GAN
- Database: PostgreSQL (Azure VM setup)
- Deployment: Azure VM

---

## 🚀 How to Run the Project

### 1️⃣ Start Backend
```bash
cd backend
gan-venv\Scripts\activate
uvicorn main:app --reload
