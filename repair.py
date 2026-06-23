import os
import json
import shutil

def run_repairs():
    print("=== STARTING ARCHITECTURE REPAIRS ===")
    
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
    
    # --- STEP 1: DEDUPLICATE CATALOG UPGRADED ARRAY ---
    print("\n[Step 1] Deduplicating upgraded list in catalog...")
    merged_upgraded = []
    seen_short_names = {}
    
    for item in upgraded:
        sname = item.get("short_name")
        if not sname:
            merged_upgraded.append(item)
            continue
            
        if sname in seen_short_names:
            # Duplicate found! Merge regular_id into regular_ids
            existing = seen_short_names[sname]
            if "regular_ids" not in existing:
                existing["regular_ids"] = [existing.get("regular_id")]
                
            reg_id = item.get("regular_id")
            if reg_id and reg_id not in existing["regular_ids"]:
                existing["regular_ids"].append(reg_id)
                
            # If the duplicate has a custom_emoji_id and the existing one doesn't, copy it
            if item.get("custom_emoji_id") and not existing.get("custom_emoji_id"):
                existing["custom_emoji_id"] = item["custom_emoji_id"]
                
            # Merge prices (keep the maximum non-null values)
            for price_field in ["floor_price_ton", "portal_price_ton", "getgems_price_ton", "tgmrkt_price_ton"]:
                val = item.get(price_field)
                if val is not None:
                    curr = existing.get(price_field)
                    if curr is None or val > curr:
                        existing[price_field] = val
        else:
            # First time seeing this short_name, create entry
            new_item = item.copy()
            if "regular_id" in new_item:
                new_item["regular_ids"] = [new_item["regular_id"]]
            seen_short_names[sname] = new_item
            merged_upgraded.append(new_item)
            
    print(f"  Reduced upgraded count from {len(upgraded)} to {len(merged_upgraded)}")
    catalog["upgraded"] = merged_upgraded
    
    # --- STEP 2: RENAME DIRECTORIES TO CANONICAL NAMES ---
    print("\n[Step 2] Renaming non-canonical models/ directories...")
    renames = {
        "b-day_candle": "bday_candle",
        "durov’s_cap": "durovs_cap",
        "durov\'s_cap": "durovs_cap",  # handle both straight/curly apostrophes
        "jack-in-the-box": "jackinthebox",
        "surge_board": "upgraded_surfboard"
    }
    
    if os.path.exists(models_dir):
        for old_name, new_name in renames.items():
            old_path = os.path.join(models_dir, old_name)
            new_path = os.path.join(models_dir, new_name)
            
            if os.path.exists(old_path):
                # If target already exists, merge/remove first
                if os.path.exists(new_path):
                    print(f"  Target directory {new_name} already exists. Merging content...")
                    for file in os.listdir(old_path):
                        shutil.move(os.path.join(old_path, file), os.path.join(new_path, file))
                    shutil.rmtree(old_path)
                else:
                    os.rename(old_path, new_path)
                    print(f"  Renamed models/{old_name} -> models/{new_name}")
                    
    # --- STEP 3: REPAIR config.json PATHS & DIRECTORY REF IN RENAMED FOLDERS ---
    print("\n[Step 3] Repairing config.json paths inside all models...")
    if os.path.exists(models_dir):
        for folder in os.listdir(models_dir):
            folder_path = os.path.join(models_dir, folder)
            if not os.path.isdir(folder_path):
                continue
                
            config_path = os.path.join(folder_path, "config.json")
            if os.path.exists(config_path):
                try:
                    with open(config_path, "r", encoding="utf-8") as cf:
                        configs = json.load(cf)
                        
                    modified_config = False
                    for item in configs:
                        tgs = item.get("tgs_path", "")
                        webp = item.get("webp_path", "")
                        
                        # Clean paths: remove prefix and use correct directory
                        for path_key, val in [("tgs_path", tgs), ("webp_path", webp)]:
                            if not val:
                                continue
                            new_val = val
                            # Remove prefix
                            if new_val.startswith("TG_Photos_repo/"):
                                new_val = new_val[len("TG_Photos_repo/"):]
                            # Update directory names
                            for old_d, new_d in renames.items():
                                if f"models/{old_d}/" in new_val:
                                    new_val = new_val.replace(f"models/{old_d}/", f"models/{new_d}/")
                                    
                            if new_val != val:
                                item[path_key] = new_val
                                modified_config = True
                                
                    if modified_config:
                        with open(config_path, "w", encoding="utf-8") as cf:
                            json.dump(configs, cf, indent=2, ensure_ascii=False)
                        print(f"  Fixed paths in models/{folder}/config.json")
                except Exception as e:
                    print(f"  ERROR fixing models/{folder}/config.json: {e}")
                    
    # --- STEP 4: UPDATE MODELS FIELD IN CATALOG FOR renamed/missing ---
    print("\n[Step 4] Updating models path fields in catalog...")
    for item in merged_upgraded:
        sname = item.get("short_name")
        # Ensure surfboard has models path
        if sname == "upgraded_surfboard":
            item["models"] = "models/upgraded_surfboard/prices.json"
            print("  Added models path to upgraded_surfboard")
        # Ensure all models paths resolve relative to repo root
        elif sname and "models" in item:
            item["models"] = f"models/{sname}/prices.json"
            
    # Save the updated catalog
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
    print("  Saved updated catalog Gifts_Details.json")
    
    # --- STEP 5: ORPHAN ASSETS CLEANUP ---
    print("\n[Step 5] Cleaning up orphan WebP and TGS files...")
    # Gather all short_names from the updated catalog
    valid_short_names = set()
    for item in merged_upgraded + unupgraded + regular + regular_gifts:
        sname = item.get("short_name")
        if sname:
            valid_short_names.add(sname)
            
    # Clean webp/by_name
    deleted_webp = 0
    if os.path.exists(webp_dir):
        for file in os.listdir(webp_dir):
            if not file.endswith(".webp"):
                continue
            name = os.path.splitext(file)[0]
            if name not in valid_short_names:
                os.remove(os.path.join(webp_dir, file))
                deleted_webp += 1
    print(f"  Deleted {deleted_webp} orphan WebP files in webp/by_name/")
    
    # Clean tgs/by_name (only compare against upgraded/unupgraded as regular gifts don't use TGS)
    deleted_tgs = 0
    valid_tgs_names = {item.get("short_name") for item in merged_upgraded + unupgraded if item.get("short_name")}
    if os.path.exists(tgs_dir):
        for file in os.listdir(tgs_dir):
            if not file.endswith(".tgs"):
                continue
            name = os.path.splitext(file)[0]
            if name not in valid_tgs_names:
                os.remove(os.path.join(tgs_dir, file))
                deleted_tgs += 1
    print(f"  Deleted {deleted_tgs} orphan TGS files in tgs/by_name/")
    
    print("\n=== REPAIRS COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    run_repairs()
