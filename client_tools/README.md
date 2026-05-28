# 🖨️ SMRITI Retail OS - Windows Print Agent

This print agent allows **SMRITI Retail OS** to print thermal barcode labels (ZPL and TSPL) automatically when clicked in the browser, without any manual copying or third-party paid software.

## How it Works
1. When you click **Print** in the barcode web UI, the web application downloads a raw print instructions file (`smriti_barcodes_*.prn`).
2. This print agent runs in the background on your Windows machine and watches your **Downloads** directory.
3. As soon as a new `.prn` file is downloaded, it automatically sends it to your selected thermal printer and moves the file to the `Downloads/smriti_printed/` folder for archiving.

## 🚀 Setup Instructions

1. **One-Time Installation:**
   Double-click the **[setup_agent.bat](file:///d:/Smriti_Retail_OS/apps/smriti_retail_os/client_tools/setup_agent.bat)** file. It will automatically check Python and install the required Windows printing dependencies.

2. **Configure and Run:**
   Double-click the **[run_agent.bat](file:///d:/Smriti_Retail_OS/apps/smriti_retail_os/client_tools/run_agent.bat)** file.
   - On the first run, it will display a list of all installed printers on your system.
   - Select the number corresponding to your barcode label printer (e.g. `IMPACT by Honeywell IH-2 (ZPL)`).
   - This preference is saved to `config.txt` and used automatically on subsequent launches.

3. **Optional: Run Automatically on Boot**
   If you want this agent to start automatically whenever you turn on your PC:
   1. Press `Win + R` on your keyboard.
   2. Type `shell:startup` and press Enter. This opens the Windows Startup folder.
   3. Right-click inside the folder, select **New > Shortcut**, and browse to `run_agent.bat`.
