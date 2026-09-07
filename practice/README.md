# Automation practice

Use sample directories you own. The scripts list only immediate files and sizes,
exclude symlinks, and make no filesystem changes.

```sh
python3 practice/python/file_inventory.py samples
```

```powershell
./practice/powershell/Get-FileInventory.ps1 -Directory samples
```

Exercises: add extension filters, test empty directories and inaccessible paths,
then compare the two implementations. These are learning tasks, not completed features.
