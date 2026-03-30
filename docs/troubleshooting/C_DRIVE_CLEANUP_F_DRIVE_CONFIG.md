# C: Drive Cleanup and F: Drive Configuration - Resolution

**Created:** October 08, 2025  
**Updated:** December 29, 2025  
**Author:** ImpressionCore Team  
**Tags:** #docs\troubleshooting\C_DRIVE_CLEANUP_F_DRIVE_CONFIG.md #documentation  
**Category:** Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

**Issue:** C: drive filled with 23.54 GB HuggingFace cache

---

## 🚨 **PROBLEM**

During Natural Questions dataset download, HuggingFace filled C: drive with 23.54 GB of cache data:

- **Location:** `C:\Users\kirkl\.cache\huggingface\`
- **Size:** 23.54 GB
- **Impact:** C: drive ran out of space, caused download failures

---

## ✅ **RESOLUTION ACTIONS**

### 1. **Deleted C: Drive Cache**

```powershell
Remove-Item -Path "C:\Users\kirkl\.cache\huggingface" -Recurse -Force
```

**Result:** Freed 23.54 GB on C: drive ✅

### 2. **Created F: Drive Structure**

``` text
F:\huggingface_cache\
├── hub\          # HuggingFace Hub models
└── datasets\     # HuggingFace datasets
```

### 3. **Created Configuration Script**

**File:** `setup_hf_cache_f_drive.ps1`

```powershell
$env:HF_HOME="F:\huggingface_cache"
$env:HUGGINGFACE_HUB_CACHE="F:\huggingface_cache\hub"
$env:HF_DATASETS_CACHE="F:\huggingface_cache\datasets"
```

### 4. **Updated Download Scripts**

Modified `download_explanatory_qa_alternative.py` to set F: drive environment variables at script startup:

```python
# Configure HuggingFace to use F: drive
os.environ['HF_HOME'] = 'F:/huggingface_cache'
os.environ['HUGGINGFACE_HUB_CACHE'] = 'F:/huggingface_cache/hub'
os.environ['HF_DATASETS_CACHE'] = 'F:/huggingface_cache/datasets'
```

---

## 📋 **HOW TO USE GOING FORWARD**

### **Before Any HuggingFace Operations:**

**Option 1: Run Setup Script (Recommended)**

```powershell
. .\setup_hf_cache_f_drive.ps1
python your_script.py
```

**Option 2: Set Environment Variables Manually**

```powershell
$env:HF_HOME="F:\huggingface_cache"
$env:HUGGINGFACE_HUB_CACHE="F:\huggingface_cache\hub"
$env:HF_DATASETS_CACHE="F:\huggingface_cache\datasets"
```

**Option 3: Make Permanent (System-Wide)**

1. Search "Environment Variables" in Windows
2. Click "Environment Variables" button
3. Under "User variables", click "New"
4. Add these three variables:
   - `HF_HOME` → `F:\huggingface_cache`
   - `HUGGINGFACE_HUB_CACHE` → `F:\huggingface_cache\hub`
   - `HF_DATASETS_CACHE` → `F:\huggingface_cache\datasets`

---

## 📊 **CURRENT STATE**

### **C: Drive**

- ✅ HuggingFace cache deleted
- ✅ 23.54 GB freed
- ✅ No more automatic downloads to C:

### **F: Drive**

- ✅ Directory structure created
- ✅ Ready for HuggingFace downloads
- ✅ 476 GB available

### **Scripts Updated**

- ✅ `download_explanatory_qa_alternative.py` - sets F: drive env vars
- ✅ `setup_hf_cache_f_drive.ps1` - configuration script created
- ✅ `cleanup_and_configure_hf_cache.py` - cleanup utility created

---

## 🎯 **LESSONS LEARNED**

1. **Always Configure Cache Location First**
   - HuggingFace defaults to C: drive (`~/.cache/huggingface/`)
   - Must explicitly set environment variables before downloading

2. **Monitor Disk Space**
   - Large datasets (Natural Questions = 50GB) can quickly fill drives
   - Always check available space before downloads

3. **Use F: Drive for AI/ML Data**
   - F: drive has 476 GB available
   - Specifically allocated for training data and models
   - C: drive should remain lean for OS and applications

4. **Set Environment Variables Early**
   - Set at session start, not mid-download
   - Include in training scripts and pipelines
   - Consider making permanent via Windows system settings

---

## 🚀 **NEXT STEPS**

### **Immediate (Before Training):**

1. **Source setup script:**

   ```powershell
   . .\setup_hf_cache_f_drive.ps1
   ```

2. **Fix training script import error:**
   - Update `train_with_true_qa_dataset.py`
   - Change import path for model

3. **Restart pipeline:**

   ```powershell
   python run_option_a_pipeline.py
   ```

### **Future Prevention:**

1. **Add to PowerShell Profile:**

   ```powershell

   # Edit profile

   notepad $PROFILE
   
   # Add these lines:

   $env:HF_HOME="F:\huggingface_cache"
   $env:HUGGINGFACE_HUB_CACHE="F:\huggingface_cache\hub"
   $env:HF_DATASETS_CACHE="F:\huggingface_cache\datasets"
   ```

2. **Update all download scripts:**
   - Add F: drive configuration to script headers
   - Include environment variable checks
   - Add disk space verification before downloads

---

## 📝 **FILES CREATED**

1. **`setup_hf_cache_f_drive.ps1`**
   - PowerShell script to configure environment
   - Run before any HuggingFace operations
   - 9 lines, simple and effective

2. **`cleanup_and_configure_hf_cache.py`**
   - Python utility for cleanup and configuration
   - Interactive C: drive cache deletion
   - F: drive structure creation
   - Environment configuration

3. **`docs/troubleshooting/C_DRIVE_CLEANUP_F_DRIVE_CONFIG.md`**
   - This documentation file
   - Reference for future issues
   - Setup instructions

---

## ✅ **VERIFICATION**

**C: Drive Status:**

```powershell
# Check C: drive cache
Test-Path "C:\Users\kirkl\.cache\huggingface"  # Should be False
```

**F: Drive Status:**

```powershell
# Check F: drive structure
Test-Path "F:\huggingface_cache"              # Should be True
Test-Path "F:\huggingface_cache\hub"          # Should be True
Test-Path "F:\huggingface_cache\datasets"     # Should be True
```

**Environment Variables:**

```powershell
# Check environment
echo $env:HF_HOME                              # Should be F:\huggingface_cache
echo $env:HUGGINGFACE_HUB_CACHE               # Should be F:\huggingface_cache\hub
echo $env:HF_DATASETS_CACHE                   # Should be F:\huggingface_cache\datasets
```

---

## 🎉 **RESOLUTION STATUS**

**STATUS:** ✅ **RESOLVED**

- C: drive cleaned: ✅ 23.54 GB freed
- F: drive configured: ✅ Structure created
- Scripts updated: ✅ Environment variables added
- Documentation created: ✅ This file
- Ready to proceed: ✅ Training can continue

**Next Action:** Fix training script import error, then restart pipeline

---

**Document Status:** COMPLETE  
**Resolution Time:** ~15 minutes  
**Space Freed:** 23.54 GB on C: drive
