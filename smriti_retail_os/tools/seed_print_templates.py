# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/tools/seed_print_templates.py
# @description: Seeds default enterprise print templates into SMRITI Print Template.
#

from smriti_retail_os import smriti

DEFAULT_TEMPLATES = [
    {
        "name": "Retail Footwear Dual Tag (50x25)",
        "template_title": "Retail Footwear Dual Tag (50x25)",
        "label_size": "50x25",
        "printer_language": "ZPL",
        "printer_family": "ZPL",
        "raw_template": """^XA
^FO20,10^BCN,50,Y,N,N^FD{barcode}^FS
^FO20,75^A0N,20,20^FD{brand} | {style}^FS
^FO20,98^A0N,22,22^FDMRP: Rs. {mrp}^FS
^FO20,122^A0N,18,18^FDSize: {size} | Col: {color}^FS
^FO20,142^A0N,14,14^FDPkd: {pkd_date}^FS
^XZ"""
    },
    {
        "name": "Retail Apparel Tag (50x30)",
        "template_title": "Retail Apparel Tag (50x30)",
        "label_size": "50x30",
        "printer_language": "ZPL",
        "printer_family": "ZPL",
        "raw_template": """^XA
^FO25,15^A0N,24,24^FD{brand}^FS
^FO25,42^A0N,20,20^FD{item_name}^FS
^FO25,68^BCN,55,Y,N,N^FD{barcode}^FS
^FO25,140^A0N,26,26^FDMRP: Rs. {mrp}^FS
^FO25,170^A0N,20,20^FDSTYLE: {style_code} | SIZE: {size}^FS
^FO25,195^A0N,16,16^FD(Incl. of all taxes) | Pkd: {pkd_date}^FS
^XZ"""
    },
    {
        "name": "Box & Logistics Tag (75x50)",
        "template_title": "Box & Logistics Tag (75x50)",
        "label_size": "75x50",
        "printer_language": "TSPL",
        "printer_family": "TSPL",
        "raw_template": """SIZE 75 mm, 50 mm
GAP 3 mm, 0 mm
SPEED 4
DENSITY 12
CLS
TEXT 30,20,"3",0,1,1,"BRAND: {brand}"
TEXT 30,55,"2",0,1,1,"ITEM: {item_name}"
TEXT 30,85,"2",0,1,1,"STYLE: {style_code}"
TEXT 30,115,"3",0,1,1,"SIZE: {size}   COLOR: {color}"
BARCODE 30,150,"128",80,1,0,2,4,"{barcode}"
TEXT 30,245,"3",0,1,1,"MRP: Rs. {mrp}"
TEXT 30,280,"2",0,1,1,"(Inclusive of all taxes)"
TEXT 30,310,"1",0,1,1,"Pkd Date: {pkd_date}"
PRINT 1,1"""
    },
    {
        "name": "Enterprise Master Carton Tag (100x50)",
        "template_title": "Enterprise Master Carton Tag (100x50)",
        "label_size": "100x50",
        "printer_language": "TSPL",
        "printer_family": "TSPL",
        "raw_template": """SIZE 100 mm, 50 mm
GAP 3 mm, 0 mm
SPEED 4
DENSITY 14
CLS
TEXT 40,20,"4",0,1,1,"{brand} - MASTER CARTON"
TEXT 40,65,"3",0,1,1,"STYLE / ARTICLE: {style_code}"
TEXT 40,105,"3",0,1,1,"COLOUR: {color} | SIZE: {size}"
TEXT 40,145,"3",0,1,1,"MRP: Rs. {mrp} (INCL. TAXES)"
BARCODE 40,195,"128",100,1,0,3,6,"{barcode}"
TEXT 40,310,"2",0,1,1,"SUPPLIER: {supplier} | PACK: {pack_size}"
TEXT 40,340,"2",0,1,1,"MERCH CAT: {merchandise_category}"
PRINT 1,1"""
    }
]

def seed_templates():
    if not smriti.db.exists("DocType", "SMRITI Print Template"):
        print("[Seed Print Templates] DocType 'SMRITI Print Template' not installed yet.")
        return

    seeded_count = 0
    for t in DEFAULT_TEMPLATES:
        if not smriti.db.exists("SMRITI Print Template", t["name"]):
            smriti.documents.create("SMRITI Print Template", **t)
            seeded_count += 1
            print(f" [OK] Seeded template: {t['name']}")

    smriti.db.commit()
    print(f"Done! Seeded {seeded_count} default templates into SMRITI Print Template.")

if __name__ == "__main__":
    seed_templates()
