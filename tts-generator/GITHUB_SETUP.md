# GitHub Setup Instructions

This directory contains all files ready to be uploaded to GitHub.

## ✅ What's Included

### Core Scripts
- `tts_generator.py` - Original version
- `tts_generator_enhanced.py` - Enhanced with audio tags
- `tts_generator_enhanced_v2.py` - Latest with HOF parsing
- `hof_to_json.py` - HOF to JSON converter utility

### Documentation
- `README.md` - Main project documentation
- `README_ENHANCED.md` - Enhanced features guide
- `HOF_PARSING_GUIDE.md` - HOF file structure documentation
- `VERSIONS_SUMMARY.md` - Version comparison guide
- `CLAUDE.md` - Developer documentation for Claude Code

### Configuration
- `.gitignore` - Excludes sensitive and generated files
- `config.json.example` - API key config template
- `.env.example` - Environment variables template
- `requirements.txt` - Python dependencies
- `LICENSE` - MIT License

### Example Files
- `zastavky.json` - Example announcements (Czech)
- `zastavky_with_tags_example.json` - Audio tags example
- `Bukovec_BUSE_V1.2 (testing).hof` - Example HOF file

### Audio Files
- `gong.wav` - Intro sound
- `nz.wav` - "Na znamení" jingle
- `pz.wav` - "Příští zastávka" jingle
- `kz.wav` - "Konečná zastávka" jingle
- `template.wav` - Template audio file

## 🔒 Security Notes

### Files EXCLUDED (for security):
- ❌ `config.json` - Contains your actual API key
- ❌ `venv/` - Virtual environment
- ❌ `__pycache__/` - Python cache
- ❌ `tts_cache/` - Generated cache files
- ❌ `generated_audio/` - Generated output files
- ❌ `.env` - Environment variables with secrets

### ⚠️ IMPORTANT:
The `.gitignore` file is configured to prevent accidental upload of:
- API keys (config.json, .env)
- Generated files
- Cache directories
- Virtual environments

## 🚀 GitHub Upload Steps

1. **Navigate to this directory:**
   ```bash
   cd C:\Users\plain\Desktop\Projekty\testing\tts_generator_github
   ```

2. **Initialize Git repository:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: TTS Generator with HOF parsing support"
   ```

3. **Create GitHub repository:**
   - Go to https://github.com/new
   - Create a new repository
   - DO NOT initialize with README (we already have one)

4. **Push to GitHub:**
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   git branch -M main
   git push -u origin main
   ```

## 📝 Suggested GitHub Repository Settings

### Repository Name Suggestions:
- `tts-generator-elevenlabs`
- `omsi-tts-generator`
- `public-transport-tts`

### Description:
"Python TTS generator for public transport announcements using ElevenLabs API with OMSI HOF file parsing, audio tag support, and free Google TTS testing mode"

### Topics (tags):
- `text-to-speech`
- `elevenlabs`
- `tts`
- `omsi`
- `public-transport`
- `czech`
- `hof-parser`
- `audio-processing`

### Features to enable:
- ✅ Issues
- ✅ Discussions (optional)
- ✅ Wiki (optional)

## 📋 Post-Upload Checklist

After uploading to GitHub:

1. ✅ Verify `.gitignore` is working (no config.json in repo)
2. ✅ Check that README.md displays correctly
3. ✅ Add repository topics/tags
4. ✅ Enable GitHub Actions (optional, for future CI/CD)
5. ✅ Star your own repo!

## 🔧 User Setup Instructions

Users cloning your repository will need to:

1. Clone the repository
2. Create virtual environment: `python -m venv venv`
3. Activate: `venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `config.json.example` to `config.json`
6. Add their ElevenLabs API key to `config.json`
7. Or create `.env` file from `.env.example`

## 📦 Optional: GitHub Release

Consider creating a release:
- Tag: `v1.0.0`
- Title: "Initial Release - TTS Generator with HOF Support"
- Description: Summarize features from VERSIONS_SUMMARY.md

## 🐛 Issues Template (Recommended)

After uploading, you can add issue templates in `.github/ISSUE_TEMPLATE/`:
- Bug report
- Feature request
- HOF parsing issues

---

**Ready to upload!** 🎉

All sensitive data has been removed and proper .gitignore is in place.
