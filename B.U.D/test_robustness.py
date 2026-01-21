import modules.skills as skills

print("--- TESTING ROBUSTNESS ---")

# 1. Test Open Fake App
print("\n[TEST] Open Fake App")
result = skills.open_app("this_app_does_not_exist")
if result is False:
    print("[SUCCESS] Correctly returned False for fake app.")
else:
    print("[FAIL] Returned True for fake app.")

# 2. Test Delete Fake File
print("\n[TEST] Delete Fake File")
result = skills.delete_file("fake_file.txt")
if result is False:
    print("[SUCCESS] Correctly returned False for missing file.")
else:
    print("[FAIL] Returned True for missing file.")

# 3. Test YouTube (We can't easily mock network failure, but we check if it runs)
print("\n[TEST] Play YouTube (Valid)")
# Should return True (even if browser fallback)
result = skills.play_youtube("Test Video")
if result is True:
    print("[SUCCESS] Returned True for valid video.")
else:
    print("[FAIL] Returned False for valid video.")

print("\n--- TEST COMPLETE ---")
