# ImpressionCore IDS Usage Guide - Quick Reference

**Created:** June 09, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #ids #standardized_header #docs\reference\ids_usage_guide.md #cuda #documentation #gpu_optimization #memory_management #performance #testing #training  
**Category:** Reference Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

## IDS Refresh Issue Resolution ✅

**Issue**: IDS searches were returning 0 results due to stale indices
**Solution**: Added refresh mechanism to keep data current

## Quick Refresh Commands

### Option 1: Batch File (Recommended)

```bash
# From project root
./refresh_ids.bat
```

### Option 2: Python Script

```bash
cd /d/Projects/impressioncore
.venv/Scripts/activate
python src/dev_tools/ids_refresh.py
```

### Option 3: Manual Refresh

```bash
cd /d/Projects/impressioncore
.venv/Scripts/activate
python docs/scripts/automation/ids_memlog_integration.py
python docs/scripts/automation/ids_maintenance_tool.py --update
```

## Search Guidelines

### ✅ Use Singular Terms

- ✅ "CUDA" (not "CUDA setup")
- ✅ "gpu" (not "GPU monitoring") 
- ✅ "training" (not "training setup")
- ✅ "memory" (not "memory management")

### 🔍 Available Search Terms After CUDA Setup

- **Hardware**: gpu, cuda, nvidia, vram, memory
- **Setup**: setup, installation, configuration, environment
- **Training**: training, optimization, performance, benchmark
- **Tools**: diagnostic, monitoring, utilities, tools
- **Status**: completion, status, validation, testing

### 📊 Search Result Format

Each result includes:

- `file_path`: Location of the document
- `matching_tags`: Relevant tags found
- `metadata`: File info (size, modified date, type)
- `total_found`: Number of matching documents

## Recent CUDA Setup Documentation

After refresh, these terms will find our recent work:

- `setup` - CUDA setup documentation
- `completion` - Setup completion reports  
- `gpu` - GPU diagnostic tools
- `diagnostic` - New diagnostic utilities
- `monitoring` - VRAM monitoring tools
- `cuda` - CUDA configuration details

## Best Practices

1. **Always refresh before major work sessions**

   ```bash
   ./refresh_ids.bat
   ```

2. **Use specific, singular terms**
   - Better: "memory" 
   - Avoid: "memory management optimization"

3. **Check total_found for scope**
   - High numbers (>100): Term is very common
   - Low numbers (<10): More specific results

4. **Combine searches for complex topics**
   - Search "cuda" then "setup" then "validation"

## Troubleshooting

### If searches still return 0 results:

1. Run refresh script again
2. Check if virtual environment is active
3. Verify project structure is intact
4. Try broader search terms first

### If refresh fails:

1. Check Python environment is working
2. Verify all required scripts exist
3. Run manual maintenance commands
4. Check logs in `ids_maintenance.log`

---

**Created**: 2025-01-06  
**Status**: ✅ IDS system refreshed and operational  
**Next**: Ready for efficient documentation searches
