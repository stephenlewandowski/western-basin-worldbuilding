# Glasspunk Systems Atlas

Phase 1 builds the validated Water System v0.1. Phase 2A adds only the first 2026 materials baseline and stops for human review. Existing TypeScript prototype files are untouched.

```powershell
.\.venv\Scripts\python.exe src\python\systems\build_water_system.py --historical-swamp-image "C:\Users\slewa\Downloads\Great Black Swamp.jpeg"
Rscript src\R\systems\validate_water_system.R .
Rscript src\R\systems\render_water_system.R .
.\.venv\Scripts\python.exe src\python\systems\build_materials_system.py
Rscript src\R\systems\validate_materials_system.R .
Rscript src\R\systems\render_materials_system.R .
.\.venv\Scripts\python.exe src\python\systems\validate_materials_system.py
```

Raw public-service responses are cached under `data/raw`. Delete a specific cached response only when intentionally refreshing that source.
