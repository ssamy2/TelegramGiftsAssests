import os
import json

def check_catalog():
    print("=== CATALOG SANITY CHECK ===")
    
    # Paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, "Gifts_Details.json")
    models_dir = os.path.join(base_dir, "models")
    webp_dir = os.path.join(base_dir, "webp", "by_name")
    tgs_dir = os.path.join(base_dir, "tgs", "by_name")
    
    if not os.path.exists(json_path):
        print(f"ERROR: Gifts_Details.json not found at {json_path}")
        return
        
    with open(json_path, "r", encoding="utf-8") as f:
        catalog = json.load(f)
        
    upgraded = catalog.get("upgraded", [])
    unupgraded = catalog.get("unupgraded", [])
    regular = catalog.get("regular", [])
    regular_gifts = catalog.get("regular_gifts", [])
    
    # 1. Duplicates in upgraded
    upg_short_names = {}
    upg_regular_ids = {}
    for idx, item in enumerate(upgraded):
        sname = item.get("short_name")
        reg_id = item.get("regular_id")
        fname = item.get("full_name")
        
        if sname:
            upg_short_names.setdefault(sname, []).append((idx, fname, reg_id))
        if reg_id:
            upg_regular_ids.setdefault(reg_id, []).append((idx, fname, sname))
            
    print("\n--- Duplicate short_names in upgraded[] ---")
    for sname, entries in upg_short_names.items():
        if len(entries) > 1:
            print(f"  '{sname}':")
            for idx, fname, reg_id in entries:
                print(f"    - Index {idx}: Name='{fname}', regular_id='{reg_id}'")
                
    print("\n--- Duplicate regular_ids in upgraded[] ---")
    for reg_id, entries in upg_regular_ids.items():
        if len(entries) > 1:
            print(f"  '{reg_id}':")
            for idx, fname, sname in entries:
                print(f"    - Index {idx}: Name='{fname}', short_name='{sname}'")
                
    # 2. Check models directory
    print("\n--- Checking models/ directories ---")
    if os.path.exists(models_dir):
        model_folders = [d for d in os.listdir(models_dir) if os.path.isdir(os.path.join(models_dir, d))]
        upg_short_names_set = set(upg_short_names.keys())
        
        print(f"  Total folders in models/: {len(model_folders)}")
        print(f"  Total short_names in catalog: {len(upg_short_names_set)}")
        
        extra_folders = [f for f in model_folders if f not in upg_short_names_set]
        missing_folders = [s for s in upg_short_names_set if s not in model_folders]
        
        if extra_folders:
            print(f"  Extra folders in models/ (not in upgraded catalog):")
            for f in sorted(extra_folders):
                print(f"    - {f}")
        if missing_folders:
            print(f"  Missing folders in models/ (in catalog but no folder):")
            for s in sorted(missing_folders):
                print(f"    - {s}")
                
    # 3. Check assets in webp/by_name and tgs/by_name
    print("\n--- Checking WebP / TGS asset completeness ---")
    all_catalog_short_names = set()
    for item in upgraded + unupgraded + regular + regular_gifts:
        sname = item.get("short_name")
        if sname:
            all_catalog_short_names.add(sname)
            
    if os.path.exists(webp_dir):
        webp_files = {os.path.splitext(f)[0] for f in os.listdir(webp_dir) if f.endswith(".webp")}
        orphan_webp = webp_files - all_catalog_short_names
        missing_webp = all_catalog_short_names - webp_files
        
        print(f"  Orphan WebP files in webp/by_name/ (not referenced in catalog): {len(orphan_webp)}")
        for w in sorted(list(orphan_webp))[:10]:
            print(f"    - {w}.webp")
        if len(orphan_webp) > 10:
            print("      ...")
            
        # Ignore regular gifts when checking missing since they don't always have TGS/WebP names
        non_regular_short_names = {item.get("short_name") for item in upgraded + unupgraded if item.get("short_name")}
        missing_webp_non_reg = non_regular_short_names - webp_files
        if missing_webp_non_reg:
            print(f"  Missing WebP files (referenced in upgraded/unupgraded but file doesn't exist): {len(missing_webp_non_reg)}")
            for w in sorted(list(missing_webp_non_reg)):
                print(f"    - {w}.webp")
                
    if os.path.exists(tgs_dir):
        tgs_files = {os.path.splitext(f)[0] for f in os.listdir(tgs_dir) if f.endswith(".tgs")}
        non_regular_short_names = {item.get("short_name") for item in upgraded + unupgraded if item.get("short_name")}
        orphan_tgs = tgs_files - non_regular_short_names
        missing_tgs = non_regular_short_names - tgs_files
        
        print(f"  Orphan TGS files in tgs/by_name/ (not referenced in upgraded/unupgraded catalog): {len(orphan_tgs)}")
        for t in sorted(list(orphan_tgs))[:10]:
            print(f"    - {t}.tgs")
        if len(orphan_tgs) > 10:
            print("      ...")
            
        if missing_tgs:
            print(f"  Missing TGS files (referenced in upgraded/unupgraded but file doesn't exist): {len(missing_tgs)}")
            for t in sorted(list(missing_tgs)):
                print(f"    - {t}.tgs")

if __name__ == "__main__":
    check_catalog()
